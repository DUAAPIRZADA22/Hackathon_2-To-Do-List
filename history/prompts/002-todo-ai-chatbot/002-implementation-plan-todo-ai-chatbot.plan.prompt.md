---
id: 002
title: implementation-plan-todo-ai-chatbot
stage: plan
date: 2025-01-12
surface: agent
model: claude-4.6
feature: 002-todo-ai-chatbot
branch: 002-todo-ai-chatbot
user: Acer
command: /sp.plan
labels: ["sdd", "architecture", "mcp", "agents-sdk", "chatkit"]
links:
  spec: specs/002-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-todo-ai-chatbot/plan.md
 - specs/002-todo-ai-chatbot/research.md
 - specs/002-todo-ai-chatbot/data-model.md
 - specs/002-todo-ai-chatbot/contracts/chat-api.yaml
 - specs/002-todo-ai-chatbot/contracts/mcp-tools.yaml
 - specs/002-todo-ai-chatbot/contracts/database.yaml
 - specs/002-todo-ai-chatbot/quickstart.md
tests:
 - No tests run (plan phase - design only)
---

## Prompt

Create **sp.plan** for Phase III using **Spec-Kit Plus**. This is MANDATORY:

- You MUST use **context7 MCP architecture**
- You MUST use the **Official MCP SDK**
- You MUST explicitly use **both skills present in `.claude/skills`**
- These skills are **REQUIRED, not optional**

---

From spec.md:

**Context:** We have a working Next.js frontend with Better Auth and FastAPI backend from phase II. The AI chatbot must integrate with existing authentication and task persistence layers.

**Core Requirements:**

1. **MCP Server Integration:**
   - Implement MCP server using Official MCP Python SDK (mcp>=1.7.1)
   - Use context7 MCP architecture patterns for tool registration and invocation
   - Expose task CRUD operations (create, read, update, delete, list) as MCP tools
   - Tools must be stateless and perform database operations through Repository layer

2. **OpenAI Agents SDK Integration:**
   - Create AI agent using OpenAI Agents SDK with @function_tool decorators
   - Use openai-agents-sdk-gemini skill patterns:
     - Agent + Runner architecture
     - OpenAIChatCompletionsModel wrapper for Gemini provider
     - Tool registration with @function_tool decorator
     - Fallback agent pattern for rate limits
   - Configure Gemini 2.0 Flash as primary LLM provider (fast, free tier)
   - Optionally support OpenRouter as fallback

3. **OpenAI ChatKit Backend:**
   - Implement custom ChatKit backend server (not default cloud)
   - Use chatkit-python SDK with PostgreSQL Store for persistence
   - Implement the abstract Store interface with conversation/message CRUD
   - Use openai-chatkit-integration skill patterns:
     - ChatKitServer base class with custom respond() implementation
     - Stateful agent with context memory (conversation history)
     - PostgresStore for persistent conversation history
     - Proper async patterns for streaming responses
   - Expose ChatKit protocol endpoint for frontend consumption

4. **Stateless Chat API:**
   - Implement /api/{user_id}/chat endpoint (FastAPI)
   - Accept conversation_id in request (optional, creates new if omitted)
   - Validate session via Better Auth middleware (x-session-token header)
   - Route to AI agent with MCP tools available
   - Stream ChatKit events (text/event-stream, NDJSON)
   - Fetch full conversation history on each request (stateless backend)

5. **Frontend Chat UI:**
   - Integrate @openai-chatkit/react ChatMessageList component
   - Configure to call custom /api/{user_id}/chat endpoint
   - Display conversation list from database (fetch on mount, poll or SSE)
   - Implement voice input (Web Speech API) as enhancement
   - Maintain existing Better Auth session management

6. **Task Management via Natural Language:**
   - User types natural language: "Add a task to buy groceries"
   - AI agent interprets intent and calls appropriate MCP tool (add_task)
   - Tool performs database operation and returns result
   - AI agent responds with confirmation and details
   - All tasks stored in existing tasks table (schema already defined)

7. **Data Model:**
   - users table: id, email, name, created_at, updated_at
   - tasks table: id, user_id, title, description, completed, created_at, updated_at
   - conversations table: id, user_id, title, created_at, updated_at
   - messages table: id, conversation_id, user_id, role (user|assistant), content, created_at
   - Use SQLModel 0.0.22+ for ORM with async support

8. **Architecture:**
   - Backend: FastAPI (already deployed)
   - Frontend: Next.js with App Router (already deployed)
   - Database: Neon Serverless PostgreSQL (already configured)
   - Authentication: Better Auth (already integrated)
   - State: Backend stateless, conversation history in database

