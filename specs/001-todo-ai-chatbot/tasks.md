# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Test tasks included - backend tests using pytest, frontend tests using Jest/React Testing Library

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (JavaScript/TypeScript/React)
- **Database**: `database/migrations/` (SQL migrations)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

### Backend Setup

- [X] T001 Create backend project structure in backend/src/ with subdirectories: api/, agent/, mcp/, db/, auth/
- [X] T002 Initialize Python project with backend/requirements.txt (FastAPI 0.104.1, SQLModel 0.0.14, OpenAI 1.3.0, MCP SDK 0.1.0, pytest 7.4.3)
- [X] T003 [P] Create backend/.env.template with DATABASE_URL, OPENROUTER_API_KEY, BETTER_AUTH_SECRET, CORS_ORIGINS
- [X] T004 [P] Create backend/pytest.ini with test discovery and async test configuration
- [X] T005 [P] Create backend/Dockerfile for production deployment
- [X] T006 [P] Create backend/README.md with setup and development instructions

### Frontend Setup

- [X] T007 Verify frontend project exists (from Phase I/II) with React 18+
- [X] T008 [P] Install chatbot-widget dependencies: npm install @your-org/chatbot-widget openai-chatkit
- [X] T009 [P] Create frontend/.env.local with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_URL

### Database Setup

- [X] T010 Create database/migrations/ directory structure
- [X] T011 Create database/migrations/001_create_tasks_conversations_messages.sql with Task, Conversation, Message tables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [X] T012 [P] Implement Task model in backend/src/db/models.py with user_id, title, description, completed, created_at, updated_at
- [X] T013 [P] Implement Conversation model in backend/src/db/models.py with user_id, id (UUID), created_at, updated_at
- [X] T014 [P] Implement Message model in backend/src/db/models.py with user_id, conversation_id, role, content, created_at, tool_calls
- [X] T015 Implement database session management in backend/src/db/session.py with async engine and connection pooling
- [X] T016 [P] Implement Task repository in backend/src/db/repository.py (get_task, create_task, list_tasks, update_task, delete_task)
- [X] T017 [P] Implement Conversation repository in backend/src/db/repository.py (get_conversation, get_or_create_conversation, add_message, get_conversation_history)
- [X] T018 Run database migrations and verify tables created correctly

### Authentication Layer

- [X] T019 [P] Implement Better Auth dependency in backend/src/auth/middleware.py with JWT validation and user_id extraction
- [X] T020 [P] Implement FastAPI auth dependency in backend/src/api/dependencies.py (get_current_user, require_user)
- [X] T021 Create FastAPI security scheme for Better Auth session token cookie

### MCP Server Layer

- [X] T022 [P] Implement base MCP tool class in backend/src/mcp/tools/base.py with error handling and user_id validation
- [X] T023 [P] Implement MCP server setup in backend/src/mcp/server.py with tool registry and initialization
- [X] T024 Implement MCP client wrapper in backend/src/mcp/client.py for agent integration

### API Framework

- [X] T025 [P] Create FastAPI application in backend/src/main.py with CORS middleware, exception handlers, health check endpoint
- [X] T026 [P] Implement error response models in backend/src/api/models.py with user-friendly messages
- [X] T027 [P] Configure structured logging in backend/src/main.py with request ID tracking

### Agent Framework

- [X] T028 [P] Implement OpenAI Agents SDK client in backend/src/agent/runner.py with OpenRouter configuration
- [X] T029 [P] Create agent system prompts in backend/src/agent/prompts.py with intent detection examples
- [X] T030 Implement conversation context builder in backend/src/agent/context.py with history loading from database

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing or speaking natural language (e.g., "Remember to buy groceries on Saturday")

**Independent Test**: User sends natural language message → task created with correct title and description → task appears in list

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T031 [P] [US1] Contract test for POST /api/{user_id}/chat in backend/tests/contract/test_chat_api.py validates request/response schema
- [X] T032 [P] [US1] Integration test for add_task MCP tool in backend/tests/integration/test_mcp_tools.py validates task creation
- [X] T033 [P] [US1] Integration test for agent intent detection in backend/tests/integration/test_agent_flow.py validates "add task" → add_task tool invocation

