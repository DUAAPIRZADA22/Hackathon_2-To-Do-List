# Feature Specification: Advanced Cloud Deployment with Event-Driven Architecture

**Feature Branch**: `005-advanced-cloud-deployment`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase 5: ActionMind AI Advanced Cloud Deployment - Dapr integration, Kafka/Redpanda event streaming, event-driven microservices architecture, advanced features (recurring tasks, due date reminders, real-time sync), cloud Kubernetes deployment (AKS/GKE/OKE), and CI/CD pipeline with GitHub Actions"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event-Driven Task Operations (Priority: P1)

A project manager creates a task in the ActionMind AI application. The system automatically publishes an event to Kafka, which triggers downstream services to handle notifications, recurring task creation, and real-time synchronization across all connected clients.

**Why this priority**: Event-driven architecture is the foundation for all advanced features. Without events flowing through Kafka, notifications, recurring tasks, and real-time updates cannot function.

**Independent Test**: Can be fully tested by creating a task via API and verifying that Kafka receives the event, downstream services consume it, and appropriate actions are triggered.

**Acceptance Scenarios**:

1. **Given** the application is deployed with Dapr and Kafka, **When** a user creates a task, **Then** a task-created event is published to the task-events topic
2. **Given** a task-created event is published, **When** the notification service consumes it, **Then** relevant users receive notifications about the new task
3. **Given** a task-completed event is published for a recurring task, **When** the recurring task service consumes it, **Then** a new task instance is automatically created with the same recurrence rules
4. **Given** any task event is published, **When** the real-time sync service consumes it, **Then** all connected WebSocket clients receive the update immediately
5. **Given** Kafka is temporarily unavailable, **When** a task operation occurs, **Then** the system queues events locally and retries when Kafka becomes available

---

### User Story 2 - Recurring Task Automation (Priority: P2)

A project manager configures a weekly team standup task to recur every Monday. When the current week's standup task is completed, the system automatically creates the next week's standup task without manual intervention.

**Why this priority**: Recurring tasks are a common productivity need. Automation reduces manual work and ensures important recurring tasks are never forgotten.

**Independent Test**: Can be fully tested by creating a task with recurrence rules, marking it complete, and verifying the next instance is created automatically.

**Acceptance Scenarios**:

1. **Given** a task is configured with weekly recurrence, **When** the task is marked complete, **Then** a new task instance is created for the next occurrence
2. **Given** a task is configured with daily recurrence, **When** the task is marked complete, **Then** a new task instance is created for the next day
3. **Given** a task is configured with an end date, **When** the recurrence end date is reached, **Then** no further instances are created after completion
4. **Given** a task has recurrence rules, **When** viewing the task list, **Then** recurring tasks display a visual indicator showing their recurrence pattern
5. **Given** a recurring task is deleted, **When** the deletion event is processed, **Then** no further instances are created

---

### User Story 3 - Due Date Reminders (Priority: P3)

A team member has a task due at 5 PM today. The system sends a reminder notification 1 hour before the due date, allowing the team member to complete the task on time.

**Why this priority**: Due date reminders help users meet deadlines and reduce the risk of forgetting important tasks.

**Independent Test**: Can be fully tested by creating a task with a due date, configuring a reminder, and verifying the notification is sent at the specified time.

**Acceptance Scenarios**:

1. **Given** a task has a due date and 1-hour reminder configured, **When** the current time is 1 hour before the due date, **Then** the system sends a reminder notification
2. **Given** a task has multiple reminder times configured, **When** each reminder time is reached, **Then** the system sends notifications at all configured times
3. **Given** a task's due date is changed, **When** the change occurs, **Then** reminder schedules are updated accordingly
4. **Given** a task is completed before its due date, **When** completion occurs, **Then** pending reminders for that task are cancelled
5. **Given** the notification service is temporarily unavailable, **When** a reminder is due, **Then** the system retries sending the notification

---

### User Story 4 - Real-Time Task Updates (Priority: P4)

Two team members are viewing the task list simultaneously. When one member creates a new task, the other member sees the task appear instantly without refreshing the page.

**Why this priority**: Real-time updates improve collaboration and ensure all team members see the latest information without manual refresh.

**Independent Test**: Can be fully tested by opening the application in two browser windows and verifying that changes in one window appear instantly in the other.

**Acceptance Scenarios**:

1. **Given** multiple users have the application open, **When** one user creates a task, **Then** all other users see the new task appear immediately
2. **Given** a task is updated, **When** the update occurs, **Then** all connected clients receive the updated task data
3. **Given** a user is assigned a task, **When** the assignment event is published, **Then** the assigned user receives a visual notification
4. **Given** the WebSocket connection is lost, **When** the connection is restored, **Then** the client synchronizes to receive any missed updates
5. **Given** multiple updates occur in quick succession, **When** events are processed, **Then** clients receive updates in the correct order

---

### User Story 5 - Cloud Kubernetes Deployment (Priority: P5)

A DevOps engineer deploys the ActionMind AI application to a cloud Kubernetes cluster (Oracle OKE) using production-grade configurations, making the application accessible over the internet.

**Why this priority**: Cloud deployment enables production availability and external access. This demonstrates the application can run in a real cloud environment.

**Independent Test**: Can be fully tested by deploying to a cloud cluster and verifying the application is accessible and functional.

**Acceptance Scenarios**:

1. **Given** a cloud Kubernetes cluster is available, **When** production Helm charts are applied, **Then** all services deploy successfully
2. **Given** Dapr is installed on the cluster, **When** application pods start, **Then** Dapr sidecars are injected and running alongside application containers
3. **Given** Kafka is deployed, **When** application services start, **Then** all services can successfully connect to Kafka
4. **Given** the application is deployed, **When** accessing via the configured domain, **Then** the web application loads and functions correctly
5. **Given** pods are running, **When** checking pod status, **Then** all pods are healthy with Dapr sidecars operational

---

### User Story 6 - Automated CI/CD Pipeline (Priority: P6)

A developer pushes code changes to the repository. The CI/CD pipeline automatically builds, tests, scans for vulnerabilities, and deploys to the staging environment.

**Why this priority**: Automated deployment reduces manual work, ensures consistency, and catches issues early through automated testing and scanning.

**Independent Test**: Can be fully tested by pushing a code change and verifying the pipeline runs through all stages successfully.

**Acceptance Scenarios**:

1. **Given** a code change is pushed, **When** the pipeline triggers, **Then** Docker images are built and pushed to the registry
2. **Given** images are built, **When** the test stage runs, **Then** all automated tests pass
3. **Given** tests pass, **When** the security scan stage runs, **Then** Trivy completes scanning without critical vulnerabilities
4. **Given** security scan passes, **When** the deploy staging stage runs, **Then** the application deploys to the staging environment
5. **Given** staging deployment succeeds, **When** manual approval is granted, **Then** the pipeline deploys to production

---

### Edge Cases

- What happens when Kafka cluster is down and events cannot be published?
- How does the system handle when Dapr sidecar crashes or fails to start?
- What happens when a recurring task's end date is in the past?
- How does the system handle when notification service is down when a reminder is due?
- What happens when WebSocket connection is unstable and messages are lost?
- How does the system handle when cloud cluster resource limits are exceeded?
- What happens when CI/CD pipeline encounters a transient network failure?
- How does the system handle when a task's recurrence rule is invalid?
- What happens when multiple users edit the same task simultaneously?
- How does the system handle when database migration fails during deployment?

## Requirements *(mandatory)*

### Functional Requirements

**Event-Driven Architecture**

- **FR-001**: System MUST publish events to Kafka for all task CRUD operations (create, update, delete, assign, complete)
- **FR-002**: System MUST use Dapr sidecar for event publishing to abstract Kafka complexity
- **FR-003**: System MUST define event schemas for task-events topic with required fields (event_type, task_id, user_id, timestamp)
- **FR-004**: System MUST define event schemas for reminders topic with required fields (reminder_type, task_id, due_date, user_id)
- **FR-005**: System MUST support at-least-once delivery semantics for events
- **FR-006**: System MUST implement retry logic with exponential backoff for failed event publishing
- **FR-007**: System MUST serialize events using JSON format for compatibility
- **FR-008**: System MUST include correlation IDs in events for distributed tracing

**Dapr Integration**

- **FR-009**: System MUST deploy Dapr sidecar alongside all application services
- **FR-010**: System MUST configure Dapr annotations for service discovery and pub/sub
- **FR-011**: System MUST create Dapr component configuration for Kafka pub/sub
- **FR-012**: System MUST create Dapr component configuration for PostgreSQL state store
- **FR-013**: System MUST create Dapr component configuration for Kubernetes secret store
- **FR-014**: System MUST create Dapr cron binding for scheduled reminder checks
- **FR-015**: System MUST expose health endpoint for Dapr sidecar readiness checks

**Kafka/Redpanda Event Streaming**

