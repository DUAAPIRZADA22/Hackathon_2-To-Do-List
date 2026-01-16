"""
Chat API Endpoint for Todo AI Chatbot (Phase III - User Story 1)

Implements POST /api/{user_id}/chat endpoint with SSE streaming.
Handles message persistence, agent execution, and response formatting.

Architecture Principles:
- Stateless: All conversation state in database
- User identity: Enforced at all layers
- SSE streaming: Real-time token delivery to frontend
- Error handling: Graceful degradation on failures
"""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

# Try backend.src imports first, fall back to src imports
try:
    from backend.src.api.dependencies import get_db, AuthenticatedRequest
    from backend.src.api.models import ChatRequest, ChatResponse, ToolCall
    from backend.src.agent.runner import AgentRunner
    from backend.src.db.repository import ConversationRepository
    from backend.src.agent.context import ConversationContextManager
    from backend.src.auth.middleware import extract_token_from_header_or_query_manual
except ImportError:
    from src.api.dependencies import get_db, AuthenticatedRequest
    from src.api.models import ChatRequest, ChatResponse, ToolCall
    from src.agent.runner import AgentRunner
    from src.db.repository import ConversationRepository
    from src.agent.context import ConversationContextManager
    from src.auth.middleware import extract_token_from_header_or_query_manual


# =====================================================
# Router
# =====================================================

router = APIRouter()


# =====================================================
# Chat Endpoint
# =====================================================

