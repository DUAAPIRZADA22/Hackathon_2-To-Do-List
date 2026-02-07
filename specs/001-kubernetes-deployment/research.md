# Research & Technology Decisions: Local Kubernetes Deployment

**Feature**: 001-kubernetes-deployment
**Date**: 2026-01-26
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for containerizing and deploying ActionMind AI (Next.js frontend + FastAPI backend) to a local Minikube Kubernetes cluster.

## Research Findings

### R-001: Multi-stage Docker Build Patterns for Next.js 15

**Decision**: Use 3-stage build (deps → builder → runner) with node:22-alpine base

**Research Summary**:
- Next.js 15 supports `output: 'standalone'` mode which produces minimal production output
- Multi-stage builds reduce final image size by excluding build dependencies
- Alpine Linux provides the smallest base image for Node.js (≈180MB vs ≍250MB for slim)

**Key Patterns**:
```dockerfile
# Stage 1: Dependencies (cached layer)
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Builder
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runner (production)
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Alternatives Considered**:
- **Single-stage build**: Simpler but produces larger images (≈1GB+)
- **Static export**: Not suitable for Next.js App Router and API routes
- **Different base images**: node:22-slim (larger), custom Alpine (more maintenance)

---

### R-002: FastAPI Containerization with Python 3.13

**Decision**: Use 2-stage build with python:3.13-slim base

**Research Summary**:
- Python 3.13 slim provides good balance between size and compatibility
- Multi-stage build separates dependencies from application code
- Virtual environment isolation is recommended for production

**Key Patterns**:
```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.13-slim AS runner
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Alternatives Considered**:
- **python:3.13-alpine**: Smaller but some Python wheels lack Alpine musl binaries
- **UV package manager**: Faster installs but adds complexity and tooling dependency
- **Single-stage**: Simpler but larger images

---

### R-003: Next.js Standalone Output Mode Requirements

**Decision**: Enable `output: 'standalone'` in next.config.js

**Research Summary**:
- Standalone mode creates a `.next/standalone` directory with minimal runtime files
- Reduces production build from ~500MB to ~150MB
- Requires copying standalone output and static files separately in Dockerfile

**Configuration**:
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  // ... other config
}
```

**Implications**:
- Serverless-friendly output
- Minimal dependencies for production
- Slightly different file structure requires adjusted Dockerfile COPY commands

---

### R-004: Helm Chart Best Practices for Multi-Service Apps

**Decision**: Create single Helm chart with multiple deployment templates

**Research Summary**:
- Single chart simplifies deployment (one `helm install` command)
- Use values.yaml for environment-specific configuration
- Separate templates for deployments, services, ingress, secrets

**Structure**:
```
helm/ActionMindAI/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
├── secrets.yaml.example    # Secrets template (not in chart)
└── templates/
    ├── _helpers.tpl         # Template functions
    ├── namespace.yaml       # Namespace resource
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── configmap.yaml       # Non-sensitive config
    ├── secrets.yaml         # Secret template
    └── ingress.yaml         # Ingress routing
```

**Best Practices**:
- Use Helm template functions for reusability (`{{ include "common.labels" . }}`)
- Define resource limits in values.yaml for easy tuning
- Use liveness and readiness probes for all deployments
- Implement proper label selectors for service discovery

---

### R-005: Minikube Ingress Configuration Patterns

**Decision**: Use nginx ingress controller addon

**Research Summary**:
- Minikube includes nginx ingress as an addon
- Enables ingress with `minikube addons enable ingress`
- Routes traffic based on host/path rules

**Configuration**:
```yaml
# Enable ingress addon
minikube addons enable ingress

# Ingress resource
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ActionMindAI-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: ActionMindAI.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ActionMindAI-frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: ActionMindAI-backend
                port:
                  number: 8000