### Implementation for User Story 1

#### MCP Tools

- [X] T034 [P] [US1] Implement add_task MCP tool in backend/src/mcp/tools/task_tools.py with user_id, title, description parameters
- [X] T035 [US1] Register add_task tool with MCP server in backend/src/mcp/server.py

#### Agent Integration

- [X] T036 [US1] Implement intent detection for "create" intent in backend/src/agent/prompts.py (add, create, remember keywords)
- [X] T037 [US1] Wire add_task tool to OpenAI Agent in backend/src/agent/runner.py with function calling schema

#### API Layer

- [X] T038 [P] [US1] Implement chat endpoint in backend/src/api/chat.py with message persistence, agent execution, response formatting
- [X] T039 [US1] Add SSE streaming support in backend/src/api/chat.py with StreamingResponse for real-time tokens
- [X] T040 [US1] Implement conversation creation logic in backend/src/api/chat.py (new conversation if conversation_id not provided)

#### Frontend Integration

- [X] T041 [P] [US1] Create chat page component in frontend/src/pages/chat.tsx with ChatWidget integration
- [X] T042 [P] [US1] Implement chat API client in frontend/src/services/chat-api.ts with fetch and EventSource support
- [X] T043 [US1] Add authentication to chat API requests in frontend/src/services/chat-api.ts (forward Better Auth cookie)
- [X] T044 [US1] Style chat widget per quickstart (clean, minimal, friendly UX)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - Conversational Task Review and Management (Priority: P2)

**Goal**: Users can view tasks (all/pending/completed) and complete them through natural language

**Independent Test**: User creates tasks → asks to see pending tasks → tasks displayed → marks one complete → status updated

### Tests for User Story 2

- [ ] T045 [P] [US2] Contract test for list_tasks filter in backend/tests/contract/test_chat_api.py validates status parameter
- [ ] T046 [P] [US2] Integration test for list_tasks MCP tool in backend/tests/integration/test_mcp_tools.py validates filtering by status
- [ ] T047 [P] [US2] Integration test for complete_task flow in backend/tests/integration/test_agent_flow.py validates "mark done" → complete_task tool

### Implementation for User Story 2

#### MCP Tools

- [ ] T048 [P] [US2] Implement list_tasks MCP tool in backend/src/mcp/tools/task_tools.py with user_id, status (all/pending/completed) parameters
- [ ] T049 [P] [US2] Implement complete_task MCP tool in backend/src/mcp/tools/task_tools.py with user_id, task_id parameters
- [ ] T050 [US2] Register list_tasks and complete_task tools with MCP server in backend/src/mcp/server.py

#### Agent Integration

- [ ] T051 [US2] Implement intent detection for "list" intent in backend/src/agent/prompts.py (show, list, see, what do I need)
- [ ] T052 [US2] Implement intent detection for "complete" intent in backend/src/agent/prompts.py (done, complete, finished, mark as done)
- [ ] T053 [US2] Wire list_tasks and complete_task tools to OpenAI Agent in backend/src/agent/runner.py

#### API Layer

- [ ] T054 [US2] Add task listing response formatting in backend/src/api/chat.py (readable task list format for agent)
- [ ] T055 [US2] Add completion confirmation in backend/src/api/chat.py (polite confirmation message after tool execution)

#### Frontend Integration

- [ ] T056 [P] [US2] Implement task list display in frontend/src/components/chatbot-widget/MessageList.tsx (render formatted task lists)
- [ ] T057 [US2] Add completion confirmation UI in frontend/src/components/chatbot-widget/MessageBubble.tsx (visual feedback for completed tasks)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Task Modification Through Conversation (Priority: P3)

**Goal**: Users can update task title or description by referencing tasks naturally

**Independent Test**: User creates task → asks to change title/description → changes verified → persisted correctly

### Tests for User Story 3

