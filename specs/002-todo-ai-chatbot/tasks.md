---

description: "Task list for Todo AI Chatbot implementation"
---

# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/002-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md

**Tests**: Tests are NOT included in this specification - spec.md does not explicitly request TDD approach

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- This is a web app with separate backend and frontend

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure: backend/src/{agent,api,auth,db,mcp,core}
- [x] T002 Initialize Python project with uv and dependencies in backend/requirements.txt
- [x] T003 [P] Configure Python linting (ruff) and formatting (black) in backend/pyproject.toml
- [x] T004 [P] Create backend/.env.template with DATABASE_URL, GEMINI_API_KEY, BETTER_AUTH_SECRET, FRONTEND_URL
- [x] T005 [P] Create backend/.gitignore for venv, __pycache__, .env
- [x] T006 [P] Create backend/Dockerfile for containerization
- [x] T007 [P] Create backend/pytest.ini for test configuration
- [x] T008 [P] Create frontend/.env.local.template with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_URL, BETTER_AUTH_SECRET
- [x] T009 [P] Verify existing backend dependencies (FastAPI, uvicorn, SQLModel) are compatible with new requirements

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Setup database schema per contracts/database.yaml in backend/src/db/init_db.py
- [x] T011 [P] Create SQLModel base classes in backend/src/db/models.py (User, Task, Conversation, Message from data-model.md)
- [ ] T012 [P] Implement async database session management in backend/src/db/session.py
- [ ] T013 [P] Create repository base class in backend/src/db/repository.py with CRUD patterns
- [ ] T014 [P] Implement Better Auth session validation middleware in backend/src/auth/middleware.py
- [ ] T015 [P] Create FastAPI app structure with CORS in backend/src/main.py
- [ ] T016 [P] Implement health check endpoint at /health in backend/src/api/health.py
- [ ] T017 [P] Setup error handling middleware in backend/src/core/errors.py
- [ ] T018 [P] Configure environment loading with python-dotenv in backend/src/core/config.py
- [ ] T019 Add OpenAI Agents SDK dependency with OpenAIChatCompletionsModel wrapper pattern in backend/requirements.txt
- [ ] T020 Add MCP Python SDK (mcp>=1.7.1) dependency in backend/requirements.txt
- [ ] T021 Add ChatKit Python SDK dependency in backend/requirements.txt
- [ ] T022 Create LLM provider configuration module in backend/src/agent/provider.py (Gemini 2.0 Flash with OpenRouter fallback)
- [ ] T023 Verify database connection and schema creation by running backend/src/db/init_db.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Users can add, list, and complete tasks using natural language in a chat interface

**Independent Test**:
1. Sign in to the app
2. Navigate to chat
3. Type "Add a task to buy groceries"
4. Verify task appears in database
5. Type "Show my tasks" and verify the task is listed
6. Type "Mark the groceries task as complete"
7. Verify task.completed is true in database

### Implementation for User Story 1

#### MCP Tools (Task Operations)

- [ ] T024 [P] [US1] Create MCP tool: add_task in backend/src/mcp/tools/add_task.py with @function_tool decorator
- [ ] T025 [P] [US1] Create MCP tool: list_tasks in backend/src/mcp/tools/list_tasks.py with @function_tool decorator
- [ ] T026 [P] [US1] Create MCP tool: complete_task in backend/src/mcp/tools/complete_task.py with @function_tool decorator
- [ ] T027 [P] [US1] Create MCP tool: delete_task in backend/src/mcp/tools/delete_task.py with @function_tool decorator
- [ ] T028 [P] [US1] Create MCP tool: update_task in backend/src/mcp/tools/update_task.py with @function_tool decorator

#### Task Repositories

