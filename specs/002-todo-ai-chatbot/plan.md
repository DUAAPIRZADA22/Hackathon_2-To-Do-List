# Implementation Plan: Todo AI Chatbot - Phase III

**Branch**: `002-todo-ai-chatbot` | **Date**: 2025-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-ai-chatbot/spec.md`

## Summary

Build a production-ready AI-powered Todo Chatbot that enables users to manage tasks through natural language conversation. The system uses OpenAI ChatKit for the frontend conversational interface, OpenAI Agents SDK for AI reasoning, MCP (Model Context Protocol) for tool operations, and Neon PostgreSQL for persistent storage. The backend is fully stateless, fetching conversation context on each request.

**Technical Approach**:
- Frontend: ChatKit React with Better Auth
- Backend: FastAPI with ChatKit Python SDK
- AI: OpenAI Agents SDK with Gemini/OpenRouter
- Tools: MCP Python SDK exposing task operations
- Storage: Neon PostgreSQL with SQLModel ORM

## Technical Context

**Language/Version**: Python 3.13+, TypeScript 5+, Node.js 20+
**Primary Dependencies**:
- Backend: `fastapi>=0.115.0`, `openai-chatkit>=0.1.0`, `agents>=0.15.0`, `mcp>=1.7.1`, `sqlmodel>=0.0.22`
- Frontend: `@openai/chatkit-react`, `better-auth`, `next@15`
**Storage**: Neon Serverless PostgreSQL (PostgreSQL 16+)
**Testing**: `pytest`, `pytest-asyncio`, `playwright` (E2E)
**Target Platform**: Linux container (Docker), Web browsers (Chrome, Firefox, Safari)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- < 10 seconds end-to-end task creation
- < 3 seconds task list retrieval
- < 5 seconds response time for 100 concurrent users
- 95% intent recognition accuracy
**Constraints**:
- Stateless backend (no in-memory session storage)
- All conversation history fetched from DB per request
- User identity enforced on all operations
- Must follow SOLID and DRY principles
**Scale/Scope**:
- 100 concurrent users (Phase 3)
- < 1000 tasks per user
- Unlimited conversation history retention

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- All implementation will reference Task IDs from `tasks.md` (to be created by `/sp.tasks`)
- No code without documented requirements
- Traceability maintained through spec → plan → tasks → implementation

### Principle II: MCP-First Architecture ✅ PASS
- Using Official MCP Python SDK (`mcp>=1.7.1`)
- All CRUD operations exposed as MCP tools
- OpenAI Agents SDK integrates with MCP tools (natively supported)
- Context7 MCP architecture pattern followed for stateless design

### Principle III: Context Verification ✅ PASS
- MCP server initialization verified before tool execution
- Database connection checked before state operations
- Fail gracefully with clear error messages

### Principle IV: Scope Boundaries ✅ PASS
**Phase 3 Scope** (this feature):
- Web-based conversational interface (ChatKit React)
- Stateless backend with persistent storage
- MCP tools for task CRUD operations
- OpenAI Agents SDK for intent reasoning
- Better Auth for authentication

**Out of Scope** (as per spec):
- Native mobile apps
- Email/calendar integrations
- Task priorities, categories, tags
- Recurring tasks or dependencies
- Collaboration features
- Analytics/dashboards

### Principle V: SOLID Principles ✅ PASS
**Single Responsibility**:
- Separate modules for Agent logic, MCP tools, Store implementation, API routes
- Each tool handles one operation (add_task, list_tasks, etc.)

**Open/Closed**:
- New task operations added as new MCP tools without modifying existing code
- Agent can be extended with new intents via instructions

**Liskov Substitution**:
- Store implementation can be swapped (in-memory → PostgreSQL)
- LLM provider can be swapped (Gemini ↔ OpenRouter ↔ OpenAI)

**Interface Segregation**:
- Minimal tool interfaces (only required parameters)
- Focused Agent responsibilities

**Dependency Inversion**:
- Depends on Store abstract interface, not concrete implementation
- Depends on Agent abstractions, not specific LLM providers

### Principle VI: DRY ✅ PASS
- Reusable tool patterns via MCP SDK
- Shared Store implementation for all data operations
- Common error handling middleware
- Reusable Agent patterns from skills

### Principle VII: Modularity ✅ PASS
**Backend Modules**:
```
backend/
├── src/
│   ├── agent/          # OpenAI Agents SDK logic
│   ├── api/            # FastAPI routes
│   ├── mcp/            # MCP server and tools
│   ├── db/             # Database models and repository
│   ├── store/          # ChatKit Store implementation
│   └── auth/           # Better Auth integration
```

**Frontend Modules**:
```
frontend/
├── src/
│   ├── app/            # Next.js App Router
│   ├── components/     # ChatKit and UI components
│   ├── lib/            # API client and auth utilities
│   └── styles/         # Global styles
```

### Principle VIII: User Experience Standards ✅ PASS
**Conversational Interface** (per ChatKit patterns):
- Natural language input (no menus)
- Real-time streaming responses
- Clear success/error messages
- Task confirmations with details

**User Feedback**:
- Success: "✓ Task added: [title]"
- Error: "⚠ Task not found: [task_id]"
- Info: "ℹ You have 3 pending tasks"

---

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   ├── mcp-tools.yaml   # MCP tool schemas
│   └── database.yaml    # Database schema
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure
backend/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── todo_agent.py      # Main Agent definition
│   │   ├── prompts.py         # Agent instructions
│   │   └── context.py         # Agent context handling
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry
│   │   ├── routes/
│   │   │   ├── chat.py        # POST /api/{user_id}/chat
│   │   │   └── health.py      # Health check endpoint
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py          # MCP server setup
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       └── update_task.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLModel models (Task, Conversation, Message)
│   │   ├── repository.py      # Database operations
│   │   └── session.py         # Database session management
│   ├── store/
│   │   ├── __init__.py
│   │   └── postgres_store.py  # ChatKit Store implementation
│   └── core/
│       ├── __init__.py
│       ├── config.py          # Configuration and settings
│       └── logging.py         # Logging setup
├── tests/
│   ├── contract/
│   │   ├── test_chat_api.py
│   │   └── test_mcp_tools.py
│   ├── integration/
│   │   ├── test_agent_flow.py
│   │   └── test_end_to_end.py
│   └── unit/
│       ├── test_tools.py
│       └── test_store.py
├── pyproject.toml            # UV dependencies
├── .env.example              # Environment variables template
└── Dockerfile                # Container image

frontend/
├── src/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx         # Root layout with providers
│   │   ├── page.tsx           # Home/redirect to chat
│   │   ├── chat/
│   │   │   └── page.tsx       # Main chat interface
│   │   └── api/
│   │       └── auth/
│   │           └── [...nextauth]/route.ts  # Better Auth API
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWidget.tsx # ChatKit wrapper
│   │   │   └── ChatPage.tsx   # Main chat page
│   │   └── ui/
│   │       └── ...            # Reusable UI components
│   └── lib/
│       ├── auth.ts           # Better Auth client
│       └── api.ts            # API client utilities
├── tests/
│   └── e2e/
│       └── chat.spec.ts      # Playwright E2E tests
├── package.json
├── tsconfig.json
└── next.config.js

database/
├── migrations/
│   └── 001_initial_schema.sql
└── README.md
```

