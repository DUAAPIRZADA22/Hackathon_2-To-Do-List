# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-kubernetes-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated tests specified in this phase. Testing is done through manual verification (Docker builds, Helm lint, cluster deployment, service access).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a **web application** with frontend and backend directories:
- Frontend: `frontend/` (Next.js application)
- Backend: `backend/` (FastAPI application)
- Helm: `helm/ActionMindAI/` (Kubernetes deployment manifests)
- Docs: `docs/` (Documentation)

---

## Phase 1: Setup (Local Kubernetes Environment)

**Purpose**: Install and configure Minikube, kubectl, Helm, and required addons

### Environment Setup

- [ ] T001 Verify Docker is installed and running (`docker --version`)
- [ ] T002 Install Minikube if not present (`minikube version`)
- [ ] T003 Install kubectl if not present (`kubectl version --client`)
- [ ] T004 Install Helm 3.x if not present (`helm version`)
- [ ] T005 Start Minikube with required resources: `minikube start --cpus=4 --memory=8192 --driver=docker`
- [ ] T006 Enable Minikube ingress addon: `minikube addons enable ingress`
- [ ] T007 Enable Minikube metrics-server addon: `minikube addons enable metrics-server`
- [ ] T008 Verify Minikube status: `minikube status`
- [ ] T009 Configure Docker CLI to use Minikube daemon: `eval $(minikube docker-env)`

**Checkpoint**: Local Kubernetes environment ready - Minikube running with ingress and metrics-server enabled

---

## Phase 2: Foundational (Containerization Prerequisites)

**Purpose**: Create Dockerfiles and optimize images for both frontend and backend

**⚠️ CRITICAL**: No Helm deployment or cluster operations can begin until this phase is complete

### Frontend Dockerfile

- [ ] T010 [P] Create frontend/Dockerfile with multi-stage build (deps → builder → runner stages using node:22-alpine base)
- [ ] T011 [P] Create frontend/.dockerignore to exclude node_modules/, .next/, *.log, .env.local, .git/
- [ ] T012 Enable Next.js standalone output in frontend/next.config.js (add `output: 'standalone'` to config object)
- [ ] T013 Build frontend Docker image: `cd frontend && docker build -t ActionMindAI/frontend:latest .`
- [ ] T014 Verify frontend image size is under 500MB: `docker images | grep ActionMindAI/frontend`

### Backend Dockerfile

- [ ] T015 [P] Create backend/Dockerfile with multi-stage build (builder → runner stages using python:3.13-slim base)
- [ ] T016 [P] Create backend/.dockerignore to exclude __pycache__/, *.pyc, .env, .pytest_cache/, *.log
- [ ] T017 Build backend Docker image: `cd backend && docker build -t ActionMindAI/backend:latest .`
- [ ] T018 Verify backend image size is under 500MB: `docker images | grep ActionMindAI/backend`

### AIOps Documentation (Docker)

- [ ] T019 Document Gordon (Docker AI) commands used in docs/PHASE4-AIOPS-COMMANDS.md
  - `docker ai "create optimized Dockerfile for Next.js 14 standalone production build"`
  - `docker ai "optimize this FastAPI Dockerfile for production"`
  - `docker ai "what base image is best for Next.js production in 2025"`

**Checkpoint**: Docker images built and verified - ready for Helm chart creation

---

## Phase 3: User Story 1 - Containerize Application (Priority: P1) 🎯 MVP

**Goal**: Package ActionMind AI frontend and backend as Docker containers for Kubernetes deployment

**Independent Test**: Build both Docker images locally and verify they start correctly with `docker run`, delivering standalone containerized applications

### Verification

- [ ] T020 [US1] Verify frontend container starts: `docker run --rm -p 3000:3000 ActionMindAI/frontend:latest`
- [ ] T021 [US1] Verify backend container starts: `docker run --rm -p 8000:8000 ActionMindAI/backend:latest`
- [ ] T022 [US1] Verify both images under 500MB combined: `docker images | grep ActionMindAI`

**Checkpoint**: User Story 1 complete - Application successfully containerized

---

## Phase 4: User Story 2 - Deploy to Minikube (Priority: P2)

**Goal**: Deploy containerized ActionMind AI application to local Minikube cluster using Helm charts

**Independent Test**: Start Minikube, apply Helm charts, and verify pods are running and accessible

### Helm Chart Structure

- [ ] T023 [P] Create helm/ActionMindAI directory structure
- [ ] T024 [P] Create helm/ActionMindAI/Chart.yaml with metadata (apiVersion: v2, name: ActionMindAI, version: 1.0.0)
- [ ] T025 [P] Create helm/ActionMindAI/values.yaml with configurable parameters (namespace, replicas, image, resources, env)
- [ ] T026 [P] Create helm/ActionMindAI/templates/_helpers.tpl with template labels and selectors
- [ ] T027 [P] Create helm/ActionMindAI/templates/namespace.yaml defining ActionMindAI namespace

### Frontend Deployment Templates

- [ ] T028 [P] [US2] Create helm/ActionMindAI/templates/frontend-deployment.yaml (2 replicas, 500m CPU / 512Mi RAM limits)
- [ ] T029 [P] [US2] Create helm/ActionMindAI/templates/frontend-service.yaml (ClusterIP on port 3000)

### Backend Deployment Templates

- [ ] T030 [P] [US2] Create helm/ActionMindAI/templates/backend-deployment.yaml (2 replicas, 1000m CPU / 1Gi RAM limits, health probes)
- [ ] T031 [P] [US2] Create helm/ActionMindAI/templates/backend-service.yaml (ClusterIP on port 8000)

### Configuration Templates

- [ ] T032 [P] [US2] Create helm/ActionMindAI/templates/configmap.yaml with NEXT_PUBLIC_API_URL
- [ ] T033 [P] [US2] Create helm/ActionMindAI/templates/secrets.yaml for DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET

### Ingress Template

- [ ] T034 [US2] Create helm/ActionMindAI/templates/ingress.yaml (nginx class, routes / to frontend, /api to backend)

### Secrets Setup

- [ ] T035 [US2] Create helm/ActionMindAI/secrets.yaml.example template (do NOT commit actual secrets)
- [ ] T036 [US2] Create helm/ActionMindAI/secrets.yaml with actual values (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)

### Helm Chart Validation

- [ ] T037 [US2] Run Helm lint validation: `helm lint helm/ActionMindAI`
- [ ] T038 [US2] Run Helm template validation: `helm template ActionMindAI helm/ActionMindAI --debug`

### AIOps Documentation (Helm)

- [ ] T039 [US2] Document kubectl-ai commands used in docs/PHASE4-AIOPS-COMMANDS.md
  - `kubectl-ai "create helm chart structure for a Next.js frontend and FastAPI backend"`
  - `kubectl-ai "generate values.yaml for multi-container deployment"`
  - `kubectl-ai "verify all pods are running in ActionMindAI namespace"`

### Deployment

- [ ] T040 [US2] Install Helm chart: `helm install ActionMindAI helm/ActionMindAI --namespace ActionMindAI --create-namespace -f helm/ActionMindAI/secrets.yaml`
- [ ] T041 [US2] Verify all pods are Running: `kubectl get pods -n ActionMindAI`
- [ ] T042 [US2] Verify services are created: `kubectl get services -n ActionMindAI`

**Checkpoint**: User Story 2 complete - Application deployed to Minikube cluster

---

## Phase 5: User Story 3 - Access Deployed Application (Priority: P3)

**Goal**: Access and verify the deployed ActionMind AI application running in Minikube

**Independent Test**: Port-forward services or use ingress to access application in browser

### Access Methods

