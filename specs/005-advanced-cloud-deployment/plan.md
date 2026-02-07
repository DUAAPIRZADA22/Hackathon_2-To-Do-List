# Implementation Plan: Advanced Cloud Deployment with Event-Driven Architecture

**Branch**: `005-advanced-cloud-deployment` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-advanced-cloud-deployment/spec.md`

## Summary

Implement event-driven architecture for ActionMind AI using Dapr and Kafka/Redpanda. This includes:
- Event-driven microservices (notification, recurring-task, realtime-sync)
- Advanced features (recurring tasks, due date reminders, real-time sync)
- Cloud Kubernetes deployment (Oracle OKE/GKE/AKS)
- CI/CD pipeline with GitHub Actions

**Technical Approach**: Add Dapr sidecars to existing services for event publishing/consumption, deploy Kafka for event streaming, implement three new microservices for event handling, extend database schema for recurrence/reminders, and establish cloud deployment with automated CI/CD.

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: Dapr 1.14+, Kafka/Redpanda, FastAPI, Next.js 16+, PostgreSQL (Neon), Kubernetes 1.29+
**Storage**: Neon PostgreSQL (serverless, existing) + Kafka (event streaming)
**Testing**: pytest (backend), Jest (frontend), integration tests for event flow
**Target Platform**: Kubernetes (Minikube for local, Oracle OKE/GKE/AKS for cloud)
**Project Type**: web (frontend + backend architecture)
**Performance Goals**: 100 events/sec throughput, <500ms event publish latency, <2s event processing
**Constraints**: <1s real-time update delivery, 99% event delivery reliability, zero-downtime deployments
**Scale/Scope**: 50 concurrent users (hackathon), 3 event-driven services, 3 Kafka topics

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Spec-Driven Development | ✅ PASS | All 69 functional requirements documented with Task ID references |
| II. MCP-First Architecture | ⚠️ PARTIAL | MCP used for Context7; Dapr/Kafka are external integrations (Phase V scope) |
| III. Context Verification | ✅ PASS | Dapr/Kafka context verification before operations |
| IV. Scope Boundaries | ✅ PASS | Event-driven architecture is Phase V scope; extends Phase IV foundation |
| V. SOLID Principles | ✅ PASS | Each microservice has single responsibility; dependencies abstracted via Dapr |
| VI. DRY | ✅ PASS | Event publishing logic centralized in DaprClient; shared event schemas |
| VII. Modularity | ✅ PASS | 3 independent microservices; each with own Dapr sidecar |
| VIII. User Experience Standards | ✅ PASS | Real-time updates; email notifications; visual recurrence indicators |

**Gate Status**: ✅ PASS - All constitution principles satisfied or justified (Phase V extends beyond Phase I CLI scope)

**Justification for Principle II (Partial)**: Phase V explicitly includes external integrations (Dapr, Kafka) as per hackathon requirements. MCP still used for Context7 where applicable.

## Project Structure

### Documentation (this feature)

```text
specs/005-advanced-cloud-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── events.yaml      # Event schemas (OpenAPI)
│   ├── dapr-api.yaml    # Dapr endpoint specifications
│   └── websocket.yaml   # WebSocket protocol
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Option 2: Web application (existing structure extended)
backend/
├── src/
│   ├── models/
│   │   ├── task.py           # Extended with recurrence_rule, reminder_settings
│   │   └── event.py          # New: event schemas
│   ├── services/
│   │   ├── task_service.py   # Modified: event publishing
│   │   ├── dapr_client.py    # New: Dapr integration
│   │   ├── notification_service.py    # New: consumes reminder events
│   │   ├── recurring_task_service.py  # New: consumes task completion events
│   │   └── realtime_sync_service.py   # New: consumes all task events
│   └── api/
│       ├── tasks.py          # Existing: task CRUD endpoints
│       ├── dapr.py           # New: event subscription endpoints
│       └── websocket.py      # New: WebSocket endpoint
├── tests/
│   ├── contract/             # Event contract tests
│   ├── integration/          # Event flow integration tests
│   └── unit/                 # Unit tests for services
└── migrations/               # Database migrations

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── RecurringTaskForm.tsx     # New: recurrence UI
│   │   │   └── ReminderSettings.tsx      # New: reminder UI
│   │   └── websocket/
│   │       └── TaskWebSocket.tsx         # New: WebSocket connection
│   ├── lib/
│   │   └── websocket.ts                  # New: WebSocket utility
│   └── app/
│       └── chat/page.tsx                 # Modified: real-time updates
└── tests/

infrastructure/
├── dapr-components/
│   ├── pubsub-kafka.yaml     # Kafka pub/sub component
│   ├── state-postgresql.yaml  # PostgreSQL state store
│   ├── secrets-kubernetes.yaml # K8s secret store
│   └── bindings-cron.yaml     # Cron binding for reminders
├── kafka/
│   ├── redpanda-minikube.yaml # Redpanda for local dev
│   └── topics/
│       ├── task-events.yaml
│       ├── reminders.yaml
│       └── time-logged.yaml
└── cloud/
    ├── oracle-oke/           # Oracle OKE manifests
    ├── gke/                  # GKE manifests
    └── aks/                  # AKS manifests

helm/
└── actionmindai-prod/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── backend-deployment.yaml    # Modified: Dapr annotations
        ├── frontend-deployment.yaml   # Modified: Dapr annotations
        ├── notification-deployment.yaml   # New
        ├── recurring-task-deployment.yaml # New
        └── realtime-sync-deployment.yaml    # New

.github/
└── workflows/
    └── deploy.yml            # New: CI/CD pipeline
```

**Structure Decision**: Web application structure (Option 2) - extends existing Phase IV frontend/backend architecture. Event-driven microservices added as new backend services. Dapr components and Kafka manifests in infrastructure/ directory for separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations requiring complexity tracking. Constitution check passed with acceptable justification for Phase V scope extension beyond Phase I CLI boundaries.