- [ ] T058 [P] [US3] Contract test for update_task parameters in backend/tests/contract/test_chat_api.py validates title/description options
- [ ] T059 [P] [US3] Integration test for update_task MCP tool in backend/tests/integration/test_mcp_tools.py validates task modification
- [ ] T060 [P] [US3] Integration test for task reference resolution in backend/tests/integration/test_agent_flow.py validates "change X to Y" intent

### Implementation for User Story 3

#### MCP Tools

- [ ] T061 [P] [US3] Implement update_task MCP tool in backend/src/mcp/tools/task_tools.py with user_id, task_id, title (optional), description (optional) parameters
- [ ] T062 [US3] Implement task reference resolution in backend/src/mcp/tools/task_tools.py (find task by title, content, or position)
- [ ] T063 [US3] Register update_task tool with MCP server in backend/src/mcp/server.py

#### Agent Integration

- [ ] T064 [US3] Implement intent detection for "update" intent in backend/src/agent/prompts.py (change, update, rename, modify)
- [ ] T065 [US3] Implement task reference parsing in backend/src/agent/runner.py (extract task identifier from natural language)
- [ ] T066 [US3] Wire update_task tool to OpenAI Agent in backend/src/agent/runner.py

#### API Layer

- [ ] T067 [US3] Add update confirmation in backend/src/api/chat.py (show what changed: old → new)
- [ ] T068 [US3] Handle "task not found" errors in backend/src/api/chat.py (user-friendly error message)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Task Deletion via Natural Commands (Priority: P4)

**Goal**: Users can delete tasks by asking the chat to remove them

**Independent Test**: User creates task → asks to delete it → task removed from list → confirmation shown

### Tests for User Story 4

- [ ] T069 [P] [US4] Contract test for delete_task in backend/tests/contract/test_chat_api.py validates task removal
- [ ] T070 [P] [US4] Integration test for delete_task MCP tool in backend/tests/integration/test_mcp_tools.py validates deletion
- [ ] T071 [P] [US4] Integration test for delete confirmation in backend/tests/integration/test_agent_flow.py validates user notification

### Implementation for User Story 4

#### MCP Tools

- [ ] T072 [P] [US4] Implement delete_task MCP tool in backend/src/mcp/tools/task_tools.py with user_id, task_id parameters
- [ ] T073 [US4] Register delete_task tool with MCP server in backend/src/mcp/server.py

#### Agent Integration

- [ ] T074 [US4] Implement intent detection for "delete" intent in backend/src/agent/prompts.py (delete, remove, cancel)
- [ ] T075 [US4] Wire delete_task tool to OpenAI Agent in backend/src/agent/runner.py

#### API Layer

- [ ] T076 [US4] Add deletion confirmation in backend/src/api/chat.py (show which task was deleted for verification)

---

## Phase 7: User Story 5 - Continuous Conversation Context (Priority: P5)

**Goal**: Chat remembers conversation history across sessions - users can return and continue where they left off

**Independent Test**: User creates tasks → closes browser → returns → asks "what did I ask you to remember?" → tasks shown

### Tests for User Story 5

- [ ] T077 [P] [US5] Contract test for conversation persistence in backend/tests/contract/test_chat_api.py validates conversation_id handling
- [ ] T078 [P] [US5] Integration test for conversation history loading in backend/tests/integration/test_conversation.py validates context restoration
- [ ] T079 [P] [US5] Integration test for conversation continuity in backend/tests/integration/test_agent_flow.py validates multi-turn context

### Implementation for User Story 5

#### Database Layer

- [ ] T080 [P] [US5] Implement conversation history pagination in backend/src/db/repository.py (limit 100 messages, offset support)
- [ ] T081 [P] [US5] Add conversation caching in backend/src/db/repository.py (60s TTL for recent conversations)

#### Agent Integration

- [ ] T082 [US5] Implement conversation history injection in backend/src/agent/context.py (load last N messages as agent context)
- [ ] T083 [US5] Add token counting in backend/src/agent/context.py (truncate if exceeding model context limit)

#### API Layer

- [ ] T084 [US5] Add conversation_id persistence in backend/src/api/chat.py (return new conversation_id for new conversations)
- [ ] T085 [US5] Implement conversation resumption in backend/src/api/chat.py (load history when conversation_id provided)

