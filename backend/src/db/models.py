"""
Database Models for Todo AI Chatbot (Phase III)

Implements SQLModel entities for User, Task, Conversation, and Message.
Uses SQLAlchemy 2.0 async engine with Neon PostgreSQL.

Architecture Principles:
- Type-safe: Built on SQLModel (SQLAlchemy 2.0 + Pydantic)
- Explicit relationships: Foreign keys with CASCADE delete
- User identity: All models enforce user_id ownership
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlmodel import Column, DateTime, Field, SQLModel, Text, func, Relationship
from sqlalchemy import Text as SAText
from sqlalchemy import Index, CheckConstraint, ForeignKey


# =====================================================
# User Entity
# =====================================================

class User(SQLModel, table=True):
    """
    An authenticated person who can own tasks, conversations, and messages.

    Attributes:
        id: UUID primary key (auto-generated)
        email: User's email address (unique)
        name: Optional display name
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"

    # UUID primary key
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    # User information
    email: str = Field(unique=True, index=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now(), onupdate=func.now())
    )

    # Relationships (will be populated by SQLAlchemy)
    tasks: list["Task"] = Relationship(back_populates="user")
    conversations: list["Conversation"] = Relationship(back_populates="user")
    messages: list["Message"] = Relationship(back_populates="user")


# =====================================================
# Task Entity
# =====================================================

class Task(SQLModel, table=True):
    """
    A todo item owned by a user with title, optional description, and completion status.

    Attributes:
        id: Auto-incrementing integer primary key
        user_id: Owner's user ID (foreign key to users)
        title: Task title (required, max 500 chars)
        description: Optional detailed description
        completed: Task completion status (default: False)
        status: Task status (todo, in_progress, done) - for API compatibility
        priority: Task priority (low, medium, high, urgent) - for API compatibility
        due_date: Optional due date - for API compatibility
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "tasks"

    # Auto-incrementing integer primary key
    id: int = Field(default=None, primary_key=True)

    # Foreign key to users (Integer to match auth User model)
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    # Task content
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, sa_column=Column(SAText))

    # Task status (for MCP/chatbot - backward compatibility)
    completed: bool = Field(default=False, index=True)

    # Task status fields (for API compatibility)
    status: str = Field(default="todo", max_length=50)
    priority: str = Field(default="medium", max_length=20)
    due_date: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now(), onupdate=func.now())
    )

    # Relationship
    user: User = Relationship(back_populates="tasks")

    # Indexes for query optimization
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_completed", "completed"),
        Index("idx_tasks_status", "status"),
        CheckConstraint("LENGTH(TRIM(title)) > 0", name="tasks_title_not_empty"),
    )


# =====================================================
# Conversation Entity
# =====================================================

class Conversation(SQLModel, table=True):
    """
    A chat session between a user and the AI assistant.

    Attributes:
        id: UUID primary key (stored as VARCHAR(36))
        user_id: Owner's user ID (foreign key to users)
        title: Conversation title (default: "New Chat")
        created_at: Conversation creation timestamp
        updated_at: Last message timestamp
    """
    __tablename__ = "conversations"

    # UUID primary key (stored as VARCHAR(36) in database)
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    # Foreign key to users (Integer to match auth User model)
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    # Conversation metadata
    title: str = Field(default="New Chat", max_length=255)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")

    # Indexes for query optimization
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_updated_at", "updated_at"),
    )


# =====================================================
# Message Entity
# =====================================================

class Message(SQLModel, table=True):
    """
    A single communication within a conversation from either the user or assistant.

    Attributes:
        id: Primary key (UUID for ChatKit compatibility)
        conversation_id: Parent conversation ID (UUID foreign key)
        user_id: Owner's user ID (foreign key to users)
        role: Message role ("user" or "assistant")
        content: Message content
        tool_calls: Optional JSON string for tool call metadata
        created_at: Message creation timestamp
    """
    __tablename__ = "messages"

    # Primary key (UUID for ChatKit SDK compatibility)
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    # Foreign keys
    # conversation_id is UUID type in database - use string type and let SQLAlchemy handle the UUID
    conversation_id: str = Field(foreign_key="conversations.id", index=True, ondelete="CASCADE")
    # user_id references auth User model (Integer)
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    # Message content
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(sa_column=Column(SAText))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(SAText))

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=func.now())
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_created_at", "created_at"),
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
        Index("idx_messages_role", "role"),
        CheckConstraint("role IN ('user', 'assistant')", name="messages_role_valid"),
        CheckConstraint("LENGTH(TRIM(content)) > 0", name="messages_content_not_empty"),
    )


# =====================================================
# Pydantic Models for API
# =====================================================

class UserCreate(SQLModel):
    """Request model for creating a user."""
    email: str
    name: Optional[str] = None


class UserRead(SQLModel):
    """Response model for user data."""
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TaskCreate(SQLModel):
    """Request model for creating a task."""
    title: str
    description: Optional[str] = None


class TaskRead(SQLModel):
    """Response model for task data."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Request model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class ConversationCreate(SQLModel):
    """Request model for creating a conversation."""
    title: Optional[str] = "New Chat"


class ConversationRead(SQLModel):
    """Response model for conversation data."""
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(SQLModel):
    """Request model for creating a message."""
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str


class MessageRead(SQLModel):
    """Response model for message data."""
    id: str  # UUID for ChatKit compatibility
    conversation_id: str  # UUID stored as string
    user_id: str
    role: str
    content: str
    tool_calls: Optional[str] = None
    created_at: datetime
