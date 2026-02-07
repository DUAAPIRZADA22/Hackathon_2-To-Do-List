---
id: 001
title: kubernetes-deployment-spec
stage: spec
date: 2026-01-26
surface: agent
model: glm-4.6
feature: 001-kubernetes-deployment
branch: 001-kubernetes-deployment
user: acer
command: /sp.specify
labels: ["kubernetes","deployment","docker","helm","minikube"]
links:
  spec: specs/001-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-kubernetes-deployment/spec.md
  - specs/001-kubernetes-deployment/checklists/requirements.md
tests: []
---

## Prompt

# Phase 4: ActionMind AI Local Kubernetes Deployment - Complete Implementation Prompt

You are acting as the **Cloud-Native DevOps Engineer** for ActionMind AI. Your goal is to containerize and deploy the ActionMind AI  application to a local Kubernetes cluster using Minikube.

---

## Context

We are implementing **Phase IV: Local Kubernetes Deployment** of theActionMind AI Hackathon.
The full-stack application (Next.js frontend + FastAPI backend) is already built and working locally.
This phase focuses on **containerization, Helm chart creation, and Minikube deployment**.

**Hackathon Points:** 250 pts
**Deadline:** January 18, 2026

---

## MANDATORY: Use Cloud-Native Blueprints Skill

Before any implementation, **READ AND APPLY** the cloud-native-blueprints skill:
```
@.claude/skills/cloud-native-blueprints/SKILL.md
```

This skill contains:
- Helm chart templates and structure
- Dapr component configurations
- AIOps command patterns (kubectl-ai, kagent, Gordon)
- Production-ready deployment patterns

**Use the templates from:**
- `@.claude/skills/cloud-native-blueprints/assets/templates/` for Helm chart YAML files
- `@.claude/skills/cloud-native-blueprints/assets/components/` for Dapr configurations
- `@.claude/skills/cloud-native-blueprints/references/` for best practices

---

## MANDATORY: Research First

Before implementing, use MCP tools for research:

**For Library/Framework Documentation:**
```
context7 resolve-library-id "helm" → get-library-docs
context7 resolve-library-id "kubernetes" → get-library-docs
```

**For Best Practices and Troubleshooting:**
```
tavily search "Docker multi-stage build FastAPI Python 3.13 2025"
tavily search "Next.js standalone Docker Kubernetes deployment"
tavily search "Minikube Helm deployment best practices"
```

---

## Current State Analysis

### Application Architecture
| Component | Technology | Port | Status |
|-----------|------------|------|--------|
| Frontend | Next.js 14 | 3000 | ✅ Running locally |
| Backend | FastAPI | 8000 | ✅ Running locally |
| Database | Neon PostgreSQL | External | ✅ Connected |

### Existing Files
| File | Location | Status |
|------|----------|--------|
| Backend Dockerfile | `ActionMindAI/backend/Dockerfile` | ⚠️ Needs optimization |
| Frontend Dockerfile | `ActionMindAI//frontend/Dockerfile` | ❌ Missing |
| next.config.ts | `ActionMindAI/frontend/next.config.ts` | ⚠️ Needs `output: 'standalone'` |
| Helm charts | `helm/ActionMindAI/` | ❌ Missing |

---

## Hackathon Requirements (250 pts)

| Requirement | Implementation | AIOps Tool |
|-------------|----------------|------------|
| Containerize frontend and backend | Multi-stage Dockerfiles | **Gordon** |
| Use Docker AI Agent (Gordon) | Document all `docker ai` commands | **Gordon** |
| Create Helm charts for deployment | Generate with AI assistance | **kubectl-ai** |
| Use kubectl-ai for K8s operations | Document all commands | **kubectl-ai** |
| Use Kagent for cluster analysis | Document usage | **Kagent** |
| Deploy on Minikube locally | Full stack deployment | All tools |

---

## Implementation Tasks

### Part 1: Docker Containerization (Use Gordon)

#### Task 1.1: Frontend Dockerfile

**File:** `ActionMindAI/frontend/Dockerfile` (CREATE)

**Requirements:**
- Multi-stage build for smaller image
- Node.js 22 Alpine base
- Next.js standalone output mode
- Non-root user for security
- Optimized layer caching

**Gordon Commands to Run and Document:**
```bash
docker ai "create optimized Dockerfile for Next.js 14 standalone production build"
docker ai "what base image is best for Next.js production in 2025"
docker ai "optimize this Dockerfile for smaller image size"
```

