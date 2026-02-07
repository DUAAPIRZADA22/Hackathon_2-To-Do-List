# AIOps Documentation for ActionMindAI Kubernetes Deployment

This document describes AI-assisted operations (AIOps) for managing the ActionMindAI application on Kubernetes using both Gordon (Docker AI) and kubectl-ai (Kubernetes AI).

## Table of Contents

1. [Gordon - Docker AI Assistant](#gordon---docker-ai-assistant)
2. [kubectl-ai - Kubernetes AI Assistant](#kubectl-ai---kubernetes-ai-assistant)
3. [Integration with ActionMindAI](#integration-with-actionmindai)
4. [Common Workflows](#common-workflows)

---

## Gordon - Docker AI Assistant

Gordon is an AI-powered CLI assistant for Docker operations.

### Installation

```bash
# Install Gordon (assuming Node.js is available)
npm install -g gordon-cli

# Or using pip
pip install gordon-cli
```

### Configuration

Set your OpenAI API key:
```bash
export GORDON_API_KEY="sk-your-openai-key"
# or
gordon config set api_key "sk-your-openai-key"
```

### Common Gordon Commands

#### Image Optimization
```bash
# Analyze and optimize an existing Dockerfile
gordon optimize Dockerfile

# Get suggestions for reducing image size
gordon analyze --target size frontend/Dockerfile

# Security scan before building
gordon scan frontend/
```

#### Build Assistance
```bash
# Build with AI monitoring
gordon build -t actionmindai-frontend:latest frontend/

# Build with error explanation
gordon build --explain -t actionmindai-backend:latest backend/

# Multi-arch build with AI assistance
gordon buildx --platform linux/amd64,linux/arm64 -t actionmindai:latest .
```

#### Troubleshooting
```bash
# Diagnose build failures
gordon diagnose build.log

# Get container runtime insights
gordon inspect actionmindai-backend

# Analyze container performance
gordon performance actionmindai-frontend
```

---

## kubectl-ai - Kubernetes AI Assistant

kubectl-ai is an AI-powered kubectl plugin that helps generate and apply Kubernetes manifests using natural language.

### Installation

```bash
# Install krew (kubectl plugin manager)
# See: https://krew.sigs.k8s.io/docs/user-guide/setup/

# Install kubectl-ai via krew
kubectl krew install ai

# Or install directly
go install github.com/jordanrutins/kubectl-ai@latest
```

### Configuration

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-your-openai-key"
# or create a kube-ai secret
kubectl create secret generic kube-ai \
  --from-literal=openai-api-key="sk-your-openai-key"
```

### Common kubectl-ai Commands

#### Manifest Generation
```bash
# Generate a deployment
kubectl ai "Create a deployment for ActionMindAI backend with 3 replicas"

# Generate a service
kubectl ai "Create a ClusterIP service for the backend on port 8000"

# Generate an ingress
kubectl ai "Create an ingress that routes /api to backend service and / to frontend"

# Generate a ConfigMap
kubectl ai "Create a ConfigMap with environment variables for the backend"
```

#### Troubleshooting
```bash
# Diagnose pod issues
kubectl ai "Why is the backend pod crashing?" --pod actionmindai-backend-xxxxx

# Get resource optimization suggestions
kubectl ai "Optimize the resource requests and limits for all pods"

# Analyze network policies
kubectl ai "Show me why the frontend cannot reach the backend"
```

#### Updates and Modifications
```bash
# Scale deployment
kubectl ai "Scale the frontend deployment to 5 replicas"

# Update image
kubectl ai "Update the backend deployment to use image actionmindai-backend:v2.0"

# Rollback changes
kubectl ai "Rollback the last deployment to the previous version"
```

---

## Integration with ActionMindAI

### Pre-deployment Checks

Using Gordon to validate Dockerfiles before building:
```bash
cd frontend
gordon optimize Dockerfile
gordon scan .

cd ../backend
gordon optimize Dockerfile
gordon scan .
```

### Deployment Workflow

1. **Build images with Gordon assistance:**
   ```bash
   gordon build -t actionmindai-frontend:1.0.0 frontend/
   gordon build -t actionmindai-backend:1.0.0 backend/
   ```

2. **Generate manifests with kubectl-ai (if needed):**
   ```bash
   kubectl ai "Create a Helm chart for a full-stack app with frontend and backend"
   ```

3. **Deploy with Helm:**
   ```bash
   helm install actionmindai ./helm/ActionMindAI \
     --values helm/ActionMindAI/secrets.yaml \
     --namespace actionmindai \
     --create-namespace
   ```

4. **Verify deployment:**
   ```bash
   kubectl get pods -n actionmindai
   kubectl get services -n actionmindai
   kubectl get ingress -n actionmindai
   ```

### Monitoring and Troubleshooting

Check pod health with AI assistance:
```bash
# Check all pods
kubectl get pods -n actionmindai

# Diagnose issues
kubectl ai "Explain why the backend pods are not ready" \
  --namespace actionmindai

# Check logs with AI analysis
kubectl ai "Analyze the backend logs for errors" \
  --namespace actionmindai \
  --selector=app.kubernetes.io/component=backend
```

---

## Common Workflows

### Workflow 1: Initial Deployment

```bash
# 1. Validate Dockerfiles
gordon optimize frontend/Dockerfile
gordon optimize backend/Dockerfile

# 2. Build images
gordon build -t actionmindai-frontend:latest frontend/
gordon build -t actionmindai-backend:latest backend/

# 3. Load into Minikube (if using local cluster)
minikube image load actionmindai-frontend:latest
minikube image load actionmindai-backend:latest

# 4. Deploy with Helm
helm install actionmindai ./helm/ActionMindAI \
  --values helm/ActionMindAI/secrets.yaml \
  --namespace actionmindai \
  --create-namespace

# 5. Verify
kubectl get pods -n actionmindai -w
```

### Workflow 2: Updating the Application

```bash
# 1. Build new images
gordon build -t actionmindai-frontend:v1.1.0 frontend/
gordon build -t actionmindai-backend:v1.1.0 backend/

# 2. Update Helm values (edit values.yaml)
# Change image tags to v1.1.0

# 3. Upgrade deployment
helm upgrade actionmindai ./helm/ActionMindAI \
  --values helm/ActionMindAI/secrets.yaml \
  --namespace actionmindai

# 4. Monitor rollout
kubectl rollout status deployment/actionmindai-frontend -n actionmindai
kubectl rollout status deployment/actionmindai-backend -n actionmindai
```

### Workflow 3: Troubleshooting

```bash
# 1. Check pod status
kubectl get pods -n actionmindai

# 2. Describe failing pod
kubectl describe pod <pod-name> -n actionmindai

# 3. Get AI diagnosis
kubectl ai "Why is this pod failing?" --pod <pod-name> --namespace actionmindai

# 4. Check logs
kubectl logs <pod-name> -n actionmindai --tail=100 -f

# 5. Analyze with Gordon
gordon diagnose <pod-name>.log
```

### Workflow 4: Scaling

```bash
# Scale using kubectl
kubectl scale deployment/actionmindai-backend --replicas=5 -n actionmindai

# Or scale using Helm upgrade
helm upgrade actionmindai ./helm/ActionMindAI \
  --set backend.replicaCount=5 \
  --namespace actionmindai

# Or get AI recommendations
kubectl ai "How many replicas do I need for the backend?" \
  --namespace actionmindai
```

---

## Best Practices

1. **Always validate Dockerfiles before building** - Use `gordon optimize` and `gordon scan`
2. **Use AI to understand complex failures** - `kubectl ai` can explain cryptic Kubernetes errors
3. **Keep secrets secure** - Never commit secrets.yaml; use sealed-secrets or external secret managers
4. **Test in Minikube first** - Validate deployments locally before pushing to production
5. **Monitor resource usage** - Use kubectl-ai to get optimization suggestions
6. **Version your images** - Use semantic versioning for easy rollbacks
7. **Document AI interactions** - Keep track of useful kubectl-ai prompts for reuse

---

## Additional Resources

- **Gordon Documentation**: [Link to Gordon docs]
- **kubectl-ai Repository**: https://github.com/jordanrutins/kubectl-ai
- **Helm Documentation**: https://helm.sh/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
