# Database Migration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Kubernetes Cluster                                │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Helm Chart Release                           │   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌──────────────┐  ┌────────────────────────┐  │   │
│  │  │ PostgreSQL     │  │ Migration    │  │ Backend Deployment     │  │   │
│  │  │ StatefulSet    │  │ Job          │  │ (waits for migrations) │  │   │
│  │  │                │  │              │  │                        │  │   │
│  │  │ Port: 5432     │  │ Hook:        │  │ Replicas: 2            │  │   │
│  │  │ Storage: 5Gi   │  │ post-install │  │ Port: 8000             │  │   │
│  │  └────────┬───────┘  │ post-upgrade │  └────────────┬───────────┘  │   │
│  │           │          └──────┬───────┘               │              │   │
│  │           │                  │                       │              │   │
│  │           │                  │                       │              │   │
│  │  ┌────────▼──────────────────▼───────────────────────▼───────┐    │   │
│  │  │              Kubernetes Service Mesh                     │    │   │
│  │  │        postgres:5432    actionmindai-backend:8000        │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Configuration                               │   │
│  │                                                                      │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐   │   │
│  │  │ Secrets          │  │ ConfigMaps       │  │ Values         │   │   │
│  │  │                  │  │                  │  │                │   │   │
│  │  │ - DATABASE_URL   │  │ - migrations     │  │ - migration.*  │   │   │
│  │  │ - OPENAI_API_KEY │  │   (SQL files)    │  │ - backend.*    │   │   │
│  │  │ - AUTH_SECRET    │  │                  │  │ - frontend.*   │   │   │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Migration Job Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Helm Install/Upgrade Trigger                          │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     Helm Hook: post-install, post-upgrade                     │
│                     Weight: -5 (runs early)                                   │
│                     Delete Policy: before-hook-creation, hook-succeeded       │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Create Migration Job                                  │
│                         Name: actionmindai-db-migrate                         │
│                         Type: batch/v1/Job                                   │
│                         Restart Policy: OnFailure                             │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          Job Pod Starts                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     Init Container: wait-for-db                        │ │
│  │                                                                        │ │
│  │  Image: postgres:16-alpine                                            │ │
│  │  Command: Wait for postgres:5432 to be ready                          │ │
│  │  Retry: Every 5 seconds until successful                              │ │
│  │                                                                        │ │
│  │  ┌────────────────────────────────────────────────────────────────┐  │ │
│  │  │  while ! nc -z postgres 5432; do                                │  │ │
│  │  │    echo "Waiting for database..."                               │  │ │
│  │  │    sleep 5                                                      │  │ │
│  │  │  done                                                           │  │ │
│  │  └────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │ Database Ready
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       Main Container: migrate                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  Image: postgres:16-alpine                                                   │
│  Volumes:                                                                    │
│    - migrations (ConfigMap with SQL files)                                   │
│    - tmp (emptyDir for temporary files)                                      │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Create Migration Tracking Table                           │
├──────────────────────────────────────────────────────────────────────────────┤
│  CREATE TABLE IF NOT EXISTS schema_migrations (                              │
│    id SERIAL PRIMARY KEY,                                                    │
│    migration_name VARCHAR(255) NOT NULL UNIQUE,                              │
│    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()                         │
│  );                                                                          │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      Process Migration Files                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Migration Files (sorted by name):                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ 001_create_tasks_conversations_messages.sql                          │   │
│  │ 002_add_conversation_title.sql                                       │   │
│  │ 003_fix_uuid_to_varchar.sql                                          │   │
│  │ 004_fix_user_id_types.sql                                            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  For each migration file:                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ 1. Check if already applied:                                          │   │
│  │    SELECT EXISTS FROM schema_migrations WHERE migration_name = ?      │   │
│  │                                                                       │   │
│  │ 2. If applied:                                                        │   │
│  │    - Skip migration                                                  │   │
│  │    - Log: "✓ migration_name already applied, skipping"               │   │
│  │                                                                       │   │
│  │ 3. If not applied:                                                    │   │
│  │    - Execute SQL file: psql -f migration.sql                          │   │
│  │    - On success:                                                      │   │
│  │      INSERT INTO schema_migrations (migration_name) VALUES (?)        │   │
│  │      Log: "✓ Successfully applied migration_name"                     │   │
│  │    - On failure:                                                      │   │
│  │      Log error details                                                │   │
│  │      Exit with error code 1                                           │   │
│  │      Job will retry (up to backoffLimit times)                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Migration Complete                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Log Summary:                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ ====================================================================  │   │
│  │ All migrations completed successfully!                               │   │
│  │ ====================================================================  │   │
│  │                                                                      │   │
│  │ Applied migrations:                                                  │   │
│  │ migration_name                           | applied_at                │   │
│  │ -----------------------------------------+--------------------------- │   │
│  │ 001_create_tasks_conversations_messages   | 2026-02-06 10:00:00      │   │
│  │ 002_add_conversation_title                | 2026-02-06 10:00:05      │   │
│  │ 003_fix_uuid_to_varchar                   | 2026-02-06 10:00:05      │   │
│  │ 004_fix_user_id_types                     | 2026-02-06 10:00:06      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Job Marked Successful                                │
│                         Kubernetes deletes Job pod                           │
└───────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Backend Deployment Can Now Start                          │
│                    (Only after migrations succeed)                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Migration Tracking

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        schema_migrations Table                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  +------------+-----------------------------------+----------------------------+  │
│  | id         | migration_name                   | applied_at                │  │
│  +------------+-----------------------------------+----------------------------+  │
│  | 1          | 001_create_tasks_...             | 2026-02-06 10:00:00+00    │  │
│  | 2          | 002_add_conversation_title       | 2026-02-06 10:00:05+00    │  │
│  | 3          | 003_fix_uuid_to_varchar          | 2026-02-06 10:00:05+00    │  │
│  | 4          | 004_fix_user_id_types            | 2026-02-06 10:00:06+00    │  │
│  +------------+-----------------------------------+----------------------------+  │
│                                                                              │
│  Unique constraint on migration_name prevents duplicates                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Retry Logic

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          Failure Handling                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Migration Fails                                                             │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Check retry count < backoffLimit (4)                               │    │
│  │                                                                     │    │
│  │  If yes:                                                            │    │
│  │    - Increment retry count                                          │    │
│  │    - Wait with exponential backoff (2^n seconds)                    │    │
│  │    - Create new pod                                                 │    │
│  │    - Re-run from beginning (skips applied migrations)               │    │
│  │                                                                     │    │
│  │  If no (4 retries failed):                                          │    │
│  │    - Mark Job as Failed                                             │    │
│  │    - Keep pod for inspection (logs)                                 │    │
│  │    - Block Helm upgrade (if applicable)                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Configuration Flow                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Helm Values                                                                │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ migration:                                                          │     │
│  │   enabled: true                                                     │     │
│  │   backoffLimit: 4                                                   │     │
│  │   database:                                                         │     │
│  │     host: postgres                                                  │     │
│  │     port: 5432                                                      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│       │                                                                      │
│       │ Helm Template Rendering                                             │
│       ▼                                                                      │
│  Kubernetes Manifests                                                        │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ Job: actionmindai-db-migrate                                        │     │
│  │   - Init container waits for postgres:5432                          │     │
│  │   - Main container runs migrations                                   │     │
│  │   - Volumes: migrations (ConfigMap)                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│       │                                                                      │
│       │ Applied to Cluster                                                   │
│       ▼                                                                      │
│  Runtime Environment                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ Environment Variables:                                              │     │
│  │   DATABASE_URL = from Secret                                         │     │
│  │   PGCONNECT_TIMEOUT = 30                                             │     │
│  │                                                                      │     │
│  │ Volume Mounts:                                                       │     │
│  │   /migrations -> ConfigMap with SQL files                           │     │
│  │   /tmp -> emptyDir for temporary files                              │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Kubernetes Resource Relationships                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐                                                           │
│  │ Helm Chart     │                                                           │
│  │ ─────────────  │                                                           │
│  │ templates/     │                                                           │
│  │   ├─ migration-job.yaml         ────────┐                                 │
│  │   ├─ migrations-configmap.yaml  ───┐    │                                 │
│  │   └─ _helpers.tpl                │  │    │                                 │
│  │                                    │  │    │                                 │
│  │ values.yaml ───────────────────────┘  │    │                                 │
│  └───────────────────────────────────────┘    │                                 │
│                                                │                                 │
│                                                ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │                     Kubernetes Cluster                              │      │
│  │                                                                      │      │
│  │  ┌──────────────────────────────────────────────────────────────┐  │      │
│  │  │ ConfigMap: actionmindai-migrations                           │  │      │
│  │  │ Data: SQL migration files                                    │  │      │
│  │  └──────────────────────────────────────────────────────────────┘  │      │
│  │                          │                                          │      │
│  │                          │ Mounted as /migrations                   │      │
│  │                          ▼                                          │      │
│  │  ┌──────────────────────────────────────────────────────────────┐  │      │
│  │  │ Job: actionmindai-db-migrate                                 │  │      │
│  │  │   ┌──────────────────────────────────────────────────────┐   │  │      │
│  │  │   │ InitContainer: wait-for-db                            │   │  │      │
│  │  │   │   ┌────────────────────────────────────────────────┐  │   │  │      │
│  │  │   │   │ Waits for Service: postgres:5432               │  │   │  │      │
│  │  │   │   └────────────────────────────────────────────────┘  │   │  │      │
│  │  │   └──────────────────────────────────────────────────────┘   │  │      │
│  │  │   ┌──────────────────────────────────────────────────────┐   │  │      │
│  │  │   │ Container: migrate                                    │   │  │      │
│  │  │   │   ┌────────────────────────────────────────────────┐  │   │  │      │
│  │  │   │   │ 1. Reads SQL from /migrations                 │  │   │  │      │
│  │  │   │   │ 2. Connects to DATABASE_URL                    │  │   │  │      │
│  │  │   │   │ 3. Creates schema_migrations table             │  │   │  │      │
│  │  │   │   │ 4. Applies pending migrations                  │  │   │  │      │
│  │  │   │   │ 5. Records applied migrations                  │  │   │  │      │
│  │  │   │   └────────────────────────────────────────────────┘  │   │  │      │
│  │  │   └──────────────────────────────────────────────────────┘   │  │      │
│  │  └──────────────────────────────────────────────────────────────┘  │      │
│  │                                                                      │      │
│  │  ┌──────────────────────────────────────────────────────────────┐  │      │
│  │  │ Service: postgres (ClusterIP:5432)                           │  │      │
│  │  │   ┌──────────────────────────────────────────────────────┐   │  │      │
│  │  │   │ StatefulSet: postgres (replicas: 1)                  │   │  │      │
│  │  │   │   ┌────────────────────────────────────────────────┐  │   │  │      │
│  │  │   │   │ PersistentVolumeClaim: postgres-pvc (5Gi)      │  │   │  │      │
│  │  │   │   └────────────────────────────────────────────────┘  │   │  │      │
│  │  │   └──────────────────────────────────────────────────────┘   │  │      │
│  │  └──────────────────────────────────────────────────────────────┘  │      │
│  │                                                                      │      │
│  │  ┌──────────────────────────────────────────────────────────────┐  │      │
│  │  │ Secret: actionmindai-secrets                                  │  │      │
│  │  │   - databaseUrl                                               │  │      │
│  │  │   - openaiApiKey                                              │  │      │
│  │  │   - betterAuthSecret                                          │  │      │
│  │  └──────────────────────────────────────────────────────────────┘  │      │
│  └─────────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Timeline Visualization