**Structure Decision**: Web application structure selected (Option 2) because:
1. Spec requires "frontend" (ChatKit React) and "backend" (FastAPI)
2. Clear separation between client and server concerns
3. Enables independent deployment and scaling
4. Matches ChatKit integration pattern from skills

---

## Phase 0: Research & Decisions

### Research Summary

This research phase leveraged:
1. **context7 MCP architecture** - For understanding MCP server patterns
2. **openai-agents-sdk-gemini skill** - For Agent + Runner patterns, tool integration
3. **openai-chatkit-integration skill** - For ChatKit backend integration patterns
4. **Web research** - For latest MCP SDK, FastAPI, and Better Auth patterns

### Key Decisions

#### Decision 1: MCP Server Integration Pattern

**Decision**: Use OpenAI Agents SDK's native MCP integration

**Rationale**:
- OpenAI Agents SDK has built-in MCP support (`openai-agents-python/mcp/`)
- Tools defined with `@function_tool` decorator automatically register as MCP tools
- Reduces boilerplate compared to manual MCP server setup
- Better type safety and error handling

**Alternatives Considered**:
- Standalone MCP server with stdio transport: More complex, requires separate process management
- HTTP-based MCP server: Added network hop, latency concerns
- Direct tool calls without MCP: Violates spec requirement, loses standardization

