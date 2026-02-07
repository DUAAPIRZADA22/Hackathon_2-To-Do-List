# Data Model: Kubernetes Deployment Entities

**Feature**: 001-kubernetes-deployment
**Date**: 2026-01-26
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the Kubernetes entities and their relationships for deploying ActionMind AI to Minikube. These entities are implemented as Helm templates in `helm/ActionMindAI/templates/`.

## Entities

### 1. Namespace

**Name**: `ActionMindAI`
**Purpose**: Logical isolation of ActionMind AI resources

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ActionMindAI
  labels:
    app: ActionMindAI
    environment: development
```

---

### 2. Frontend Deployment

**Name**: `ActionMindAI-frontend`
**Purpose**: Manages Next.js frontend pods

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| replicas | 2 | High availability for local testing |
| image | ActionMindAI/frontend:latest | Built from frontend/Dockerfile |
| port | 3000 | Next.js default port |
| cpu.request | 100m | Minimum CPU reservation |
| cpu.limit | 500m | Maximum CPU allocation |
| memory.request | 128Mi | Minimum memory reservation |
| memory.limit | 512Mi | Maximum memory allocation |
| livenessProbe | N/A | Not configured (static serving) |
| readinessProbe | HTTP GET /:3000 | Traffic routing check |

**Relationships**:
- Uses `FrontendService` for internal networking
- Exposed via `Ingress` on `/` path
- Consumes `NEXT_PUBLIC_API_URL` from ConfigMap
- Consumes secrets if needed (none currently)

---

### 3. Backend Deployment

**Name**: `ActionMindAI-backend`
**Purpose**: Manages FastAPI backend pods

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| replicas | 2 | High availability for local testing |
| image | ActionMindAI/backend:latest | Built from backend/Dockerfile |
| port | 8000 | FastAPI default port |
| cpu.request | 200m | Minimum CPU reservation |
| cpu.limit | 1000m | Maximum CPU allocation |
| memory.request | 256Mi | Minimum memory reservation |
| memory.limit | 1Gi | Maximum memory allocation |
| livenessProbe | HTTP GET /health:8000 | Dead pod detection |
| readinessProbe | HTTP GET /health:8000 | Traffic routing check |

**Relationships**:
- Uses `BackendService` for internal networking
- Exposed via `Ingress` on `/api` path
- Consumes `DATABASE_URL` from Secret
- Consumes `OPENAI_API_KEY` from Secret
- Consumes `BETTER_AUTH_SECRET` from Secret
- Connects to external Neon PostgreSQL

---

### 4. Frontend Service

**Name**: `ActionMindAI-frontend`
**Purpose**: ClusterIP service for frontend pods

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| type | ClusterIP | Internal cluster communication |
| port | 3000 | Service port |
| targetPort | 3000 | Pod container port |
| selector | app: ActionMindAI-frontend | Pod label selector |

**Relationships**:
- Selects pods with label `app: ActionMindAI-frontend`
- Target of Ingress route for `/` path

---

### 5. Backend Service

**Name**: `ActionMindAI-backend`
**Purpose**: ClusterIP service for backend pods

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| type | ClusterIP | Internal cluster communication |
| port | 8000 | Service port |
| targetPort | 8000 | Pod container port |
| selector | app: ActionMindAI-backend | Pod label selector |

**Relationships**:
- Selects pods with label `app: ActionMindAI-backend`
- Target of Ingress route for `/api` path
- Called by frontend via `NEXT_PUBLIC_API_URL` environment variable

---

### 6. Application Secret

**Name**: `ActionMindAI-secrets`
**Purpose**: Sensitive configuration data

**Attributes**:
| Key | Source | Description |
|-----|--------|-------------|
| DATABASE_URL | Neon PostgreSQL | External database connection string |
| OPENAI_API_KEY | OpenAI | AI model API key |
| BETTER_AUTH_SECRET | Generated | JWT secret for authentication |

**Data Types**:
- DATABASE_URL: `postgresql://user:pass@host:port/database`
- OPENAI_API_KEY: `sk-xxxxxxxxxxxxx`
- BETTER_AUTH_SECRET: Random 32+ character string

**Relationships**:
- Mounted as environment variables in Backend Deployment
- NOT committed to git (use secrets.yaml.example as template)

---

### 7. ConfigMap

**Name**: `ActionMindAI-config`
**Purpose**: Non-sensitive configuration data

**Attributes**:
| Key | Value | Description |
|-----|-------|-------------|
| NEXT_PUBLIC_API_URL | http://ActionMindAI-backend:8000 | Backend API URL for frontend |

**Relationships**:
- Mounted as environment variable in Frontend Deployment
- Frontend uses this to call backend APIs

---

### 8. Ingress

