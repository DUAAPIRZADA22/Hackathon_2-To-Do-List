# Research: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2025-01-09
**Status**: Complete

## Overview

This document captures research findings and technology decisions for implementing the Todo AI Chatbot feature. All unknowns from the planning phase have been resolved.

## Research Questions & Decisions

### 1. OpenAI Agents SDK Integration with MCP Tools

**Question**: How to integrate OpenAI Agents SDK with custom MCP tools?

**Investigation**:
- OpenAI Agents SDK supports function calling through `tools` parameter
- MCP tools can be wrapped as Python callables with type hints
- Agents SDK automatically serializes tool schemas for OpenAI API

**Decision**: Use Agents SDK's tool registration mechanism
- Wrap each MCP tool as a Python async function with type annotations
- Register tools with agent using `@agent.tool` decorator or manual registration
- MCP tool execution happens via standard Python function calls

**Rationale**:
- Clean separation between MCP protocol and Agent SDK
- Type safety through Python function signatures
- OpenAI-compatible function calling format

**Alternatives Considered**:
- Direct MCP server-client communication: Rejected due to added complexity
- Custom tool protocol: Rejected due to non-standard approach

**Implementation Notes**:
```python
# MCP tool wrapper pattern
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Add a new task for the user."""
    result = await mcp_client.call_tool("add_task", {"user_id": user_id, "title": title, "description": description})
    return result

# Register with agent
agent = Agent(name="todo_assistant", tools=[add_task, list_tasks, ...])
```

---

### 2. MCP SDK for Tool Implementation

**Question**: What's the official MCP SDK pattern for stateless tools?

**Investigation**:
- MCP Python SDK provides `@mcp_tool` decorator
- Tools receive parameters as function arguments
- Stateless design requires all context (including user_id) as parameters

**Decision**: Use `@mcp_tool` decorator pattern with explicit user_id

**Rationale**:
- Standard pattern in MCP SDK ecosystem
- Explicit user_id parameter enforces security boundary
- Decorator handles tool schema generation automatically

**Security Considerations**:
- Every MCP tool MUST validate user_id parameter
- Tools must check user owns the data being accessed/modified
- Never trust client-provided user_id without authentication

**Implementation Pattern**:
```python
@mcp_tool
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    # Validate user exists (auth check)
    # Create task with user_id foreign key
    # Return created task
```

---

### 3. Streaming Responses via Server-Sent Events (SSE)

**Question**: How to implement SSE streaming from FastAPI to frontend widget?

**Investigation**:
- FastAPI provides `StreamingResponse` for SSE
- Frontend uses EventSource API or compatible library
- chatbot-widget-creator includes SSE client implementation

**Decision**: Use FastAPI `StreamingResponse` with `text/event-stream` content type

**Architecture**:
```
FastAPI (StreamingResponse) → SSE stream → Frontend EventSource
```

**Rationale**:
- Native FastAPI support, no additional dependencies
- Compatible with chatbot-widget-creator Agent Skill
- Simpler than WebSockets for unidirectional streaming

**Implementation Notes**:
```python
from fastapi.responses import StreamingResponse

async def generate_chat_response(user_id: str, message: str):
    # Run agent, stream tokens
    async for token in agent.stream(user_id, message):
        yield f"data: {json.dumps({'token': token})}\n\n"

@app.post("/api/{user_id}/chat")
async def chat(user_id: str, message: str):
    return StreamingResponse(
        generate_chat_response(user_id, message),
        media_type="text/event-stream"
    )
```

---

### 4. OpenRouter as OpenAI-Compatible API

**Question**: How to configure OpenAI Agents SDK to use OpenRouter?

**Investigation**:
- OpenRouter provides OpenAI-compatible API endpoint
- Requires API key in `Authorization` header (not standard OpenAI format)
- Base URL: `https://openrouter.ai/api/v1`

**Decision**: Set custom `base_url` and pass API key in headers

**Rationale**:
- Maintains OpenAI compatibility for easy fallback
- No subscription required (pay-per-use)
- Access to multiple models (Claude, GPT-4, etc.)

**Configuration**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "https://your-app.com",
        "X-Title": "Todo AI Chatbot"
    }
)
```

**Model Selection**:
- Primary: `anthropic/claude-3-haiku` (fast, cost-effective)
- Fallback: `openai/gpt-4o-mini` (if Claude unavailable)

---

### 5. SQLModel with PostgreSQL Best Practices

**Question**: Optimal SQLModel patterns for performance and type safety?

**Investigation**:
- SQLModel combines SQLAlchemy 2.0 + Pydantic
- Foreign keys require explicit relationship definitions
- Indexes critical for query performance (< 500ms p95 goal)

**Decision**:
- Explicit foreign key constraints in model definitions
- Composite indexes on (user_id, conversation_id) for Message queries
- Index on (user_id, completed) for Task filtering
- Use `select_for_update()` for concurrent modification safety

**Schema Design**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_task_user_completed", "user_id", "completed"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="tasks")
```

**Query Optimization**:
- Pagination for conversations > 100 messages
- Use `exec(select(Message).where(...).limit(100).offset(offset))`
- Connection pooling: `pool_size=20`, `max_overflow=40`

