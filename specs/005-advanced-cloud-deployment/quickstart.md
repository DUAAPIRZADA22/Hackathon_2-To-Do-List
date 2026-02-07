# Quickstart Guide: Advanced Cloud Deployment with Event-Driven Architecture

**Feature**: 005-advanced-cloud-deployment
**Date**: 2026-02-08
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide provides step-by-step instructions for setting up and deploying the ActionMind AI application with event-driven architecture using Dapr and Kafka/Redpanda.

## Prerequisites

### Required Tools

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install kubectl (if not already installed)
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Windows (using Chocolatey)
choco install kubectl

# Install Helm
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
dapr version
kubectl version --client
helm version
```

### Cloud Provider Account

Choose one:
- **Oracle OKE** (recommended): Sign up at https://oracle.com/cloud/free
- **Google GKE**: Create project at https://console.cloud.google.com
- **Azure AKS**: Create account at https://portal.azure.com

## Local Development Setup (Minikube)

### Step 1: Start Minikube with Sufficient Resources

```bash
# Start Minikube with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify
minikube status
```

### Step 2: Initialize Dapr on Minikube

```bash
# Install Dapr on Kubernetes
dapr init -k

# Verify installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE  READY  STATUS
# dapr-sidecar-injector  dapr-system True   Running
# dapr-scheduler         dapr-system True   Running
# dapr-dashboard         dapr-system True   Running
# dapr-placement         dapr-system True   Running
# dapr-sentry            dapr-system True   Running
# dapr-operator          dapr-system True   Running
```

### Step 3: Deploy Redpanda (Kafka) to Minikube

```bash
# Create Redpanda single-node cluster
kubectl apply -f infrastructure/kafka/redpanda-minikube.yaml

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=300s

# Verify
kubectl get pods -l app=redpanda
```

**Alternative: Deploy Kafka with Strimzi**

```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Deploy Kafka cluster
kubectl apply -f infrastructure/kafka/kafka-cluster.yaml

# Wait for Kafka to be ready
kubectl wait --for=condition=ready kafka/my-cluster -n kafka --timeout=600s
```

### Step 4: Create Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f infrastructure/dapr-components/

# Verify components
kubectl get daprcomponents

# Expected output:
# NAME                 AGE
# kafka-pubsub         1m
# statestore           1m
# kubernetes-secret    1m
# reminder-check-cron  1m
```

### Step 5: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace actionmindai

# Create secrets from environment
kubectl create secret generic neon-db-secret \
  --from-literal=connection-string="postgresql://user:pass@host/db" \
  -n actionmindai

kubectl create secret generic sendgrid-api-key \
  --from-literal=api-key="SG.xxx" \
  -n actionmindai

# For local development, use test values
kubectl create secret generic openai-api-key \
  --from-literal=api-key="sk-test" \
  -n actionmindai
```

### Step 6: Build and Load Docker Images

```bash
# Build images
docker build -t actionmindai-backend:latest -f backend/Dockerfile backend/
docker build -t actionmindai-frontend:latest -f frontend/Dockerfile frontend/

# Load images into Minikube
minikube image load actionmindai-backend:latest
minikube image load actionmindai-frontend:latest

# Verify
minikube image ls | grep actionmindai
```

### Step 7: Deploy Application with Helm

```bash
# Install dependencies
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install application
helm install actionmindai helm/actionmindai-prod/ \
  --namespace actionmindai \
  --create-namespace \
  --set image.pullPolicy=Never \
  --values helm/actionmindai-prod/values-minikube.yaml

# Wait for deployment
kubectl wait --for=condition=available deployment \
  -l app.kubernetes.io/instance=actionmindai \
  -n actionmindai \
  --timeout=300s

# Verify pods
kubectl get pods -n actionmindai

# Expected output:
# NAME                                      READY  STATUS
# actionmindai-backend-xxx                  2/2    Running
# actionmindai-frontend-xxx                 2/2    Running
# actionmindai-notification-service-xxx     2/2    Running
# actionmindai-recurring-task-service-xxx   2/2    Running
# actionmindai-realtime-sync-service-xxx    2/2    Running
```

Note: Each pod shows 2/2 READY because of the Dapr sidecar.

### Step 8: Access Application

```bash
# Option 1: Port-forward
kubectl port-forward -n actionmindai svc/actionmindai-frontend 3000:80

