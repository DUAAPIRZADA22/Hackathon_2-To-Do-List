# Tasks: Advanced Cloud Deployment with Event-Driven Architecture

**Input**: Design documents from `/specs/005-advanced-cloud-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Not explicitly requested - tests marked as optional

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/src/`, `infrastructure/`, `helm/`
- Tests in: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Dapr, Kafka, and development environment for event-driven architecture

- [ ] T001 Install and configure Dapr CLI locally per quickstart.md
- [ ] T002 Initialize Dapr on Minikube cluster per quickstart.md
- [ ] T003 [P] Create infrastructure directory structure at infrastructure/
- [ ] T004 [P] Create infrastructure/dapr-components/ directory for Dapr configurations
- [ ] T005 [P] Create infrastructure/kafka/ directory for Kafka/Redpanda manifests
- [ ] T006 [P] Create infrastructure/cloud/ directory for cloud provider manifests
- [ ] T007 [P] Add Dapr Python dependency to backend/requirements.txt
- [ ] T008 [P] Add SSE client dependency to frontend/package.json for real-time updates
- [ ] T009 [P] Create helm/actionmindai-prod/templates/ directory for new service deployments

**Checkpoint**: Development environment ready with Dapr and Kafka infrastructure directories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core event-driven infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Dapr Infrastructure

- [ ] T010 Create Dapr Kafka pub/sub component in infrastructure/dapr-components/pubsub-kafka.yaml
- [ ] T011 Create Dapr PostgreSQL state store component in infrastructure/dapr-components/state-postgresql.yaml
- [ ] T012 Create Dapr Kubernetes secret store component in infrastructure/dapr-components/secrets-kubernetes.yaml
- [ ] T013 Create Dapr cron binding for reminder checks in infrastructure/dapr-components/bindings-cron.yaml

### Kafka/Redpanda Infrastructure

- [ ] T014 Create Redpanda single-node cluster for Minikube in infrastructure/kafka/redpanda-minikube.yaml
- [ ] T015 [P] Create Kafka topic definition for task-events in infrastructure/kafka/topics/task-events.yaml
- [ ] T016 [P] Create Kafka topic definition for reminders in infrastructure/kafka/topics/reminders.yaml
- [ ] T017 [P] Create Kafka topic definition for time-logged in infrastructure/kafka/topics/time-logged.yaml

### Backend Event Infrastructure

- [ ] T018 Create Event schema classes in backend/src/models/event.py
- [ ] T019 Create DaprClient for event publishing in backend/src/services/dapr_client.py
- [ ] T020 Create Dapr subscription API route in backend/src/api/dapr.py

### Database Schema

- [ ] T021 Create Alembic migration to add recurrence_rule column in backend/migrations/versions/001_add_recurrence_rule.py
- [ ] T022 Create Alembic migration to add reminder_settings column in backend/migrations/versions/002_add_reminder_settings.py
- [ ] T023 Create database indexes for recurrence queries in backend/migrations/versions/003_add_recurrence_indexes.py
- [ ] T024 Create database indexes for reminder queries in backend/migrations/versions/004_add_reminder_indexes.py

### Extended Task Model

- [ ] T025 Update Task model with recurrence_rule field in backend/src/models/task.py
- [ ] T026 Update Task model with reminder_settings field in backend/src/models/task.py

**Checkpoint**: Event-driven foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Event-Driven Task Operations (Priority: P1) 🎯 MVP

**Goal**: Enable task CRUD operations to publish events to Kafka via Dapr, with downstream services consuming those events

**Independent Test**: Create a task via API, verify Kafka receives the event, verify notification/recurring-task/realtime-sync services consume it

### Event Publishing Integration

- [ ] T027 [US1] Integrate DaprClient into TaskService in backend/src/services/task_service.py
- [ ] T028 [US1] Add event publishing after task creation in backend/src/services/task_service.py
- [ ] T029 [US1] Add event publishing after task update in backend/src/services/task_service.py
- [ ] T030 [US1] Add event publishing after task deletion in backend/src/services/task_service.py
- [ ] T031 [US1] Add event publishing after task assignment in backend/src/services/task_service.py
- [ ] T032 [US1] Add event publishing after task completion in backend/src/services/task_service.py

