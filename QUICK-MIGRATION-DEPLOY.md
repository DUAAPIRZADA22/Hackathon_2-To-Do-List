# Quick Migration Deployment Guide

## Prerequisites

```bash
# Ensure kubectl is configured
kubectl cluster-info

# Ensure Helm is installed
helm version

# Verify namespace exists (or create it)
kubectl create namespace actionmindai --dry-run=client -o yaml | kubectl apply -f -
```

## Step 1: Prepare Secrets

Create a file `secrets.yaml` with your actual values:

```yaml
namespace: actionmindai

secrets:
  # Format: postgresql://user:password@host:port/database
  databaseUrl: "postgresql://postgres:your-password@postgres:5432/actionmindai"
  openaiApiKey: "your-openai-api-key"
  betterAuthSecret: "your-auth-secret-min-32-chars"
```

Apply the secrets:

```bash
# On Windows
kubectl create secret generic actionmindai-secrets `
  --from-literal=databaseUrl='postgresql://postgres:password@postgres:5432/actionmindai' `
  --from-literal=openaiApiKey='sk-your-key' `
  --from-literal=betterAuthSecret='your-secret-at-least-32-chars' `
  -n actionmindai

# On Linux/Mac
kubectl create secret generic actionmindai-secrets \
  --from-literal=databaseUrl='postgresql://postgres:password@postgres:5432/actionmindai' \
  --from-literal=openaiApiKey='sk-your-key' \
  --from-literal=betterAuthSecret='your-secret-at-least-32-chars' \
  -n actionmindai
```

## Step 2: Install the Chart

```bash
# From project root
helm install actionmindai ./helm/ActionMindAI -n actionmindai --create-namespace
```

This will automatically:
1. Deploy PostgreSQL database
2. Run all database migrations
3. Deploy backend service
4. Deploy frontend service

## Step 3: Verify Migration Success

```bash
# Check migration job status
kubectl get jobs -n actionmindai -l app.kubernetes.io/component=migration

# Should show: COMPLETED or SUCCESSFUL

# View migration logs
kubectl logs -n actionmindai job/actionmindai-db-migrate

# Verify tables in database
kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai -c "\\dt"
```

## Step 4: Verify Application

```bash
# Check all pods are running
kubectl get pods -n actionmindai

# Port forward to test locally
kubectl port-forward -n actionmindai svc/actionmindai-backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health
```

## Upgrading with New Migrations

When you add new migrations:

1. Update `helm/ActionMindAI/templates/migrations-configmap.yaml` with new SQL
2. Upgrade the Helm release:

```bash
helm upgrade actionmindai ./helm/ActionMindAI -n actionmindai
```

The migration job will automatically:
- Skip already-applied migrations (checked via `schema_migrations` table)
- Apply only new migrations
- Track all applied migrations

## Troubleshooting Quick Reference

| Problem | Command |
|---------|---------|
| Check migration job status | `kubectl get jobs -n actionmindai -l component=migration` |
| View migration logs | `kubectl logs -n actionmindai job/actionmindai-db-migrate` |
| Re-run migrations | `kubectl delete job -n actionmindai actionmindai-db-migrate && helm upgrade actionmindai ./helm/ActionMindAI -n actionmindai` |
| Check applied migrations | `kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai -c "SELECT * FROM schema_migrations;"` |
| Verify database connectivity | `kubectl exec -n actionmindai deploy/postgres -- psql -U postgres -d actionmindai -c "SELECT 1;"` |

## Migration File Naming Convention

```
[three-digit number]_[description].sql

Examples:
001_create_tasks_conversations_messages.sql
002_add_conversation_title.sql
003_fix_uuid_to_varchar.sql
```

## What Happens During Helm Install

```
Timeline ( Helm Hook Weight: -5 ):

0s  ──► Init container: wait-for-db starts
       ├─ Waits for postgres:5432 to be ready
       └─ Retries every 5 seconds until connected

5s  ──► Main container: migrate starts
       ├─ Creates schema_migrations tracking table
       ├─ Checks which migrations are already applied
       ├─ Applies pending migrations in order
       └─ Records each successful migration

30s ──► Migration completes
       └─ Job marked as SUCCESSFUL

31s ──► Backend deployment starts
       └─ Only after migrations succeed
```

## Clean Slate (Reset Everything)

⚠️ **WARNING: This deletes all data**

```bash
# Delete everything
helm uninstall actionmindai -n actionmindai
kubectl delete secret actionmindai-secrets -n actionmindai
kubectl delete configmap actionmindai-migrations -n actionmindai

# Delete PVC (if using persistent storage)
kubectl delete pvc -n actionmindai -l app=postgres

# Re-install from scratch
helm install actionmindai ./helm/ActionMindAI -n actionmindai --create-namespace
```

## Production Checklist

- [ ] Use strong random secrets (generate with `openssl rand -base64 32`)
- [ ] Set `secrets.databaseUrl` with production PostgreSQL endpoint
- [ ] Enable TLS for ingress
- [ ] Configure resource limits based on load testing
- [ ] Set up database backups before migrations
- [ ] Test migrations in staging environment first
- [ ] Configure monitoring/alerting for migration jobs
