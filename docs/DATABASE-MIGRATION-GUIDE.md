# Database Migration Guide for ActionMindAI

This guide explains the cloud-native database initialization and migration strategy for the ActionMindAI application deployed on Kubernetes.

## Overview

The migration strategy uses Kubernetes Jobs with Helm hooks to automatically run database migrations on install and upgrade. The implementation includes:

- **Kubernetes Job** (`migration-job.yaml`) - Executes migrations in a containerized environment
- **ConfigMap** (`migrations-configmap.yaml`) - Stores SQL migration scripts as configuration
- **Helm Hooks** - Automates migration execution during install/upgrade
- **Idempotent Migrations** - Tracks applied migrations to avoid re-running
- **Retry Logic** - Configurable retry attempts for failed migrations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Helm Install/Upgrade                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Helm Hook: post-install, post-upgrade (weight: -5)         │
│  Job: actionmindai-db-migrate                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌─────────────────────┐             ┌─────────────────────────┐
│  Init Container     │             │  Main Container         │
│  wait-for-db        │             │  migrate                │
└──────────┬──────────┘             └───────────┬─────────────┘
           │                                    │
           ▼                                    ▼
    ┌─────────────┐                   ┌──────────────────┐
    │ PostgreSQL  │◄──────────────────│  psql client     │
    │ Database    │                   │  Apply migrations│
    └─────────────┘                   └──────────────────┘
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │ schema_migrations   │
                                    │ (tracking table)    │
                                    └─────────────────────┘
```

## Components

### 1. Migration Job (`migration-job.yaml`)

**Purpose:** Executes database migrations in a Kubernetes Job

**Key Features:**
- Helm hooks: `post-install`, `post-upgrade`
- Retry logic with `backoffLimit: 4`
- Timeout with `activeDeadlineSeconds: 600`
- Init container waits for database readiness
- Idempotent migration tracking via `schema_migrations` table

**Helm Hook Annotations:**
```yaml
helm.sh/hook: post-install,post-upgrade
helm.sh/hook-weight: "-5"
helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
```

### 2. Migrations ConfigMap (`migrations-configmap.yaml`)

**Purpose:** Stores SQL migration scripts as Kubernetes ConfigMap

**Migrations Included:**
1. `001_create_tasks_conversations_messages.sql` - Core tables
2. `002_add_conversation_title.sql` - Conversation titles
3. `003_fix_uuid_to_varchar.sql` - UUID compatibility (no-op)
4. `004_fix_user_id_types.sql` - User ID type consistency

### 3. Migration Configuration (`values.yaml`)

```yaml
migration:
  enabled: true
  backoffLimit: 4              # Max retry attempts
  activeDeadlineSeconds: 600   # Max execution time
  initContainer:
    image: postgres:16-alpine  # Database client image
  database:
    host: postgres             # Database service name
    port: 5432
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

## Usage

### Initial Deployment

```bash
# Set up secrets first
kubectl create secret generic actionmindai-secrets \\
  --from-literal=databaseUrl='postgresql://user:password@postgres:5432/actionmindai' \\
  --from-literal=openaiApiKey='your-key-here' \\
  --from-literal=betterAuthSecret='your-secret-here'

# Install the chart (migrations run automatically)
helm install actionmindai ./helm/ActionMindAI
```

### Upgrading with New Migrations

```bash
# Add new migration to migrations-configmap.yaml
# Then upgrade the chart
helm upgrade actionmindai ./helm/ActionMindAI
```

### Manually Triggering Migrations

```bash
# Create the job manually from the template
kubectl apply -f helm/ActionMindAI/templates/migration-job.yaml

# Watch the job logs
kubectl logs -f job/actionmindai-db-migrate
```

### Checking Migration Status

```bash
# Check if migrations completed successfully
kubectl get jobs -l app.kubernetes.io/component=migration

# View migration job logs
kubectl logs job/actionmindai-db-migrate -n actionmindai

# Check applied migrations in the database
kubectl exec -it postgres-0 -n actionmindai -- psql -U postgres -d actionmindai \\
  -c "SELECT * FROM schema_migrations ORDER BY applied_at;"
```

## Migration Process

### 1. Database Readiness Check

The init container waits for the database to be ready:

```bash
until nc -z -v -w30 postgres 5432; do
  echo "Database not ready yet, waiting..."
  sleep 5
done
```

### 2. Migration Tracking Table

The job creates a `schema_migrations` table to track applied migrations:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  id SERIAL PRIMARY KEY,
  migration_name VARCHAR(255) NOT NULL UNIQUE,
  applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Idempotent Execution

For each migration file:
1. Check if already applied in `schema_migrations`
2. Skip if applied, otherwise apply
3. Record successful application

