# ActionMindAI Minikube Deployment Guide

Quick start guide for deploying ActionMindAI to a local Minikube cluster.

## Prerequisites

- Docker Desktop or Docker Engine
- Minikube v1.30+
- kubectl configured to use Minikube
- Helm 3.x

## Installation

```bash
# Install Minikube (macOS)
brew install minikube

# Install Minikube (Windows)
choco install minikube

# Install Minikube (Linux)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install Helm (macOS)
brew install helm

# Install Helm (Windows)
choco install kubernetes-helm

# Install Helm (Linux)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Quick Start

### 1. Start Minikube

```bash
# Start with sufficient resources (4 CPUs, 8GB RAM)
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify status
minikube status
```

### 2. Configure Docker Environment

```bash
# Point Docker CLI to Minikube's daemon
eval $(minikube docker-env)

# Verify (should show minikube context)
docker context ls
```

### 3. Build Docker Images

```bash
# Build frontend image
docker build -t actionmindai/frontend:latest -f frontend/Dockerfile frontend/

# Build backend image
docker build -t actionmindai/backend:latest -f backend/Dockerfile backend/

# Verify images
docker images | grep actionmindai
```

### 4. Configure Secrets

```bash
# Copy the example secrets file
cp helm/ActionMindAI/secrets.yaml.example helm/ActionMindAI/secrets.yaml

# Edit with actual values
# IMPORTANT: Never commit secrets.yaml to git
nano helm/ActionMindAI/secrets.yaml
```

**secrets.yaml:**
```yaml
databaseUrl: "postgresql://user:password@host:5432/actionmindai"
openaiApiKey: "sk-your-openai-key-here"
betterAuthSecret: "generate-with-openssl-rand-base64-32"
```

### 5. Deploy with Helm

```bash
# Create namespace
kubectl create namespace actionmindai

# Create Kubernetes secret from values
kubectl create secret generic actionmindai-secrets \
  --from-literal=databaseUrl='postgresql://user:password@host:5432/actionmindai' \
  --from-literal=openaiApiKey='sk-your-openai-key' \
  --from-literal=betterAuthSecret='your-secret' \
  --namespace actionmindai

# Install the Helm chart
helm install actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --create-namespace \
  --wait \
  --timeout 5m
```

### 6. Access the Application

```bash
# Get the Minikube IP
minikube ip

# Add to /etc/hosts (macOS/Linux)
echo "$(minikube ip) ActionMindAI.local" | sudo tee -a /etc/hosts

# Add to C:\Windows\System32\drivers\etc\hosts (Windows as Administrator)
# <minikube-ip> ActionMindAI.local

# Access the application
open http://ActionMindAI.local        # macOS
xdg-open http://ActionMindAI.local    # Linux
start http://ActionMindAI.local       # Windows
```

## Verification

```bash
# Check all pods are running
kubectl get pods -n actionmindai

# Expected output:
# NAME                                      READY   STATUS    RESTARTS   AGE
# actionmindai-backend-xxxxxxxxxx-xxxxx     1/1     Running   0          1m
# actionmindai-frontend-xxxxxxxxxx-xxxxx    1/1     Running   0          1m

# Check services
kubectl get svc -n actionmindai

# Check ingress
kubectl get ingress -n actionmindai

# View logs
kubectl logs -l app.kubernetes.io/component=backend -n actionmindai
kubectl logs -l app.kubernetes.io/component=frontend -n actionmindai

# Test backend health endpoint
kubectl exec -n actionmindai deployment/actionmindai-backend -- \
  curl http://localhost:8000/health
```

## Common Issues

### Issue: Images not found (ErrImageNeverPull)

**Solution:** Ensure you're using Minikube's Docker daemon:
```bash
eval $(minikube docker-env)
docker images | grep actionmindai
```

### Issue: Ingress not working

**Solution:** Verify ingress addon is enabled:
```bash
minikube addons enable ingress
minikube addons list
```

### Issue: Pods in CrashLoopBackOff

**Solution:** Check pod logs and describe events:
```bash
kubectl logs pod/<pod-name> -n actionmindai
kubectl describe pod/<pod-name> -n actionmindai
```

### Issue: Port conflicts

**Solution:** Stop conflicting services or change Minikube port:
```bash
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker
```

## Development Workflow

### View Logs in Real-Time

```bash
# Follow backend logs
kubectl logs -l app.kubernetes.io/component=backend -n actionmindai -f

# Follow frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -n actionmindai -f
```

### Port Forward for Local Testing

```bash
# Forward backend to localhost:8000
kubectl port-forward -n actionmindai svc/actionmindai-backend 8000:8000

# Forward frontend to localhost:3000
kubectl port-forward -n actionmindai svc/actionmindai-frontend 3000:3000
```

### Exec into Container

```bash
# Shell into backend container
kubectl exec -it -n actionmindai deployment/actionmindai-backend -- /bin/sh

# Shell into frontend container
kubectl exec -it -n actionmindai deployment/actionmindai-frontend -- /bin/sh
```

### Rebuild and Update

```bash
# Rebuild images
eval $(minikube docker-env)
docker build -t actionmindai/frontend:v2 -f frontend/Dockerfile frontend/
docker build -t actionmindai/backend:v2 -f backend/Dockerfile backend/

# Update image tags in values.yaml, then upgrade
helm upgrade actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --set frontend.image.tag=v2 \
  --set backend.image.tag=v2
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall actionmindai -n actionmindai

# Delete namespace
kubectl delete namespace actionmindai

# Remove /etc/hosts entry
sudo sed -i '' '/ActionMindAI.local/d' /etc/hosts  # macOS
sudo sed -i '/ActionMindAI.local/d' /etc/hosts      # Linux

# Stop Minikube
minikube stop

# Delete Minikube cluster (WARNING: destroys all data)
minikube delete
```

## Advanced: Enable Auto-scaling

```bash
# Enable HPA for frontend
helm upgrade actionmindai ./helm/ActionMindAI \
  --namespace actionmindai \
  --set frontend.autoscaling.enabled=true \
  --set backend.autoscaling.enabled=true

# Verify HPA
kubectl get hpa -n actionmindai

# Trigger load test to see autoscaling
kubectl run -it --rm load-test --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://actionmindai-frontend; done"
```

## Production Considerations

For production deployment to AKS/GKE/OKE:

1. **Use container registry** (ACR/GCR/ECR) instead of local images
2. **Pin image versions** - Avoid `latest` tag
3. **Enable TLS** - Configure cert-manager or cloud provider certificates
4. **Configure monitoring** - Prometheus/Grafana or cloud provider monitoring
5. **Set up logging** - EFK stack or cloud provider logging
6. **Enable autoscaling** - HPA with appropriate metrics
7. **Configure backups** - Database backup strategy
8. **Implement CI/CD** - Automated deployment pipeline

See `docs/production-checklist.md` for complete production readiness guide.
