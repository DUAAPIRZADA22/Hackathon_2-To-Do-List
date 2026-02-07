# Database Migration Implementation Summary

## Overview

A complete cloud-native database initialization and migration strategy has been implemented for ActionMindAI using Kubernetes Jobs, Helm hooks, and PostgreSQL.

## Implementation Details

### Files Created

| File | Purpose |
|------|---------|
| `helm/ActionMindAI/templates/migration-job.yaml` | Helm template for migration Job |
| `helm/ActionMindAI/templates/migrations-configmap.yaml` | ConfigMap with SQL migration scripts |
| `helm/ActionMindAI/values.yaml` (updated) | Migration configuration values |
| `helm/ActionMindAI/templates/_helpers.tpl` (updated) | Added migration labels helper |
| `k8s/migration-job-standalone.yaml` | Standalone Kubernetes Job manifest |
| `k8s/postgres-with-migrations.yaml` | Complete PostgreSQL + migrations deployment |
| `k8s/secrets-example.yaml` | Example secrets configuration |
| `docs/DATABASE-MIGRATION-GUIDE.md` | Comprehensive migration documentation |
| `QUICK-MIGRATION-DEPLOY.md` | Quick reference deployment guide |

### Key Features Implemented

1. **Kubernetes Job with Helm Hooks**
   - Runs automatically on `post-install` and `post-upgrade`
   - Hook weight: `-5` (runs before most other resources)
   - Cleanup policy: `before-hook-creation,hook-succeeded`

2. **Retry Logic**
   - `backoffLimit: 4` - Up to 4 retry attempts for failed migrations
   - `activeDeadlineSeconds: 600` - 10-minute maximum execution time
   - Exponential backoff between retries

3. **Idempotent Migrations**
   - Tracks applied migrations in `schema_migrations` table
   - Automatically skips already-applied migrations
   - Safe to run multiple times

4. **Database Readiness Check**
   - Init container waits for PostgreSQL to be ready
   - Uses `nc` (netcat) and `pg_isready` for health checks
   - Retries every 5 seconds until connection succeeds

5. **Migration Tracking**
   - `schema_migrations` table stores migration history
   - Records migration name and timestamp
   - Prevents duplicate migrations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Helm Install/Upgrade                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Helm Hook: post-install, post-upgrade (weight: -5)         │
│  Job: actionmindai-db-migrate                               │
│  Cleanup: before-hook-creation, hook-succeeded              │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌─────────────────────┐             ┌─────────────────────────┐
│  Init Container     │             │  Main Container         │
│  postgres:16-alpine │             │  postgres:16-alpine     │
│  wait-for-db        │             │  migrate                │
└─────────────────────┘             └───────────┬─────────────┘
                                                │
                                                ▼
                                    ┌─────────────────────────┐
                                    │  PostgreSQL Database    │
                                    │  - Apply migrations     │
                                    │  - Track in             │
                                    │    schema_migrations    │
                                    └─────────────────────────┘
```

## Migrations Included

1. **001_create_tasks_conversations_messages.sql**
   - Creates `tasks`, `conversations`, and `messages` tables
   - Sets up indexes for performance
   - Creates trigger for automatic `updated_at` timestamps
   - Adds foreign key constraints

2. **002_add_conversation_title.sql**
   - Adds `title` column to conversations table
   - Creates index on user_id and title

3. **003_fix_uuid_to_varchar.sql**
   - No-op migration (kept for compatibility)

4. **004_fix_user_id_types.sql**
   - Ensures consistent VARCHAR(255) type for user_id columns

## Configuration

### Helm Values (`values.yaml`)

```yaml
migration:
  enabled: true
  backoffLimit: 4              # Max retry attempts
  activeDeadlineSeconds: 600   # 10 minutes timeout
  initContainer:
    image: postgres:16-alpine
  database:
    host: postgres
    port: 5432
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### Environment Variables

The migration job uses these environment variables:
- `DATABASE_URL` - From secret `actionmindai-secrets`
- `PGCONNECT_TIMEOUT` - Connection timeout (30 seconds)
- `PYTHONUNBUFFERED` - Python output buffering disabled

## Deployment Methods