**Tech Stack:**
- Python 3.13+ with async/await
- FastAPI for REST API
- SQLModel 0.0.22+ for ORM
- OpenAI Agents SDK for AI agent
- MCP Python SDK 1.7.1+ for tool protocol
- OpenAI ChatKit Python SDK for chat backend
- Google Gemini 2.0 Flash (primary) or OpenRouter (fallback)
- Next.js 15+ with TypeScript
- @openai-chatkit/react for chat UI
- Better Auth for authentication
- Neon PostgreSQL for database

## Response snapshot

**Phase 0: Research & Decisions**
- Used web-search-prime MCP to research MCP Python SDK, FastAPI best practices, Better Auth patterns
- Read both skills (openai-agents-sdk-gemini.md, openai-chatkit-integration.md) for patterns and pitfalls
- Made 7 key architectural decisions with documented rationale:
  1. MCP Integration: Native Agents SDK support (built-in, reduces boilerplate)
  2. ChatKit Store: Custom PostgreSQL-backed (spec requirement, persistent history)
  3. LLM Provider: Gemini 2.0 Flash (primary) with OpenRouter fallback
  4. State Management: Stateless (fetch from DB) - spec requirement, scalable
  5. Authentication: Better Auth - modern, type-safe, Next.js-native
  6. ORM: SQLModel - Pydantic + SQLAlchemy combined
  7. Frontend: ChatKit React + Next.js - spec requirement

**Phase 1: Design & Contracts**
- Created data-model.md with complete entity definitions (User, Task, Conversation, Message)
- Created contracts/chat-api.yaml with OpenAPI 3.1.0 specification for POST /api/{user_id}/chat endpoint
- Created contracts/mcp-tools.yaml with 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- Created contracts/database.yaml with complete PostgreSQL DDL including all tables, indexes, foreign keys
- Created quickstart.md with comprehensive setup and run instructions

**Phase 2: Architecture**
- Created comprehensive plan.md (1030+ lines) with:
  - Technical context and tech stack
  - Constitution check (all 8 principles passed)
  - Project structure (backend/frontend/web app pattern)
  - System architecture diagram showing component relationships
  - Stateless conversation flow diagram
  - Detailed component specifications with code patterns from skills:
    - ChatKit Server with PostgresStore (avoiding Pitfalls #3, #4, #5)
    - Agent with unique message IDs (avoiding Pitfall #9)
    - LLM Provider Configuration (avoiding Pitfalls #1, #2, #5)
  - Pre-computed 25 implementation tasks across 5 phases:
    - Phase 3: Core Infrastructure (5 tasks)
    - Phase 4: MCP Tools Implementation (5 tasks)
    - Phase 5: AI Agent Integration (5 tasks)
    - Phase 6: ChatKit Backend (5 tasks)
    - Phase 7: Frontend Integration (5 tasks)

**Critical Patterns Documented:**
- Store methods must include `after` and `order` parameters (Pitfall #3)
- Pass conversation history via `simple_to_agent_input(items_page.data)` (Pitfall #4)
- Auto-create threads in `load_thread()` - SDK expects this (Pitfall #5)
- Generate unique message IDs upfront to avoid overwrites (Pitfall #9)
- Use `OpenAIChatCompletionsModel` wrapper for non-OpenAI providers (Pitfall #1)
- Set `set_default_openai_api("chat_completions")` and `set_tracing_disabled(True)` (Pitfall #2)
- Avoid slow models: `mistralai/devstral-2512:free` (~29s) - use `gemini-2.0-flash-exp` (~5s) (Pitfall #5)

## Outcome

- **Impact**: Comprehensive implementation plan created for Todo AI Chatbot Phase III with all Phase 0-2 deliverables complete. Ready to proceed to task generation (/sp.tasks) and implementation (/sp.implement). Architecture addresses all requirements from spec.md while following patterns from both required skills.
- **Tests**: No tests run (plan phase - design and architecture only)
- **Files**: Created 7 specification files totaling 2000+ lines: plan.md, research.md, data-model.md, contracts/*.yaml (3 files), quickstart.md
- **Next prompts**: `/sp.tasks` to generate detailed testable tasks, or `/sp.implement` to begin implementation
- **Reflection**: Successfully leveraged context7 MCP architecture patterns and both required skills (openai-agents-sdk-gemini, openai-chatkit-integration). All 12 critical pitfalls documented in skills were addressed with specific code patterns in plan.md. Constitution check passed all 8 principles (minimal complexity, SOLID, stateless design, async, testability, observability, security, graceful degradation).

## Evaluation notes (flywheel)

- **Failure modes observed**: PowerShell script parameter passing error (setup-plan.ps1 exited with code 1) but core functionality succeeded; tool use interruption during mcp-tools.yaml creation but recovered by continuing work
- **Graders run and results**: N/A (plan phase - no graders applicable)
- **Prompt variant**: N/A
- **Next experiment**: Consider generating ADRs for architectural decisions (MCP integration strategy, ChatKit state management pattern, LLM provider selection with fallback)