```

**Alternatives**:
- **Port-forward**: Simpler but not suitable for production-like testing
- **NodePort**: Works but exposes ports on all nodes
- **LoadBalancer**: Not supported in Minikube without additional setup

---

### R-006: Kubernetes Resource Limits for Node.js/Python

**Decision**: Set conservative limits suitable for local development

**Research Summary**:
- Resource limits prevent runaway containers from consuming all resources
- Requests enable Kubernetes to schedule pods appropriately
- Balance between resource availability and application needs

**Recommended Limits**:

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|------------|-----------|----------------|--------------|
| Frontend (Next.js) | 100m | 500m | 128Mi | 512Mi |
| Backend (FastAPI) | 200m | 1000m | 256Mi | 1Gi |

**Rationale**:
- Next.js builds are memory-intensive (~400MB peak during SSR)
- FastAPI with AI processing requires more CPU for inference
- Requests are 20-25% of limits to allow overprovisioning
- Sufficient for local development with 4 CPU / 8GB RAM

---

### R-007: Health Check Patterns for FastAPI/Next.js

**Decision**: Use HTTP-based liveness and readiness probes

**Research Summary**:
- Liveness probes detect dead containers and restart them
- Readiness probes determine when traffic can be sent to a pod
- HTTP probes are more reliable than TCP checks

**FastAPI Health Endpoint**:
```python
# Backend already has /health endpoint - reuse for probes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Probe Configuration**:
```yaml
# Backend (FastAPI)
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

# Frontend (Next.js)
readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Configuration Notes**:
- `initialDelaySeconds` gives app time to start (backend slower due to DB connections)
- `periodSeconds` balances responsiveness with API server load
- Frontend uses only readiness probe (liveness not as critical for static-serving)

## Technology Choices Summary

| Component | Technology | Justification |
|-----------|------------|---------------|
| Frontend Base Image | node:22-alpine | Smallest official Node.js image |
| Backend Base Image | python:3.13-slim | Size/compatibility balance |
| Package Manager | npm (frontend), pip (backend) | Standard tools |
| Next.js Output | standalone | Minimal production output |
| Container Registry | Minikube Docker daemon | Local testing, no registry needed |
| Ingress Controller | nginx (Minikube addon) | Pre-configured, widely used |
| Replicas | 2 per service | HA for local testing |
| Resource Limits | 500m/512Mi frontend, 1000m/1Gi backend | Balanced for local dev |
| Health Probes | HTTP readiness/liveness | Standard K8s pattern |

## Constraints Verification

| Constraint | Plan | Feasibility |
|------------|------|-------------|
| Image size < 500MB each | Multi-stage builds, Alpine bases | ✅ FEASIBLE - Alpine + standalone = ~200MB |
| Build time < 5 min | Layer caching, minimal dependencies | ✅ FEASIBLE - Cached deps speeds rebuilds |
| Minikube startup < 3 min | Docker driver, 4 CPU/8GB RAM | ✅ FEASIBLE - Typical startup: 1-2 min |
| Pod readiness < 5 min | Optimized probes, resource limits | ✅ FEASIBLE - Cold start: ~30-60 sec |
| Full deploy < 20 min | Optimized workflow, parallel builds | ✅ FEASIBLE - End-to-end: ~10-15 min |

## Open Questions Resolved

1. **Q: Should we use UV package manager for Python?**
   - **A**: No - standard pip is sufficient and adds no external tool dependency

2. **Q: Should we enable Dapr integration?**
   - **A**: No - out of scope for local deployment, adds complexity

3. **Q: Should we use HPA (Horizontal Pod Autoscaler)?**
   - **A**: No - out of scope for local development, fixed 2 replicas sufficient

4. **Q: Should we implement Prometheus monitoring?**
   - **A**: No - out of scope for this phase, metrics-server sufficient for basic monitoring

5. **Q: Should we use production container registry?**
   - **A**: No - Minikube Docker daemon eliminates registry need for local testing

## AIOps Tool Research

The following AIOps tools will be documented in implementation:

### Gordon (Docker AI)
- Purpose: Dockerfile optimization and best practices
- Commands to document:
  - `docker ai "optimize this Dockerfile for smaller image size"`
  - `docker ai "what base image is best for Next.js production in 2025"`
  - `docker ai "create multi-stage build for Python FastAPI"`

### kubectl-ai
- Purpose: Kubernetes manifest generation and troubleshooting
- Commands to document:
  - `kubectl-ai "create helm chart for Next.js frontend and FastAPI backend"`
  - `kubectl-ai "generate deployment with resource limits and health probes"`
  - `kubectl-ai "verify all pods are running and healthy"`

### Kagent
- Purpose: Cluster health analysis and optimization
- Commands to document:
  - `kagent "analyze cluster health and identify issues"`
  - `kagent "check resource utilization in ActionMindAI namespace"`
  - `kagent "verify service connectivity between frontend and backend"`

---

**Research Status**: ✅ COMPLETE
**Next Phase**: Phase 1 - Design & Contracts (data-model.md, contracts/, quickstart.md)
