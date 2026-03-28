# Data Model: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2025-01-09
**Status**: Complete

## Overview

This document defines the database schema for the Todo AI Chatbot feature. The model supports conversational task management with full user isolation, conversation history persistence, and stateless backend architecture.

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │1       *│Conversation  │1       *│  Message    │
│ (Better Auth)│─────────│              │─────────│             │
└─────────────┘         └──────────────┘         └─────────────┘
                                │
                                │1
                                │
                                │*
                         ┌──────────────┐
                         │     Task     │
                         └──────────────┘
```

## Entities

### User

**Description**: User account managed by Better Auth (existing from Phase I/II)
**Table**: `users` (managed by Better Auth, not created by this feature)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PRIMARY KEY | Unique user identifier |
| email | str | UNIQUE, NOT NULL | User email address |
| ... | ... | ... | (Other fields managed by Better Auth) |

**Relationships**:
- Has many Tasks
- Has many Conversations
- Has many Messages

**Notes**:
- User table is NOT created by this feature
- We reference the existing Better Auth user table
- user_id is a foreign key in all our tables

---

### Task

**Description**: A single todo item belonging to a user

**Table**: `tasks`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| user_id | str | FOREIGN KEY → users.id, NOT NULL, INDEX | Owning user |
| title | str | NOT NULL, MAX 255 chars | Task title |
| description | text | NULLABLE | Detailed task description |
| completed | bool | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last modification timestamp |

**Indexes**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `users(id)`
- COMPOSITE INDEX: `idx_task_user_completed` on (`user_id`, `completed`)
- INDEX: `idx_task_user_created` on (`user_id`, `created_at DESC`)

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
```

**Validation Rules** (from functional requirements):
- FR-033: title required, max 255 chars
- FR-033: description optional, unlimited length
- FR-033: completed defaults to FALSE
- FR-036: updated_at must be updated on any modification
- FR-002: user_id enforced (all queries filtered by user_id)

**State Transitions**:

```
[NEW] → (complete) → [COMPLETED]
  ↑                    ↓
  └── (uncomplete) ──────┘
```

---

### Conversation

**Description**: A chat session between a user and the AI

**Table**: `conversations`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str | PRIMARY KEY (UUID) | Unique conversation identifier |
| user_id | str | FOREIGN KEY → users.id, NOT NULL, INDEX | Participating user |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last activity timestamp |

**Indexes**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `users(id)`
- COMPOSITE INDEX: `idx_conv_user_updated` on (`user_id`, `updated_at DESC`)

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
```

**Validation Rules** (from functional requirements):
- FR-034: user_id required
- FR-034: id is UUID (auto-generated)
- FR-034: updated_at updated on new message
- FR-034: Only one conversation per user per session (or multiple for history)

**Notes**:
- Conversation ID is passed from frontend to continue existing conversation
- If no conversation_id provided, create new conversation

---

### Message

**Description**: A single exchange in a conversation (user or assistant)

**Table**: `messages`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| user_id | str | FOREIGN KEY → users.id, NOT NULL, INDEX | Owning user |
| conversation_id | str | FOREIGN KEY → conversations.id, NOT NULL, INDEX | Associated conversation |
| role | enum | NOT NULL, VALUES ('user', 'assistant') | Message sender |
| content | text | NOT NULL | Message text content |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| tool_calls | jsonb | NULLABLE | MCP tool calls made (assistant only) |

**Indexes**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `users(id)`
- FOREIGN KEY: `conversation_id` → `conversations(id)`
- COMPOSITE INDEX: `idx_msg_conv_created` on (`conversation_id`, `created_at ASC`)
- COMPOSITE INDEX: `idx_msg_user_conv` on (`user_id`, `conversation_id`)

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Literal
from datetime import datetime
import uuid

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: Literal["user", "assistant"] = Field(index=True)
    content: str = Field(index=False)  # Don't index full text
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[dict] = Field(default=None)  # JSONB for MCP tool calls

    # Relationships
    user: "User" = Relationship(back_populates="messages")
    conversation: "Conversation" = Relationship(back_populates="messages")
```

**Validation Rules** (from functional requirements):
- FR-035: user_id required
- FR-035: conversation_id required
- FR-035: role must be 'user' or 'assistant'
- FR-035: content required (text message)
- FR-035: tool_calls optional (assistant messages only)
- FR-035: Ordered by created_at ASC

**tool_calls JSON Schema**:

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "tool": { "type": "string", "enum": ["add_task", "list_tasks", "update_task", "complete_task", "delete_task"] },
      "parameters": { "type": "object" },
      "result": { "type": "object" },
      "timestamp": { "type": "string", "format": "date-time" }
    }
  }
}
```

---

## Database Migration

**Migration File**: `database/migrations/001_create_tasks_conversations_messages.sql`

```sql
-- ===================================================================
-- Migration: 001_create_tasks_conversations_messages
-- Description: Create tables for Todo AI Chatbot feature
-- Author: Spec-Kit Plus /sp.plan
-- Date: 2025-01-09
-- ===================================================================

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_calls JSONB
);

