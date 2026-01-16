"""
Database module for Todo AI Chatbot (Phase III)

Exports:
- Models: Task, Conversation, Message and Pydantic schemas
- Session: Database engine and session management
- Repository: Data access layer with user identity enforcement
"""

# Try backend.src imports first, fall back to src imports
try:
    from backend.src.db.models import (
        Task,
        Conversation,
        Message,
        TaskCreate,
        TaskRead,
        TaskUpdate,
        ConversationCreate,
        ConversationRead,
        MessageCreate,
        MessageRead,
    )

    from backend.src.db.session import (
        engine,
        async_session_maker,
        get_session,
        init_db,
        close_db,
        check_db_connection,
    )

    from backend.src.db.repository import (
        TaskRepository,
        ConversationRepository,
    )
except ImportError:
    from src.db.models import (
        Task,
        Conversation,
        Message,
        TaskCreate,
        TaskRead,
        TaskUpdate,
        ConversationCreate,
        ConversationRead,
        MessageCreate,
        MessageRead,
    )

    from src.db.session import (
        engine,
        async_session_maker,
        get_session,
        init_db,
        close_db,
        check_db_connection,
    )

    from src.db.repository import (
        TaskRepository,
        ConversationRepository,
    )

__all__ = [
    # Models
    "Task",
    "Conversation",
    "Message",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    "ConversationCreate",
    "ConversationRead",
    "MessageCreate",
    "MessageRead",
    # Session
    "engine",
    "async_session_maker",
    "get_session",
    "init_db",
    "close_db",
    "check_db_connection",
    # Repository
    "TaskRepository",
    "ConversationRepository",
]
