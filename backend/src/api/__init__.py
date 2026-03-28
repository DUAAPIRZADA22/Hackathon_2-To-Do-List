"""
API module for Todo AI Chatbot (Phase III)

FastAPI endpoints and request/response models.
Provides REST API for chat interaction with AI agent.

Exports:
- Models: Request/response models for all endpoints
- Dependencies: FastAPI dependencies for auth and database
"""

# Try backend.src imports first, fall back to src imports
try:
    from backend.src.api.models import (
        ErrorResponse,
        HealthResponse,
        ChatRequest,
        ChatResponse,
        ChatChunk,
        ToolCall,
        TaskResponse,
        TaskListResponse,
        ValidationErrorResponse,
        ErrorCode,
        create_error_response,
        create_validation_error_response,
    )

    from backend.src.api.dependencies import (
        get_db,
        get_current_user,
        get_optional_user,
        get_authenticated_user,
        get_optional_authenticated_user,
        get_conversation_id,
        AuthenticatedRequest,
    )
except ImportError:
    from src.api.models import (
        ErrorResponse,
        HealthResponse,
        ChatRequest,
        ChatResponse,
        ChatChunk,
        ToolCall,
        TaskResponse,
        TaskListResponse,
        ValidationErrorResponse,
        ErrorCode,
        create_error_response,
        create_validation_error_response,
    )

    from src.api.dependencies import (
        get_db,
        get_current_user,
        get_optional_user,
        get_authenticated_user,
        get_optional_authenticated_user,
        get_conversation_id,
        AuthenticatedRequest,
    )

__all__ = [
    # Models
    "ErrorResponse",
    "HealthResponse",
    "ChatRequest",
    "ChatResponse",
    "ChatChunk",
    "ToolCall",
    "TaskResponse",
    "TaskListResponse",
    "ValidationErrorResponse",
    "ErrorCode",
    "create_error_response",
    "create_validation_error_response",
    # Dependencies
    "get_db",
    "get_current_user",
    "get_optional_user",
    "get_authenticated_user",
    "get_optional_authenticated_user",
    "get_conversation_id",
    "AuthenticatedRequest",
]
