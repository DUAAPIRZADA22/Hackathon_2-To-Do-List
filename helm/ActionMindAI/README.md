# ActionMindAI Helm Chart

Production-ready Helm chart for deploying ActionMindAI (Next.js frontend + FastAPI backend) to Kubernetes clusters.

## Quick Start

```bash
# Install the chart
helm install actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --create-namespace

# Upgrade the chart
helm upgrade actionmindai ./helm/ActionMindAI \
  --namespace actionmindai
```

## Prerequisites

- Kubernetes 1.23+
- Helm 3.x
- Ingress controller (nginx recommended)
- PostgreSQL database (external or managed)
- OpenAI API key

## Installation

### Step 1: Clone and Configure

```bash
# Copy secrets example
cp helm/ActionMindAI/secrets.yaml.example helm/ActionMindAI/secrets.yaml

# Edit with your values (NEVER commit this file)
nano helm/ActionMindAI/secrets.yaml
```

### Step 2: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace actionmindai

# Create secret
kubectl create secret generic actionmindai-secrets \
  --from-literal=databaseUrl='postgresql://user:password@host:5432/actionmindai' \
  --from-literal=openaiApiKey='sk-your-openai-key' \
  --from-literal=betterAuthSecret='your-secret' \
  --namespace actionmindai
```

### Step 3: Install Chart

```bash
helm install actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --create-namespace
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n actionmindai

# Check services
kubectl get svc -n actionmindai

# Check ingress
kubectl get ingress -n actionmindai
```

## Configuration

### Required Values

| Parameter | Description | Example |
|-----------|-------------|---------|
| `secrets.databaseUrl` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `secrets.openaiApiKey` | OpenAI API key | `sk-proj-...` |
| `secrets.betterAuthSecret` | Auth session secret | Generate with `openssl rand -base64 32` |

### Optional Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `namespace` | Kubernetes namespace | `ActionMindAI` |
| `frontend.replicaCount` | Frontend replica count | `2` |
| `backend.replicaCount` | Backend replica count | `2` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `backend.image.tag` | Backend image tag | `latest` |
| `frontend.autoscaling.enabled` | Enable HPA for frontend | `false` |
| `backend.autoscaling.enabled` | Enable HPA for backend | `false` |
| `ingress.host` | Ingress host | `ActionMindAI.local` |

See [values.yaml](values.yaml) for all configuration options.

## Deployment Components

The chart deploys the following Kubernetes resources:

### Core Resources

- **Namespace**: `actionmindai`
- **ServiceAccount**: `actionmindai`
- **ConfigMap**: Backend non-sensitive configuration
- **Secret**: `actionmindai-secrets` (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)

### Frontend (Next.js)

- **Deployment**: 2 replicas, resource limits 500m CPU / 512Mi RAM
- **Service**: ClusterIP on port 3000
- **PodDisruptionBudget**: minAvailable: 1
- **HPA**: Available (disabled by default)

### Backend (FastAPI)

- **Deployment**: 2 replicas, resource limits 1000m CPU / 1Gi RAM
- **Service**: ClusterIP on port 8000
- **PodDisruptionBudget**: minAvailable: 1
- **HPA**: Available (disabled by default)

### Networking

- **Ingress**: nginx class, routes `/` → frontend, `/api` → backend
- **TLS**: Optional (configure with cert-manager)

## Security Features

- ✅ Non-root user execution (UID 1000/1001)
- ✅ Security contexts configured
- ✅ Secrets via Kubernetes (not in values)
- ✅ Resource limits defined
- ✅ Privilege escalation disabled
- ✅ Read-only root filesystem (frontend)

## Upgrade

```bash
# Upgrade with new values
helm upgrade actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --set frontend.image.tag=v1.2.0 \
  --set backend.image.tag=v1.2.0

# Or upgrade with custom values file
helm upgrade actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --values helm/ActionMindAI/secrets.yaml
```

## Rollback

```bash
# View revision history
helm history actionmindai -n actionmindai

# Rollback to previous version
helm rollback actionmindai 1 -n actionmindai
```

## Uninstall

```bash
# Uninstall the release
helm uninstall actionmindai -n actionmindai

# Delete namespace
kubectl delete namespace actionmindai
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n actionmindai
kubectl describe pod <pod-name> -n actionmindai
```

### View Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -n actionmindai

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -n actionmindai

# Follow logs
kubectl logs -l app.kubernetes.io/component=backend -n actionmindai -f
```

### Port Forward for Debugging

```bash
# Backend to localhost:8000
kubectl port-forward -n actionmindai svc/actionmindai-backend 8000:8000

# Frontend to localhost:3000
kubectl port-forward -n actionmindai svc/actionmindai-frontend 3000:3000
```

### Exec into Container

```bash
# Backend shell
kubectl exec -it -n actionmindai deployment/actionmindai-backend -- /bin/sh

# Frontend shell
kubectl exec -it -n actionmindai deployment/actionmindai-frontend -- /bin/sh
```

## Documentation

- [Minikube Deployment Guide](docs/minikube-deployment.md) - Local development setup
- [Production Checklist](docs/production-checklist.md) - Production readiness verification
- [AIOps Documentation](docs/aiops.md) - Gordon and kubectl-ai commands

## Architecture

```
                    ┌─────────────────┐
                    │   Ingress       │
                    │   (nginx)       │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │                              │
              ▼                              ▼
    ┌─────────────────┐          ┌─────────────────┐
    │   Frontend      │          │    Backend      │
    │   (Next.js)     │◄─────────►│   (FastAPI)     │
    │   Port: 3000    │  /api    │   Port: 8000    │
    └─────────────────┘          └────────┬────────┘
                                           │
                                           ▼
                                   ┌───────────────┐
                                   │   PostgreSQL  │
                                   │  (External)   │
                                   └───────────────┘
```

## Contributing

When modifying the Helm chart:

1. Test with `helm lint`
2. Validate with `helm template --debug`
3. Update this README
4. Update relevant documentation in `docs/`

## License

Proprietary - All rights reserved
