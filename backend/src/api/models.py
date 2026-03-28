"""
API Response Models for Todo AI Chatbot (Phase III)

Standardized request/response models for FastAPI endpoints.
Provides consistent error handling and user-friendly messages.

Architecture Principles:
- Type-safe: Pydantic models for validation
- User-friendly: Clear error messages
- Consistent: Standard format across all endpoints
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# =====================================================
# Common Response Models
# =====================================================

class ErrorResponse(BaseModel):
    """
    Standard error response model.

    Attributes:
        error: Error message (user-friendly)
        detail: Optional technical error details
        code: Optional error code for client handling
    """
    error: str = Field(..., description="User-friendly error message")
    detail: Optional[str] = Field(None, description="Technical error details")
    code: Optional[str] = Field(None, description="Error code for client handling")


class HealthResponse(BaseModel):
    """
    Health check response model.

    Attributes:
        status: Service status (healthy/unhealthy)
        version: API version string
        database: Database connection status
        mcp_server: MCP server status
    """
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")
    mcp_server: str = Field(..., description="MCP server status")


# =====================================================
# Chat Request/Response Models
# =====================================================

class ChatRequest(BaseModel):
    """
    Chat endpoint request model.

    Attributes:
        message: User message text
        conversation_id: Optional conversation UUID for context
    """
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation UUID for context")


class ToolCall(BaseModel):
    """
    MCP tool call information.

    Attributes:
        tool: Tool name (e.g., "add_task")
        parameters: Tool parameters
        result: Tool execution result
    """
    tool: str = Field(..., description="MCP tool name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    result: Optional[str] = Field(None, description="Tool execution result")


class ChatResponse(BaseModel):
    """
    Chat endpoint response model.

    Attributes:
        conversation_id: Conversation UUID
        response: Assistant response text
        tool_calls: List of MCP tools invoked
    """
    conversation_id: str = Field(..., description="Conversation UUID")
    response: str = Field(..., description="Assistant response text")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="MCP tools invoked")


# =====================================================
# SSE Streaming Models
# =====================================================

class ChatChunk(BaseModel):
    """
    SSE chat chunk for streaming responses.

    Attributes:
        type: Chunk type (token/done/error)
        content: Chunk content
        conversation_id: Conversation UUID
        tool_calls: Tool calls (on done chunk)
    """
    type: str = Field(..., description="Chunk type: token, done, error")
    content: Optional[str] = Field(None, description="Chunk content")
    conversation_id: Optional[str] = Field(None, description="Conversation UUID")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls on done")


# =====================================================
# Task Response Models
# =====================================================

class TaskResponse(BaseModel):
    """
    Task data response model.

    Attributes:
        id: Task ID
        title: Task title
        description: Optional task description
        completed: Task completion status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    """
    Task list response model.

    Attributes:
        tasks: List of tasks
        count: Total task count
    """
    tasks: List[TaskResponse]
    count: int = Field(..., description="Total task count")


# =====================================================
# Validation Errors
# =====================================================

class ValidationErrorDetail(BaseModel):
    """
    Validation error detail.

    Attributes:
        field: Field name with error
        message: Error message
    """
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Error message")


class ValidationErrorResponse(BaseModel):
    """
    Validation error response.

    Attributes:
        error: General error message
        details: List of validation errors
    """
    error: str = Field(default="Validation error", description="General error message")
    details: List[ValidationErrorDetail] = Field(..., description="List of validation errors")


# =====================================================
# Error Codes
# =====================================================

class ErrorCode:
    """Standard error codes for client handling."""

    # Authentication errors
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_TOKEN = "INVALID_TOKEN"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"

    # Permission errors
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"

    # Server errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # MCP tool errors
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"


# =====================================================
# Helper Functions
# =====================================================

def create_error_response(
    message: str,
    code: Optional[str] = None,
    detail: Optional[str] = None
) -> ErrorResponse:
    """
    Create standardized error response.

    Args:
        message: User-friendly error message
        code: Optional error code
        detail: Optional technical details

    Returns:
        ErrorResponse object
    """
    return ErrorResponse(
        error=message,
        detail=detail,
        code=code
    )


def create_validation_error_response(errors: List[Dict[str, str]]) -> ValidationErrorResponse:
    """
    Create validation error response from Pydantic errors.

    Args:
        errors: List of Pydantic validation errors

    Returns:
        ValidationErrorResponse object
    """
    details = [
        ValidationErrorDetail(
            field=str(error.get("loc", ["unknown"])[0]),
            message=error.get("msg", "Unknown error")
        )
        for error in errors
    ]

    return ValidationErrorResponse(
        error="Validation error",
        details=details
    )
