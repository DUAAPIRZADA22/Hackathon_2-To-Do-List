# Tasks: ActionMind AI CLI Task Manager (Phase 1)

**Input**: Design documents from `/specs/001-cli-task-manager/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No automated tests for Phase 1 per spec (manual testing via CLI execution)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure (src/, src/models/, src/services/, src/cli/, src/lib/)
- [x] T002 [P] Create src/__init__.py with package docstring
- [x] T003 [P] Create src/models/__init__.py
- [x] T004 [P] Create src/services/__init__.py
- [x] T005 [P] Create src/cli/__init__.py
- [x] T006 [P] Create src/lib/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Model

- [x] T007 Create TaskStatus enum in src/models/task.py
- [x] T008 Create Task dataclass in src/models/task.py with id, description, status, created_at fields
- [x] T009 Implement Task.__post_init__() for validation in src/models/task.py

### Storage Layer

- [x] T010 Create StorageInterface abstract class in src/lib/mcp_placeholder.py
- [x] T011 Create InMemoryStorage class in src/services/storage.py
- [x] T012 Implement InMemoryStorage.add() method in src/services/storage.py
- [x] T013 Implement InMemoryStorage.get_all() method in src/services/storage.py
- [x] T014 Implement InMemoryStorage.get_by_id() method in src/services/storage.py
- [x] T015 Implement InMemoryStorage.update() method in src/services/storage.py
- [x] T016 Implement InMemoryStorage.delete() method in src/services/storage.py
- [x] T017 Implement InMemoryStorage.generate_id() method in src/services/storage.py

### Validation Utilities

- [x] T018 Create validate_menu_selection() function in src/lib/validation.py
- [x] T019 Create validate_task_id() function in src/lib/validation.py
- [x] T020 Create validate_description() function in src/lib/validation.py

### Display Utilities

- [x] T021 Create display_styled_heading() function in src/cli/display.py
- [x] T022 Create display_success() function in src/cli/display.py
- [x] T023 Create display_warning() function in src/cli/display.py
- [x] T024 Create display_error() function in src/cli/display.py
- [x] T025 Create display_task_table() function in src/cli/display.py
- [x] T026 Create prompt_for_input() function in src/cli/display.py
- [x] T027 Create pause_for_acknowledgment() function in src/cli/display.py

### Task Service

- [x] T028 Create TaskService class in src/services/task_service.py
- [x] T029 Implement TaskService.__init__() with storage dependency injection in src/services/task_service.py
- [x] T030 Implement TaskService.create_task() method in src/services/task_service.py
- [x] T031 Implement TaskService.get_all_tasks() method in src/services/task_service.py
- [x] T032 Implement TaskService.get_task_by_id() method in src/services/task_service.py
- [x] T033 Implement TaskService.complete_task() method in src/services/task_service.py
- [x] T034 Implement TaskService.delete_task() method in src/services/task_service.py

### Main Menu Infrastructure

- [x] T035 Create display_main_menu() function in src/cli/menu.py
- [x] T036 Create get_menu_selection() function in src/cli/menu.py
- [x] T037 Create main_menu_loop() function in src/cli/menu.py with routing logic

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Main Menu (Priority: P1) 🎯 MVP

**Goal**: Display styled main menu with heading and 5 numbered options

**Independent Test**: Launching the application (`python -m src.main`) displays the main menu with styled heading, 5 numbered options (1-5), and an exit option

### Implementation for User Story 1

- [x] T038 [US1] Create application entry point in src/main.py
- [x] T039 [US1] Initialize storage and task_service in src/main.py
- [x] T040 [US1] Call main_menu_loop() from src/main.py and handle graceful exit

**Checkpoint**: At this point, User Story 1 should be fully functional - launching the app displays a styled menu

---

## Phase 4: User Story 2 - Add New Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks through interactive prompts with visual feedback

**Independent Test**: Selecting option 1 prompts for task description, creates task with unique ID, displays ✅ success message, and returns to menu. Empty description shows ⚠️ warning.

### Implementation for User Story 2

- [x] T041 [US2] Create add_task_handler() function in src/cli/handlers.py
- [x] T042 [US2] Wire add_task_handler to menu option 1 in src/cli/menu.py
- [x] T043 [US2] Implement task description prompt in add_task_handler() with error handling
- [x] T044 [US2] Call task_service.create_task() from add_task_handler()
- [x] T045 [US2] Display success/warning feedback via display utilities in add_task_handler()
- [x] T046 [US2] Call pause_for_acknowledgment() before returning to menu in add_task_handler()

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View All Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can view all tasks in a formatted table with status indicators

**Independent Test**: Selecting option 2 displays a formatted table showing ID, description, status for all tasks. Empty list shows friendly "No tasks found" message.

### Implementation for User Story 3

- [x] T047 [US3] Create view_tasks_handler() function in src/cli/handlers.py
- [x] T048 [US3] Wire view_tasks_handler to menu option 2 in src/cli/menu.py
- [x] T049 [US3] Call task_service.get_all_tasks() from view_tasks_handler()
- [x] T050 [US3] Handle empty task list with friendly message in view_tasks_handler()
- [x] T051 [US3] Call display_task_table() with task list in view_tasks_handler()
- [x] T052 [US3] Call pause_for_acknowledgment() before returning to menu in view_tasks_handler()

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Complete Tasks (Priority: P2)

**Goal**: Users can mark tasks as completed by entering task ID

**Independent Test**: Selecting option 3 prompts for task ID, marks task complete, displays ✅ success or ⚠️ already complete or ❌ not found

### Implementation for User Story 4

- [x] T053 [US4] Create complete_task_handler() function in src/cli/handlers.py
- [x] T054 [US4] Wire complete_task_handler to menu option 3 in src/cli/menu.py
- [x] T055 [US4] Implement task ID prompt with validation in complete_task_handler()
- [x] T056 [US4] Call task_service.complete_task() from complete_task_handler()
- [x] T057 [US4] Display success/warning/error feedback in complete_task_handler()
- [x] T058 [US4] Call pause_for_acknowledgment() before returning to menu in complete_task_handler()

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Users can delete tasks by entering task ID

**Independent Test**: Selecting option 4 prompts for task ID, removes task, displays ✅ success or ❌ not found. Deleted task no longer appears in task list.

### Implementation for User Story 5

- [x] T059 [US5] Create delete_task_handler() function in src/cli/handlers.py
- [x] T060 [US5] Wire delete_task_handler to menu option 4 in src/cli/menu.py
- [x] T061 [US5] Implement task ID prompt with validation in delete_task_handler()
- [x] T062 [US5] Call task_service.delete_task() from delete_task_handler()
- [x] T063 [US5] Display success/error feedback in delete_task_handler()
- [x] T064 [US5] Call pause_for_acknowledgment() before returning to menu in delete_task_handler()

**Checkpoint**: At this point, ALL User Stories (1-5) should work independently

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T065 Add KeyboardInterrupt (Ctrl+C) handling in src/main.py
- [x] T066 Add graceful exit message when selecting option 5 (Exit)
- [x] T067 Review all docstrings for completeness and clarity
- [x] T068 Verify all constitution requirements are met (SOLID, DRY, modularity)
- [x] T069 Run manual testing per quickstart.md scenarios
- [x] T070 Verify edge case handling (invalid input, empty lists, non-existent IDs)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - May integrate with US2 for testing but no code dependencies
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Uses US2-created tasks for testing but no code dependencies
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Uses US2-created tasks for testing but no code dependencies

### Within Each Phase

- Setup phase: All [P] tasks can run in parallel
- Foundational phase: Most [P] tasks can run in parallel within their module groups
- User story phases: Tasks must be sequential (handler → wire → prompts → service call → feedback → pause)
- Polish phase: Most [P] tasks can run in parallel

### Parallel Opportunities

- **Phase 1**: All tasks (T002-T006) can run in parallel
- **Phase 2**: Group parallel execution by module:
  - Model tasks (T007-T009) run together
  - Storage tasks (T010-T017) mostly sequential
  - Validation tasks (T018-T020) run together
  - Display tasks (T021-T027) run together
  - Service tasks (T028-T034) mostly sequential
  - Menu tasks (T035-T037) sequential
- **User Stories**: Different stories can be worked on in parallel by different team members after Foundational phase

---

## Parallel Example: User Story 2

```bash
# After Foundational phase complete, multiple developers can work on different user stories:

# Developer A: User Story 2 (Add Tasks)
Task T041: Create add_task_handler() function
Task T042: Wire handler to menu
Task T043: Implement prompt
Task T044: Call service
Task T045: Add feedback
Task T046: Add pause

# Developer B (in parallel): User Story 3 (View Tasks)
Task T047: Create view_tasks_handler() function
Task T048: Wire handler to menu
Task T049: Call service
Task T050: Handle empty list
Task T051: Display table
Task T052: Add pause

# Developer C (in parallel): User Story 4 (Complete Tasks)
Task T053: Create complete_task_handler() function
... (and so on)
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Main Menu)
4. Complete Phase 4: User Story 2 (Add Tasks)
5. Complete Phase 5: User Story 3 (View Tasks)
6. **STOP and VALIDATE**: Test core workflow (add tasks, view them)
7. Deploy/demo MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Deploy/Demo (can display menu)
3. Add US2 → Test independently → Deploy/Demo (can create tasks)
4. Add US3 → Test independently → Deploy/Demo (can view tasks - **MVP complete!**)
5. Add US4 → Test independently → Deploy/Demo (can complete tasks)
6. Add US5 → Test independently → Deploy/Demo (full feature set)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 2 (Add Tasks)
   - Developer B: User Story 3 (View Tasks)
   - Developer C: User Story 4 (Complete Tasks)
   - Developer D: User Story 5 (Delete Tasks)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Every code file must include Task ID comment: `# [Task]: T###`
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Manual testing only (no automated tests per spec)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