### Retry Logic

- [ ] T033 [US1] Implement exponential backoff retry in backend/src/services/dapr_client.py
- [ ] T034 [US1] Add event queuing for Kafka unavailability in backend/src/services/dapr_client.py

**Checkpoint**: Task operations publish events to Kafka - US1 independently testable

---

## Phase 4: User Story 2 - Recurring Task Automation (Priority: P2)

**Goal**: Automatically create next instance when recurring task is completed

**Independent Test**: Create recurring task, mark complete, verify next instance created automatically

### Recurring Task Service

- [ ] T035 [P] [US2] Create RecurringTaskService in backend/src/services/recurring_task_service.py
- [ ] T036 [P] [US2] Create recurrence rule validator in backend/src/services/recurrence_validator.py
- [ ] T037 [US2] Implement next occurrence calculator in backend/src/services/recurring_task_service.py
- [ ] T038 [US2] Add event consumer for task_completed in backend/src/services/recurring_task_service.py
- [ ] T039 [US2] Implement automatic task creation logic in backend/src/services/recurring_task_service.py
- [ ] T040 [US2] Add end date validation in backend/src/services/recurring_task_service.py

### Helm Chart

- [ ] T041 [US2] Create recurring-task service deployment in helm/actionmindai-prod/templates/recurring-task-deployment.yaml
- [ ] T042 [US2] Add Dapr annotations to recurring-task deployment in helm/actionmindai-prod/templates/recurring-task-deployment.yaml

**Checkpoint**: Recurring tasks auto-create next instance - US2 independently testable

---

## Phase 5: User Story 3 - Due Date Reminders (Priority: P3)

**Goal**: Send reminder notifications before tasks are due

**Independent Test**: Create task with due date and reminder, verify notification sent at specified time

### Notification Service

- [ ] T043 [P] [US3] Create NotificationService in backend/src/services/notification_service.py
- [ ] T044 [US3] Add event consumer for reminder events in backend/src/services/notification_service.py
- [ ] T045 [US3] Implement email notification sending in backend/src/services/notification_service.py
- [ ] T046 [US3] Add SendGrid integration in backend/src/services/notification_service.py
- [ ] T047 [US3] Implement reminder deduplication logic in backend/src/services/notification_service.py
- [ ] T048 [US3] Add reminder cancellation on task completion in backend/src/services/notification_service.py

### Reminder Check Cron

- [ ] T049 [US3] Create reminder check scheduler in backend/src/services/reminder_scheduler.py
- [ ] T050 [US3] Implement due date scanning logic in backend/src/services/reminder_scheduler.py
- [ ] T051 [US3] Add reminder event publishing in backend/src/services/reminder_scheduler.py

### Helm Chart

- [ ] T052 [US3] Create notification service deployment in helm/actionmindai-prod/templates/notification-deployment.yaml
- [ ] T053 [US3] Add Dapr annotations to notification deployment in helm/actionmindai-prod/templates/notification-deployment.yaml

**Checkpoint**: Due date reminders sent at configured times - US3 independently testable

---

## Phase 6: User Story 4 - Real-Time Task Updates (Priority: P4)

**Goal**: Broadcast task updates to all connected clients instantly

**Independent Test**: Open app in two windows, create task in one, verify it appears in other

### Backend WebSocket/SSE

- [ ] T054 [US4] Create WebSocket/SSE endpoint in backend/src/api/websocket.py
- [ ] T055 [US4] Implement SSE event stream in backend/src/api/websocket.py
- [ ] T056 [US4] Add connection state management in backend/src/api/websocket.py
- [ ] T057 [US4] Implement reconnection handling in backend/src/api/websocket.py

### Real-Time Sync Service

- [ ] T058 [P] [US4] Create RealtimeSyncService in backend/src/services/realtime_sync_service.py
- [ ] T059 [US4] Add event consumer for all task events in backend/src/services/realtime_sync_service.py
- [ ] T060 [US4] Implement WebSocket broadcast logic in backend/src/services/realtime_sync_service.py
- [ ] T061 [US4] Add client connection tracking in backend/src/services/realtime_sync_service.py
- [ ] T062 [US4] Implement missed event sync on reconnection in backend/src/services/realtime_sync_service.py

