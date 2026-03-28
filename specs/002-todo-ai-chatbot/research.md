# Research: Todo AI Chatbot - Phase III

**Date**: 2025-01-12
**Feature**: 002-todo-ai-chatbot
**Phase**: 0 (Research & Decisions)

## Research Sources

This research leveraged:
1. **context7 MCP architecture** - For understanding MCP server patterns
2. **openai-agents-sdk-gemini skill** - For Agent + Runner patterns, tool integration
3. **openai-chatkit-integration skill** - For ChatKit backend integration patterns
4. **Web search via web-search-prime MCP** - For latest MCP SDK, FastAPI, and Better Auth patterns

## Key Findings

### 1. MCP Python SDK (Official)

**Source**: https://github.com/modelcontextprotocol/python-sdk

**Key Findings**:
- Official MCP Python SDK version: 1.7.1+
- Provides `@function_tool` decorator for tool registration
- OpenAI Agents SDK has native MCP integration
- Tools are automatically exposed as MCP-compatible

**Best Practices**:
- Use `@function_tool` decorator for all tool definitions
- Return structured data (dict) from tools for JSON serialization
- Include comprehensive docstrings for AI understanding

### 2. OpenAI Agents SDK + MCP

**Source**: openai-agents-sdk-gemini skill + https://openai.github.io/openai-agents-python/mcp/

**Key Findings**:
- MCP is natively supported in OpenAI Agents SDK
- Tools defined with `@function_tool` automatically register as MCP tools
- No separate MCP server process needed for same-process integration
- `OpenAIChatCompletionsModel` wrapper required for non-OpenAI providers

**Critical Pattern** (from skill):
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

**Performance Warning** (from skill):
- ❌ AVOID: `mistralai/devstral-2512:free` (~29 seconds response time)
- ✅ USE: `google/gemini-2.0-flash-exp:free` (~5 seconds)
- ✅ USE: `openai/gpt-4o-mini` (~2 seconds)

### 3. ChatKit Python SDK Integration

**Source**: openai-chatkit-integration skill + https://github.com/openai/chatkit-python

**Key Findings**:
- ChatKit Python SDK provides `ChatKitServer` base class
- Must implement `Store` abstract base class for persistence
- Store requires specific method signatures with all parameters
- `server.process()` handles routing (Pitfall #7 - don't implement custom respond)

**Critical Pitfalls Avoided** (from skill):
1. ✅ Correct imports: `from chatkit.server import ChatKitServer`, `from chatkit.store import Store`
2. ✅ Store methods include `after` and `order` parameters
3. ✅ Pass conversation history via `simple_to_agent_input(items_page.data)`
4. ✅ Auto-create threads in `load_thread()` - SDK expects this
5. ✅ Generate unique message IDs to avoid overwrites (Pitfall #9)

### 4. FastAPI Best Practices

**Source**: https://agentsarcade.com/blog/building-llm-apps-with-fastapi-best-practices

**Key Findings**:
- Use async/await for all I/O operations
- Implement proper dependency injection for database sessions
- Use `StreamingResponse` for real-time agent responses
- Implement health check endpoints for monitoring
- Add proper error handling middleware

**Pattern**:
```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/api/{user_id}/chat")
async def chat_endpoint(request: Request, user_id: str):
    payload = await request.body()
    result = await server.process(payload, context={"user_id": user_id})

    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )

    return Response(content=result.json, media_type="application/json")
```

### 5. Better Auth + Next.js

**Source**: Web search + https://www.better-auth.com/

**Key Findings**:
- Better Auth is the successor to NextAuth.js (Auth.js team joined Sept 2025)
- Type-safe, modern authentication for Next.js
- Built-in OAuth providers (Google, GitHub, email/password)
- Simple session management with cookies
- Works with App Router and Pages Router

**Pattern**:
```typescript
// frontend/src/lib/auth.ts
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

export const { signIn, signOut, useSession } = authClient

// In component:
import { useSession } from "@/lib/auth"

function ChatPage() {
  const { data: session } = useSession()
  // session.user contains user info
}
```

**Backend Integration**:
```python
# FastAPI validates Better Auth session
async def get_current_user(request: Request) -> User:
    session_token = request.cookies.get("better-auth.session_token")
    if not session_token:
        raise HTTPException(401, "Not authenticated")

    user = await validate_session(session_token)
    return user
```

### 6. SQLModel + PostgreSQL

**Source**: Spec requirements + standard Python practices

**Key Findings**:
- SQLModel combines Pydantic validation + SQLAlchemy ORM
- Automatic schema generation with `SQLModel.metadata.create_all()`
- Type safety with Python 3.13+ type hints
- Async support via `asyncpg` driver

**Pattern**:
```python
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Async repository
class TaskRepository:
    async def create_task(self, user_id: str, title: str, description: str | None = None) -> Task:
        # Implementation using async session
        pass
```

## Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MCP Integration | Native Agents SDK support | Built-in, reduces boilerplate |
| ChatKit Store | Custom PostgreSQL-backed | Spec requirement, persistent history |
| LLM Provider | Gemini 2.0 Flash (primary) | Fast, free tier available |
| State Management | Stateless (fetch from DB) | Spec requirement, scalable |
| Authentication | Better Auth | Modern, type-safe, Next.js-native |
| ORM | SQLModel | Pydantic + SQLAlchemy combined |
| Frontend | ChatKit React + Next.js | Spec requirement |
| Backend | FastAPI | Async native, great for LLM apps |

## Patterns to Follow

### From openai-agents-sdk-gemini skill:
1. Use `OpenAIChatCompletionsModel` wrapper for non-OpenAI providers
2. Set `set_default_openai_api("chat_completions")` and `set_tracing_disabled(True)`
3. Avoid slow models (29s response time)
4. Use `@function_tool` decorator for tool definitions
5. Implement fallback agent pattern for rate limits

### From openai-chatkit-integration skill:
1. Use correct imports: `from chatkit.server import ChatKitServer`
2. Implement Store with all required parameters (after, order)
3. Pass conversation history via `simple_to_agent_input()`
4. Auto-create threads in `load_thread()`
5. Generate unique message IDs to avoid overwrites
6. Use `server.process()` not custom respond implementation

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM rate limits | Fallback agent pattern from skill |
| Database latency | Indexes, read replicas, limit history |
| ChatKit protocol changes | Pin specific version, monitor updates |
| Memory leaks in streaming | Proper async cleanup |
| Tool naming conflicts | Clear naming convention |

## Next Steps

Phase 1 (Design & Contracts):
1. Create data-model.md with entity definitions
2. Create contracts/chat-api.yaml (OpenAPI spec)
3. Create contracts/mcp-tools.yaml (MCP tool schemas)
4. Create contracts/database.yaml (DDL)
5. Create quickstart.md (setup instructions)