- [ ] T029 [P] [US1] Create TaskRepository in backend/src/db/repositories/task_repository.py with async create, list, update methods
- [ ] T030 [P] [US1] Implement TaskRepository.create_task() in backend/src/db/repositories/task_repository.py
- [ ] T031 [P] [US1] Implement TaskRepository.list_tasks() in backend/src/db/repositories/task_repository.py with status filter
- [ ] T032 [P] [US1] Implement TaskRepository.get_by_id() in backend/src/db/repositories/task_repository.py
- [ ] T033 [US1] Implement TaskRepository.update_task() in backend/src/db/repositories/task_repository.py (depends on T032)

#### AI Agent Integration

- [ ] T034 [P] [US1] Create agent module in backend/src/agent/__init__.py
- [ ] T035 [P] [US1] Create task agent in backend/src/agent/task_agent.py using OpenAI Agents SDK patterns
- [ ] T036 [US1] Register MCP tools with agent using @function_tool decorator in backend/src/agent/task_agent.py (depends on T024-T028)
- [ ] T037 [US1] Implement agent Runner with streaming in backend/src/agent/task_agent.py (depends on T035, T022)
- [ ] T038 [US1] Add unique message ID generation to avoid overwrites (Pitfall #9) in backend/src/agent/task_agent.py

#### Chat API Endpoint

- [ ] T039 [P] [US1] Create chat request/response models in backend/src/api/models.py (ChatRequest, ChatResponse)
- [ ] T040 [P] [US1] Create chat endpoint dependencies in backend/src/api/dependencies.py (get_current_user from session token)
- [ ] T041 [US1] Implement POST /api/{user_id}/chat endpoint in backend/src/api/chat.py (depends on T037, T040)
- [ ] T042 [US1] Add session validation middleware to chat endpoint in backend/src/api/chat.py (depends on T014, T041)
- [ ] T043 [US1] Implement streaming response format (text/event-stream, NDJSON) in backend/src/api/chat.py (depends on T041)

#### Frontend Chat UI

- [ ] T044 [P] [US1] Install @openai-chatkit/react dependency in frontend/package.json
- [ ] T045 [P] [US1] Create chat page at frontend/src/app/chat/page.tsx
- [ ] T046 [P] [US1] Create ChatMessageList component in frontend/src/components/ChatMessageList.tsx
- [ ] T047 [US1] Implement chat API service in frontend/src/services/chat-api.ts (depends on T044)
- [ ] T048 [US1] Connect ChatMessageList to backend /api/{user_id}/chat endpoint in frontend/src/components/ChatMessageList.tsx (depends on T046, T047)
- [ ] T049 [US1] Add chat route to navigation in frontend/src/components/Sidebar.tsx

#### Integration & Testing

- [ ] T050 [US1] Test full flow: user types "Add task" → MCP tool → database → confirmation in frontend
- [ ] T051 [US1] Test task completion flow via natural language in backend/src/agent/task_agent.py
- [ ] T052 [US1] Verify conversation history persistence in backend/src/db/session.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can manage tasks via natural language chat

---

## Phase 4: User Story 2 - Conversation History (Priority: P2)

**Goal**: Users can view past conversations and continue existing chats

**Independent Test**:
1. Create a new conversation and add tasks
2. Navigate away and back
3. Verify conversation list shows the previous conversation
4. Click to resume and verify message history loads
5. Add a new task and verify it's added to the correct conversation

### Implementation for User Story 2

#### Conversation & Message Repositories

- [ ] T053 [P] [US2] Create ConversationRepository in backend/src/db/repositories/conversation_repository.py
- [ ] T054 [P] [US2] Create MessageRepository in backend/src/db/repositories/message_repository.py
- [ ] T055 [P] [US2] Implement ConversationRepository.create_or_get() in backend/src/db/repositories/conversation_repository.py
- [ ] T056 [P] [US2] Implement ConversationRepository.list_by_user() in backend/src/db/repositories/conversation_repository.py
- [ ] T057 [P] [US2] Implement MessageRepository.create_message() in backend/src/db/repositories/message_repository.py
- [ ] T058 [P] [US2] Implement MessageRepository.list_by_conversation() in backend/src/db/repositories/message_repository.py

#### ChatKit Store Implementation

- [ ] T059 [P] [US2] Create PostgresStore class in backend/src/mcp/store/postgres_store.py implementing chatkit.store.Store
- [ ] T060 [US2] Implement PostgresStore.load_thread_items() with after/order parameters in backend/src/mcp/store/postgres_store.py (Pitfall #3)
- [ ] T061 [US2] Implement PostgresStore.load_thread() with auto-create pattern in backend/src/mcp/store/postgres_store.py (Pitfall #5)
- [ ] T062 [US2] Implement PostgresStore.upsert_thread() in backend/src/mcp/store/postgres_store.py
- [ ] T063 [US2] Implement PostgresStore.create_item() in backend/src/mcp/store/postgres_store.py with unique ID generation (Pitfall #9)
- [ ] T064 [US2] Implement PostgresStore.update_thread_title() in backend/src/mcp/store/postgres_store.py
- [ ] T065 [US2] Convert database messages to ThreadItem format in backend/src/mcp/store/postgres_store.py (Pitfall #4)

#### ChatKit Server Integration

- [ ] T066 [P] [US2] Create ChatKit server base in backend/src/mcp/server.py extending ChatKitServer
- [ ] T067 [US2] Implement ChatKit server.respond() with agent integration in backend/src/mcp/server.py (depends on T059, T035)
- [ ] T068 [US2] Wire PostgresStore to ChatKit server in backend/src/mcp/server.py (depends on T066)
- [ ] T069 [US2] Integrate ChatKit server with chat endpoint in backend/src/api/chat.py (depends on T041, T067)
- [ ] T070 [US2] Update chat endpoint to handle conversation_id parameter in backend/src/api/chat.py (depends on T069)

#### Frontend Conversation List

- [ ] T071 [P] [US2] Create conversation list API service in frontend/src/services/conversation-api.ts
- [ ] T072 [P] [US2] Create ConversationList component in frontend/src/components/ConversationList.tsx
- [ ] T073 [US2] Fetch and display conversations on mount in frontend/src/components/ConversationList.tsx (depends on T072)
- [ ] T074 [US2] Implement conversation selection/resumption in frontend/src/components/ConversationList.tsx (depends on T073)
- [ ] T075 [US2] Pass conversation_id to chat endpoint when resuming in frontend/src/components/ChatMessageList.tsx (depends on T048, T074)

#### Integration & Testing

- [ ] T076 [US2] Test conversation creation and persistence across page refreshes
- [ ] T077 [US2] Test conversation resumption with full message history
- [ ] T078 [US2] Test multiple conversations per user isolation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can manage tasks via chat with conversation history

---

## Phase 5: User Story 3 - Task Editing & Deletion (Priority: P3)

**Goal**: Users can update task details and delete tasks via natural language

**Independent Test**:
1. Create a task "Buy groceries"
2. Type "Change the groceries task to Buy organic groceries"
3. Verify task title is updated in database
4. Type "Delete the groceries task"
5. Verify task is removed from database

### Implementation for User Story 3

#### Task Repository Extensions

- [ ] T079 [P] [US3] Implement TaskRepository.delete_task() in backend/src/db/repositories/task_repository.py
- [ ] T080 [P] [US3] Add user ownership validation to TaskRepository methods in backend/src/db/repositories/task_repository.py
- [ ] T081 [US3] Add error handling for task not found (404) and wrong user (403) in backend/src/db/repositories/task_repository.py

#### MCP Tool Enhancements

- [ ] T082 [P] [US3] Add update_task error handling in backend/src/mcp/tools/update_task.py
- [ ] T083 [P] [US3] Add delete_task error handling in backend/src/mcp/tools/delete_task.py
- [ ] T084 [US3] Update agent to handle task ownership errors gracefully in backend/src/agent/task_agent.py

#### Frontend Enhancements

- [ ] T085 [P] [US3] Add task edit/delete confirmation UI in frontend/src/components/ChatMessageList.tsx
- [ ] T086 [US3] Display error messages for failed operations in frontend/src/components/ChatMessageList.tsx

#### Integration & Testing

- [ ] T087 [US3] Test task title update via natural language
- [ ] T088 [US3] Test task description update via natural language
- [ ] T089 [US3] Test task deletion via natural language
- [ ] T090 [US3] Test permission errors (user cannot access another user's tasks)

**Checkpoint**: All user stories should now be independently functional - full CRUD on tasks via natural language

---

## Phase 6: User Story 4 - AI Assistant Personality & Context (Priority: P4)

**Goal**: AI assistant provides helpful, contextual responses about task management

**Independent Test**:
1. Ask "What tasks do I have?" when no tasks exist
2. Verify helpful "You have no tasks" response
3. Create tasks, ask again
4. Verify task list with suggestions
5. Ask for help on task management
6. Verify helpful guidance

### Implementation for User Story 4

#### Agent System Prompt

- [ ] T091 [P] [US4] Create system prompt module in backend/src/agent/prompts.py
- [ ] T092 [US4] Implement task management context prompt in backend/src/agent/prompts.py
- [ ] T093 [US4] Add personality and tone guidelines to system prompt in backend/src/agent/prompts.py

#### Context Injection

- [ ] T094 [P] [US4] Create context builder module in backend/src/agent/context.py
- [ ] T095 [US4] Implement fetch_user_context() for task count and pending status in backend/src/agent/context.py (depends on T031)
- [ ] T096 [US4] Inject context into agent Runner call in backend/src/agent/task_agent.py (depends on T094, T037)

#### Response Formatting

- [ ] T097 [P] [US4] Add response formatter module in backend/src/agent/formatter.py
- [ ] T098 [US4] Implement friendly response formatting for task operations in backend/src/agent/formatter.py
- [ ] T099 [US4] Add suggestions and tips to responses in backend/src/agent/formatter.py

#### Frontend Display

- [ ] T100 [P] [US4] Style assistant messages for better readability in frontend/src/app/globals.css
- [ ] T101 [US4] Add markdown rendering for assistant responses in frontend/src/components/ChatMessageList.tsx

#### Integration & Testing

- [ ] T102 [US4] Test empty state responses (no tasks)
- [ ] T103 [US4] Test contextual responses with pending tasks
- [ ] T104 [US4] Test help and guidance responses

**Checkpoint**: AI assistant now provides helpful, contextual, personality-driven responses

---

## Phase 7: User Story 5 - Voice Input (Priority: P5)

**Goal**: Users can use voice input for natural language commands

**Independent Test**:
1. Click microphone button in chat
2. Speak "Add a task to call mom"
3. Verify transcribed text appears in input
4. Send message and verify task is created

### Implementation for User Story 5

#### Frontend Voice Input

- [ ] T105 [P] [US5] Check Web Speech API browser support in frontend/src/components/VoiceInput.tsx
- [ ] T106 [P] [US5] Create VoiceInput button component in frontend/src/components/VoiceInput.tsx
- [ ] T107 [US5] Implement speech recognition in frontend/src/components/VoiceInput.tsx
- [ ] T108 [US5] Handle recognition errors gracefully in frontend/src/components/VoiceInput.tsx
- [ ] T109 [US5] Add visual feedback during recording in frontend/src/components/VoiceInput.tsx
- [ ] T110 [US5] Integrate VoiceInput with ChatMessageList in frontend/src/components/ChatMessageList.tsx

#### Integration & Testing

- [ ] T111 [US5] Test voice input on supported browsers (Chrome, Edge)
- [ ] T112 [US5] Test graceful degradation on unsupported browsers
- [ ] T113 [US5] Test recognition accuracy with various accents

**Checkpoint**: Voice input enabled for hands-free task management

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T114 [P] Create backend/README.md with setup and run instructions
- [ ] T115 [P] Add API documentation using FastAPI auto-docs in backend/src/main.py
- [ ] T116 [P] Implement structured logging with correlation IDs in backend/src/core/logging.py
- [ ] T117 [P] Add rate limiting to chat endpoint in backend/src/api/middleware/rate_limit.py
- [ ] T118 [P] Add request timeout handling in backend/src/api/chat.py
- [ ] T119 [P] Implement graceful degradation when LLM API fails in backend/src/agent/task_agent.py
- [ ] T120 [P] Add database connection pooling configuration in backend/src/db/session.py
- [ ] T121 [P] Optimize conversation history queries (limit, pagination) in backend/src/db/repositories/message_repository.py
- [ ] T122 [P] Add input sanitization for user messages in backend/src/api/chat.py
- [ ] T123 [P] Add CSP headers for XSS protection in backend/src/main.py
- [ ] T124 [P] Create database migration strategy in backend/src/db/migrations/
- [ ] T125 [P] Add monitoring/metrics endpoints in backend/src/api/metrics.py
- [ ] T126 Code cleanup: remove unused imports and dead code across backend/
- [ ] T127 Performance optimization: profile and optimize slow queries
- [ ] T128 Security: run dependency audit and update vulnerable packages
- [ ] T129 Run quickstart.md validation to ensure setup works end-to-end
- [ ] T130 Create deployment documentation for production environment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Task Management): No dependencies on other user stories
  - US2 (Conversation History): Builds on US1 chat infrastructure, but independently testable
  - US3 (Task Edit/Delete): Extends US1 MCP tools, independently testable
  - US4 (AI Personality): Enhances all stories, independently deployable
  - US5 (Voice Input): Purely frontend enhancement, independently testable
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    │
    ├─→ US1: Task Management (P1) 🎯 MVP ──────────────────────┐
    │                                                          │
    ├─→ US2: Conversation History (P2) ────┐                  │
    │         │                             │                  │
    │         └─→ Uses US1 chat infra ──────┤                  │
    │                                       │                  │
    ├─→ US3: Task Edit/Delete (P3) ────────┤                  │
    │         │                             │                  │
    │         └─→ Extends US1 MCP tools ────┤                  │
    │                                       │                  │
    ├─→ US4: AI Personality (P4) ──────────┼──────────────────┤
    │         │                             │                  │
    │         └─→ Enhances all stories ─────┴──────────────────┤
    │                                                          │
    └─→ US5: Voice Input (P5) ────────────────────────────────┘
              │
              └─→ Purely frontend, no backend deps
```

### Within Each User Story

- Models and repositories before agent integration
- MCP tools can be created in parallel (same file structure, no dependencies)
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (1)**:
- T003, T004, T005, T007, T008 can run in parallel (different files)

**Foundational Phase (2)**:
- T011, T012, T013 can run in parallel (different files)
- T014, T015, T017, T018 can run in parallel (different files)

**User Story 1**:
- T024-T028 (5 MCP tools) can run in parallel
- T029-T032 (repository methods) can run in parallel
- T034, T035 can run in parallel
- T039, T040 can run in parallel
- T044, T045, T046 can run in parallel

**User Story 2**:
- T053, T054 can run in parallel
- T055-T058 can run in parallel
- T071, T072 can run in parallel

**Across User Stories**:
- Once Foundational (Phase 2) completes, US1-US3 can be worked on in parallel by different developers
- US4 and US5 can be developed alongside US1-US3

---

## Parallel Example: User Story 1

```bash
# Launch all MCP tools for US1 together (5 parallel agents):
Task T024: "Create MCP tool: add_task in backend/src/mcp/tools/add_task.py"
Task T025: "Create MCP tool: list_tasks in backend/src/mcp/tools/list_tasks.py"
Task T026: "Create MCP tool: complete_task in backend/src/mcp/tools/complete_task.py"
Task T027: "Create MCP tool: delete_task in backend/src/mcp/tools/delete_task.py"
Task T028: "Create MCP tool: update_task in backend/src/mcp/tools/update_task.py"

# Launch all repository methods for US1 together (4 parallel agents):
Task T029: "Create TaskRepository in backend/src/db/repositories/task_repository.py"
Task T030: "Implement TaskRepository.create_task()"
Task T031: "Implement TaskRepository.list_tasks()"
Task T032: "Implement TaskRepository.get_by_id()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯

**Target**: Natural language task management in ~23 tasks

1. Complete Phase 1: Setup (9 tasks, T001-T009)
2. Complete Phase 2: Foundational (14 tasks, T010-T023)
3. Complete Phase 3: User Story 1 (29 tasks, T024-T052)
4. **STOP and VALIDATE**: Test full flow independently
5. Deploy/demo MVP

**MVP delivers**: Users can add, list, and complete tasks via natural language chat

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup and infrastructure ready
2. **MVP** (+Phase 3): Basic task management via chat → Deploy/Demo 🎯
3. **Conversation History** (+Phase 4): Resume past chats → Deploy/Demo
4. **Full CRUD** (+Phase 5): Edit and delete tasks → Deploy/Demo
5. **Enhanced AI** (+Phase 6): Personality and context → Deploy/Demo
6. **Voice Input** (+Phase 7): Hands-free operation → Deploy/Demo
7. **Production Ready** (+Phase 8): Polish and hardening → Final Release

### Parallel Team Strategy

With 3 developers:

1. **Week 1**: All work together on Setup + Foundational (23 tasks)
2. **Week 2-3**: Parallel work on user stories:
   - **Developer A**: US1 Task Management (29 tasks)
   - **Developer B**: US2 Conversation History (26 tasks)
   - **Developer C**: US3 Task Edit/Delete (12 tasks)
3. **Week 4**: Polish and integration (17 tasks)

---

## Task Count Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1: Setup | 9 | Project initialization |
| 2: Foundational | 14 | Core infrastructure (BLOCKS all stories) |
| 3: US1 - Task Management | 29 | Natural language CRUD (P1) 🎯 |
| 4: US2 - Conversation History | 26 | Chat persistence (P2) |
| 5: US3 - Edit/Delete | 12 | Full task CRUD (P3) |
| 6: US4 - AI Personality | 14 | Enhanced responses (P4) |
| 7: US5 - Voice Input | 9 | Speech recognition (P5) |
| 8: Polish | 17 | Cross-cutting improvements |
| **TOTAL** | **130** | |

**Parallelizable Tasks**: ~75 tasks marked [P]

### MVP Scope (User Story 1)

- **Tasks**: 52 total (Setup + Foundational + US1)
- **Time Estimate**: 1-2 weeks with 1 developer
- **Delivers**: Natural language task management chat interface

---

## Format Validation

**All tasks follow checklist format**:
- ✅ Checkbox: `- [ ]`
- ✅ Task ID: T001-T130 sequential
- ✅ [P] marker: Applied to parallelizable tasks
- ✅ [Story] label: Applied to user story tasks (US1-US5)
- ✅ File paths: Included in all task descriptions
- ✅ Independent test criteria: Defined for each user story

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## References

- **Specification**: `specs/002-todo-ai-chatbot/spec.md`
- **Architecture Plan**: `specs/002-todo-ai-chatbot/plan.md`
- **Data Model**: `specs/002-todo-ai-chatbot/data-model.md`
- **API Contracts**: `specs/002-todo-ai-chatbot/contracts/`
- **Research**: `specs/002-todo-ai-chatbot/research.md`
- **Quickstart**: `specs/002-todo-ai-chatbot/quickstart.md`