- **FR-016**: System MUST deploy Kafka or Redpanda cluster in Kubernetes
- **FR-017**: System MUST create task-events topic with appropriate retention and partition settings
- **FR-018**: System MUST create reminders topic with appropriate retention and partition settings
- **FR-019**: System MUST create time-logged topic for time tracking events (if applicable)
- **FR-020**: System MUST support topic creation through infrastructure-as-code
- **FR-021**: System MUST configure consumer groups for each service (notification, recurring-task, realtime-sync)
- **FR-022**: System MUST handle consumer offset management for message processing

**Event-Driven Microservices**

- **FR-023**: System MUST implement notification service that consumes reminder events
- **FR-024**: System MUST implement recurring task service that consumes task completion events
- **FR-025**: System MUST implement real-time sync service that consumes all task events
- **FR-026**: Each microservice MUST be independently scalable
- **FR-027**: Each microservice MUST have its own Dapr sidecar configuration
- **FR-028**: Services MUST communicate asynchronously through Kafka only

**Recurring Tasks Feature**

- **FR-029**: System MUST support daily, weekly, and monthly recurrence frequencies
- **FR-030**: System MUST store recurrence rules as JSON in the database
- **FR-031**: System MUST support specifying end dates for recurrence
- **FR-032**: System MUST automatically create next task instance when recurring task is completed
- **FR-033**: System MUST display recurrence indicator in UI for recurring tasks
- **FR-034**: System MUST support editing recurrence rules for existing tasks
- **FR-035**: System MUST calculate next occurrence date based on recurrence rules

**Due Date Reminders Feature**

- **FR-036**: System MUST support configurable reminder times (15 minutes, 1 hour, 1 day, 1 week before due date)
- **FR-037**: System MUST store reminder preferences per task
- **FR-038**: System MUST use Dapr cron binding to trigger reminder checks
- **FR-039**: System MUST send reminder notifications via email
- **FR-040**: System MUST cancel pending reminders when task is completed
- **FR-041**: System MUST update reminder schedules when due dates change
- **FR-042**: System MUST support multiple reminder times per task

**Real-Time Updates Feature**

- **FR-043**: Frontend MUST establish WebSocket connection for real-time updates
- **FR-044**: Backend MUST support WebSocket connections for task updates
- **FR-045**: System MUST broadcast task events to all connected clients
- **FR-046**: System MUST handle WebSocket connection failures with reconnection logic
- **FR-047**: System MUST synchronize missed updates when client reconnects
- **FR-048**: System MUST maintain connection state for active users

**Cloud Kubernetes Deployment**

- **FR-049**: System MUST support deployment to Oracle OKE (Always Free tier)
- **FR-050**: System MUST support deployment to Google GKE (as alternative)
- **FR-051**: System MUST support deployment to Azure AKS (as alternative)
- **FR-052**: System MUST include production-grade Helm charts
- **FR-053**: System MUST configure ingress for external domain access
- **FR-054**: System MUST configure TLS/SSL certificates for secure connections
- **FR-055**: System MUST configure resource limits appropriate for cloud provider
- **FR-056**: System MUST support zero-downtime rolling updates

**CI/CD Pipeline**

- **FR-057**: System MUST include GitHub Actions workflow for automated deployment
- **FR-058**: Pipeline MUST build Docker images on every push
- **FR-059**: Pipeline MUST run automated tests on every push
- **FR-060**: Pipeline MUST run Trivy security scanning on Docker images
- **FR-061**: Pipeline MUST deploy to staging environment automatically
- **FR-062**: Pipeline MUST require manual approval for production deployment
- **FR-063**: Pipeline MUST send deployment notifications
- **FR-064**: Pipeline MUST support environment-specific configurations

**Database Schema Changes**

- **FR-065**: Tasks table MUST include recurrence_rule column (JSONB type)
- **FR-066**: Tasks table MUST include reminder_settings column (JSONB type)
- **FR-067**: System MUST support database migrations for schema changes
- **FR-068**: Recurrence rule MUST support frequency, days, interval, and end_date fields
- **FR-069**: Reminder settings MUST support reminder_times array and notification_method fields

### Key Entities