**Implementation Pattern** (from skills):
```python
from agents import Agent, function_tool
from agents.mcp import MCPServer

# Create MCP server
mcp_server = MCPServer("todo-server")

# Define tools as function_tool decorated functions
@function_tool
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Add a new task for the user."""
    # Implementation calls database
    pass

# Agent with MCP tools
agent = Agent(
    name="Todo Assistant",
    instructions="...",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
)
```

#### Decision 2: ChatKit Store Implementation

**Decision**: Implement custom PostgreSQL-backed Store

**Rationale**:
- Spec requires persistent conversation history
- ChatKit Python SDK provides `Store` abstract base class
- In-memory store (default) doesn't meet persistence requirement
- PostgreSQL chosen per spec (Neon Serverless)

**Alternatives Considered**:
- MongoDB: More flexible schema, but spec requires SQL
- Redis: Fast but not primary storage, would need cache-aside pattern
- SQLite: Not suitable for multi-user concurrent access

**Critical Pitfalls Avoided** (from openai-chatkit-integration skill):
1. ✅ Correct imports: `from chatkit.server import ChatKitServer`, `from chatkit.store import Store`
2. ✅ Store methods include all required parameters: `load_threads(context, limit, after, order)`
3. ✅ Pass conversation history to agent: `simple_to_agent_input(items_page.data)` not just string
4. ✅ Auto-create threads in `load_thread()` - SDK expects this behavior

#### Decision 3: Stateless Conversation Flow

**Decision**: Fetch conversation history from database on every request

**Rationale**:
- Spec requires "stateless backend"
- Enables horizontal scaling (any server can handle any request)
- No session affinity required
- Database provides single source of truth

**Flow** (from spec):
```
1. Receive user message
2. Fetch conversation history from DB (if conversation_id provided)
3. Build agent message context from history
4. Store user message
5. Run agent with context
6. Agent calls MCP tool(s)
7. Store assistant message
8. Return response
9. Hold NO server state
```

**Performance Considerations**:
- Index on `(user_id, conversation_id, created_at)`
- Limit history to last N messages (configurable)
- Consider read replicas for scaling

#### Decision 4: Agent Intent Mapping

**Decision**: Single Agent with tool-based intent resolution

**Rationale**:
- OpenAI Agents SDK automatically maps user intent to tools
- Agent instructions specify tool usage patterns
- More maintainable than multiple intent classification agents

**Intent Mapping** (from spec):
```
add / create / remember → add_task
show / list / see → list_tasks
done / complete / finished → complete_task
delete / remove / cancel → delete_task
change / update / rename → update_task
```

**Agent Instructions Pattern** (from skills):
```python
TODO_AGENT_INSTRUCTIONS = """
You are a helpful todo assistant. Use the available tools to manage tasks.

TOOLS AVAILABLE:
- add_task: Create new tasks (when user says: add, create, remember)
- list_tasks: Show tasks (when user says: show, list, see, what's pending)
- complete_task: Mark tasks done (when user says: done, complete, finished)
- delete_task: Remove tasks (when user says: delete, remove, cancel)
- update_task: Modify tasks (when user says: change, update, rename, edit)

BEHAVIOR:
- Always confirm actions with task details
- Handle errors gracefully (task not found, invalid input)
- Be friendly and conversational
- Ask for clarification if intent is unclear
"""
```