# Option 2: Minikube tunnel
minikube tunnel

# Get ingress URL
kubectl get ingress -n actionmindai

# Open browser
# http://actionmindai.local (or the URL from ingress)
```

### Step 9: Verify Event Flow

```bash
# Check Kafka topics
kubectl exec -n actionmindai redpanda-0 -- rpk topic list

# Consume events from task-events topic
kubectl exec -n actionmindai redpanda-0 -- rkp topic consume task-events

# In another terminal, create a task via API or UI
# You should see the event in the consumer output

# Check consumer group offsets
kubectl exec -n actionmindai redpanda-0 -- rkp group list
kubectl exec -n actionmindai redpanda-0 -- rkp group describe notification-service
```

## Cloud Deployment (Oracle OKE)

### Step 1: Create Oracle OKE Cluster

```bash
# Install OCI CLI
# macOS
brew install oci-cli

# Linux
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure OCI CLI
oci setup config

# Create OKE cluster
oci ce cluster create \
  --name actionmindai \
  --compartment-id $COMPARTMENT_ID \
  --node-pool-shape VM.Standard.E4.Flex \
  --node-pool-config-ocpus 2 \
  --node-pool-config-memory-in-gbs 12 \
  --size 1 \
  --kubernetes-version 1.29.1

# Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config \
  --region us-ashburn-1

# Verify
kubectl get nodes
```

### Step 2: Install Dapr on Cloud Cluster

```bash
# Install Dapr
dapr init -k

# Install ingress controller (if not present)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s
```

### Step 3: Deploy Redpanda to Cloud

```bash
# Apply Redpanda manifests (scaled for cloud)
kubectl apply -f infrastructure/cloud/oracle-oke/redpanda-cluster.yaml

# Wait for readiness
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=600s
```

### Step 4: Create Dapr Components (Cloud Config)

```bash
# Apply Dapr components with cloud-specific configuration
kubectl apply -f infrastructure/dapr-components/cloud/
```

### Step 5: Push Docker Images to Registry

```bash
# Tag images for registry
docker tag actionmindai-backend:latest ${REGISTRY}/actionmindai-backend:${VERSION}
docker tag actionmindai-frontend:latest ${REGISTRY}/actionmindai-frontend:${VERSION}

# Push to registry
docker push ${REGISTRY}/actionmindai-backend:${VERSION}
docker push ${REGISTRY}/actionmindai-frontend:${VERSION}

# Set environment variables
export REGISTRY=your-registry
export VERSION=v1.0.0
```

### Step 6: Deploy with Helm (Cloud Values)

```bash
# Install application with cloud values
helm install actionmindai helm/actionmindai-prod/ \
  --namespace actionmindai \
  --create-namespace \
  --set image.registry=${REGISTRY} \
  --set image.tag=${VERSION} \
  --values helm/actionmindai-prod/values-oke.yaml

# Verify deployment
kubectl get pods -n actionmindai
kubectl get svc -n actionmindai
kubectl get ingress -n actionmindai
```

### Step 7: Configure DNS

```bash
# Get ingress load balancer IP
kubectl get ingress actionmindai -n actionmindai

# Add DNS record
# actionmindai.yourdomain.com A <LOAD_BALANCER_IP>

# Or use local testing with /etc/hosts
# <LB_IP> actionmindai.local
```

## CI/CD Pipeline Setup

### Step 1: Configure GitHub Secrets

Navigate to: Repository → Settings → Secrets and Variables → Actions

Add the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_USERNAME` | Container registry username | `your-dockerhub-username` |
| `DOCKER_PASSWORD` | Container registry password/token | `dckr_pat_xxxxx` |
| `KUBE_CONFIG` | Base64-encoded kubeconfig | `(cat ~/.kube/config \| base64)` |
| `NEON_DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `SENDGRID_API_KEY` | SendGrid API key | `SG.xxxxx` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxxxx` |

