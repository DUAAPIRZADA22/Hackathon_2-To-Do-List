# Quickstart Guide: Local Kubernetes Deployment

**Feature**: 001-kubernetes-deployment
**Date**: 2026-01-26
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide provides step-by-step instructions for deploying ActionMind AI to a local Minikube Kubernetes cluster.

## Prerequisites

### Required Software

| Tool | Version | Installation Check |
|------|---------|-------------------|
| Docker | Latest | `docker --version` |
| Minikube | Latest | `minikube version` |
| Helm | 3.x | `helm version` |
| kubectl | Latest | `kubectl version --client` |

### Hardware Requirements

- **CPU**: 4 cores minimum
- **RAM**: 8GB minimum
- **Disk**: 20GB free space

### Installation

#### macOS
```bash
brew install docker minikube helm kubectl
```

#### Windows
```bash
# Using Chocolatey
choco install docker-cli minikube kubernetes-helm kubectl
```

#### Linux
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

---

## Environment Setup

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster status
minikube status
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

### 2. Enable Required Addons

```bash
# Enable ingress controller
minikube addons enable ingress

# Enable metrics-server for monitoring
minikube addons enable metrics-server

# Verify addons
minikube addons list
```

### 3. Configure Minikube Docker Environment

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify Docker is using Minikube daemon
docker context ls
```

---

## Build Container Images

### 1. Build Backend Image

```bash
cd backend

# Build multi-stage Docker image
docker build -t ActionMindAI/backend:latest .

# Verify image size (should be < 500MB)
docker images | grep ActionMindAI/backend
```

### 2. Build Frontend Image

```bash
cd ../frontend

# Build multi-stage Docker image
docker build -t ActionMindAI/frontend:latest .

# Verify image size (should be < 500MB)
docker images | grep ActionMindAI/frontend
```

### 3. Verify Images

```bash
# List all ActionMindAI images
docker images | grep ActionMindAI

# Expected output:
# ActionMindAI/backend    latest   abc123   2 minutes ago   350MB
# ActionMindAI/frontend   latest   def456   1 minute ago    180MB
```

---

## Helm Chart Deployment

### 1. Create Secrets File

**IMPORTANT**: Do NOT commit this file to git!

```bash
cd helm/ActionMindAI

# Create secrets file from template
cat > secrets.yaml << EOF
secrets:
  databaseUrl: "postgresql://neondb_owner:password@ep-xxxxx.c-2.us-east-1.aws.neon.tech/neondb"
  openaiApiKey: "sk-your-openai-api-key-here"
  betterAuthSecret: "generate-a-secure-random-string-min-32-chars"
EOF

# Verify secrets file
cat secrets.yaml
```

### 2. Install Helm Chart

```bash
# Install the chart with secrets
helm install ActionMindAI . \
  --namespace ActionMindAI \
  --create-namespace \
  -f secrets.yaml

# Expected output:
# NAME: ActionMindAI
# LAST DEPLOYED: [timestamp]
# NAMESPACE: ActionMindAI
# STATUS: deployed
# REVISION: 1
```

### 3. Verify Deployment

```bash
# Check all pods
kubectl get pods -n ActionMindAI

# Expected output (after ~1 minute):
# NAME                                    READY   STATUS    RESTARTS   AGE
# ActionMindAI-backend-xxxxxxxxxx-xxxxx   1/1     Running   0          45s
# ActionMindAI-backend-xxxxxxxxxx-yyyyy   1/1     Running   0          45s
# ActionMindAI-frontend-xxxxxxxxxx-xxxxx  1/1     Running   0          30s
# ActionMindAI-frontend-xxxxxxxxxx-yyyyy  1/1     Running   0          30s

# Check services
kubectl get services -n ActionMindAI

# Expected output:
# NAME                   TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
# ActionMindAI-backend    ClusterIP   10.100.200.50    <none>        8000/TCP   1m
# ActionMindAI-frontend   ClusterIP   10.100.200.51    <none>        3000/TCP   1m

# Check ingress
kubectl get ingress -n ActionMindAI

# Expected output:
# NAME                   CLASS   HOSTS                ADDRESS        PORTS   AGE
# ActionMindAI-ingress    nginx   ActionMindAI.local   192.168.49.2   80      2m
```

---

## Access the Application

### Option 1: Port Forwarding

```bash
# Forward backend service
kubectl port-forward svc/ActionMindAI-backend 8000:8000 -n ActionMindAI

# In another terminal, forward frontend service
kubectl port-forward svc/ActionMindAI-frontend 3000:3000 -n ActionMindAI

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Health check: curl http://localhost:8000/health
```

### Option 2: Minikube Service

```bash
# Open frontend in default browser
minikube service ActionMindAI-frontend -n ActionMindAI