#### Decision 5: LLM Provider

**Decision**: Support multiple providers via OpenAI-compatible interface

**Rationale**:
- Flexibility for different cost/latency requirements
- Easy fallback between providers
- OpenAI Agents SDK supports this via `AsyncOpenAI` client

**Options** (from openai-agents-sdk-gemini skill):
1. **Gemini 2.0 Flash** (primary): Fast, free tier available
2. **OpenRouter** (fallback): Access to multiple models
3. **OpenAI GPT-4o-mini**: High quality, low cost

**Configuration Pattern** (avoiding pitfalls from skills):
```python
# CORRECT - Use OpenAIChatCompletionsModel wrapper
from agents import OpenAIChatCompletionsModel, set_default_openai_api, set_tracing_disabled
from openai import AsyncOpenAI

set_default_openai_api("chat_completions")
set_tracing_disabled(True)  # Not using OpenAI tracing

provider = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash-exp",
)
```

**Critical Performance Note** (from skills):
- ❌ AVOID: `mistralai/devstral-2512:free` (~29 seconds response time)
- ✅ USE: `google/gemini-2.0-flash-exp:free` (~5 seconds)
- ✅ USE: `openai/gpt-4o-mini` (~2 seconds)

#### Decision 6: Authentication Strategy

**Decision**: Better Auth for Next.js frontend with session-based backend auth

**Rationale**:
- Better Auth is modern, type-safe, Next.js-native
- Successor to NextAuth.js (Auth.js team joined Better Auth in Sept 2025)
- Built-in OAuth providers (Google, GitHub, etc.)
- Simple session management

**Implementation Pattern** (from web research):
```typescript
// frontend/src/lib/auth.ts
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

export const { signIn, signOut, useSession } = authClient
```

**Backend Integration**:
```python
# FastAPI dependency to validate session
async def get_current_user(request: Request) -> User:
    session_token = request.cookies.get("better-auth.session_token")
    if not session_token:
        raise HTTPException(401, "Not authenticated")

    user = await validate_session(session_token)
    return user
```

#### Decision 7: Database Schema Design

**Decision**: SQLModel with PostgreSQL, following spec entity definitions

**Rationale**:
- SQLModel provides Pydantic validation + SQLAlchemy ORM
- Type safety with Python 3.13+ type hints
- Automatic schema generation
- Easy migration management

**Schema** (from spec):
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    user_id: str = Field(foreign_key="users.id")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    user_id: str = Field(foreign_key="users.id")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    user_id: str = Field(foreign_key="users.id")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

---

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for detailed entity definitions, relationships, and state transitions.

### API Contracts

See [contracts/chat-api.yaml](./contracts/chat-api.yaml) for OpenAPI specification.

### MCP Tools

See [contracts/mcp-tools.yaml](./contracts/mcp-tools.yaml) for MCP tool schemas.

### Database Schema

See [contracts/database.yaml](./contracts/database.yaml) for DDL.

### Quickstart Guide

See [quickstart.md](./quickstart.md) for setup and run instructions.

---