#### Frontend Integration

- [ ] T086 [P] [US5] Implement conversation persistence in frontend/src/services/chat-api.ts (store and reuse conversation_id)
- [ ] T087 [US5] Add conversation restoration in frontend/src/pages/chat.tsx (load previous messages on page load)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling

- [ ] T088 [P] Implement graceful database error handling in backend/src/api/chat.py (retry with exponential backoff, user-friendly messages)
- [ ] T089 [P] Add AI service timeout handling in backend/src/agent/runner.py (fallback response on timeout)
- [ ] T090 [P] Implement MCP tool error formatting in backend/src/mcp/tools/task_tools.py (descriptive user messages)

### Security

- [ ] T091 [P] Add user_id enforcement validation in backend/src/mcp/tools/task_tools.py (verify user owns data)
- [ ] T092 [P] Implement SQL injection prevention in backend/src/db/models.py (use parameterized queries only)
- [ ] T093 [P] Add input sanitization in backend/src/api/chat.py (max length checks, XSS prevention)

### Performance

- [ ] T094 [P] Add database indexes in database/migrations/001_create_tasks_conversations_messages.sql (idx_tasks_user_completed, idx_messages_conv_created)
- [ ] T095 [P] Implement connection pooling in backend/src/db/session.py (pool_size=20, max_overflow=40)
- [ ] T096 [P] Add response time monitoring in backend/src/api/chat.py (log p95 latency)

### Documentation

- [ ] T097 [P] Update backend/README.md with environment setup, migration steps, testing instructions
- [ ] T098 [P] Update backend/requirements.txt with exact pinned versions
- [ ] T099 [P] Add API documentation comments in backend/src/api/chat.py (OpenAPI descriptions)

### Testing

- [ ] T100 [P] Add unit tests for Task model validation in backend/tests/unit/test_models.py
- [ ] T101 [P] Add unit tests for repository layer in backend/tests/unit/test_repository.py
- [ ] T102 [P] Add frontend ChatWidget unit tests in frontend/tests/chatbot/ChatWidget.test.tsx
- [ ] T103 [P] Add frontend SSE client tests in frontend/tests/chatbot/sse-client.test.ts

### Deployment

- [ ] T104 [P] Create production environment variable template in backend/.env.production
- [ ] T105 [P] Add Docker Compose configuration for local development in docker-compose.yml
- [ ] T106 Validate quickstart.md setup instructions work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1 tasks but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses US1 tasks but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Cross-cutting but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- MCP tools before agent integration
- Agent integration before API layer
- API layer before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- MCP tools within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/{user_id}/chat in backend/tests/contract/test_chat_api.py"
Task: "Integration test for add_task MCP tool in backend/tests/integration/test_mcp_tools.py"
Task: "Integration test for agent intent detection in backend/tests/integration/test_agent_flow.py"

# Launch all MCP tools for User Story 1 together:
Task: "Implement add_task MCP tool in backend/src/mcp/tools/task_tools.py"
Task: "Register add_task tool with MCP server in backend/src/mcp/server.py"

# Launch all frontend components for User Story 1 together:
Task: "Create chat page component in frontend/src/pages/chat.tsx"
Task: "Implement chat API client in frontend/src/services/chat-api.ts"
Task: "Add authentication to chat API requests in frontend/src/services/chat-api.ts"
Task: "Style chat widget per quickstart"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP delivers**: Users can create tasks by typing natural language

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Complete Polish phase → Production-ready
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (P1 - MVP)
   - Developer B: User Story 2 (P2)
   - Developer C: User Story 3 (P3)
3. Stories complete and integrate independently
4. Developer D: User Stories 4 & 5 (P4, P5)
5. All: Polish phase together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests written first (TDD), ensure they fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 106
- MVP tasks (Phases 1-3): 44 tasks
- Per user story average: 13-15 tasks
- Parallel opportunities: 67 tasks marked [P]

---

**Generated**: 2025-01-09
**Feature**: 001-todo-ai-chatbot
**Branch**: 001-todo-ai-chatbot
**Ready for**: Implementation after explicit approval