-- Indexes for messages
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at ASC);
CREATE INDEX idx_messages_user_conv ON messages(user_id, conversation_id);

-- Trigger to update updated_at on tasks
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update conversation updated_at when message is added
CREATE OR REPLACE FUNCTION update_conv_updated_at_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations SET updated_at = NOW() WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conv_on_new_message AFTER INSERT ON messages
    FOR EACH ROW EXECUTE FUNCTION update_conv_updated_at_on_message();
```

---

## Query Patterns

### Common Queries

**1. Fetch conversation history (paginated)**

```python
async def get_conversation_history(
    db: Session,
    user_id: str,
    conversation_id: str,
    limit: int = 50,
    offset: int = 0
) -> list[Message]:
    """Fetch messages for conversation, ordered by creation time."""
    return await db.exec(
        select(Message)
        .where(
            Message.user_id == user_id,
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    ).all()
```

**2. List user's tasks (with filter)**

```python
async def list_tasks(
    db: Session,
    user_id: str,
    status: str = "all"  # "all" | "pending" | "completed"
) -> list[Task]:
    """List tasks for user with optional status filter."""
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    return await db.exec(
        query.order_by(Task.created_at.desc())
    ).all()
```

**3. Create or continue conversation**

```python
async def get_or_create_conversation(
    db: Session,
    user_id: str,
    conversation_id: str | None = None
) -> Conversation:
    """Get existing conversation or create new one."""
    if conversation_id:
        conv = await db.get(Conversation, conversation_id)
        if conv and conv.user_id == user_id:
            return conv
        raise ValueError("Conversation not found or access denied")

    # Create new conversation
    conv = Conversation(user_id=user_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv
```

**4. Get task by ID (with user verification)**

```python
async def get_task_for_user(
    db: Session,
    user_id: str,
    task_id: int
) -> Task | None:
    """Get task if it belongs to user."""
    return await db.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()
```

---

## Performance Considerations

### Index Strategy

**Critical Indexes** (for < 500ms query performance):
1. `idx_tasks_user_completed`: Fast status-filtered task listing
2. `idx_tasks_user_created`: Recent task queries
3. `idx_conv_user_updated`: Recent conversation queries
4. `idx_messages_conv_created`: Conversation history loading

### Connection Pooling

**Recommended Settings** (for 1000 concurrent users):
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Base connection pool
    max_overflow=40,        # Additional connections under load
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600       # Recycle connections after 1 hour
)
```

### Caching Strategy

**Cache Keys** (TTL: 60 seconds):
- `conv:{conversation_id}` → Conversation messages (last 50)
- `tasks:{user_id}:status:{status}` → Task list cache

**Invalidation**:
- Invalidate on new message
- Invalidate on task modification
- Short TTL prevents stale data

---

## Data Retention

**Policies** (not implemented in Phase III, documented for future):

| Entity | Retention Period | Cleanup Strategy |
|--------|-----------------|------------------|
| Tasks | Forever | No cleanup (user data) |
| Conversations | 1 year inactive | Delete conversations with no messages after 1 year |
| Messages | 1 year inactive | Cascade with conversation |

**Note**: Phase III does NOT implement automated cleanup. All data persists indefinitely.

---

## Security & Privacy

### User Isolation

**Multi-tenancy Model**: Every query MUST filter by `user_id`

```python
# BAD: Returns all tasks (cross-user data leak!)
tasks = await db.exec(select(Task)).all()

# GOOD: Only returns user's tasks
tasks = await db.exec(
    select(Task).where(Task.user_id == current_user_id)
).all()
```

### Foreign Key Constraints

- `ON DELETE CASCADE`: Delete user's data when user is deleted
- Prevents orphaned records
- Enforces referential integrity

### Sensitive Data

**Stored**:
- Task titles and descriptions (user content)
- Conversation messages (AI interactions)

**NOT Stored**:
- Authentication credentials (handled by Better Auth)
- API keys or tokens
- PII beyond email (managed by Better Auth)

---

## Compliance

### FR Compliance Matrix

| FR | Compliance |
|----|------------|
| FR-002 | ✅ user_id foreign key on all tables |
| FR-033 | ✅ Task model with all required fields |
| FR-034 | ✅ Conversation model with all required fields |
| FR-035 | ✅ Message model with all required fields |
| FR-036 | ✅ updated_at trigger implemented |
| FR-037 | ✅ Foreign key constraints for atomicity |

---

## Next Steps

1. ✅ Data model complete
2. ⏭️ Generate API contracts (OpenAPI + MCP schemas)
3. ⏭️ Create migration scripts
4. ⏭️ Write quickstart.md
5. ⏭️ Update agent context

---

**Schema Version**: 1.0.0
**Last Updated**: 2025-01-09
