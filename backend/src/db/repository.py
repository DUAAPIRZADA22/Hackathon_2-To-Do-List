"""
Database Repository Layer for Todo AI Chatbot (Phase III)

Implements data access layer with user identity enforcement.
All repository methods enforce user ownership (users can only access their own data).

Architecture Principles:
- User identity: All methods require and enforce user_id
- Type-safe: Uses SQLModel with type hints
- Explicit transactions: Session management handled by caller
- No ORM magic: Clear SQL operations via SQLAlchemy Core

Note: user_id and task_id are accepted as strings (from JWT) and converted to int internally
"""

from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.src.db.models import Task, Conversation, Message
except ImportError:
    from src.db.models import Task, Conversation, Message


def _to_int(value: Union[str, int]) -> int:
    """Convert string or int to int for database operations."""
    if isinstance(value, int):
        return value
    return int(value)


# =====================================================
# Task Repository
# =====================================================

class TaskRepository:
    """Data access layer for Task entity."""

    @staticmethod
    async def get_task(session: AsyncSession, user_id: Union[str, int], task_id: Union[str, int]) -> Optional[Task]:
        """
        Get a single task by ID.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            task_id: Task ID to retrieve - converted from string to int

        Returns:
            Task object if found and owned by user, None otherwise
        """
        user_id_int = _to_int(user_id)
        task_id_int = _to_int(task_id)
        query = select(Task).where(
            Task.id == task_id_int,
            Task.user_id == user_id_int  # Enforce user ownership
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_task(session: AsyncSession, user_id: Union[str, int], title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            title: Task title
            description: Optional task description

        Returns:
            Created Task object
        """
        user_id_int = _to_int(user_id)
        task = Task(
            user_id=user_id_int,
            title=title,
            description=description,
            completed=False,
            status="todo",
            priority="medium"
        )
        session.add(task)
        await session.flush()  # Get ID without committing
        return task

    @staticmethod
    async def list_tasks(
        session: AsyncSession,
        user_id: Union[str, int],
        status: str = "all"
    ) -> List[Task]:
        """
        List all tasks for a user, optionally filtered by status.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            status: Filter by status ('all', 'pending', 'completed')

        Returns:
            List of Task objects (sorted by created_at DESC)
        """
        user_id_int = _to_int(user_id)
        query = select(Task).where(Task.user_id == user_id_int)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        # Sort by creation date (newest first)
        query = query.order_by(desc(Task.created_at))

        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_task(
        session: AsyncSession,
        user_id: Union[str, int],
        task_id: Union[str, int],
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> Optional[Task]:
        """
        Update a task.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            task_id: Task ID to update - converted from string to int
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Updated Task object if found and owned by user, None otherwise
        """
        user_id_int = _to_int(user_id)
        task_id_int = _to_int(task_id)

        # Build update values dict (only include non-None values)
        update_values = {}
        if title is not None:
            update_values["title"] = title
        if description is not None:
            update_values["description"] = description
        if completed is not None:
            update_values["completed"] = completed
            # Sync status with completed for API compatibility
            update_values["status"] = "done" if completed else "todo"

        if not update_values:
            # No updates to make
            return await TaskRepository.get_task(session, user_id_int, task_id_int)

        # Execute update with user ownership enforcement
        query = update(Task).where(
            Task.id == task_id_int,
            Task.user_id == user_id_int  # Enforce user ownership
        ).values(**update_values).returning(Task)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_task(session: AsyncSession, user_id: Union[str, int], task_id: Union[str, int]) -> bool:
        """
        Delete a task.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            task_id: Task ID to delete - converted from string to int

        Returns:
            True if task was deleted, False if not found or not owned by user
        """
        user_id_int = _to_int(user_id)
        task_id_int = _to_int(task_id)
        query = delete(Task).where(
            Task.id == task_id_int,
            Task.user_id == user_id_int  # Enforce user ownership
        )
        result = await session.execute(query)
        return result.rowcount > 0


# =====================================================
# Conversation Repository
# =====================================================

class ConversationRepository:
    """Data access layer for Conversation entity."""

    @staticmethod
    async def get_conversation(session: AsyncSession, user_id: Union[str, int], conversation_id: UUID) -> Optional[Conversation]:
        """
        Get a single conversation by ID.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            conversation_id: Conversation UUID

        Returns:
            Conversation object if found and owned by user, None otherwise
        """
        user_id_int = _to_int(user_id)
        # Convert UUID to string for database query
        conversation_id_str = str(conversation_id) if conversation_id else None

        # DEBUG: Log query details
        print(f"[DEBUG CONV REPO] get_conversation: user_id={user_id_int}, conversation_id={conversation_id_str}")

        query = select(Conversation).where(
            Conversation.id == conversation_id_str,
            Conversation.user_id == user_id_int  # Enforce user ownership
        )
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()

        # DEBUG: Log result
        if conversation:
            print(f"[DEBUG CONV REPO] get_conversation: FOUND conversation {conversation.id}")
        else:
            print(f"[DEBUG CONV REPO] get_conversation: NOT FOUND")

        return conversation

    @staticmethod
    async def get_or_create_conversation(session: AsyncSession, user_id: Union[str, int], conversation_id: Optional[UUID] = None) -> Conversation:
        """
        Get existing conversation or create new one.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            conversation_id: Optional conversation UUID (if None, creates new)

        Returns:
            Conversation object (existing or newly created)
        """
        user_id_int = _to_int(user_id)

        # DEBUG: Log incoming parameters
        print(f"[DEBUG CONV REPO] get_or_create_conversation called: user_id={user_id_int}, conversation_id={conversation_id}")

        if conversation_id:
            # Try to get existing conversation
            print(f"[DEBUG CONV REPO] Attempting to retrieve existing conversation {conversation_id}")
            conversation = await ConversationRepository.get_conversation(session, user_id_int, conversation_id)
            if conversation:
                print(f"[DEBUG CONV REPO] Found existing conversation: {conversation.id}")
                return conversation
            else:
                print(f"[DEBUG CONV REPO] Conversation {conversation_id} NOT FOUND - will create new")

        # Create new conversation
        print(f"[DEBUG CONV REPO] Creating new conversation for user {user_id_int}")
        conversation = Conversation(user_id=user_id_int)
        session.add(conversation)
        await session.flush()  # Get UUID without committing
        print(f"[DEBUG CONV REPO] Created new conversation with ID: {conversation.id}")
        return conversation

    @staticmethod
    async def add_message(
        session: AsyncSession,
        user_id: Union[str, int],
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[str] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            conversation_id: Conversation UUID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            tool_calls: Optional JSONB string of tool calls

        Returns:
            Created Message object
        """
        user_id_int = _to_int(user_id)
        # Convert UUID to string for database
        conversation_id_str = str(conversation_id)
        message = Message(
            conversation_id=conversation_id_str,
            user_id=user_id_int,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)
        await session.flush()  # Get ID without committing

        # Update conversation's updated_at timestamp
        await session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id_str, Conversation.user_id == user_id_int)
            .values(updated_at=datetime.utcnow())
        )

        return message

    @staticmethod
    async def get_conversation_history(
        session: AsyncSession,
        user_id: Union[str, int],
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """
        Get message history for a conversation.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            conversation_id: Conversation UUID
            limit: Maximum number of messages (default: 100)
            offset: Number of messages to skip (for pagination)

        Returns:
            List of Message objects (sorted by created_at ASC)
        """
        user_id_int = _to_int(user_id)
        # Convert UUID to string for database
        conversation_id_str = str(conversation_id)
        query = select(Message).where(
            Message.conversation_id == conversation_id_str,
            Message.user_id == user_id_int  # Enforce user ownership
        ).order_by(Message.created_at.asc()).limit(limit).offset(offset)

        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def list_conversations(session: AsyncSession, user_id: Union[str, int], limit: int = 50) -> List[Conversation]:
        """
        List all conversations for a user.

        Args:
            session: Database session
            user_id: User ID (enforces ownership) - converted from string (JWT) to int
            limit: Maximum number of conversations (default: 50)

        Returns:
            List of Conversation objects (sorted by updated_at DESC)
        """
        user_id_int = _to_int(user_id)
        query = select(Conversation).where(
            Conversation.user_id == user_id_int
        ).order_by(desc(Conversation.updated_at)).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

