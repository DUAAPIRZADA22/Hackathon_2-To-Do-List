# Research: Advanced Cloud Deployment with Event-Driven Architecture

**Feature**: 005-advanced-cloud-deployment
**Date**: 2026-02-08
**Phase**: Phase 0 - Outline & Research

## Overview

This document captures research findings for implementing event-driven architecture with Dapr and Kafka/Redpanda, cloud Kubernetes deployment, and CI/CD pipeline for the ActionMind AI application.

## Technology Decisions

### Decision 1: Kafka vs. Redpanda

**Selected**: Redpanda (for local Minikube) and Kafka Strimzi (for cloud production)

**Rationale**:
- **Redpanda for Local**: Single binary deployment, no ZooKeeper dependency, faster setup for hackathon timeline
- **Kafka Strimzi for Cloud**: Production-grade, better cloud provider support, more mature ecosystem
- Both are Kafka-compatible - same client libraries work for both environments

**Alternatives Considered**:
1. **Apache Kafka only**: More complex local setup requiring ZooKeeper
2. **Redpanda Cloud**: Easiest but requires external service account and potential costs
3. **Redpanda self-hosted everywhere**: Simpler but less cloud-native tooling

**Implementation Notes**:
```yaml
# Local: Redpanda single node
apiVersion: redpanda.vectorized.io/v1alpha1
kind: Cluster
metadata:
  name: redpanda
spec:
  replicas: 1

# Cloud: Kafka with Strimzi
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: actionmindai-kafka
spec:
  kafka:
    replicas: 3
    storage:
      type: ephemeral  # For hackathon scale
```

---

### Decision 2: Dapr Component Configuration

**Selected**: Dapr 1.14+ with Kubernetes mode deployment

**Rationale**:
- Kubernetes-native integration with automatic sidecar injection
- Built-in service discovery and pub/sub abstraction
- Supports multiple building blocks (pubsub, state store, secret store, bindings)

**Component Configuration**:

```yaml
# pubsub-kafka.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda-0.redpanda.default.svc.cluster.local:9092"
  - name: authRequired
    value: "false"
  - name: autoCreateTopics
    value: "true"

# state-postgresql.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: neon-db-secret
      key: connection-string

# secrets-kubernetes.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secret-store
spec:
  type: secretstores.kubernetes
  version: v1

# bindings-cron.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-check-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 5m"
```

---

### Decision 3: Cloud Provider Selection

**Selected**: Oracle OKE (primary) with GKE/AKS as documented alternatives

**Rationale**:
- **Oracle OKE Always Free**: 4 OCPUs, 24GB RAM at $0/month - perfect for hackathon
- **Sufficient for hackathon scale**: 50 concurrent users, 3 microservices
- **Full Kubernetes feature parity**: Same kubectl commands apply to all providers

**Provider Comparison**:

| Provider | Free Tier | Monthly Cost | Setup Complexity |
|----------|-----------|--------------|------------------|
| **Oracle OKE** ⭐ | 4 OCPUs, 24GB RAM | $0 | Medium (OCI account setup) |
| **Google GKE** | $74.40 credit (one-time) | ~$150 | Low (gcloud CLI) |
| **Azure AKS** | Free control plane | ~$175 | Low (az CLI) |

**Implementation Notes**:
```bash
# Oracle OKE Setup
oci cluster create --name actionmindai --node-pool-shape VM.Standard.E4.Flex

# kubectl config
oci ce cluster create-kubeconfig --cluster-id $CLUSTER_ID --file $HOME/.kube/config
```

---

### Decision 4: Event Schema Design

**Selected**: JSON event format with OpenAPI specification

**Rationale**:
- Language-agnostic serialization
- Human-readable for debugging
- Compatible with Dapr pub/sub default format
- Schema validation with OpenAPI

**Event Schemas**:

```yaml
# Task Event
event_type: string (required)
task_id: string (UUID, required)
project_id: string (UUID, optional)
user_id: string (UUID, required)
timestamp: string (ISO 8601, required)
correlation_id: string (UUID, required)
data: object (event-specific)

# Reminder Event
reminder_type: string (required)
task_id: string (UUID, required)
due_date: string (ISO 8601, required)
user_id: string (UUID, required)
message: string (required)
```

---

### Decision 5: WebSocket Protocol

**Selected**: Server-Sent Events (SSE) for real-time updates

**Rationale**:
- Simpler than raw WebSocket (unidirectional is sufficient)
- Better browser support
- Automatic reconnection handling
- Lower complexity for hackathon timeline

**Alternative**: Raw WebSocket was considered but rejected for:
- More complex connection state management
- Bidirectional not needed (server → client only)

**Implementation Notes**:
```python
# FastAPI SSE endpoint
from fastapi.responses import StreamingResponse

@app.get("/ws/tasks")
async def task_events():
    async def event_generator():
        async for event in event_queue:
            yield f"data: {event.json()}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

### Decision 6: CI/CD Pipeline Structure

**Selected**: GitHub Actions with environment-based deployments

**Rationale**:
- Native GitHub integration
- Free for public repositories
- Environment-specific secrets management
- Manual approval gates for production

**Pipeline Stages**:

```yaml
# .github/workflows/deploy.yml
stages:
  1. build: Build and push Docker images
  2. test: Run unit and integration tests
  3. scan: Trivy vulnerability scanning
  4. deploy-staging: Deploy to Minikube/staging (auto)
  5. integration-test: Smoke tests on staging
  6. deploy-production: Deploy to cloud (manual approval)
  7. notify: Slack/email notification
