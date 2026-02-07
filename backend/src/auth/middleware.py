"""
Authentication Middleware for Todo AI Chatbot (Phase III)

Implements Better Auth JWT validation and user identity extraction.
Enforces user authentication at all API layers.

Architecture Principles:
- User identity: All requests must include valid user ID
- Better Auth integration: Uses existing auth from Phase I/II
- JWT validation: Verifies session tokens from Better Auth
- Security first: No authenticated endpoints bypass this layer
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# Load .env file at module import time
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)


# =====================================================
# Configuration
# =====================================================

# Use SECRET_KEY to match the existing auth system (src.auth.jwt)
# This ensures tokens created by signin/signup work properly
def get_jwt_secret() -> str:
    """
    Get JWT secret from environment.

    Returns:
        JWT secret key

    Raises:
        ValueError: If SECRET_KEY not set
    """
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise ValueError(
            "SECRET_KEY environment variable not set. "
            "Please configure it in your .env file or start_server.py"
        )
    return secret

JWT_ALGORITHM = "HS256"


# =====================================================
# JWT Validation
# =====================================================

def validate_jwt_token(token: str) -> dict:
    """
    Validate JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Decoded JWT payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID string

    Raises:
        HTTPException: If user_id not found in token
    """
    payload = validate_jwt_token(token)
    user_id = payload.get("sub") or payload.get("userId") or payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return str(user_id)


# =====================================================
# FastAPI Security Schemes
# =====================================================

# HTTP Bearer token scheme for FastAPI
# Using class directly in Depends() - this is the standard pattern
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract and validate user ID from request.

    Usage in FastAPI endpoints:
        @app.get("/api/tasks")
        async def list_tasks(user_id: str = Depends(get_current_user)):
            # user_id is guaranteed to be valid
            ...

    Args:
        credentials: HTTP Bearer credentials (auto-extracted by FastAPI)

    Returns:
        Validated user ID string

    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a valid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    return extract_user_id_from_token(token)


async def require_user(user_id: str) -> str:
    """
    Additional dependency to enforce user authentication.

    This is a passthrough that can be used for explicit intent.

    Usage:
        @app.get("/api/tasks")
        async def list_tasks(
            current_user: str = Depends(get_current_user),
            user_id: str = Depends(require_user)
        ):
            # Both dependencies return the same validated user_id
            ...

    Args:
        user_id: User ID from get_current_user

    Returns:
        Same user ID (passes through)
    """
    # This is already validated by get_current_user
    # This dependency exists for explicit intent in endpoint signatures
    return user_id


# =====================================================
# Optional Authentication (for public endpoints)
# =====================================================

async def get_token_from_header_or_query(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    token: Optional[str] = None
) -> str:
    """
    Extract JWT token from Authorization header or query parameter.

    This is useful for SSE endpoints where EventSource doesn't support
    custom headers. The token can be passed as a query parameter instead.

    Args:
        credentials: HTTP Bearer credentials (auto-extracted by FastAPI)
        token: Token from query parameter (for SSE/EventSource)

    Returns:
        Validated user ID string

    Raises:
        HTTPException: If authentication fails
    """
    # First try header, then query parameter
    jwt_token = None
    if credentials is not None:
        jwt_token = credentials.credentials
    elif token is not None:
        jwt_token = token

    if jwt_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a valid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return extract_user_id_from_token(jwt_token)


def extract_token_from_header_or_query_manual(
    auth_header: Optional[str] = None,
    token: Optional[str] = None
) -> str:
    """
    Manually extract JWT token from Authorization header or query parameter.

    This is a helper function that can be called directly (not as a dependency)
    for endpoints that need to manually extract the token.

    Args:
        auth_header: Raw Authorization header value
        token: Token from query parameter

    Returns:
        Validated user ID string

    Raises:
        HTTPException: If authentication fails
    """
    jwt_token = None

    # Try to extract from Authorization header
    if auth_header:
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header[7:]  # Remove "Bearer " prefix
        else:
            jwt_token = auth_header
    # Fall back to query parameter
    elif token:
        jwt_token = token

    if jwt_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a valid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return extract_user_id_from_token(jwt_token)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security)
) -> Optional[str]:
    """
    FastAPI dependency for optional authentication.

    Returns None if no token provided, validates token if present.

    Usage in FastAPI endpoints:
        @app.get("/api/health")
        async def health_check(user_id: Optional[str] = Depends(get_optional_user)):
            # user_id is None if not authenticated
            ...

    Args:
        credentials: HTTP Bearer credentials (auto-extracted by FastAPI)

    Returns:
        Validated user ID string or None
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        return extract_user_id_from_token(token)
    except HTTPException:
        # If token is invalid, return None instead of raising
        return None


# =====================================================
# User Context Helper
# =====================================================

class UserContext:
    """
    Helper class for passing user context through the application.

    Used to ensure user identity is enforced at all layers.
    """

    def __init__(self, user_id: str):
        """
        Initialize user context.

        Args:
            user_id: Validated user ID
        """
        self.user_id = user_id

    def __str__(self) -> str:
        return self.user_id

    def verify_ownership(self, resource_user_id: str) -> None:
        """
        Verify that a resource belongs to the current user.

        Args:
            resource_user_id: User ID of the resource

        Raises:
            HTTPException: If resource doesn't belong to user
        """
        if resource_user_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource",
            )


# =====================================================
# Development Helpers
# =====================================================

def create_mock_token(user_id: str, secret: Optional[str] = None) -> str:
    """
    Create a mock JWT token for testing/development.

    WARNING: Only use in development environments!

    Args:
        user_id: User ID to encode in token
        secret: Optional JWT secret (uses env var if not provided)

    Returns:
        Mock JWT token string
    """
    import time

    payload = {
        "sub": user_id,
        "userId": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # 1 hour
    }

    return jwt.encode(
        payload,
        secret or get_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )
