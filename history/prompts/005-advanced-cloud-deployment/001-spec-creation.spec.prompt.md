---
prompt:
  id: "005-001"
  title: "Phase 5 Advanced Cloud Deployment Specification"
  stage: "spec"
  date_iso: "2026-02-08"
  surface: "agent"
  model: "claude-opus-4-6"
  feature: "005-advanced-cloud-deployment"
  branch: "005-advanced-cloud-deployment"
  user: "User"
  command: "/sp.specify"
  labels:
    - "cloud-native"
    - "event-driven"
    - "kubernetes"
    - "dapr"
    - "kafka"
    - "cicd"
  links:
    spec: "specs/005-advanced-cloud-deployment/spec.md"
    ticket: "null"
    adr: "null"
    pr: "null"

files_yaml:
  - specs/005-advanced-cloud-deployment/spec.md
  - specs/005-advanced-cloud-deployment/checklists/requirements.md
  - .specify/skills/cloud-native-blueprints.skill.md

tests_yaml: []

prompt_text: |
  # Phase 5: ActionMind AI Advanced Cloud Deployment - Complete Specification Prompt

  You are acting as the **Cloud-Native Solutions Architect** for ActionMind AI. Your goal is to generate the **Specify (Requirement Specification)** for Phase 5 of the hackathon project.

  ---

  ## Context

  We are implementing **Phase V: Advanced Cloud Deployment** of the ActionMind AI Hackathon.

  **Current Implementation Status:**
  - ✅ **Phase I Complete**: Console app with in-memory task distribution
  - ✅ **Phase II Complete**: Full-stack web app with Next.js + FastAPI + Neon DB + Better Auth
  - ✅ **Phase III Complete**: AI Chatbot with OpenAI Agents SDK + MCP tools
  - ✅ **Phase IV Complete**: Local Kubernetes deployment with Minikube + Helm charts

  **What We Have (Phase IV):**
  - Working Docker images (frontend + backend)
  - Helm charts for Minikube deployment
  - Basic Kubernetes manifests (Deployment, Service, Ingress)
  - Local Minikube testing environment

  **What's Missing (Phase V Goals):**
  - ❌ Dapr sidecar integration
  - ❌ Kafka/Redpanda event streaming
  - ❌ Event-driven microservices architecture
  - ❌ Advanced features (recurring tasks, due date reminders, real-time sync)
  - ❌ Cloud Kubernetes deployment (AKS/GKE/OKE)
  - ❌ CI/CD pipeline with GitHub Actions
  - ❌ Production monitoring and observability

  **Hackathon Points:** 300 pts
  **Deadline:** January 18, 2026

  [Full specification prompt with all requirements...]

  ---make phase 5 branch in current github and push phase 5 code on it

response_text: |
  Created comprehensive specification for Phase 5 Advanced Cloud Deployment including:

  1. **Event-Driven Architecture** - Dapr integration with Kafka/Redpanda for event streaming
  2. **Advanced Features** - Recurring tasks, due date reminders, real-time sync
  3. **Cloud Deployment** - Oracle OKE/GKE/AKS with production Helm charts
  4. **CI/CD Pipeline** - GitHub Actions with build, test, scan, deploy stages
  5. **Documentation** - Architecture diagrams, migration guide, troubleshooting

  Branch: `005-advanced-cloud-deployment`
  Spec: `specs/005-advanced-cloud-deployment/spec.md`
  Checklist: All items passed ✅

  Ready for `/sp.plan` phase.
---