```

---

### Decision 7: Database Migration Strategy

**Selected**: Alembic for PostgreSQL schema migrations

**Rationale**:
- Existing FastAPI project likely uses SQLAlchemy
- Alembic is standard migration tool for SQLAlchemy
- Supports rollback and versioning
- Compatible with Neon PostgreSQL serverless

**Migration Scripts**:

```python
# migrations/versions/001_add_recurrence_and_reminders.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('tasks', sa.Column('recurrence_rule', sa.JSON(), nullable=True))
    op.add_column('tasks', sa.Column('reminder_settings', sa.JSON(), nullable=True))
    op.create_index('idx_tasks_recurrence', 'tasks', [sa.text("(recurrence_rule->>'frequency')")])

def downgrade():
    op.drop_index('idx_tasks_recurrence')
    op.drop_column('tasks', 'reminder_settings')
    op.drop_column('tasks', 'recurrence_rule')
```

---

## Best Practices Research

### Event-Driven Architecture Patterns

**Idempotent Event Handlers**:
```python
# ✅ GOOD: Idempotent using event ID
async def handle_task_event(event: TaskEvent):
    if await event_store.is_processed(event.id):
        return  # Skip already processed
    await process_task(event)
    await event_store.mark_processed(event.id)

# ❌ BAD: Not idempotent
async def handle_task_event(event: TaskEvent):
    await process_task(event)  # May duplicate work
```

**Exponential Backoff for Retries**:
```python
async def publish_with_retry(topic: str, event: dict, max_retries=3):
    for attempt in range(max_retries):
        try:
            await dapr.publish_event(topic, event)
            return
        except Exception as e:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(wait_time)
    raise PublishFailedError(f"Failed after {max_retries} attempts")
```

---

### Dapr Best Practices

**Sidecar Health Checks**:
```yaml
# Deployment health checks should include Dapr sidecar
livenessProbe:
  httpGet:
    path: /healthz
    port: 3500  # Dapr sidecar health
readinessProbe:
  httpGet:
    path: /healthz
    port: 3500
```

**App Port Configuration**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "actionmindai-backend"
  dapr.io/app-port: "8000"  # Critical for sidecar to find app
  dapr.io/config: "actionmindai-dapr-config"
```

---

### Kafka Topic Configuration

**Topic Naming**: Use kebab-case, descriptive names
- `task-events` ✅
- `task_events` ❌ (inconsistent)
- `TaskEvents` ❌ (not kebab-case)

**Partition Strategy**:
```yaml
# 3 partitions for parallelism
spec:
  partitions: 3
  replicationFactor: 1  # Minikube/hackathon scale

# Partition key: user_id for ordering per user
partition_key = event.user_id
```

**Retention Policy**:
```yaml
# 7 days retention for hackathon scale
retentionMs: 604800000  # 7 days
```

---

### Kubernetes Deployment Best Practices

**Resource Limits** (Oracle OKE Always Free):
```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

**Liveness vs Readiness Probes**:
```yaml
# Liveness: Is the app alive?
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Readiness: Can the app serve traffic?
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Zero-Downtime Rolling Updates**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # One extra pod during update
    maxUnavailable: 0  # No downtime
```

---

### Testing Event-Driven Systems

**Contract Tests**:
```python
# Test event schema validation
def test_task_event_schema():
    event = TaskEvent(
        event_type="task_created",
        task_id=uuid4(),
        user_id=uuid4(),
        timestamp=datetime.utcnow(),
        correlation_id=uuid4()
    )
    assert event.event_type in VALID_EVENT_TYPES
    assert event.task_id is not None
```

**Integration Tests**:
```python
# Test event flow end-to-end
async def test_task_event_flow():
    # Publish event
    await dapr.publish_event("task-events", test_event)

    # Verify consumption
    consumed = await notification_service.wait_for_event(timeout=5)
    assert consumed.task_id == test_event.task_id
```

---

## Unresolved Items (NEEDS CLARIFICATION)

None - all technical decisions have been resolved through research.

## Summary

| Area | Decision | Key Resource |
|------|----------|--------------|
| Event Streaming | Redpanda (local), Kafka Strimzi (cloud) | Redpanda docs, Strimzi docs |
| Distributed Runtime | Dapr 1.14+ Kubernetes mode | dapr.io/docs |
| Cloud Provider | Oracle OKE (primary), GKE/AKS (alt) | Oracle Cloud docs |
| WebSocket Protocol | Server-Sent Events (SSE) | FastAPI docs |
| CI/CD | GitHub Actions with manual approval | GitHub Actions docs |
| Migrations | Alembic with SQLAlchemy | Alembic docs |
| Testing | pytest + integration tests | pytest docs |

All research complete. Ready for Phase 1: Design & Contracts.