- **Task Event**: Message published to Kafka when tasks change, contains event_type, task_id, project_id, user_id, timestamp, and event-specific data
- **Reminder Event**: Message published when reminders are triggered, contains reminder_type, task_id, due_date, user_id, and message content
- **Recurrence Rule**: Configuration for recurring tasks, defines frequency (daily/weekly/monthly), specific days, interval, and optional end date
- **Reminder Settings**: Per-task configuration for due date reminders, defines array of reminder times and notification method
- **Dapr Component**: Kubernetes configuration for Dapr building blocks (pubsub, state store, secret store, bindings)
- **Kafka Topic**: Event streaming channel with configuration for partitions, replication, and retention
- **Event-Driven Service**: Independent microservice (notification, recurring-task, realtime-sync) that consumes Kafka events
- **WebSocket Connection**: Persistent connection between client and server for real-time updates

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Task events are published to Kafka within 500 milliseconds of user action
- **SC-002**: Downstream services consume and process events within 2 seconds of publication
- **SC-003**: Recurring task instances are created automatically within 5 seconds of task completion
- **SC-004**: Due date reminders are sent within 1 minute of the configured reminder time
- **SC-005**: Real-time updates are delivered to all connected clients within 1 second of event occurrence
- **SC-006**: Application deploys to cloud Kubernetes cluster within 15 minutes
- **SC-007**: All services (including Dapr sidecars) are healthy within 5 minutes of deployment
- **SC-008**: CI/CD pipeline completes build, test, and security scan stages within 10 minutes
- **SC-009**: Zero-downtime deployment succeeds without service interruption
- **SC-010**: System handles at least 100 events per second without performance degradation
- **SC-011**: WebSocket connections remain stable for at least 1 hour
- **SC-012**: Event delivery reliability is at least 99% (at-least-once delivery)
- **SC-013**: Cloud deployment supports at least 50 concurrent users
- **SC-014**: Security scanning reports no critical vulnerabilities in deployed images

## Out of Scope *(optional but recommended)*

The following items are explicitly out of scope for this phase:

- **Multi-region deployment** and geographic redundancy
- **Advanced observability** (distributed tracing with Jaeger/Zipkin, metrics with Prometheus/Grafana)
- **Service mesh implementation** (Istio, Linkerd) for advanced traffic management
- **Event sourcing** with full event replay capabilities
- **CQRS (Command Query Responsibility Segregation)** pattern implementation
- **Advanced message ordering** guarantees (beyond Kafka partition ordering)
- **Message dead letter queues** with complex retry policies
- **Push notifications** (mobile) - email only for this phase
- **Custom authentication/authorization** beyond existing Better Auth
- **Database sharding** or advanced scaling patterns
- **Advanced caching strategies** (Redis caching layers)
- **Rate limiting** and API quota management
- **Automated backup and disaster recovery** procedures
- **Multi-tenant support** for multiple organizations
- **Advanced monitoring dashboards** and alerting rules
- **Cost optimization** features (auto-scaling, spot instances)

## Dependencies & Assumptions

### Dependencies

- **Phase IV Completion**: Local Kubernetes deployment must be complete with working Docker images and Helm charts
- **Dapr CLI**: Must be installed for local development and cluster initialization
- **Kafka or Redpanda**: Must be deployable to Kubernetes (Redpanda recommended for simplicity)
- **Cloud Provider Account**: Oracle OKE, Google GKE, or Azure AKS account with appropriate permissions
- **Container Registry**: Docker Hub, GHCR, or cloud provider registry for image storage
- **GitHub Repository**: Must support GitHub Actions for CI/CD pipeline
- **External Services**: Neon PostgreSQL database, notification service (SendGrid or similar)
- **Existing Application**: Frontend and backend code from Phase IV must be functional

### Assumptions

- Development machine has sufficient resources to run Dapr, Kafka, and application locally
- Cloud provider free tier has sufficient resources for application deployment
- Kafka cluster with 3 brokers is sufficient for hackathon scale
- Events can be processed with at-least-once semantics without requiring exactly-once guarantees
- Email notifications via SendGrid or similar service are acceptable for notification delivery
- WebSocket connections scale to expected number of concurrent users
- Dapr sidecar adds acceptable latency overhead for pub/sub operations
- Minikube can be used for local development with Dapr and Kafka
- Existing database schema can be modified without breaking existing data
- CI/CD pipeline secrets can be securely stored in GitHub
- Rolling updates can be performed without database schema conflicts

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Dapr sidecar injection fails causing pods to not start | High | Low | Include Dapr installation verification in deployment checklist; provide manual remediation steps |
| Kafka cluster fails to start in Minikube due to resource constraints | High | Medium | Document minimum resource requirements; provide Redpanda single-node alternative for local development |
| Event delivery failures cause data inconsistency | High | Medium | Implement idempotent event handlers; include event replay capability for recovery |
| Recurring task calculation errors create incorrect next instances | Medium | Medium | Include comprehensive unit tests for date calculations; validate recurrence rules on input |
| Reminder service sends duplicate notifications | Low | High | Implement deduplication logic using event IDs and processed message tracking |
| WebSocket connections overwhelm backend service | High | Medium | Implement connection limits and graceful degradation; document scaling requirements |
| Cloud provider costs exceed free tier limits | Medium | Medium | Implement resource monitoring alerts; document cost optimization practices |
| CI/CD pipeline exposes secrets in logs | High | Low | Use GitHub Actions secrets management; implement secret scanning in pipeline |
| Database migration fails causing deployment rollback | High | Medium | Include pre-migration validation; implement rollback procedures for schema changes |
| Real-time updates arrive out of order causing UI inconsistency | Medium | Low | Include sequence numbers in events; implement client-side ordering logic |
| Notification service rate limits prevent reminder delivery | Medium | Medium | Implement queue-based delivery with retry logic; monitor rate limit usage |
| Dapr version incompatibility with Kubernetes version | Medium | Low | Document tested version combinations; provide version upgrade guide |

## AIOps Tool Requirements

This phase requires documentation of AIOps tool usage:

- **kubectl-ai**: Commands for generating Kubernetes manifests for Dapr components, Kafka deployment, and microservices
- **Kagent**: Commands for analyzing cluster health, resource utilization, and optimization suggestions for cloud deployment
- **Gordon (Docker AI)**: Commands for optimizing Dockerfiles for event-driven services
- **GitHub Copilot/Cursor**: Commands for generating CI/CD pipeline configuration and Helm chart templates
- **Documentation**: All AIOps commands must be documented with purpose, prompts used, and results obtained

This documentation ensures reproducibility and provides evidence of AI-assisted development for hackathon submission.

## Architecture Overview

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cloud Kubernetes Cluster                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Ingress / Gateway                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Frontend   │    │   Backend   │    │  Services   │        │
│  │  (Next.js)  │    │  (FastAPI)  │    │             │        │
│  │  + Dapr     │    │  + Dapr     │    │  + Dapr     │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Kafka / Redpanda Cluster                     │  │
│  │  Topics: task-events, reminders, time-logged              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │Notification │    │  Recurring  │    │  Real-Time  │        │
│  │  Service   │    │   Task      │    │   Sync      │        │
│  │  + Dapr    │    │  Service    │    │  Service    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Neon   │  │ SendGrid │  │Container │  │   Cloud  │       │
│  │PostgreSQL│  │   Email  │  │ Registry │  │Provider  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Event Flow

```
User Action (Create Task)
      │
      ▼
Frontend → Backend API
      │
      ▼
Backend → Dapr Sidecar (Publish)
      │
      ▼
Kafka Topic: task-events
      │
      ├─→ Notification Service → Email Notification
      ├─→ Recurring Task Service → (if applicable) Create Next Task
      └─→ Real-Time Sync Service → WebSocket Broadcast → All Clients
```

## Migration Guide: Phase IV to Phase V

### Step 1: Database Schema Migration

1. Add new columns to tasks table:
   ```sql
   ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB DEFAULT NULL;
   ALTER TABLE tasks ADD COLUMN reminder_settings JSONB DEFAULT NULL;
   ```

2. Create index on recurrence_rule for efficient queries:
   ```sql
   CREATE INDEX idx_tasks_recurrence ON tasks((recurrence_rule->>'frequency')) WHERE recurrence_rule IS NOT NULL;
   ```

### Step 2: Backend Modifications

1. Add Dapr client dependency to `requirements.txt`:
   ```
   dapr>=1.14.0
   ```

2. Create `dapr_client.py` for event publishing

3. Modify `task_service.py` to publish events after each operation

4. Create `dapr.py` API routes for event subscriptions

5. Create event-driven services:
   - `notification_service.py`
   - `recurring_task_service.py`
   - `realtime_sync_service.py`

### Step 3: Frontend Modifications

1. Add WebSocket connection utility (`websocket.ts`)

2. Create recurring task form component

3. Create reminder settings component

4. Update task list to handle real-time updates

### Step 4: Kubernetes Infrastructure

1. Install Dapr on Minikube:
   ```bash
   dapr init -k
   ```

2. Deploy Kafka/Redpanda:
   ```bash
   kubectl apply -f kafka/redpanda-minikube.yaml
   ```

3. Create Dapr components:
   ```bash
   kubectl apply -f dapr-components/
   ```

4. Update Helm charts with Dapr annotations