### Frontend WebSocket

- [ ] T063 [P] [US4] Create WebSocket utility in frontend/src/lib/websocket.ts
- [ ] T064 [US4] Create TaskWebSocket component in frontend/src/components/websocket/TaskWebSocket.tsx
- [ ] T065 [US4] Implement event message handling in frontend/src/lib/websocket.ts
- [ ] T066 [US4] Add automatic reconnection logic in frontend/src/lib/websocket.ts
- [ ] T067 [US4] Update chat page to use WebSocket in frontend/src/app/chat/page.tsx
- [ ] T068 [US4] Add visual notification for task assignment in frontend/src/components/websocket/TaskWebSocket.tsx

### Helm Chart

- [ ] T069 [US4] Create realtime-sync service deployment in helm/actionmindai-prod/templates/realtime-sync-deployment.yaml
- [ ] T070 [US4] Add Dapr annotations to realtime-sync deployment in helm/actionmindai-prod/templates/realtime-sync-deployment.yaml

**Checkpoint**: Real-time updates appear across all clients - US4 independently testable

---

## Phase 7: User Story 5 - Cloud Kubernetes Deployment (Priority: P5)

**Goal**: Deploy application to cloud Kubernetes cluster (Oracle OKE/GKE/AKS)

**Independent Test**: Deploy to cloud cluster, verify application accessible and functional

### Cloud Provider Configuration

- [ ] T071 [P] [US5] Create Oracle OKE manifests in infrastructure/cloud/oracle-oke/
- [ ] T072 [P] [US5] Create GKE manifests in infrastructure/cloud/gke/
- [ ] T073 [P] [US5] Create AKS manifests in infrastructure/cloud/aks/

### Production Helm Charts

- [ ] T074 [US5] Update Helm Chart.yaml for production in helm/actionmindai-prod/Chart.yaml
- [ ] T075 [US5] Create production values.yaml in helm/actionmindai-prod/values-prod.yaml
- [ ] T076 [US5] Add Dapr annotations to backend deployment in helm/actionmindai-prod/templates/backend-deployment.yaml
- [ ] T077 [US5] Add Dapr annotations to frontend deployment in helm/actionmindai-prod/templates/frontend-deployment.yaml
- [ ] T078 [US5] Configure ingress for external domain in helm/actionmindai-prod/templates/ingress.yaml
- [ ] T079 [US5] Configure TLS/SSL certificates in helm/actionmindai-prod/templates/ingress.yaml
- [ ] T080 [US5] Set resource limits for cloud provider in helm/actionmindai-prod/values-prod.yaml
- [ ] T081 [US5] Configure zero-downtime rolling updates in helm/actionmindai-prod/templates/backend-deployment.yaml

### Cloud Deployment Documentation

- [ ] T082 [US5] Add Oracle OKE setup to quickstart.md
- [ ] T083 [US5] Add GKE setup instructions to quickstart.md
- [ ] T084 [US5] Add AKS setup instructions to quickstart.md

**Checkpoint**: Application deployed and accessible on cloud - US5 independently testable

---

## Phase 8: User Story 6 - Automated CI/CD Pipeline (Priority: P6)

**Goal**: Automated build, test, scan, and deploy via GitHub Actions

**Independent Test**: Push code change, verify pipeline runs through all stages

### GitHub Actions Workflow

- [ ] T085 [US6] Create GitHub Actions workflow in .github/workflows/deploy.yml
- [ ] T086 [US6] Configure Docker image build stage in .github/workflows/deploy.yml
- [ ] T087 [US6] Configure test stage in .github/workflows/deploy.yml
- [ ] T088 [US6] Add Trivy security scanning stage in .github/workflows/deploy.yml
- [ ] T089 [US6] Configure staging deployment stage in .github/workflows/deploy.yml
- [ ] T090 [US6] Add integration test stage in .github/workflows/deploy.yml
- [ ] T091 [US6] Configure manual approval gate for production in .github/workflows/deploy.yml
- [ ] T092 [US6] Add deployment notification stage in .github/workflows/deploy.yml