- [ ] T043 [US3] Test backend health endpoint via port-forward: `kubectl port-forward svc/ActionMindAI-backend 8000:8000 -n ActionMindAI` then `curl http://localhost:8000/health`
- [ ] T044 [US3] Test frontend via port-forward: `kubectl port-forward svc/ActionMindAI-frontend 3000:3000 -n ActionMindAI` then open http://localhost:3000
- [ ] T045 [US3] Test ingress routing: Get Minikube IP (`minikube ip`) and access via http://ActionMindAI.local (or use `minikube service ActionMindAI-frontend -n ActionMindAI`)

### Integration Verification

- [ ] T046 [US3] Verify frontend can communicate with backend API (test chat functionality in browser)
- [ ] T047 [US3] Verify backend connects to external Neon PostgreSQL (check logs for successful connection)

**Checkpoint**: User Story 3 complete - Application accessible and functional

---

## Phase 6: User Story 4 - Monitor Cluster Health (Priority: P4)

**Goal**: Monitor and analyze the health of the deployed application in Kubernetes cluster

**Independent Test**: Check pod logs, resource utilization, and use analysis tools to review cluster state

### Health Verification

- [ ] T048 [US4] Check pod logs for errors: `kubectl logs -l app.kubernetes.io/component=frontend -n ActionMindAI`
- [ ] T049 [US4] Check pod logs for errors: `kubectl logs -l app.kubernetes.io/component=backend -n ActionMindAI`
- [ ] T050 [US4] Verify resource metrics are available: `kubectl top pods -n ActionMindAI`
- [ ] T051 [US4] Verify resource utilization stays within limits (CPU 500m/1000m, Memory 512Mi/1Gi)

### Cluster Analysis

- [ ] T052 [US4] Analyze cluster health using Kagent: `kagent "analyze the cluster health and identify issues"`
- [ ] T053 [US4] Check resource utilization: `kagent "check resource utilization in ActionMindAI namespace"`
- [ ] T054 [US4] Verify service connectivity: `kagent "verify service connectivity between frontend and backend"`
- [ ] T055 [US4] Generate optimization suggestions: `kagent "suggest optimizations for the ActionMindAI deployment"`
- [ ] T056 [US4] Identify security concerns: `kagent "identify any security concerns in current configuration"`

### AIOps Documentation (Cluster)

- [ ] T057 [US4] Document all Kagent commands in docs/PHASE4-AIOPS-COMMANDS.md with purpose and results

**Checkpoint**: User Story 4 complete - Cluster health monitored and analyzed

---

## Phase 7: Polish & AIOps Documentation

**Purpose**: Complete AIOps documentation and final verification

### AIOps Documentation

- [ ] T058 [P] Create docs/PHASE4-AIOPS-COMMANDS.md with sections for Gordon, kubectl-ai, and Kagent
- [ ] T059 [P] Document all Gordon commands with purpose and results (image optimization, base image selection, multi-stage builds)
- [ ] T060 [P] Document all kubectl-ai commands with purpose and results (Helm chart creation, deployment verification)
- [ ] T061 [P] Document all Kagent commands with purpose and results (health analysis, resource utilization, optimization suggestions)

### Final Verification

- [ ] T062 Verify Docker images build successfully in under 5 minutes combined
- [ ] T063 Verify both images are under 500MB: `docker images | grep ActionMindAI`
- [ ] T064 Verify Helm chart passes linting: `helm lint helm/ActionMindAI`
- [ ] T065 Verify Minikube cluster starts in under 3 minutes
- [ ] T066 Verify all pods reach Running state within 5 minutes of Helm install
- [ ] T067 Verify application is accessible within 10 minutes of deployment start
- [ ] T068 Verify health checks pass within 2 minutes of pod startup
- [ ] T069 Verify frontend successfully communicates with backend API
- [ ] T070 Verify backend successfully connects to Neon PostgreSQL database
- [ ] T071 Verify resource utilization stays within defined limits
- [ ] T072 Verify full deployment completes in under 20 minutes