## Phase 2: Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ ChatKit React│  │ Better Auth  │  │     API Client Layer    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘  │
│         │                  │                     │                   │
│         └──────────────────┴─────────────────────┘                   │
│                              │                                         │
└──────────────────────────────│─────────────────────────────────────┘
                               │ HTTP/SSE
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  API Layer (FastAPI Routes)                                  │   │
│  │  - POST /api/{user_id}/chat                                   │   │
│  │  - GET /health                                                │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                        │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │  ChatKit Server (chatkit.server.ChatKitServer)               │   │
│  │  - respond()         # Main chat handler                     │   │
│  │  - Streaming support for real-time responses                │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                        │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │  PostgreSQL Store (store/postgres_store.PostgresStore)       │   │
│  │  - load_thread()     # Auto-create threads                   │   │
│  │  - save_thread()                                            │   │
│  │  - load_thread_items() # Fetch conversation history          │   │
│  │  - add_thread_item() # Store messages                        │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                        │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │  OpenAI Agents SDK (agents.Agent, Runner)                    │   │
│  │  - Todo Agent with tool definitions                          │   │
│  │  - Runner.run_streamed() for streaming responses             │   │
│  │  - simple_to_agent_input() for context building              │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                        │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │  MCP Tools (mcp/tools/*.py)                                  │   │
│  │  - @function_tool decorated functions                        │   │
│  │  - add_task, list_tasks, complete_task, delete_task, update  │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                        │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │  Repository Layer (db/repository.py)                         │   │
│  │  - Database operations via SQLModel/SQLAlchemy               │   │
│  │  - Connection pooling and session management                │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────│─────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NEON POSTGRESQL DATABASE                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Tables: tasks, conversations, messages, users               │  │
│  │  Indexes: user_id, conversation_id, created_at               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Request Flow (Stateless Chat)

```
User Message (via ChatKit)
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. FastAPI receives POST /api/{user_id}/chat                 │
│    - Validate user authentication                             │
│    - Parse: conversation_id (optional), message (required)    │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Load conversation context from PostgreSQL                  │
│    - If conversation_id provided: fetch all messages         │
│    - If new conversation: create new conversation record      │
│    - Store user message immediately                           │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Build Agent Input                                          │
│    - Use chatkit.agents.simple_to_agent_input()              │
│    - Convert messages to Agent input format                   │
│    - Include current user message                             │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Run Agent with Streaming                                   │
│    - Runner.run_streamed(agent, input_items, context)        │
│    - Agent reasons over conversation history                  │
│    - Agent determines intent and calls MCP tools              │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. MCP Tool Execution                                          │
│    - Agent calls: add_task(), list_tasks(), etc.             │
│    - Tools call Repository layer                              │
│    - Database operations executed                             │
│    - Return results to Agent                                  │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Stream Response                                            │
│    - Agent generates response                                 │
│    - stream_agent_response() yields events                    │
│    - Store assistant message to database                      │
│    - Stream events to frontend via SSE                        │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
Frontend displays response (no server state retained)
```

### Component Specifications

#### 1. Todo Agent (`backend/src/agent/todo_agent.py`)

**Responsibility**: Interpret natural language and invoke appropriate tools

**Key Components**:
```python
from agents import Agent, function_tool, AgentContext
from agents.mcp import MCPServer

class TodoAgent:
    def __init__(self, model: OpenAIChatCompletionsModel):
        self.agent = Agent(
            name="Todo Assistant",
            instructions=TODO_AGENT_INSTRUCTIONS,
            model=model,
            tools=self._register_tools(),
        )

    def _register_tools(self) -> list:
        """Register MCP tools as Agent tools"""
        return [
            add_task,
            list_tasks,
            complete_task,
            delete_task,
            update_task,
        ]
```

#### 2. MCP Tools (`backend/src/mcp/tools/*.py`)

**Pattern** (from openai-agents-sdk-gemini skill):
```python
from agents import function_tool
from backend.src.db.repository import TaskRepository

@function_tool
async def add_task(
    user_id: str,
    title: str,
    description: str | None = None
) -> dict:
    """
    Add a new task for the user.

    Args:
        user_id: The user's unique identifier
        title: Task title (required)
        description: Optional task description

    Returns:
        dict with task_id, status, and title
    """
    repo = TaskRepository()
    task = await repo.create_task(
        user_id=user_id,
        title=title,
        description=description,
    )
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title,
    }
```

#### 3. PostgreSQL Store (`backend/src/store/postgres_store.py`)

**Pattern** (from openai-chatkit-integration skill - avoiding pitfalls):
```python
from chatkit.store import Store, Page, ThreadMetadata, ThreadItem
from chatkit.server import StreamingResult
from backend.src.db.models import Conversation, Message
from datetime import datetime

class PostgresStore(Store[dict]):
    async def load_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> ThreadMetadata | None:
        """Load thread by ID, auto-create if not exists"""
        repo = Repository()
        thread = await repo.get_conversation(thread_id)

        if thread:
            return ThreadMetadata(
                id=thread.id,
                title=thread.title or "New Chat",
                created_at=thread.created_at,
                metadata={"user_id": thread.user_id},
            )

        # Auto-create thread (Pitfall #5 from skill)
        new_thread = await repo.create_conversation(
            conversation_id=thread_id,
            user_id=context.get("user_id"),
        )
        return ThreadMetadata(
            id=new_thread.id,
            title="New Chat",
            created_at=new_thread.created_at,
            metadata={"user_id": new_thread.user_id},
        )

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None = None,
        limit: int = 100,
        order: str = "asc",
        context: dict = None,
    ) -> Page[ThreadItem]:
        """Load messages for thread - MUST include all params (Pitfall #3)"""
        repo = Repository()
        messages = await repo.get_messages(
            conversation_id=thread_id,
            after=after,
            limit=limit,
            order=order,
        )

        items = [
            ThreadItem(
                id=msg.id,
                role=msg.role,
                content=[{"type": "text", "text": msg.content}],
            )
            for msg in messages
        ]

        return Page(
            data=items,
            has_more=len(messages) == limit,
            after=items[-1].id if items else None,
        )
```

#### 4. ChatKit Server (`backend/src/api/chat.py`)

**Pattern** (from openai-chatkit-integration skill - avoiding Pitfall #7):
```python
from fastapi import APIRouter, Request, Response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.agents import stream_agent_response, simple_to_agent_input, AgentContext
from agents import Runner
import uuid

router = APIRouter()

server = ChatKitServer(store=PostgresStore())

@router.post("/api/{user_id}/chat")
async def chat_endpoint(request: Request, user_id: str):
    """Main chat endpoint - uses server.process()"""
    payload = await request.body()
    context = {"user_id": user_id}

    result = await server.process(payload, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    return Response(content=result.json, media_type="application/json")

async def respond(
    self,
    thread: ThreadMetadata,
    input: UserMessageItem | ClientToolCallItem,
    context: Any,
) -> AsyncIterator[ThreadStreamEvent]:
    """Generate response with unique message ID (Pitfall #9 from skill)"""
    # Load conversation history
    items_page = await self.store.load_thread_items(
        thread.id,
        after=None,
        limit=20,
        order="asc",
        context=context,
    )

    # Convert to agent input (Pitfall #4 from skill)
    input_items = await simple_to_agent_input(items_page.data)

    agent_context = AgentContext(
        thread=thread,
        store=self.store,
        request_context=context,
    )

    # Generate unique message ID upfront
    unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

    result = Runner.run_streamed(
        self.assistant_agent,
        input_items,
        context=agent_context,
    )

    async for event in stream_agent_response(agent_context, result):
        # Replace __fake_id__ with unique ID (Pitfall #9 from skill)
        if hasattr(event, 'item') and event.item.id == "__fake_id__":
            new_item = event.item.model_copy(update={"id": unique_message_id})
            event = event.model_copy(update={"item": new_item})

        yield event
```

### Implementation Tasks (Pre-computation)

The following tasks will be generated by `/sp.tasks`:

**Phase 1: Foundation (Days 1-2)**
1. Set up backend project structure and dependencies (UV, Python 3.13)
2. Set up frontend project structure (Next.js 15, TypeScript)
3. Configure Better Auth (frontend + backend)
4. Create database models and migrations
5. Set up Neon PostgreSQL connection

**Phase 2: Core Features (Days 3-5)**
6. Implement MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
7. Implement Repository layer (CRUD operations)
8. Implement PostgreSQL Store for ChatKit
9. Implement Todo Agent with OpenAI Agents SDK
10. Configure LLM provider (Gemini/OpenRouter)

**Phase 3: Integration (Days 6-7)**
11. Implement ChatKit server respond() method
12. Implement FastAPI chat endpoint
13. Implement ChatKit frontend integration
14. Implement streaming response handling
15. Test end-to-end conversation flow

**Phase 4: Polish & Testing (Days 8-9)**
16. Write unit tests for tools and repository
17. Write integration tests for agent flow
18. Write E2E tests with Playwright
19. Error handling and edge cases
20. Documentation and quickstart guide

**Phase 5: Deployment (Day 10)**
21. Docker containerization
22. Environment configuration
23. Deploy to production (Neon + hosting)
24. Performance testing (100 concurrent users)
25. Final validation and handoff

---

## Complexity Tracking

> No constitution violations. All requirements align with Spec-Kit Plus methodology and project constitution.

| Aspect | Compliance | Notes |
|--------|-----------|-------|
| Spec-Driven | ✅ | All implementation references Task IDs from tasks.md |
| MCP-First | ✅ | Official MCP Python SDK used for all tools |
| Context Verification | ✅ | MCP server initialization verified |
| Scope Boundaries | ✅ | Web app, stateless, persistent storage only |
| SOLID Principles | ✅ | Modular architecture with clear separation |
| DRY | ✅ | Reusable patterns from skills, shared Store implementation |
| Modularity | ✅ | Separate modules for agent, API, MCP, store, DB |
| UX Standards | ✅ | Conversational interface with clear feedback |

---

## Open Questions & Risks

### Open Questions (Resolved in Research)

1. **Q: How to integrate MCP tools with OpenAI Agents SDK?**
   **A**: Use `@function_tool` decorator - Agents SDK automatically registers as MCP-compatible tools

2. **Q: How to handle conversation history in stateless architecture?**
   **A**: Fetch from PostgreSQL on each request via Store.load_thread_items()

3. **Q: Which LLM provider for best performance/cost?**
   **A**: Gemini 2.0 Flash (primary) with OpenRouter fallback - avoid slow free-tier models

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API rate limits | High | Implement fallback agent pattern (from skill) |
| Database query latency | Medium | Add indexes, limit history fetch size, read replicas |
| ChatKit protocol changes | Medium | Pin specific version, monitor for breaking changes |
| Memory leaks in streaming | Medium | Proper async cleanup, monitor connections |
| Tool naming conflicts | Low | Clear naming convention (add_task, list_tasks, etc.) |

---

## Dependencies

### External Services
- **Neon PostgreSQL**: Database hosting
- **Gemini API**: Primary LLM provider
- **OpenRouter**: Fallback LLM provider (optional)

### Python Packages
```toml
[dependencies]
fastapi = ">=0.115.0"
uvicorn = {extras = ["standard"], version = ">=0.32.0"}
openai-chatkit = ">=0.1.0"
agents = ">=0.15.0"
mcp = ">=1.7.1"
sqlmodel = ">=0.0.22"
asyncpg = ">=0.29.0"
pydantic = ">=2.0.0"
python-dotenv = ">=1.0.0"
python-jose = {extras = ["cryptography"], version = ">=3.3.0"}
```

### Node Packages
```json
{
  "dependencies": {
    "@openai/chatkit-react": "latest",
    "better-auth": "latest",
    "next": "15",
    "react": "^19",
    "react-dom": "^19"
  }
}
```

---

## Success Metrics

From spec, these are the key measurable outcomes:

| Metric | Target | How Measured |
|--------|--------|--------------|
| Task creation time | < 10 seconds | End-to-end timing from message send to confirmation |
| Intent recognition | 95% accuracy | Percentage of correctly identified intents |
| Task list retrieval | < 3 seconds | Database query + render time |
| Concurrent users | 100 users | Load testing with simultaneous conversations |
| Response time | < 5 seconds (p95) | Agent reasoning + tool execution + streaming |
| Operation success rate | 99% | Error tracking / total operations |
| Cross-user data leakage | 0 instances | Security testing, access control validation |

---

## Next Steps

1. ✅ **Complete**: `/sp.plan` generates this comprehensive plan
2. **Next**: Run `/sp.tasks` to generate testable tasks from this plan
3. **Then**: Begin implementation following task order
4. **Finally**: Run tests, validate against success criteria

**Ready for `/sp.tasks` command.**
