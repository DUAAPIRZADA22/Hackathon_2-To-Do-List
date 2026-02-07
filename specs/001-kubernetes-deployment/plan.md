# Implementation Plan: Local Kubernetes Deployment

**Branch**: `001-kubernetes-deployment` | **Date**: 2026-01-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-kubernetes-deployment/spec.md`

## Summary

Containerize the ActionMind AI full-stack application (Next.js frontend + FastAPI backend) and deploy to a local Minikube Kubernetes cluster. The solution includes multi-stage Dockerfiles, Helm charts for orchestration, and comprehensive deployment documentation with AIOps tool integration (Gordon, kubectl-ai, Kagent).

**Primary Requirements**:
- Docker images under 500MB each using multi-stage builds
- Helm charts with 2 replicas, resource limits, and health probes
- Minikube deployment with ingress and monitoring
- Full deployment in under 20 minutes

**Technical Approach**:
- Use Alpine-based images for minimal size
- Configure Next.js standalone output for containerization
- Implement proper Kubernetes resource management
- Document AIOps command patterns for reproducibility

## Technical Context

**Language/Version**:
- Frontend: Node.js 22, Next.js 15, TypeScript
- Backend: Python 3.13, FastAPI 0.104+

**Primary Dependencies**:
- Frontend: React 19, @openai/chatkit-react, axios, recharts
- Backend: uvicorn, sqlmodel, OpenAI SDK, MCP Python SDK, python-jose, passlib

**Storage**:
- External: Neon PostgreSQL (managed cloud database)
- Internal: None (no persistent volumes required)

**Testing**:
- Container: Docker build/run validation
- K8s: `helm lint`, `helm template`, pod readiness checks
- Integration: Health endpoint validation, service connectivity

**Target Platform**:
- Local: Minikube with Docker driver
- Future: AWS EKS, GKE, or AKS (out of scope for this phase)

**Project Type**: Web (frontend + backend)

**Performance Goals**:
- Image build time: < 5 minutes combined
- Cluster startup: < 3 minutes
- Pod readiness: < 5 minutes post-install
- Health check response: < 2 seconds

**Constraints**:
- Image size: < 500MB each
- Resource limits: 500m CPU / 512Mi RAM (frontend), 1000m CPU / 1Gi RAM (backend)
- Development machine: 8GB RAM, 4 CPU cores minimum

**Scale/Scope**:
- 2 replicas per service for HA
- Single namespace deployment
- 2 services (frontend, backend)
- 1 ingress controller
- Local development/testing only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Applicability

The constitution primarily governs CLI application development (Phase 1 CLI scope). This Kubernetes deployment feature is infrastructure/DevOps focused, not a CLI application. However, we evaluate relevant principles:

### Principle Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | All work references spec.md functional requirements (FR-001 through FR-037) |
| II. MCP-First Architecture | N/A | Infrastructure feature - no MCP operations required |
| III. Context Verification | N/A | No MCP operations to verify |
| IV. Scope Boundaries | ✅ PASS | Strictly within scope: local Minikube deployment only. No production, CI/CD, or advanced observability |
| V. SOLID Principles | ✅ PASS | Helm templates follow modular design, separation of concerns |
| VI. DRY | ✅ PASS | Reusable Helm templates, shared configuration patterns |
| VII. Modularity | ✅ PASS | Separate Dockerfiles, Helm charts, and deployment scripts |
| VIII. User Experience Standards | N/A | Infrastructure feature - no CLI UX required |

### Deviations Requiring Justification

**None** - All applicable principles are satisfied.

### Complexity Tracking

> No violations to justify - section omitted.

## Project Structure

### Documentation (this feature)

```text
specs/001-kubernetes-deployment/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (/sp.plan output) - IN PROGRESS
├── research.md          # Phase 0 output - TO BE CREATED
├── data-model.md        # Phase 1 output - TO BE CREATED
├── quickstart.md        # Phase 1 output - TO BE CREATED
├── contracts/           # Phase 1 output - TO BE CREATED
│   └── kubernetes-entities.yaml  # K8s resource definitions
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (COMPLETE)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py          # FastAPI application entry
│   ├── models/          # Database models
│   ├── api/             # API endpoints
│   ├── agent/           # AI agent logic
│   ├── auth/            # Authentication middleware
│   └── db/              # Database session
├── Dockerfile           # TO BE CREATED - multi-stage build
├── .dockerignore        # TO BE CREATED
└── requirements.txt     # Existing - Python dependencies