### Method 1: Helm Chart (Recommended)

```bash
# Install with automatic migrations
helm install actionmindai ./helm/ActionMindAI -n actionmindai --create-namespace

# Upgrade with automatic migrations
helm upgrade actionmindai ./helm/ActionMindAI -n actionmindai
```

### Method 2: Standalone Kubernetes Manifest

```bash
# Apply standalone job
kubectl apply -f k8s/migration-job-standalone.yaml

# Or apply complete stack (PostgreSQL + migrations)
kubectl apply -f k8s/postgres-with-migrations.yaml
```

### Method 3: Manual Execution

```bash
# Create job from template
kubectl apply -f helm/ActionMindAI/templates/migration-job.yaml

# Watch logs
kubectl logs -f job/actionmindai-db-migrate -n actionmindai
```

## Adding New Migrations

1. Create SQL file: `005_new_feature.sql`
2. Add to `migrations-configmap.yaml`:
   ```yaml
   "005_new_feature.sql": |
     -- Your SQL here
   ```
3. Deploy: `helm upgrade actionmindai ./helm/ActionMindAI -n actionmindai`

## Verification

### Check Migration Status

```bash
# Job status
kubectl get jobs -n actionmindai -l component=migration

# Migration logs
kubectl logs -n actionmindai job/actionmindai-db-migrate

# Applied migrations in database
kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai \\
  -c "SELECT * FROM schema_migrations ORDER BY applied_at;"
```

### Verify Database Schema

```bash
# List tables
kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai -c "\\dt"

# Check indexes
kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai \\
  -c "SELECT indexname FROM pg_indexes WHERE schemaname = 'public';"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Job fails with "connection refused" | Check DATABASE_URL secret and PostgreSQL service |
| Migration timeout | Increase `activeDeadlineSeconds` in values.yaml |
| Migration already applied error | Normal - job skips applied migrations automatically |
| SQL syntax error | Test migration manually: `psql -f migration.sql` |
| Job stuck in "Running" | Check pod logs: `kubectl logs pod/<migration-pod>` |

## Security Considerations

1. **Secrets Management**
   - DATABASE_URL stored in Kubernetes Secret
   - Use SealedSecrets or External Secrets Operator for production
   - Never commit secrets to version control

2. **Network Policies**
   - Restrict database access to application pods only
   - Migration pods should have temporary access

3. **RBAC**
   - Migration job uses service account with minimal permissions
   - Consider creating dedicated migration service account

## Production Recommendations

1. **Pre-migration Backup**
   ```bash
   # Backup database before migration
   kubectl exec -n actionmindai deploy/postgres -- pg_dump -U postgres actionmindai > backup.sql
   ```

2. **Staging Testing**
   - Always test migrations in staging first
   - Verify data integrity after migration

3. **Monitoring**
   - Set up alerts for migration job failures
   - Monitor migration duration over time

4. **Rollback Plan**
   - Include rollback SQL in migration file comments
   - Document rollback procedure

## Migration Process Flow

```
1. Helm install/upgrade triggered
   ↓
2. Helm hook creates migration Job (weight: -5)
   ↓
3. Job Pod starts
   ↓
4. Init container waits for database (pg_isready)
   ↓
5. Main container starts
   ↓
6. Creates schema_migrations tracking table
   ↓
7. For each migration file (sorted by name):
   ├─ Check if already applied
   ├─ If yes: Skip
   └─ If no: Apply and record
   ↓
8. Job completes successfully
   ↓
9. Helm deletes Job (hook-succeeded policy)
   ↓
10. Backend deployment starts
```

## Related Documentation

- [Complete Migration Guide](docs/DATABASE-MIGRATION-GUIDE.md)
- [Quick Deployment Reference](QUICK-MIGRATION-DEPLOY.md)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)

## Support

For issues or questions:
1. Check migration job logs
2. Verify database connectivity
3. Review migration SQL syntax
4. Consult [DATABASE-MIGRATION-GUIDE.md](docs/DATABASE-MIGRATION-GUIDE.md)

---

**Implementation Date:** 2026-02-06
**Status:** Complete
**Version:** 1.0.0