### Step 2: Create GitHub Actions Workflow

The workflow is already defined in `.github/workflows/deploy.yml`.

### Step 3: Test Pipeline

```bash
# Push a commit to trigger pipeline
git commit --allow-empty -m "test: trigger CI/CD pipeline"
git push origin 005-advanced-cloud-deployment

# Monitor pipeline at:
# https://github.com/DUAAPIRZADA22/Hackathon_2-To-Do-List/actions
```

## Verification Checklist

### Event-Driven Architecture

- [ ] Dapr sidecars are injected (pods show 2/2 ready)
- [ ] Kafka topics are created
- [ ] Task CRUD operations publish events
- [ ] Notification service consumes events
- [ ] Recurring task service creates new instances
- [ ] Real-time sync service broadcasts updates

### Advanced Features

- [ ] Can create recurring tasks
- [ ] Recurring tasks auto-create next instance on completion
- [ ] Can set due date reminders
- [ ] Reminders are sent at configured times
- [ ] Real-time updates appear across multiple clients

### Cloud Deployment

- [ ] Application accessible via ingress
- [ ] All pods are healthy
- [ ] Database connections work
- [ ] Events flow through Kafka

### CI/CD Pipeline

- [ ] Docker images build successfully
- [ ] Tests pass
- [ ] Security scans complete
- [ ] Deployment to staging works
- [ ] Manual approval gate works

## Troubleshooting

### Dapr Sidecar Not Injecting

```bash
# Check Dapr installation
dapr status -k

# Check pod annotations
kubectl describe pod <pod-name> -n actionmindai

# Verify dapr.io/enabled: "true" annotation exists
```

### Kafka Connection Issues

```bash
# Check Redpanda pods
kubectl get pods -l app=redpanda

# Check Redpanda logs
kubectl logs -f redpanda-0

# Test Kafka connectivity from application pod
kubectl exec -it actionmindai-backend-xxx -n actionmindai -- \
  curl http://localhost:3500/v1.0/healthz
```

### Events Not Being Published

```bash
# Check Dapr component configuration
kubectl get daprcomponents

# Describe component
kubectl describe daprcomponent kafka-pubsub

# Check application logs for Dapr errors
kubectl logs actionmindai-backend-xxx -c actionmindai-backend -n actionmindai
```

### Real-Time Updates Not Working

```bash
# Check WebSocket/SSE endpoint
kubectl exec actionmindai-backend-xxx -n actionmindai -- \
  curl http://localhost:8000/ws/tasks

# Check realtime-sync service logs
kubectl logs actionmindai-realtime-sync-service-xxx -n actionmindai

# Verify Kafka topic subscription
kubectl logs actionmindai-realtime-sync-service-xxx -c daprd -n actionmindai
```

## Development Workflow

### Local Development with Dapr CLI

```bash
# Run backend with Dapr
cd backend
dapr run \
  --app-id actionmindai-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../infrastructure/dapr-components/ \
  -- python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# In another terminal, run frontend
cd frontend
npm run dev

# Test event publishing
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task"}'

# Check Dapr metrics
# http://localhost:3500/v1.0/metrics
```

### Testing Event Flow Locally

```bash
# Subscribe to events
curl http://localhost:3500/v1.0/subscribe

# Publish event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task_created",
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-02-08T12:00:00Z",
    "correlation_id": "880e8400-e29b-41d4-a716-446655440000",
    "data": {"title": "Test task"}
  }'
```

## Next Steps

After completing this quickstart:

1. **Review Architecture**: See `plan.md` for architecture details
2. **Understand Data Model**: See `data-model.md` for entity definitions
3. **Review API Contracts**: See `contracts/` for API specifications
4. **Run Tests**: Execute test suites to verify functionality
5. **Implement Tasks**: Follow `tasks.md` (generated by `/sp.tasks`)

## Support

For issues or questions:
- Check `plan.md` for architecture decisions
- Check `research.md` for technology choices
- Check `spec.md` for requirements
- Check troubleshooting sections above