### CI/CD Configuration

- [ ] T093 [US6] Document GitHub secrets setup in quickstart.md
- [ ] T094 [US6] Create environment-specific values files in helm/actionmindai-prod/values-staging.yaml
- [ ] T095 [US6] Create production values file in helm/actionmindai-prod/values-production.yaml

**Checkpoint**: CI/CD pipeline builds, tests, scans, and deploys automatically - US6 independently testable

---

## Phase 9: Advanced Feature UI Components

**Purpose**: Frontend UI for recurring tasks and reminder settings

### Recurring Task UI

- [ ] T096 [P] Create RecurringTaskForm component in frontend/src/components/tasks/RecurringTaskForm.tsx
- [ ] T097 [P] Add recurrence frequency selector in frontend/src/components/tasks/RecurringTaskForm.tsx
- [ ] T098 [P] Add weekly day selector in frontend/src/components/tasks/RecurringTaskForm.tsx
- [ ] T099 [P] Add end date picker in frontend/src/components/tasks/RecurringTaskForm.tsx
- [ ] T100 Integrate RecurringTaskForm into task creation modal in frontend/src/app/chat/page.tsx
- [ ] T101 Add recurrence indicator to task list items in frontend/src/app/chat/page.tsx

### Reminder Settings UI

- [ ] T102 [P] Create ReminderSettings component in frontend/src/components/tasks/ReminderSettings.tsx
- [ ] T103 [P] Add reminder time selector in frontend/src/components/tasks/ReminderSettings.tsx
- [ ] T104 [P] Add enable/disable toggle in frontend/src/components/tasks/ReminderSettings.tsx
- [ ] T105 Integrate ReminderSettings into task creation modal in frontend/src/app/chat/page.tsx

**Checkpoint**: UI components for recurring tasks and reminders complete

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [ ] T106 [P] Update quickstart.md with complete setup instructions
- [ ] T107 [P] Add troubleshooting section to quickstart.md
- [ ] T108 [P] Create AIOps commands documentation in docs/aiops-commands.md
- [ ] T109 [P] Document all Dapr component configurations in docs/dapr-components.md

### Helm Chart Completion

- [ ] T110 Update existing Helm templates with Dapr annotations in helm/actionmindai-prod/templates/
- [ ] T111 Add production values to values.yaml in helm/actionmindai-prod/values.yaml
- [ ] T112 Create minikube-specific values file in helm/actionmindai-prod/values-minikube.yaml

### Validation

- [ ] T113 Run quickstart.md validation for local deployment
- [ ] T114 Verify Dapr sidecar injection on all pods
- [ ] T115 Verify Kafka topics are created and accessible
- [ ] T116 Test event flow end-to-end

### Security Hardening

- [ ] T117 Add secrets management documentation to quickstart.md
- [ ] T118 Configure resource quotas in Helm values
- [ ] T119 Add network policies for service-to-service communication

**Checkpoint**: All user stories integrated, documentation complete, ready for hackathon submission

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Event-Driven Operations) - PRIORITY: Foundation for all other stories
  - US2-US6: Can proceed in parallel after US1, or sequentially in priority order
- **Advanced Feature UI (Phase 9)**: Depends on US2 and US3 completion
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Foundation for US2, US3, US4
- **User Story 2 (P2)**: Can start after Foundational - Depends on US1 for event publishing
- **User Story 3 (P3)**: Can start after Foundational - Depends on US1 for event publishing
- **User Story 4 (P4)**: Can start after Foundational - Depends on US1 for event consumption
- **User Story 5 (P5)**: Can start after Foundational - Independent deployment story
- **User Story 6 (P6)**: Can start after Foundational - Independent automation story

### Critical Path

1. Phase 1: Setup → Phase 2: Foundational → Phase 3: US1 (Event Publishing)
2. After US1: US2, US3, US4 can proceed in parallel
3. US5, US6 can proceed in parallel with US2-US4
4. Phase 9: UI depends on US2, US3
5. Phase 10: Polish depends on all stories

### Parallel Opportunities