frontend/
├── src/
│   ├── app/             # Next.js pages
│   └── components/      # React components
├── Dockerfile           # TO BE CREATED - multi-stage build
├── .dockerignore        # TO BE CREATED
├── next.config.js       # TO BE MODIFIED - add standalone output
├── package.json         # Existing - Node dependencies
└── tsconfig.json        # Existing - TypeScript config

helm/ActionMindAI/       # TO BE CREATED - Helm chart
├── Chart.yaml           # Helm chart metadata
├── values.yaml          # Configuration values
├── secrets.yaml.example # Template for secrets (not committed)
└── templates/
    ├── _helpers.tpl     # Template helpers
    ├── namespace.yaml   # Namespace definition
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── configmap.yaml   # Non-sensitive config
    ├── secrets.yaml     # Sensitive data
    └── ingress.yaml     # External access

docs/
└── PHASE4-AIOPS-COMMANDS.md  # TO BE CREATED - AIOps tool documentation
```

**Structure Decision**: This is a web application with existing frontend (Next.js) and backend (FastAPI) directories. The Kubernetes infrastructure will be added as a new `helm/` directory at the repository root, following Kubernetes best practices for multi-service applications. Docker files will be added to each service directory.

## Phase 0: Research & Technology Decisions

### Research Tasks

| # | Task | Status | Output |
|---|------|--------|--------|
| R-001 | Multi-stage Docker build patterns for Next.js 15 | PENDING | research.md |
| R-002 | FastAPI containerization with Python 3.13 | PENDING | research.md |
| R-003 | Next.js standalone output mode requirements | PENDING | research.md |
| R-004 | Helm chart best practices for multi-service apps | PENDING | research.md |
| R-005 | Minikube ingress configuration patterns | PENDING | research.md |
| R-006 | Kubernetes resource limits for Node.js/Python | PENDING | research.md |
| R-007 | Health check patterns for FastAPI/Next.js | PENDING | research.md |

### Decisions Log

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|-------------------------|
| Frontend base image | node:22-alpine | Smallest image size, official Node.js image | node:22-slim (larger), alpine-based custom builds (more maintenance) |
| Backend base image | python:3.13-slim | Official Python image, good balance of size and compatibility | python:3.13-alpine (compatibility issues with some wheels), scratch (too complex) |
| Package manager | npm (frontend), pip (backend) | Standard tools, good compatibility | yarn/pnpm (not required), uv (backend - added complexity) |
| Next.js output mode | standalone | Minimal production output, optimized for containers | export (static only), default (too large) |
| Container registry | Minikube Docker daemon | Local testing, no registry needed | Docker Hub, ECR, GCR (out of scope for local deployment) |
| Ingress controller | nginx (Minikube addon) | Pre-configured in Minikube, widely used | Traefik, Contour (additional setup required) |
| Replicas | 2 per service | HA for local testing, reasonable resource usage | 1 (no HA), 3+ (too resource-intensive for local) |
| Resource limits | 500m/512Mi frontend, 1000m/1Gi backend | Balanced for local development, prevents resource exhaustion | Unlimited (risk of OOM), higher (requires more machine resources) |
| Health probes | HTTP readiness/liveness | Standard Kubernetes pattern, reliable | TCP (less reliable), exec (higher overhead) |

## Phase 1: Design & Contracts

### Data Model

**Kubernetes Entities** - See [contracts/kubernetes-entities.yaml](./contracts/kubernetes-entities.yaml)

Key entities:
- **FrontendDeployment**: Manages Next.js pods (replicas: 2, resources: 500m CPU / 512Mi RAM)
- **BackendDeployment**: Manages FastAPI pods (replicas: 2, resources: 1000m CPU / 1Gi RAM)
- **FrontendService**: ClusterIP on port 3000
- **BackendService**: ClusterIP on port 8000
- **ApplicationSecret**: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET
- **Ingress**: Routes / to frontend, /api to backend

### API Contracts

**Kubernetes API Contract** - See [contracts/kubernetes-entities.yaml](./contracts/kubernetes-entities.yaml)

All Kubernetes resources follow standard API conventions:
- API version: apps/v1 (deployments), v1 (services, secrets, ingress)
- Kind: Deployment, Service, Secret, Ingress
- Metadata: labels, annotations for organization
- Spec: replicas, selector, template, ports

### Quickstart

See [quickstart.md](./quickstart.md) for:
- Prerequisites installation (Docker, Minikube, Helm, kubectl)
- Environment setup
- Image building instructions
- Cluster deployment steps
- Troubleshooting common issues

## Implementation Phases

### Phase 0: Research (OUTPUT: research.md)

**Deliverables**:
- research.md with all technology decisions and rationale
- Verification that all constraints are achievable

**Tasks**:
1. Document Next.js containerization patterns
2. Document FastAPI containerization patterns
3. Research Helm chart structure for multi-service apps
4. Verify Minikube ingress configuration
5. Document health check patterns

### Phase 1: Design & Contracts (OUTPUT: data-model.md, contracts/, quickstart.md)

**Deliverables**:
- data-model.md: Kubernetes entities and relationships
- contracts/kubernetes-entities.yaml: Resource definitions
- quickstart.md: Deployment guide

**Tasks**:
1. Define Kubernetes deployment specifications
2. Create service and ingress configurations
3. Document quickstart procedure
4. Define AIOps command patterns

### Phase 2: Implementation (OUTPUT: Code changes via /sp.tasks)

**Deliverables**:
- frontend/Dockerfile: Multi-stage build
- backend/Dockerfile: Multi-stage build
- frontend/.dockerignore: Build optimization
- backend/.dockerignore: Build optimization
- frontend/next.config.js: Add standalone output
- helm/ActionMindAI/: Complete Helm chart
- docs/PHASE4-AIOPS-COMMANDS.md: AIOps documentation

**Tasks**:
1. Create frontend Dockerfile with multi-stage build
2. Create backend Dockerfile with multi-stage build
3. Create .dockerignore files
4. Update next.config.js for standalone output
5. Create Helm chart structure
6. Create Helm templates (deployments, services, ingress, secrets)
7. Create quickstart guide
8. Document AIOps commands
9. Validate deployment end-to-end

## Success Criteria Validation

From spec.md, verify:

| Criterion | Plan Address | Validation |
|-----------|--------------|------------|
| SC-001: Images build < 5 min | Multi-stage builds, Alpine bases | `time docker build` |
| SC-002: Frontend < 500MB | Node:22-alpine, standalone output | `docker images` |
| SC-003: Backend < 500MB | Python:3.13-slim, multi-stage | `docker images` |
| SC-004: Helm lint passes | Template validation | `helm lint` |
| SC-005: Minikube < 3 min startup | Resource allocation, Docker driver | `time minikube start` |
| SC-006: Pods running < 5 min | Quick health checks, proper images | `kubectl get pods -w` |
| SC-007: Accessible < 10 min | Ingress configuration, port-forward | `minikube service` |
| SC-008: Health checks < 2 min | Probe configuration | `kubectl describe pod` |
| SC-009: Frontend→Backend comms | Service discovery, env vars | Integration test |
| SC-010: Backend→DB connection | External DB configuration | Connection test |
| SC-011: Resources within limits | Resource requests/limits | `kubectl top pods` |
| SC-012: Logs accessible | Standard output logging | `kubectl logs` |
| SC-013: Full deploy < 20 min | Optimized workflow | End-to-end timing |

## Risk Management

### Technical Risks

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| Image size exceeds 500MB | Multi-stage builds, Alpine bases, .dockerignore | Analyze layers, remove dependencies |
| Minikube fails to start | Document resource requirements clearly | Provide troubleshooting guide |
| Health probe failures | Configure appropriate delays/periods | Adjust probe values based on startup time |
| Ingress not available | Provide port-forward alternative | Document fallback access method |
| Database connection issues | Test connectivity before deployment | Provide connection validation commands |

### Execution Risks

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| Insufficient machine resources | Clear documentation of requirements | Suggest cloud-based alternatives |
| Helm chart errors | lint/template validation before deploy | Provide step-by-step validation |
| Environment configuration gaps | Example secrets file with documentation | Comprehensive .env setup guide |

## Next Steps

1. **Execute Phase 0**: Generate research.md with technology decisions
2. **Execute Phase 1**: Generate design artifacts (data-model.md, contracts/, quickstart.md)
3. **Proceed to /sp.tasks**: Break down into implementation tasks
4. **Create PHR**: Document planning session outcomes

---

**Plan Status**: ✅ COMPLETE - Ready for Phase 0 research generation