**Expected Dockerfile Structure:**
```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Builder
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Runner
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

#### Task 1.2: Update Next.js Config

**File:** `ActionMindAI/frontend/next.config.ts` (MODIFY)

Add to the config object:
```typescript
output: 'standalone',
```

This enables the optimized standalone build for Docker.

#### Task 1.3: Backend Dockerfile Optimization

**File:** `ActionMindAI/backend/Dockerfile` (MODIFY)

**Gordon Commands to Run and Document:**
```bash
docker ai "optimize this FastAPI Dockerfile for production"
docker ai "create multi-stage build for Python 3.13 uv package manager"
```

**Requirements:**
- Multi-stage build
- Python 3.13 slim base
- UV package manager for fast installs
- Non-root user
- Health check endpoint

#### Task 1.4: Create .dockerignore Files

**Files to Create:**
- `ActionMindAI/frontend/.dockerignore`
- `ActionMindAI/backend/.dockerignore`

```
node_modules/
.next/
*.log
.env.local
.git/
```

---

### Part 2: Helm Chart Creation (Use kubectl-ai)

#### Task 2.1: Initialize Helm Chart Structure

**Directory:** `helm/ActionMindAI/`

**kubectl-ai Commands to Run and Document:**
```bash
kubectl-ai "create helm chart structure for a Next.js frontend and FastAPI backend"
kubectl-ai "generate values.yaml for multi-container deployment"
```

**Required Structure:**
```
helm/ActionMindAI/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── namespace.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   └── ingress.yaml
```

#### Task 2.2: Chart.yaml

**File:** `helm/ActionMindAI/Chart.yaml`

```yaml
apiVersion: v2
name: ActionMindAI
description: ActionMindAI - Full-Stack Application
version: 1.0.0
appVersion: "1.0"
type: application
keywords:
  - ActionMindAI
  - agency
  - task-management
```

#### Task 2.3: values.yaml

**File:** `helm/ActionMindAI/values.yaml`

```yaml
namespace: ActionMindAI

frontend:
  name: ActionMindAI-frontend
  replicaCount: 2
  image:
    repository: ActionMindAI/frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  env:
    NEXT_PUBLIC_API_URL: "http://ActionMindAI-backend:8000"

backend:
  name: ActionMindAI-backend
  replicaCount: 2
  image:
    repository: ActionMindAI/backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 200m
      memory: 256Mi

secrets:
  databaseUrl: ""  # Set via --set or secrets file
  openaiApiKey: ""
  betterAuthSecret: ""

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: ActionMindAI.local
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
```

#### Task 2.4: Deployment Templates

Use templates from `@.claude/skills/cloud-native-blueprints/assets/templates/`

**Create:**
- `templates/frontend-deployment.yaml`
- `templates/backend-deployment.yaml`
- `templates/frontend-service.yaml`
- `templates/backend-service.yaml`

Include:
- Proper labels and selectors
- Resource limits
- Health probes (liveness/readiness)
- Environment variables from ConfigMap/Secrets

#### Task 2.5: Secrets Template

**File:** `helm/ActionMindAI/templates/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ActionMindAI-secrets
  namespace: {{ .Values.namespace }}
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | quote }}
```

---

### Part 3: Minikube Deployment

#### Task 3.1: Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster status
minikube status
```

#### Task 3.2: Build Images in Minikube

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
cd ActionMindAI/backend
docker build -t ActionMindAI/backend:latest .

# Build frontend image
cd ../frontend
docker build -t ActionMindAI/frontend:latest .

# Verify images
docker images | grep ActionMindAI
```

#### Task 3.3: Deploy with Helm

**kubectl-ai Commands to Run and Document:**
```bash
kubectl-ai "install helm chart from ./helm/ActionMindAI to namespace ActionMindAI"
kubectl-ai "verify all pods are running in ActionMindAI namespace"
```

**Manual Commands:**
```bash
# Create secrets file (do not commit!)
cat > helm/ActionMindAI/secrets.yaml << EOF
secrets:
  databaseUrl: "postgresql://user:pass@host/db"
  openaiApiKey: "sk-..."
  betterAuthSecret: "your-secret-here"
EOF

# Install Helm chart
helm install ActionMindAI ./helm/ActionMindAI \
  --namespace ActionMindAI \
  --create-namespace \
  -f helm/ActionMindAI/secrets.yaml

# Verify deployment
kubectl get pods -n ActionMindAI
kubectl get services -n ActionMindAI
```

#### Task 3.4: Access Application

```bash
# Get Minikube IP
minikube ip

# Add to hosts file (optional)
echo "$(minikube ip) ActionMindAI.local" | sudo tee -a /etc/hosts

# Or use minikube service
minikube service ActionMindAI-frontend -n ActionMindAI
```

---

### Part 4: Cluster Analysis (Use Kagent)

#### Task 4.1: Health Check

**Kagent Commands to Run and Document:**
```bash
kagent "analyze the cluster health and identify any issues"
kagent "check resource utilization in ActionMindAI namespace"
kagent "verify service connectivity between frontend and backend"
```

#### Task 4.2: Optimization Suggestions

```bash
kagent "suggest optimizations for the ActionMindAI deployment"
kagent "identify any security concerns in current configuration"
```

---

## AIOps Documentation Requirement

**CRITICAL:** Document ALL AIOps commands used in a file:

**File:** `docs/PHASE4-AIOPS-COMMANDS.md`

```markdown
# Phase 4: AIOps Commands Documentation

## Docker AI (Gordon)

### Commands Used
| Command | Purpose | Result |
|---------|---------|--------|
| `docker ai "optimize this Dockerfile"` | Image optimization | Reduced size by X% |
| ... | ... | ... |