#### Within Setup (Phase 1)
- T003-T009: All directory creation and dependency updates can run in parallel

#### Within Foundational (Phase 2)
- T010-T013: Dapr components can be created in parallel
- T015-T017: Kafka topic definitions can be created in parallel

#### Within User Story 2 (Phase 4)
- T035-T036: RecurringTaskService and validator can be created in parallel

#### Within User Story 3 (Phase 5)
- T043: NotificationService creation can start in parallel with other stories

#### Within User Story 4 (Phase 6)
- T058, T063-T064: Service and frontend components can be created in parallel

#### Within User Story 5 (Phase 7)
- T071-T073: All cloud provider manifests can be created in parallel

#### Within Advanced Feature UI (Phase 9)
- T096-T099: All RecurringTaskForm subcomponents can be created in parallel
- T102-T104: All ReminderSettings subcomponents can be created in parallel

#### Within Polish (Phase 10)
- T106-T109: All documentation tasks can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all event publishing tasks together after T027:
Task: "Add event publishing after task creation in backend/src/services/task_service.py"
Task: "Add event publishing after task update in backend/src/services/task_service.py"
Task: "Add event publishing after task deletion in backend/src/services/task_service.py"
Task: "Add event publishing after task assignment in backend/src/services/task_service.py"
Task: "Add event publishing after task completion in backend/src/services/task_service.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch service creation tasks together:
Task: "Create RecurringTaskService in backend/src/services/recurring_task_service.py"
Task: "Create recurrence rule validator in backend/src/services/recurrence_validator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T026) - CRITICAL
3. Complete Phase 3: User Story 1 (T027-T034)
4. **STOP and VALIDATE**: Test event publishing independently
5. Deploy demo if ready

**MVP Delivers**: Event-driven task operations with Kafka integration

### Incremental Delivery

1. Setup + Foundational → Event infrastructure ready
2. Add US1 (Event Publishing) → Test → Deploy (MVP: Events flow)
3. Add US2 (Recurring Tasks) → Test → Deploy (Recurring tasks work)
4. Add US3 (Reminders) → Test → Deploy (Reminders sent)
5. Add US4 (Real-Time) → Test → Deploy (Real-time updates)
6. Add US5 (Cloud) → Test → Deploy (Cloud accessible)
7. Add US6 (CI/CD) → Test → Deploy (Automated deployment)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Event Publishing) - CRITICAL: Do first
   - Developer B: US2 (Recurring Tasks) - Start after US1 T027
   - Developer C: US3 (Reminders) - Start after US1 T027
   - Developer D: US4 (Real-Time) - Start after US1 T027
   - Developer E: US5 (Cloud) - Can start anytime after Foundational
   - Developer F: US6 (CI/CD) - Can start anytime after Foundational
3. Stories complete and integrate independently

---

## Task Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1: Setup | 9 tasks | Dapr/Kafka initialization |
| Phase 2: Foundational | 15 tasks | Core event infrastructure |
| Phase 3: US1 | 8 tasks | Event publishing |
| Phase 4: US2 | 8 tasks | Recurring tasks |
| Phase 5: US3 | 11 tasks | Due date reminders |
| Phase 6: US4 | 17 tasks | Real-time updates |
| Phase 7: US5 | 14 tasks | Cloud deployment |
| Phase 8: US6 | 11 tasks | CI/CD pipeline |
| Phase 9: UI | 10 tasks | Advanced feature UI |
| Phase 10: Polish | 14 tasks | Documentation & validation |
| **TOTAL** | **117 tasks** | Complete event-driven architecture |

### Parallel Opportunities Summary

- **Setup**: 7 parallel tasks (T003-T009)
- **Foundational**: 6 parallel tasks across Dapr/Kafka
- **US2**: 2 parallel tasks (service + validator)
- **US3**: 1 parallel task (service start)
- **US4**: 3 parallel tasks (service + 2 frontend)
- **US5**: 3 parallel tasks (cloud manifests)
- **US9**: 7 parallel tasks (UI components)
- **US10**: 4 parallel tasks (documentation)

**Total parallelizable tasks**: 33 tasks can run in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = Phase 1 + Phase 2 + Phase 3 (US1 only)
