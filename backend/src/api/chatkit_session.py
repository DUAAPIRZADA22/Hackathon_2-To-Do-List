"""
ChatKit Session API Endpoint

Implements POST /api/chatkit/session endpoint for creating ChatKit sessions.
This endpoint generates a client secret for the ChatKit web component.

Reference: https://platform.openai.com/docs/guides/chatkit
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI
import structlog

# Try backend.src imports first, fall back to src imports
try:
    from backend.src.api.dependencies import get_db, AuthenticatedRequest
    from backend.src.auth.middleware import extract_token_from_header_or_query_manual
except ImportError:
    from src.api.dependencies import get_db, AuthenticatedRequest
    from src.auth.middleware import extract_token_from_header_or_query_manual


# =====================================================
# Router
# =====================================================

router = APIRouter()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# =====================================================
# Request/Response Models
# =====================================================

class ChatKitSessionRequest(BaseModel):
    """Request model for creating a ChatKit session."""
    thread_id: Optional[str] = None  # Optional thread ID for continuing conversations


class ChatKitSessionResponse(BaseModel):
    """Response model for ChatKit session creation."""
    client_secret: str
    expires_at: Optional[int] = None


# =====================================================
# ChatKit Session Endpoint
# =====================================================

@router.post(
    "/api/chatkit/session",
    response_model=ChatKitSessionResponse,
    tags=["ChatKit"],
    summary="Create ChatKit session",
    description="Creates a ChatKit session and returns a client secret for the web component"
)
async def create_chatkit_session(
    request: ChatKitSessionRequest,
    auth_req: AuthenticatedRequest = Depends(AuthenticatedRequest)
) -> ChatKitSessionResponse:
    """
    Create a ChatKit session for the authenticated user.

    This endpoint calls OpenAI's ChatKit sessions API to generate
    a client secret that the ChatKit web component can use.

    Note: Requires CHATKIT_WORKFLOW_ID env var set with an Agent Builder workflow ID.
    For local development without a workflow, this will return a mock session.
    """
    logger = structlog.get_logger().bind(user_id=auth_req.user_id)

    logger.info("ChatKit session request received", thread_id=request.thread_id)

    api_key = os.environ.get("OPENAI_API_KEY")
    workflow_id = os.environ.get("CHATKIT_WORKFLOW_ID")

    if not api_key:
        logger.error("OPENAI_API_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )

    try:
        # Use OpenAI SDK to create ChatKit session (official method)
        # Reference: https://github.com/openai/chatkit-js/blob/main/README.md

        logger.info("Creating ChatKit session with OpenAI SDK", workflow_id=workflow_id)

        # Build session parameters
        session_params = {}

        if workflow_id:
            session_params["workflow"] = {"id": workflow_id}
        else:
            logger.warning("CHATKIT_WORKFLOW_ID not set - Agent Builder workflow recommended")

        # Add user identification
        session_params["user"] = str(auth_req.user_id)

        # Configure chatkit settings
        session_params["chatkit_configuration"] = {
            "file_upload": {"enabled": False}
        }

        # Create session using OpenAI SDK's chatkit.sessions.create()
        session = openai_client.chatkit.sessions.create(**session_params)

        logger.info(
            "ChatKit session created successfully",
            session_id=getattr(session, 'id', 'N/A')
        )

        return ChatKitSessionResponse(
            client_secret=session.client_secret,
            expires_at=getattr(session, 'expires_at', None)
        )

    except Exception as e:
        logger.error("Failed to create ChatKit session", error=str(e), type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ChatKit session: {str(e)}"
        )


# =====================================================
# Router Export
# =====================================================

__all__ = ["router"]