---

### 6. Stateless Conversation Context Loading

**Question**: How to efficiently load conversation history on every request?

**Investigation**:
- Full history fetch on every request is expensive
- LLM context windows have limits (typically 4k-128k tokens)
- User experience degrades with slow loads

**Decision**: Hybrid approach with pagination + short-term caching

**Strategy**:
1. **Fetch last N messages** (default: 50, max: 100) from database
2. **Cache recent conversations** (60s TTL) using Redis or in-memory cache
3. **Token counting**: Truncate history if exceeding model's context limit

**Implementation**:
```python
async def load_conversation_context(
    db: Session,
    user_id: str,
    conversation_id: str,
    limit: int = 50
) -> list[Message]:
    # Check cache first
    cached = await cache.get(f"conv:{conversation_id}")
    if cached:
        return cached

    # Fetch from DB with pagination
    messages = await exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    # Cache for 60 seconds
    await cache.set(f"conv:{conversation_id}", messages, ttl=60)

    return messages
```

**Performance Targets**:
- Cached loads: < 50ms
- Database loads: < 500ms (with indexes)
- Token limit: 8k tokens for context (~200-400 messages)

---

### 7. Better Auth Integration with FastAPI

**Question**: How to extract user_id from Better Auth JWT in FastAPI?

**Investigation**:
- Better Auth uses HTTP-only cookies or Authorization header
- JWT contains session data with user_id
- FastAPI dependencies are ideal for auth logic

**Decision**: Create FastAPI dependency that validates JWT and extracts user_id

**Implementation**:
```python
from fastapi import Depends, HTTPException, Cookie
from better_auth import BetterAuth

async def get_current_user(
    better_auth: BetterAuth = Depends(),
    session_token: str = Cookie(None)
) -> str:
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Validate session and extract user_id
    session = await better_auth.validateSession(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    return session.user_id

# Usage in endpoint
@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    message: str,
    current_user: str = Depends(get_current_user)
):
    # Verify user_id matches current_user
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="User mismatch")
    ...
```

**Security Layers**:
1. FastAPI dependency validates JWT
2. Endpoint verifies path user_id matches authenticated user
3. MCP tools verify user_id owns the data

---

### 8. Error Handling for MCP Tool Failures

**Question**: How should agent handle MCP tool failures?

**Investigation**:
- Database failures (connection timeout, query errors)
- Validation failures (invalid input, not found)
- Agent needs to communicate errors to user naturally

**Decision**: Two-layer error handling

**Layer 1: MCP Tools**
- Raise descriptive exceptions with error codes
- Never expose internal details (stack traces, DB errors)
- Return user-friendly error messages

**Layer 2: Agent**
- Catch tool exceptions
- Format natural language error explanation
- Suggest recovery actions

**Implementation**:
```python
# MCP tool
class TaskNotFoundError(Exception):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")

@mcp_tool
async def complete_task(user_id: str, task_id: str) -> dict:
    task = await get_task(task_id)
    if not task or task.user_id != user_id:
        raise TaskNotFoundError(task_id)
    task.completed = True
    await save(task)
    return {"task_id": task_id, "completed": True}

# Agent error handler
async def run_agent_with_error_handling(user_id: str, message: str):
    try:
        response = await agent.run(user_id, message)
    except TaskNotFoundError as e:
        response = f"I couldn't find a task with ID {e.task_id}. Would you like me to list your tasks?"
    except ValidationError as e:
        response = f"I understood you want to update a task, but I need a bit more information: {e}"
    except DatabaseError:
        response = "I'm having trouble connecting to my memory right now. Please try again in a moment."
    return response
```

---

## Technology Stack Summary

| Component | Technology | Version/Notes |
|-----------|-----------|---------------|
| **Backend** | | |
| Web Framework | FastAPI | 0.104+ |
| AI Orchestration | OpenAI Agents SDK | Latest |
| LLM Provider | OpenRouter | Claude 3 Haiku / GPT-4o-mini |
| Tool Protocol | MCP Python SDK | Official |
| Database ORM | SQLModel | 0.0.14+ (SQLAlchemy 2.0) |
| Database | Neon PostgreSQL | Serverless |
| Authentication | Better Auth | Existing from Phase I/II |
| **Frontend** | | |
| UI Framework | React | 18+ |
| Widget | chatbot-widget-creator | Agent Skill |
| Chat Library | OpenAI ChatKit | Per spec requirement |
| Streaming | EventSource API | Native browser API |
| **Testing** | | |
| Backend Tests | pytest + httpx | Async support |
| Frontend Tests | Jest + React Testing Library | Standard |

---

## Unresolved Questions

**None** - All technical decisions have been made.

---

## Next Steps

1. ✅ Research complete
2. ⏭️ Generate data-model.md with database schema
3. ⏭️ Generate API contracts (OpenAPI + MCP schemas)
4. ⏭️ Write quickstart.md with setup instructions
5. ⏭️ Update agent context with new technologies

---

**References**:
- [OpenAI Agents SDK Documentation](https://github.com/openai/agents-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [OpenRouter API](https://openrouter.ai/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Better Auth](https://better-auth.com)