# Get backend URL
minikube service ActionMindAI-backend -n ActionMindAI --url
```

### Option 3: Ingress (requires hosts file entry)

```bash
# Get Minikube IP
minikube ip

# Add to hosts file (requires sudo)
# macOS/Linux:
echo "$(minikube ip) ActionMindAI.local" | sudo tee -a /etc/hosts

# Windows (run as Administrator):
# Add entry to C:\Windows\System32\drivers\etc\hosts

# Access via browser
open http://ActionMindAI.local
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n ActionMindAI

# Describe pod for details
kubectl describe pod <pod-name> -n ActionMindAI

# View pod logs
kubectl logs <pod-name> -n ActionMindAI

# Common issues:
# - ImagePullBackOff: Images not built in Minikube Docker daemon
#   Solution: Run `eval $(minikube docker-env)` and rebuild
# - CrashLoopBackOff: Application error, check logs
# - ErrImagePull: Image name mismatch, verify image tags
```

### Health Check Failures

```bash
# Check probe configuration
kubectl get pod <pod-name> -n ActionMindAI -o yaml | grep -A 10 livenessProbe
kubectl get pod <pod-name> -n ActionMindAI -o yaml | grep -A 10 readinessProbe

# Common issues:
# - Initial delay too short: Application still starting
#   Solution: Increase initialDelaySeconds in values.yaml
# - Wrong probe path: Verify /health endpoint exists
#   Solution: Check backend logs for health endpoint registration
```

### Ingress Not Working

```bash
# Verify ingress controller is running
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress ActionMindAI-ingress -n ActionMindAI

# Common issues:
# - Ingress addon not enabled
#   Solution: `minikube addons enable ingress`
# - Wrong ingress class
#   Solution: Verify `ingressClassName: nginx` in ingress.yaml
# - DNS resolution: Use Minikube IP or add to hosts file
```

### Resource Issues

```bash
# Check resource usage
kubectl top pods -n ActionMindAI

# Check node resources
kubectl top nodes

# Common issues:
# - Insufficient resources: Increase Minikube memory/CPU
#   Solution: `minikube start --cpus=4 --memory=8192`
# - OOMKilled: Increase memory limits in values.yaml
```

### Database Connection Issues

```bash
# Test database connectivity from pod
kubectl exec -it <backend-pod-name> -n ActionMindAI -- bash
curl -v https://your-neon-host.com

# Verify secrets are mounted
kubectl exec -it <backend-pod-name> -n ActionMindAI -- env | grep DATABASE_URL

# Common issues:
# - Wrong connection string: Verify DATABASE_URL format
# - Network restrictions: Neon may require IP whitelisting
# - Missing SSL certificate: Add ?sslmode=require to connection string
```

---

## Cleanup

### Remove Deployment

```bash
# Uninstall Helm chart
helm uninstall ActionMindAI -n ActionMindAI

# Delete namespace
kubectl delete namespace ActionMindAI

# Verify cleanup
kubectl get namespaces | grep ActionMindAI
```

### Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# Delete cluster (optional)
minikube delete

# Reset Docker context
docker context use default
```

---

## AIOps Commands Reference

### Gordon (Docker AI)

```bash
# Optimize Dockerfile
docker ai "optimize this Dockerfile for smaller image size"

# Best practices
docker ai "what base image is best for Next.js production in 2025"

# Multi-stage builds
docker ai "create multi-stage build for Python FastAPI"
```

### kubectl-ai

```bash
# Create Helm chart
kubectl-ai "create helm chart structure for Next.js frontend and FastAPI backend"

# Generate deployments
kubectl-ai "generate deployment with resource limits and health probes"

# Troubleshoot
kubectl-ai "verify all pods are running in ActionMindAI namespace"
```

### Kagent

```bash
# Health analysis
kagent "analyze the cluster health and identify issues"

# Resource utilization
kagent "check resource utilization in ActionMindAI namespace"

# Connectivity
kagent "verify service connectivity between frontend and backend"

# Optimization
kagent "suggest optimizations for the ActionMindAI deployment"
```

---

## Next Steps

After successful deployment:

1. **Test Application**: Verify chat functionality works end-to-end
2. **Monitor Resources**: Check resource usage under load
3. **Review Logs**: Ensure no errors in pod logs
4. **Scale Testing**: Adjust replicas based on resource availability

---

**Quickstart Status**: ✅ COMPLETE
**Implementation Phase**: See `/sp.tasks` for implementation tasks
