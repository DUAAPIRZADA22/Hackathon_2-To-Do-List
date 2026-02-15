# ActionMind AI - Oracle Kubernetes Engine (OKE) Deployment Guide

## Prerequisites

1. **Oracle Cloud Account** with OKE access
2. **OCI CLI** installed and configured
3. **kubectl** configured for your OKE cluster
4. **Helm 3.x** installed
5. **Docker** installed (for building images)

## Quick Start

### 1. Build and Push Images

```bash
# Build backend image
docker build -t your-registry/backend:v1.0.0 ./backend

# Build frontend image
docker build -t your-registry/frontend:v1.0.0 ./frontend

# Push to your registry (OCI Registry, GHCR, etc.)
docker push your-registry/backend:v1.0.0
docker push your-registry/frontend:v1.0.0
```

### 2. Update Configuration

Edit `helm/actionmindai-prod/values-oke.yaml`:

```yaml
image:
  repository: your-registry/actionmindai  # UPDATE THIS
  tag: "v1.0.0"

ingress:
  host: your-domain.com  # UPDATE THIS
```

### 3. Deploy

```bash
# Run the deployment script
./scripts/deploy-oke.sh
```

Or manually:

```bash
# Create namespace
kubectl create namespace actionmindai

# Create secrets
kubectl create secret generic postgres-connection-string \
  --from-literal=connection-string='postgresql://...' \
  -n actionmindai

kubectl create secret generic openai-api-key \
  --from-literal=api-key='sk-...' \
  -n actionmindai

kubectl create secret generic app-secrets \
  --from-literal=secret-key='your-secret-key' \
  -n actionmindai

# Deploy with Helm
helm install actionmindai ./helm/actionmindai-prod \
  --namespace actionmindai \
  --values helm/actionmindai-prod/values-oke.yaml
```

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n actionmindai

# Check services
kubectl get svc -n actionmindai

# Check logs
kubectl logs -n actionmindai deployment/backend
kubectl logs -n actionmindai deployment/frontend

# Port forward to test locally
kubectl port-forward -n actionmindai svc/frontend 3000:80
```

## OKE-Specific Considerations

### Virtual Nodes vs Worker Nodes

**Virtual Nodes** (default in OKE):
- ✅ Fast scaling, no node management
- ❌ No persistent volume support (CSI issues)
- ❌ No DaemonSet support

**Worker Nodes**:
- ✅ Full Kubernetes features
- ✅ Persistent volumes supported
- ✅ DaemonSet support (Dapr, monitoring)
- ❌ Manual node management required

### Dapr on OKE

Dapr is **disabled by default** for OKE virtual nodes. To enable:

1. Use worker node pools
2. Set `dapr.enabled: true` in values-oke.yaml
3. Install Dapr on the cluster:
   ```bash
   helm repo add dapr https://dapr.github.io/helm-charts/
   helm install dapr dapr/dapr --namespace dapr-system --create-namespace
   ```

### Database Options

For production, use managed services:

1. **Oracle Autonomous Database** (recommended)
2. **Oracle Cloud PostgreSQL** (managed)
3. **External** (Neon, Supabase, AWS RDS)

Update the connection string secret accordingly.

## Monitoring

### OCI Application Performance Monitoring

```bash
# Enable APM integration
kubectl create configmap apm-config \
  --from-literal=apm-domain='your-apm-domain' \
  -n actionmindai
```

### Logs

```bash
# View logs with OCI Logging
kubectl logs -n actionmindai -l app.kubernetes.io/component=backend --tail=100 -f
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod for events
kubectl describe pod -n actionmindai <pod-name>

# Check node resources
kubectl top nodes

# Check events
kubectl get events -n actionmindai --sort-by='.lastTimestamp'
```

### CSI Driver Issues

If you see CSINode errors:
- Use virtual nodes without PVCs
- Or add worker node pool with CSI enabled
- Use managed database services

### Image Pull Errors

```bash
# Create image pull secret for private registries
kubectl create secret docker-registry registry-credentials \
  --docker-server=your-registry \
  --docker-username=your-username \
  --docker-password=your-password \
  -n actionmindai
```

## Scaling

### Horizontal Pod Autoscaler

```bash
# Check HPA status
kubectl get hpa -n actionmindai

# Manually scale
kubectl scale deployment/backend -n actionmindai --replicas=5
```

### Cluster Scaling

Via OCI Console or CLI:
```bash
oci ce node-pool update --node-pool-id <id> --quantity 3
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall actionmindai -n actionmindai

# Delete namespace
kubectl delete namespace actionmindai

# Note: Managed databases and load balancers need manual cleanup
```