**Checkpoint**: All Phase 4 success criteria met - deployment complete and verified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all deployment
- **User Story 1 (Phase 3)**: Depends on Foundational phase - Can run independently
- **User Story 2 (Phase 4)**: Depends on User Story 1 - Requires containerized images
- **User Story 3 (Phase 5)**: Depends on User Story 2 - Requires deployed application
- **User Story 4 (Phase 6)**: Depends on User Story 3 - Requires running application
- **Polish (Phase 7)**: Depends on User Story 4 - Requires deployed and accessible application

### User Story Dependencies

- **User Story 1 (P1 - Containerize)**: Can start after Setup - No dependencies on other stories
- **User Story 2 (P2 - Deploy)**: Depends on User Story 1 - Requires Docker images
- **User Story 3 (P3 - Access)**: Depends on User Story 2 - Requires deployed Helm chart
- **User Story 4 (P4 - Monitor)**: Depends on User Story 3 - Requires running pods

### Within Each Phase

- Dockerfiles must be created before building images
- Images must be built before verification
- Helm templates must be created before validation
- Secrets must be created before Helm install
- Port-forward tests before ingress tests

### Parallel Opportunities

- All Setup phase tasks marked [P] can run in parallel (tool installations can be done together)
- All Foundational phase Dockerfile tasks marked [P] can run in parallel (frontend and backend independent)
- All Helm template creation tasks marked [P] can run in parallel (different files, no dependencies)
- All AIOps documentation tasks marked [P] can run in parallel (different tool sections)

---

## Parallel Example: Helm Chart Creation (User Story 2)

```bash
# Launch all Helm template tasks together (they are independent files):
Task: "Create helm/ActionMindAI/Chart.yaml"
Task: "Create helm/ActionMindAI/values.yaml"
Task: "Create helm/ActionMindAI/templates/_helpers.tpl"
Task: "Create helm/ActionMindAI/templates/namespace.yaml"
Task: "Create helm/ActionMindAI/templates/frontend-deployment.yaml"
Task: "Create helm/ActionMindAI/templates/frontend-service.yaml"
Task: "Create helm/ActionMindAI/templates/backend-deployment.yaml"
Task: "Create helm/ActionMindAI/templates/backend-service.yaml"
Task: "Create helm/ActionMindAI/templates/configmap.yaml"
Task: "Create helm/ActionMindAI/templates/secrets.yaml"
Task: "Create helm/ActionMindAI/templates/ingress.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2)

1. Complete Phase 1: Setup (Minikube environment)
2. Complete Phase 2: Foundational (Docker containerization)
3. Complete Phase 3: User Story 1 (Containerize Application)
4. **STOP and VALIDATE**: Test Docker images independently
5. Complete Phase 4: User Story 2 (Deploy to Minikube)
6. **STOP and VALIDATE**: Test Helm deployment independently
7. Deploy/demo if ready

### Incremental Delivery

1. Environment Setup → Minikube ready
2. Containerization → Docker images built
3. Add Helm Deployment → Application deployed to cluster
4. Add Access Verification → Application accessible
5. Add Monitoring → Cluster health verified
6. Each phase adds value without breaking previous phases

### Linear Execution

Given the sequential dependencies in this feature:
1. Complete User Story 1 (Containerize) first
2. Then User Story 2 (Deploy)
3. Then User Story 3 (Access)
4. Finally User Story 4 (Monitor)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently verifiable
- Commit after each task or logical group
- Stop at any checkpoint to validate phase independently
- AIOps commands must be documented with purpose and results
- All success criteria from spec.md must be verified
- Ensure secrets.yaml is NOT committed to git

---

## Task Summary

- **Total Tasks**: 72
- **Setup Phase**: 9 tasks
- **Foundational Phase**: 10 tasks
- **User Story 1**: 3 tasks (containerization focus)
- **User Story 2**: 17 tasks (Helm deployment focus)
- **User Story 3**: 5 tasks (access verification focus)
- **User Story 4**: 10 tasks (monitoring focus)
- **Polish Phase**: 15 tasks (documentation and verification)

**Parallel Opportunities**: 31 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-4 (Tasks T001-T042) deliver a fully containerized and deployable application
