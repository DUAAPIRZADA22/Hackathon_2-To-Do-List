"""
Simple Chat API - Working with Phase I/II Authentication
Uses the same auth system as tasks API for consistency.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import structlog

# Use Phase I/II authentication (same as tasks API)
from src.auth.jwt import get_current_active_user
from src.models.user import User


# =====================================================
# Router
# =====================================================

router = APIRouter()


# =====================================================
# Request/Response Models
# =====================================================

class SimpleChatRequest(BaseModel):
    message: str


class SimpleChatResponse(BaseModel):
    response: str


# =====================================================
# Simple Chat Endpoint
# =====================================================

@router.post(
    "/api/simple-chat",
    response_model=SimpleChatResponse,
    tags=["Chat"],
    summary="Simple chat with task creation support",
)
async def simple_chat(
    request: SimpleChatRequest,
    current_user: User = Depends(get_current_active_user)
) -> SimpleChatResponse:
    """
    Simple chat endpoint that uses Phase I/II authentication.
    Creates tasks using the same sync database as tasks API.
    """
    logger = structlog.get_logger().bind(user_id=current_user.id)

    logger.info("Simple chat request", message_length=len(request.message))

    try:
        # Import AgentRunner here to avoid issues
        from src.agent.runner import AgentRunner

        # Run agent with the authenticated user's ID
        agent = AgentRunner(user_id=str(current_user.id))
        result = await agent.chat(
            message=request.message,
            conversation_history=[],
            stream=False
        )

        return SimpleChatResponse(response=result["response"])

    except Exception as e:
        logger.error("Simple chat failed", error=str(e), type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI response: {str(e)}"
        )


__all__ = ["router"]
