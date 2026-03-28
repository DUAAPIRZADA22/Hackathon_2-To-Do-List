# Data Model: Todo AI Chatbot

**Feature**: 002-todo-ai-chatbot
**Date**: 2025-01-12
**Phase**: 1 (Design & Contracts)

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ├──────────────────────────────────────────┐
       │                                          │
       ▼                                          ▼
┌─────────────┐                          ┌─────────────┐
│  Conversation                           │    Task     │
└──────┬──────┘                          └─────────────┘
       │
       ▼
┌─────────────┐
│   Message   │
└─────────────┘
```

## Entities

### 1. User

**Description**: An authenticated person who can own tasks, conversations, and messages.

**Attributes**:
- `id` (str, PK): Unique user identifier
- `email` (str): User's email address
- `name` (str, optional): Display name
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- One-to-Many with Task (user has many tasks)
- One-to-Many with Conversation (user has many conversations)
- One-to-Many with Message (user has many messages)

**Constraints**:
- `email` must be unique
- `id` is immutable

### 2. Task

**Description**: A todo item owned by a user with title, optional description, and completion status.

**Attributes**:
- `id` (str, PK): Unique task identifier (UUID)
- `user_id` (str, FK): Owner's user ID
- `title` (str): Task title (max 500 chars)
- `description` (text, optional): Detailed description (unlimited)
- `completed` (boolean): Completion status (default: false)
- `created_at` (datetime): Task creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- Many-to-One with User (task belongs to one user)

**Constraints**:
- `user_id` must reference valid User
- `title` is required (not null)
- `completed` defaults to false
- `updated_at` automatically updated on modifications

**State Transitions**:
```
┌──────────┐
│  Pending │ (completed=false)
└─────┬────┘
      │ complete_task()
      ▼
┌──────────┐
│Completed │ (completed=true)
└──────────┘
```

**Indexes**:
- `idx_tasks_user_id` on `user_id`
- `idx_tasks_created_at` on `created_at DESC`

### 3. Conversation

**Description**: A chat session between a user and the AI assistant.

**Attributes**:
- `id` (str, PK): Unique conversation identifier (UUID)
- `user_id` (str, FK): Owner's user ID
- `title` (str, optional): Conversation title (default: "New Chat")
- `created_at` (datetime): Conversation creation timestamp
- `updated_at` (datetime): Last message timestamp

**Relationships**:
- Many-to-One with User (conversation belongs to one user)
- One-to-Many with Message (conversation has many messages)

**Constraints**:
- `user_id` must reference valid User
- `title` defaults to "New Chat"
- `updated_at` automatically updated on new messages

**Indexes**:
- `idx_conversations_user_id` on `user_id`
- `idx_conversations_updated_at` on `updated_at DESC`

### 4. Message

**Description**: A single communication within a conversation from either the user or assistant.

**Attributes**:
- `id` (str, PK): Unique message identifier (UUID)
- `conversation_id` (str, FK): Parent conversation ID
- `user_id` (str, FK): Owner's user ID
- `role` (enum): "user" or "assistant"
- `content` (text): Message content (unlimited)
- `created_at` (datetime): Message creation timestamp

**Relationships**:
- Many-to-One with Conversation (message belongs to one conversation)
- Many-to-One with User (message belongs to one user)

**Constraints**:
- `conversation_id` must reference valid Conversation
- `user_id` must reference valid User
- `role` must be "user" or "assistant"
- `content` is required (not null, but can be empty string)

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id`
- `idx_messages_created_at` on `created_at DESC`
- `idx_messages_conversation_created` on `(conversation_id, created_at DESC)`

## SQLModel Definitions

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class UserBase(SQLModel):
    email: str
    name: Optional[str] = None

class User(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None

class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ConversationBase(SQLModel):
    title: Optional[str] = "New Chat"

class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MessageBase(SQLModel):
    content: str

class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id")
    user_id: str = Field(foreign_key="users.id")
    role: str  # "user" or "assistant"
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Database Schema (DDL)

```sql
-- Users table
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Conversations table
CREATE TABLE conversations (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Messages table
CREATE TABLE messages (
    id VARCHAR(255) PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

## Validation Rules

### Task
- `title`: Required, max 500 characters, trimmed
- `description`: Optional, trimmed, no max limit
- `completed`: Boolean, defaults to false
- `user_id`: Required, must exist in users table

### Conversation
- `title`: Optional, max 255 characters, defaults to "New Chat"
- `user_id`: Required, must exist in users table

### Message
- `role`: Required, must be "user" or "assistant"
- `content`: Required, trimmed (can be empty string after trim)
- `conversation_id`: Required, must exist in conversations table
- `user_id`: Required, must exist in users table

## Cascade Rules

- **ON DELETE CASCADE** for all foreign keys
- When a User is deleted:
  - All their Tasks are deleted
  - All their Conversations are deleted
  - All their Messages are deleted
- When a Conversation is deleted:
  - All its Messages are deleted

## Migration Strategy

1. **Initial Migration**: Create all tables with indexes
2. **Seed Data**: No seed data required (user-driven app)
3. **Rollback**: Drop tables in reverse order (messages, conversations, tasks, users)
4. **Future Migrations**: Use SQLModel Alembic integration or manual SQL