```bash
for migration in $MIGRATION_FILES; do
  migration_name=$(basename "$migration")
  applied=$(psql "$DATABASE_URL" -tAc "SELECT EXISTS(...)")

  if [ "$applied" = "t" ]; then
    echo "Migration $migration_name already applied, skipping..."
  else
    psql "$DATABASE_URL" -f "$migration"
    psql "$DATABASE_URL" -c "INSERT INTO schema_migrations ..."
  fi
done
```

## Adding New Migrations

### Step 1: Create Migration SQL File

```sql
-- Migration: 005_add_new_feature.sql
-- Purpose: Add new feature table
-- Database: PostgreSQL 16+

CREATE TABLE IF NOT EXISTS new_feature (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Step 2: Add to ConfigMap

Add the migration to `migrations-configmap.yaml`:

```yaml
"data":
  "005_add_new_feature.sql": |
    -- Your SQL here
```

### Step 3: Re-deploy

```bash
helm upgrade actionmindai ./helm/ActionMindAI
```

## Troubleshooting

### Migration Job Failed

**Check job status:**
```bash
kubectl describe job actionmindai-db-migrate -n actionmindai
```

**View logs:**
```bash
kubectl logs job/actionmindai-db-migrate -n actionmindai
```

**Common issues:**
1. **Database not ready** - Check PostgreSQL service and pods
2. **Connection refused** - Verify DATABASE_URL secret
3. **SQL syntax error** - Test migration manually first

### Migration Already Applied

The job automatically skips already-applied migrations. To re-apply:

```sql
-- Remove migration record
DELETE FROM schema_migrations WHERE migration_name = '001_...sql';
```

Then re-run the job.

### Resource Constraints

If migrations time out, increase limits in `values.yaml`:

```yaml
migration:
  activeDeadlineSeconds: 1200  # Increase to 20 minutes
```

### Retrying Failed Migrations

The job automatically retries up to `backoffLimit` times. To retry immediately:

```bash
# Delete the failed job
kubectl delete job actionmindai-db-migrate -n actionmindai

# Re-apply the manifest
kubectl apply -f helm/ActionMindAI/templates/migration-job.yaml
```

## Validation

### Verify Tables Created

```sql
-- Connect to database
kubectl exec -it postgres-0 -n actionmindai -- psql -U postgres -d actionmindai

-- Check tables
\\dt

-- Expected output:
-- public | conversations | table
-- public | messages      | table
-- public | schema_migrations | table
-- public | tasks         | table
```

### Verify Indexes

```sql
-- Check indexes
SELECT indexname FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY indexname;
```

### Verify Constraints

```sql
-- Check constraints
SELECT conname, conrelid::regclass
FROM pg_constraint
WHERE conrelid::regclass IN ('tasks', 'conversations', 'messages')
ORDER BY conrelid::regclass::text, conname;
```

## Best Practices

1. **Always test migrations locally first** before deploying
2. **Use transactions** for complex migrations
3. **Add rollback comments** in migration files
4. **Version migrations** with sequential numbering
5. **Document breaking changes** in migration comments
6. **Monitor job completion** after deployments
7. **Backup database** before major upgrades

## Migration Rollback

To rollback a migration:

1. Manually execute rollback SQL from migration file comments
2. Remove migration record:

```sql
DELETE FROM schema_migrations
WHERE migration_name = 'migration_to_rollback.sql';
```

3. Re-run migration job to apply remaining migrations

## Security Considerations

1. **Secrets Management** - DATABASE_URL stored in Kubernetes Secret
2. **Least Privilege** - Migration job uses service account with minimal permissions
3. **Network Policies** - Restrict database access to migration pods only
4. **Audit Logging** - All migrations logged to `schema_migrations` table

## Monitoring

### Prometheus Metrics (if configured)

```yaml
# Job completion time
helm_hook_job_completion_seconds{hook="post-install"}

# Migration success/failure
helm_hook_job_success_total{hook="post-install", component="migration"}
```

### Logging

Migration job outputs detailed logs:

```
Starting database migrations...
Waiting for database to be ready...
Database is ready!
Found migrations directory: /migrations
Found migration files:
/migrations/001_create_tasks_conversations_messages.sql
/migrations/002_add_conversation_title.sql
...

Creating migrations tracking table if not exists...
Applying migration: 001_create_tasks_conversations_messages.sql
Successfully applied migration: 001_create_tasks_conversations_messages.sql
...

All migrations completed successfully!
```

## References

- [Helm Hooks Documentation](https://helm.sh/docs/topics/charts_hooks/)
- [Kubernetes Jobs Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [PostgreSQL Migration Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_rollback_scripts)

## Support

For issues or questions:
1. Check job logs: `kubectl logs job/actionmindai-db-migrate`
2. Verify database connectivity
3. Review migration SQL syntax
4. Check Helm chart values
