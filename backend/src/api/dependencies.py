"""
FastAPI Dependencies for Todo AI Chatbot (Phase III)

Common dependencies for FastAPI endpoints.
Provides authentication, database session, and request context.

Architecture Principles:
- Type-safe: All dependencies return typed values
- User identity: All authenticated endpoints enforce user ownership
- Session management: Database sessions managed per-request
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.src.auth.middleware import get_current_user, get_optional_user
    from backend.src.db.session import get_session
    from backend.src.auth.middleware import UserContext
except ImportError:
    from src.auth.middleware import get_current_user, get_optional_user
    from src.db.session import get_session
    from src.auth.middleware import UserContext


# =====================================================
# Common Dependencies
# =====================================================

async def get_db(
    session: AsyncSession = Depends(get_session)
) -> AsyncSession:
    """
    Dependency that provides a database session.

    Usage:
        @app.get("/api/tasks")
        async def list_tasks(db: AsyncSession = Depends(get_db)):
            ...
    """
    return session


async def get_authenticated_user(
    user_id: str = Depends(get_current_user)
) -> UserContext:
    """
    Dependency that provides a UserContext for authenticated requests.

    Enforces that user is authenticated and provides context object
    that can be used for ownership verification.

    Usage:
        @app.post("/api/tasks")
        async def create_task(
            ctx: UserContext = Depends(get_authenticated_user),
            db: AsyncSession = Depends(get_db)
        ):
            # ctx.user_id is guaranteed to be valid
            # ctx.verify_ownership(resource_user_id) to check ownership
            ...

    Returns:
        UserContext object with validated user_id
    """
    return UserContext(user_id)


async def get_optional_authenticated_user(
    user_id: Optional[str] = Depends(get_optional_user)
) -> Optional[UserContext]:
    """
    Dependency that provides optional UserContext.

    Returns UserContext if authenticated, None otherwise.

    Usage:
        @app.get("/api/health")
        async def health_check(
            ctx: Optional[UserContext] = Depends(get_optional_authenticated_user)
        ):
            if ctx:
                # Authenticated request
                ...
            else:
                # Unauthenticated request
                ...

    Returns:
        UserContext object or None
    """
    return UserContext(user_id) if user_id else None


# =====================================================
# Path Parameter Dependencies
# =====================================================

async def get_conversation_id(
    conversation_id: Optional[UUID] = None
) -> Optional[UUID]:
    """
    Dependency for extracting conversation_id from path/query.

    Usage:
        @app.post("/api/{user_id}/chat")
        async def chat(
            conversation_id: Optional[UUID] = Depends(get_conversation_id),
            ...
        ):
            # conversation_id is UUID or None
            ...

    Args:
        conversation_id: Optional conversation UUID from request

    Returns:
        Conversation UUID or None
    """
    return conversation_id


# =====================================================
# Combined Dependencies
# =====================================================

class AuthenticatedRequest:
    """
    Combined dependency for authenticated requests with database access.

    Provides user context, database session, and common utilities in one object.
    """

    def __init__(
        self,
        user_id: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        """
        Initialize authenticated request context.

        Args:
            user_id: Validated user ID from JWT
            db: Database session
        """
        self.ctx = UserContext(user_id)
        self.db = db
        self.user_id = user_id

    def verify_ownership(self, resource_user_id: str) -> None:
        """
        Verify that a resource belongs to the current user.

        Args:
            resource_user_id: User ID of the resource

        Raises:
            HTTPException: If resource doesn't belong to user
        """
        self.ctx.verify_ownership(resource_user_id)


# Export commonly used dependencies
__all__ = [
    "get_db",
    "get_current_user",
    "get_optional_user",
    "get_authenticated_user",
    "get_optional_authenticated_user",
    "get_conversation_id",
    "AuthenticatedRequest",
    "UserContext",
]