### Step 5: Testing

1. Test event publishing to Kafka
2. Test event consumption by services
3. Test recurring task creation
4. Test reminder notifications
5. Test real-time updates across multiple clients

## Troubleshooting

### Dapr Issues

**Problem**: Dapr sidecar not injecting
- **Solution**: Verify namespace has Dapr installed with `dapr status -k`
- **Check**: Pod annotations include `dapr.io/enabled: "true"`

**Problem**: Events not publishing to Kafka
- **Solution**: Verify Dapr component configuration is applied
- **Check**: `kubectl get daprcomponents -A`
- **Check**: Kafka service is reachable from Dapr sidecar

### Kafka Issues

**Problem**: Kafka cluster fails to start
- **Solution**: Check resource limits in Minikube
- **Check**: Pod logs with `kubectl logs -f kafka-0`
- **Alternative**: Use single-node Redpanda configuration

**Problem**: Topics not created
- **Solution**: Manually create topics if auto-creation disabled
- **Command**: `kubectl exec -it kafka-0 -- kafka-topics --create --topic task-events`

### Event-Driven Services

**Problem**: Service not consuming events
- **Solution**: Verify Dapr subscription endpoint is configured
- **Check**: Service logs show subscription registrations
- **Check**: Topic name matches Dapr component configuration

**Problem**: Duplicate events being processed
- **Solution**: Implement idempotency in event handlers
- **Check**: Consumer group configuration is correct

### Real-Time Updates

**Problem**: WebSocket connection drops frequently
- **Solution**: Increase heartbeat interval in ingress configuration
- **Check**: Load balancer timeout settings

**Problem**: Updates not appearing in real-time
- **Solution**: Verify WebSocket service is running and healthy
- **Check**: Browser console for WebSocket errors

### Cloud Deployment

**Problem**: Pods not starting on cloud cluster
- **Solution**: Verify resource requests are within free tier limits
- **Check**: `kubectl describe pod <pod-name>` for specific errors

**Problem**: Ingress not accessible
- **Solution**: Verify ingress controller is installed on cloud cluster
- **Check**: DNS records point to correct load balancer IP

### CI/CD Pipeline

**Problem**: Pipeline fails on security scan
- **Solution**: Update base images to fix vulnerabilities
- **Check**: Trivy scan results for specific vulnerabilities

**Problem**: Deployment fails due to missing secrets
- **Solution**: Verify all required secrets are configured in GitHub
- **Check**: Secret names match values in Helm chart

## Bonus Features Implementation

### Reusable Intelligence (+200 points)

Create agent skills for common Dapr/Kafka patterns:

1. **Dapr Event Publishing Skill**: Template for adding event publishing to services
2. **Kafka Consumer Service Skill**: Template for creating event-driven services
3. **Dapr Component Configuration Skill**: Template for configuring Dapr building blocks
4. **Helm Chart with Dapr Skill**: Template for Helm charts with Dapr annotations

**Location**: `.specify/skills/dapr-patterns/` and `.specify/skills/kafka-patterns/`

### Cloud-Native Blueprints (+200 points)

Document reusable deployment patterns:

1. **Event-Driven Microservice Blueprint**: Complete service template
2. **Kafka Cluster Blueprint**: Production Kafka deployment guide
3. **Dapr Integration Blueprint**: Dapr setup and configuration guide
4. **Cloud Deployment Blueprint**: Step-by-step cloud deployment guide

**Location**: `docs/blueprints/`

## Hackathon Submission Checklist

### Required Deliverables

- [ ] Working Dapr integration with sidecar injection
- [ ] Kafka/Redpanda cluster deployed and accessible
- [ ] Event-driven microservices (notification, recurring-task, realtime-sync)
- [ ] Recurring task feature working end-to-end
- [ ] Due date reminder feature working end-to-end
- [ ] Real-time updates working across multiple clients
- [ ] Cloud Kubernetes deployment (AKS/GKE/OKE)
- [ ] CI/CD pipeline with GitHub Actions
- [ ] All AIOps commands documented
- [ ] Architecture diagrams updated
- [ ] Deployment guide created
- [ ] Demo video recorded (< 90 seconds)
- [ ] Hackathon form submitted with all links

### Evidence Collection

- Screenshots of Dapr sidecar running
- Screenshots of Kafka topics and consumer groups
- Screenshots of event flow in action
- Screenshots of cloud deployment
- Screenshot of successful CI/CD pipeline run
- Links to GitHub repository with all code
- Link to deployed application (if public)