**Name**: `ActionMindAI-ingress`
**Purpose**: External access routing

**Attributes**:
| Attribute | Value | Description |
|-----------|-------|-------------|
| className | nginx | Ingress controller type |
| host | ActionMindAI.local | Virtual hostname |

**Routes**:

| Path | PathType | Service | Port | Description |
|------|----------|---------|------|-------------|
| / | Prefix | ActionMindAI-frontend | 3000 | Frontend application |
| /api | Prefix | ActionMindAI-backend | 8000 | Backend API |

**Relationships**:
- Routes to Frontend Service and Backend Service
- Requires nginx ingress controller enabled in Minikube

---

## Entity Relationships Diagram

```
                    ┌──────────────────────────────────────┐
                    │         Ingress                      │
                    │   (ActionMindAI-ingress)             │
                    │   / → Frontend, /api → Backend        │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────┴───────────────────────┐
                    │                                      │
           ┌────────▼────────┐                   ┌────────▼────────┐
           │ Frontend Service │                   │ Backend Service  │
           │ (ClusterIP:3000) │                   │ (ClusterIP:8000) │
           └────────┬────────┘                   └────────┬────────┘
                    │                                      │
           ┌────────▼────────┐                   ┌────────▼────────┐
           │ Frontend Deploy │                   │ Backend Deploy  │
           │ (2 replicas)    │                   │ (2 replicas)    │
           │ 500m CPU        │                   │ 1000m CPU       │
           │ 512Mi RAM       │                   │ 1Gi RAM         │
           └─────────────────┘                   └────────┬────────┘
                                                       │
                                    ┌──────────────────┴─────────────────┐
                                    │                                      │
                            ┌───────▼────────┐                   ┌───────▼────────┐
                            │ Application    │                   │ External:       │
                            │ Secret         │                   │ Neon PostgreSQL │
                            │ (DB_URL,       │                   │                 │
                            │  API_KEY,      │                   │                 │
                            │  AUTH_SECRET)  │                   │                 │
                            └────────────────┘                   └─────────────────┘
```

---

## Pod Specifications

### Frontend Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ActionMindAI-frontend-xxxxx
  namespace: ActionMindAI
  labels:
    app: ActionMindAI-frontend
spec:
  containers:
  - name: frontend
    image: ActionMindAI/frontend:latest
    ports:
    - containerPort: 3000
    env:
    - name: NEXT_PUBLIC_API_URL
      valueFrom:
        configMapKeyRef:
          name: ActionMindAI-config
          key: NEXT_PUBLIC_API_URL
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 512Mi
    readinessProbe:
      httpGet:
        path: /
        port: 3000
      initialDelaySeconds: 10
      periodSeconds: 5
```

### Backend Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ActionMindAI-backend-xxxxx
  namespace: ActionMindAI
  labels:
    app: ActionMindAI-backend
spec:
  containers:
  - name: backend
    image: ActionMindAI/backend:latest
    ports:
    - containerPort: 8000
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: ActionMindAI-secrets
          key: DATABASE_URL
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: ActionMindAI-secrets
          key: OPENAI_API_KEY
    - name: BETTER_AUTH_SECRET
      valueFrom:
        secretKeyRef:
          name: ActionMindAI-secrets
          key: BETTER_AUTH_SECRET
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 1Gi
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
```

---

## State Transitions

### Pod Lifecycle States

1. **Pending** → Pod scheduled, pulling images
2. **ContainerCreating** → Images pulled, containers starting
3. **Running** → Containers running, health checks in progress
4. **Ready** → Readiness probe passing, receiving traffic
5. **Failed** → Liveness probe failing or container crash → **Restart**

### Deployment States

1. **Progressing** → Rolling update in progress
2. **Complete** → All replicas ready and updated
3. **Failed** → Deployment failed to progress

---

## Labels and Selectors

### Standard Labels

All resources use these labels for organization:

```yaml
app: ActionMindAI              # Application name
component: [frontend|backend]  # Component identifier
tier: [web|api]                # Architectural tier
environment: development       # Environment
```

### Pod Selectors

Services select pods using these label selectors:

```yaml
# Frontend Service
selector:
  app: ActionMindAI-frontend

# Backend Service
selector:
  app: ActionMindAI-backend
```

---

## Storage Requirements

### Persistent Volumes

**None required** - This deployment is stateless:
- Frontend serves static files from container image
- Backend stores state in external Neon PostgreSQL

### Temporary Storage

Each pod has default ephemeral storage for:
- Logs: stdout/stderr captured by Kubernetes
- Temp files: /tmp directory
- Cache: Node.js .next cache (already baked into image)

---

**Data Model Status**: ✅ COMPLETE
**Contract Definition**: See [contracts/kubernetes-entities.yaml](./contracts/kubernetes-entities.yaml)
