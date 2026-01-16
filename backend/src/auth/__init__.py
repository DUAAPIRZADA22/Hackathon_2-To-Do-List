"""
Authentication module for Todo AI Chatbot (Phase III)

Exports:
- Middleware: JWT validation and user ID extraction
"""

try:
    from backend.src.auth.middleware import (
        get_current_user,
        get_optional_user,
        require_user,
        extract_user_id_from_token,
        validate_jwt_token,
        UserContext,
        create_mock_token,
        security,
        get_token_from_header_or_query,
        extract_token_from_header_or_query_manual,
    )
except ImportError:
    from src.auth.middleware import (
        get_current_user,
        get_optional_user,
        require_user,
        extract_user_id_from_token,
        validate_jwt_token,
        UserContext,
        create_mock_token,
        security,
        get_token_from_header_or_query,
        extract_token_from_header_or_query_manual,
    )

__all__ = [
    # Middleware
    "get_current_user",
    "get_optional_user",
    "require_user",
    "extract_user_id_from_token",
    "validate_jwt_token",
    "UserContext",
    "create_mock_token",
    "security",
    "get_token_from_header_or_query",
    "extract_token_from_header_or_query_manual",
]

# Note: Dependencies (get_db, get_authenticated_user, etc.) are exported from
# backend.src.api.dependencies to avoid circular imports