## kubectl-ai

### Commands Used
| Command | Purpose | Result |
|---------|---------|--------|
| `kubectl-ai "deploy backend with 2 replicas"` | Initial deployment | Created deployment |
| ... | ... | ... |

## Kagent

### Commands Used
| Command | Purpose | Result |
|---------|---------|--------|
| `kagent "analyze cluster health"` | Health check | All systems healthy |
| ... | ... | ... |
```

---

## Success Criteria

### Containerization
- [ ] Frontend Dockerfile created with multi-stage build
- [ ] Backend Dockerfile optimized
- [ ] `next.config.ts` has `output: 'standalone'`
- [ ] Both images build successfully
- [ ] Images are under 500MB each

### Helm Charts
- [ ] Chart structure created
- [ ] `values.yaml` properly configured
- [ ] All templates render without errors (`helm template`)
- [ ] Chart passes linting (`helm lint`)

### Minikube Deployment
- [ ] Minikube cluster running
- [ ] All pods in Running state
- [ ] Services accessible via port-forward or ingress
- [ ] Frontend can communicate with backend
- [ ] Backend can connect to Neon database

### AIOps Documentation
- [ ] All Gordon commands documented
- [ ] All kubectl-ai commands documented
- [ ] All Kagent commands documented
- [ ] Results and outcomes recorded

---

## Verification Steps

### 1. Validate Dockerfiles
```bash
cd ActionMindAI-web/backend && docker build -t ActionMindAI/backend:test .
cd ActionMindAI-web/frontend && docker build -t ActionMindAI/frontend:test .
```

### 2. Validate Helm Chart
```bash
helm lint ./helm/ActionMindAI
helm template ActionMindAI ./helm/ActionMindAI --debug
```

### 3. Verify Running Application
```bash
# Check pods
kubectl get pods -n ActionMindAI

# Check logs
kubectl logs -l app=ActionMindAI-frontend -n ActionMindAI
kubectl logs -l app=ActionMindAI-backend -n ActionMindAI

# Test health endpoints
kubectl port-forward svc/ActionMindAI-backend 8000:8000 -n ActionMindAI
curl http://localhost:8000/health

# Test frontend
kubectl port-forward svc=ActionMindAI-frontend 3000:3000 -n ActionMindAI
# Open http://localhost:3000 in browser
```

---

## Files to Create/Modify

| Action | File | Description |
|--------|------|-------------|
| CREATE | `ActionMindAI-web/frontend/Dockerfile` | Multi-stage Next.js build |
| MODIFY | `ActionMindAI-web/frontend/next.config.ts` | Add `output: 'standalone'` |
| MODIFY | `ActionMindAI-web/backend/Dockerfile` | Optimize for production |
| CREATE | `helm/ActionMindAI/Chart.yaml` | Ch

## Response snapshot

Successfully created feature specification for "Local Kubernetes Deployment" with the following key components:

1. **Feature Branch Created**: `001-kubernetes-deployment`

2. **User Stories Defined** (4 prioritized stories):
   - **P1 - Containerize Application**: Multi-stage Dockerfiles for frontend and backend
   - **P2 - Deploy to Minikube**: Helm chart deployment to local cluster
   - **P3 - Access Deployed Application**: Service access verification
   - **P4 - Monitor Cluster Health**: Health checks and monitoring

3. **Functional Requirements**: 37 requirements (FR-001 through FR-037) covering:
   - Docker containerization (image sizes, multi-stage builds, security)
   - Helm chart configuration (metadata, templates, validation)
   - Kubernetes deployment (replicas, resources, probes, services)
   - Cluster operations (Minikube commands, deployment, access)
   - Health and monitoring (endpoints, probes, metrics, logs)

4. **Success Criteria**: 13 measurable outcomes including:
   - Image build times (<5 min combined)
   - Image sizes (<500MB each)
   - Cluster startup (<3 min)
   - Pod readiness (<5 min)
   - Full deployment (<20 min)

5. **Additional Sections**:
   - Out of Scope (production deployment, CI/CD, observability)
   - Dependencies (Minikube, Docker, Helm, kubectl, Neon DB, OpenAI)
   - Assumptions (resources, connectivity, permissions)
   - Risks & Mitigations (8 identified risks with mitigation strategies)
   - AIOps Tool Requirements (Gordon, kubectl-ai, Kagent documentation)

## Outcome

- ✅ Impact: Complete specification created for Phase 4 Kubernetes deployment covering containerization, Helm charts, and Minikube deployment
- 🧪 Tests: No tests run (spec phase)
- 📁 Files: Created spec.md and requirements checklist
- 🔁 Next prompts: `/sp.plan` to create architectural plan
- 🧠 Reflection: Specification is comprehensive with clear prioritization. All requirements are testable and success criteria are measurable. No [NEEDS CLARIFICATION] markers needed as requirements were well-defined in the prompt.

## Evaluation notes (flywheel)

- Failure modes observed: None. Script completed successfully after initial parameter issue was bypassed.
- Graders run and results (PASS/FAIL): Checklist validation PASSED all items
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - spec is complete and ready for planning phase