@router.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Chat with AI assistant",
    description="Send a message to the AI assistant and get a response with tool calls"
)
async def chat(
    user_id: str,
    request: ChatRequest,
    auth_req: AuthenticatedRequest = Depends(AuthenticatedRequest)
) -> ChatResponse:
    """
    Chat endpoint for AI-powered task management.

    Args:
        user_id: User ID from URL path (as string from JWT)
        request: Chat request with message and optional conversation_id
        auth_req: Authenticated request context

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls

    Raises:
        HTTPException: If authentication fails or request is invalid

    Example:
        POST /api/6/chat
        {
            "message": "Add a task to buy groceries",
            "conversation_id": null
        }

        Response:
        {
            "conversation_id": "12345678-1234-5678-1234-567812345678",
            "response": "I've added that task for you!",
            "tool_calls": [
                {
                    "tool": "add_task",
                    "parameters": {"title": "Buy groceries"},
                    "result": "Task created successfully"
                }
            ]
        }
    """
    logger = structlog.get_logger().bind(
        user_id=user_id,
        request_id=auth_req.ctx.user_id
    )

    # Verify user identity (T038: User identity enforcement)
    if auth_req.user_id != user_id:
        logger.warning("User ID mismatch", auth_user=auth_req.user_id, path_user=user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch. You can only access your own conversations."
        )

    logger.info("Chat request received", message_length=len(request.message))

    try:
        # Prepare conversation (T040: Conversation creation logic)
        context_manager = ConversationContextManager()
        conversation_id, context = await context_manager.prepare_conversation(
            user_id=user_id,
            conversation_id=(
                uuid.UUID(request.conversation_id) if request.conversation_id else None
            ),
            user_message=request.message,
            db_session=auth_req.db
        )

        # Save user message to database (T038: Message persistence)
        await context_manager.save_message(
            user_id=user_id,
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            db_session=auth_req.db
        )

        # Execute agent (T038: Agent execution)
        agent = AgentRunner(user_id=user_id)
        result = await agent.chat(
            message=request.message,
            conversation_history=context[1:],  # Skip system message
            stream=False
        )

        # Save assistant message to database
        # Format tool_calls as JSON string for storage
        tool_calls_json = json.dumps([
            {
                "id": tc.get("id"),
                "name": tc["name"],
                "arguments": tc["arguments"]
            }
            for tc in result["tool_calls"]
        ]) if result["tool_calls"] else None

        await context_manager.save_message(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"],
            tool_calls=tool_calls_json,
            db_session=auth_req.db
        )

        # Format response (T038: Response formatting)
        tool_calls_formatted = [
            ToolCall(
                tool=tc["name"],
                parameters=tc["arguments"],
                result=json.dumps(tc.get("result")) if tc.get("result") else None
            )
            for tc in result["tool_calls"]
        ]

        response = ChatResponse(
            conversation_id=str(conversation_id),
            response=result["response"],
            tool_calls=tool_calls_formatted
        )

        logger.info(
            "Chat request completed",
            conversation_id=str(conversation_id),
            tool_call_count=len(result["tool_calls"]),
            finished=result["finished"]
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (auth, validation)
        raise

    except Exception as e:
        logger.error("Chat request failed", error=str(e), type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


# =====================================================
# SSE Streaming Endpoint (T039)
# =====================================================

@router.get(
    "/api/{user_id}/chat/stream",
    tags=["Chat"],
    summary="Chat with streaming response",
    description="Send a message and stream the AI response via Server-Sent Events"
)
async def chat_stream(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None,
    token: Optional[str] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat endpoint with SSE streaming.

    Yields response tokens as they arrive from the AI agent.

    Args:
        user_id: User ID from URL path (as string from JWT)
        message: User message (query parameter)
        conversation_id: Optional conversation ID (query parameter)
        token: JWT token (query parameter for SSE/EventSource)
        request: FastAPI Request object
        db: Database session

    Returns:
        StreamingResponse with SSE events

    Example:
        GET /api/6/chat/stream?message=Add a task to buy groceries&token=xxx

        SSE events:
        data: {"type": "token", "content": "I've"}
        data: {"type": "token", "content": " added"}
        data: {"type": "token", "content": " that"}
        ...
        data: {"type": "done", "conversation_id": "...", "tool_calls": [...]}
    """
    # Get Authorization header from request
    auth_header = request.headers.get("Authorization") if request else None

    # Get authenticated user ID from token (header or query param)
    auth_user_id = extract_token_from_header_or_query_manual(
        auth_header=auth_header,
        token=token
    )

    # Verify user identity
    if auth_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )

    logger = structlog.get_logger().bind(user_id=user_id)

    # DEBUG: Log incoming request parameters
    print(f"[DEBUG STREAM ENDPOINT] user_id={user_id}, message={message}, conversation_id={conversation_id}")
    logger.info("Chat stream request received", conversation_id=conversation_id)

    async def stream_generator():
        """Generate SSE events for streaming response."""

        try:
            # Prepare conversation
            context_manager = ConversationContextManager()
            conversation_id_uuid, context = await context_manager.prepare_conversation(
                user_id=user_id,
                conversation_id=(
                    uuid.UUID(conversation_id) if conversation_id else None
                ),
                user_message=message,
                db_session=db
            )

            # Save user message
            await context_manager.save_message(
                user_id=user_id,
                conversation_id=conversation_id_uuid,
                role="user",
                content=message,
                db_session=db
            )

            # Stream agent response (T039: SSE streaming support)
            agent = AgentRunner(user_id=user_id)

            # For now, use non-streaming and send as chunks
            # Full token-level streaming requires more complex setup
            result = await agent.chat(
                message=message,
                conversation_history=context[1:],
                stream=False
            )

            # Send response in chunks for demo
            response_text = result["response"]
            chunk_size = 5  # Send 5 characters at a time for demo

            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i + chunk_size]
                event = {
                    "type": "token",
                    "content": chunk
                }
                yield f"data: {json.dumps(event)}\n\n"

            # Send final event with conversation_id and tool_calls
            tool_calls_data = [
                {
                    "tool": tc["name"],
                    "parameters": tc["arguments"],
                    "result": tc.get("result")  # Include tool result data
                }
                for tc in result["tool_calls"]
            ]

            final_event = {
                "type": "done",
                "conversation_id": str(conversation_id_uuid),
                "tool_calls": tool_calls_data
            }
            yield f"data: {json.dumps(final_event)}\n\n"

            # Save assistant message
            tool_calls_json = json.dumps([
                {
                    "id": tc.get("id"),
                    "name": tc["name"],
                    "arguments": tc["arguments"]
                }
                for tc in result["tool_calls"]
            ]) if result["tool_calls"] else None

            await context_manager.save_message(
                user_id=user_id,
                conversation_id=conversation_id_uuid,
                role="assistant",
                content=result["response"],
                tool_calls=tool_calls_json,
                db_session=db
            )

        except Exception as e:
            logger.error("Stream error", error=str(e))
            error_event = {
                "type": "error",
                "content": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering
        }
    )


# =====================================================
# Router Export
# =====================================================

__all__ = ["router"]