```
Time:  0s      5s      10s     15s     20s     25s     30s     35s     40s
       │       │       │       │       │       │       │       │       │
       ├───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┤
       │
PostgreSQL
       │       ████████████████████████████████████████████████████
       │       (Running, accepting connections)
       │
Init Container
       │       ████████
       │       (Waiting for DB)
       │
Migration Job
       │               ██████████████████████████████
       │               (Running migrations)
       │
Backend Deployment
       │                                               ████████████████████
       │                                               (Starts after migrations)
       │
Frontend Deployment
       │                                               ████████████████████
       │                                               (Can start now)
       │
```

## Success Criteria

- [ ] Migration Job completes with exit code 0
- [ ] All 4 migration files applied successfully
- [ ] `schema_migrations` table contains 4 records
- [ ] All tables created: tasks, conversations, messages, schema_migrations
- [ ] All indexes created correctly
- [ ] Backend pods can connect to database
- [ ] Backend health endpoint returns 200 OK
- [ ] No migration errors in logs

## Failure Recovery

If migration fails:
1. Check logs: `kubectl logs job/actionmindai-db-migrate`
2. Identify failed migration
3. Fix SQL syntax or data issue
4. Delete job: `kubectl delete job actionmindai-db-migrate`
5. Re-run: `helm upgrade actionmindai ./helm/ActionMindAI`

## Monitoring Commands

```bash
# Watch migration progress
kubectl logs -f job/actionmindai-db-migrate -n actionmindai

# Check job status
kubectl get jobs -n actionmindai -l component=migration

# Verify migrations in database
kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai \\
  -c "SELECT * FROM schema_migrations ORDER BY applied_at;"

# Check all tables created
kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai -c "\\dt"
```

---

Document Version: 1.0.0
Last Updated: 2026-02-06
Author: ActionMindAI Development Team
