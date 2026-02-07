# ActionMindAI Kubernetes Production Checklist

Verify that all production-ready requirements are met before deploying to cloud environments (AKS/GKE/OKE).

## Production Readiness Checklist

### Security

- [ ] **Non-root user execution** - Containers run as non-root user
  - Frontend: UID 1001 (nextjs)
  - Backend: UID 1000 (appuser)
  - [x] `runAsNonRoot: true` in securityContext
  - [x] `runAsUser` specified in deployment templates

- [ ] **Security contexts configured**
  - [x] Pod-level securityContext applied
  - [x] `allowPrivilegeEscalation: false`
  - [x] `readOnlyRootFilesystem: true` (frontend)
  - [x] `fsGroup` specified for volume permissions

- [ ] **Secrets management**
  - [x] Secrets stored in Kubernetes Secret resource
  - [x] secrets.yaml.example provided (safe to commit)
  - [x] secrets.yaml in .gitignore (actual secrets)
  - [x] No hardcoded secrets in values.yaml

- [ ] **Network policies** (TODO - recommended for production)
  - [ ] Restrict pod-to-pod communication
  - [ ] Allow only necessary ingress/egress traffic

### Reliability

- [ ] **Resource limits and requests**
  - [x] CPU/memory requests defined for all pods
  - [x] CPU/memory limits defined for all pods
  - Frontend: 100m/128Mi requests, 500m/512Mi limits
  - Backend: 200m/256Mi requests, 1000m/1Gi limits

- [ ] **Health checks**
  - [x] Liveness probes configured (backend)
  - [x] Readiness probes configured (frontend & backend)
  - [x] Proper timeouts and thresholds set

- [ ] **High availability**
  - [x] Multiple replicas configured (2 each)
  - [x] PodDisruptionBudget enabled (minAvailable: 1)
  - [x] HorizontalPodAutoscaler templates available (disabled by default)

- [ ] **Deployment strategy** (TODO - optional)
  - [ ] Consider using RollingUpdate with maxSurge/maxUnavailable
  - [ ] Configure maxUnavailable for zero-downtime deployments

### Observability

- [ ] **Logging**
  - [ ] Structured JSON logging configured
  - [ ] Log aggregation integration (Loki/ELK/cloud provider)

- [ ] **Monitoring**
  - [ ] Prometheus metrics enabled (if using metrics-server)
  - [ ] Custom application metrics exposed
  - [ ] Alerting rules configured

- [ ] **Tracing** (TODO - optional)
  - [ ] Distributed tracing integration (Jaeger/Zipkin)

### Performance

- [ ] **Resource optimization**
  - [x] Multi-stage Docker builds implemented
  - [ ] Image size verification (< 500MB target)
  - [ ] Resource usage profiling completed

- [ ] **Autoscaling**
  - [x] HPA templates created
  - [ ] HPA enabled (set `autoscaling.enabled: true`)
  - [ ] Target metrics tuned (CPU: 80%, Memory: 80%)

### Deployment

- [ ] **Helm chart quality**
  - [x] Chart metadata complete (Chart.yaml)
  - [x] Values schema documented (values.yaml)
  - [x] Template helpers defined (_helpers.tpl)
  - [x] Labels and selectors consistent
  - [ ] Chart linted: `helm lint ./helm/ActionMindAI`
  - [ ] Templates validated: `helm template actionmindai ./helm/ActionMindAI`

- [ ] **Image versioning**
  - [ ] Pin specific image tags (avoid `latest` in production)
  - [ ] Use semantic versioning (e.g., `v1.0.0`)
  - [ ] Tag images with git commit SHA for traceability

- [ ] **Ingress configuration**
  - [x] Ingress resource created
  - [x] nginx ingress class specified
  - [ ] TLS certificates configured (cert-manager/Let's Encrypt)
  - [ ] Custom domain configured

### Infrastructure

- [ ] **Cluster setup**
  - [ ] Kubernetes cluster provisioned (Minikube/AKS/GKE/OKE)
  - [ ] kubectl configured and credentials valid
  - [ ] Helm 3.x installed
  - [ ] Ingress controller installed (nginx)
  - [ ] Cert-manager installed (for TLS)

- [ ] **Database**
  - [ ] PostgreSQL instance provisioned
  - [ ] DATABASE_URL configured in secrets
  - [ ] Connection pooling configured
  - [ ] Backup strategy defined

- [ ] **External services**
  - [ ] OpenAI API key configured and valid
  - [ ] Better Auth secret generated (`openssl rand -base64 32`)

## Pre-Deployment Commands

```bash
# 1. Lint the Helm chart
helm lint ./helm/ActionMindAI

# 2. Render templates (dry-run)
helm template actionmindai ./helm/ActionMindAI \
  --values helm/ActionMindAI/secrets.yaml \
  --namespace actionmindai \
  --debug

# 3. Create namespace
kubectl create namespace actionmindai

# 4. Create secrets from file
kubectl create secret generic actionmindai-secrets \
  --from-literal=databaseUrl='postgresql://user:pass@host:5432/db' \
  --from-literal=openaiApiKey='sk-your-key' \
  --from-literal=betterAuthSecret='your-secret' \
  --namespace actionmindai

# 5. Install/upgrade the release
helm upgrade --install actionmindai ./helm/ActionMindAI \
  --values helm/ActionMindAI/secrets.yaml \
  --namespace actionmindai \
  --wait \
  --timeout 5m

# 6. Verify deployment
kubectl get pods -n actionmindai
kubectl get services -n actionmindai
kubectl get ingress -n actionmindai

# 7. Check logs
kubectl logs -l app.kubernetes.io/component=backend -n actionmindai
kubectl logs -l app.kubernetes.io/component=frontend -n actionmindai
```

## Post-Deployment Verification

```bash
# 1. Check all pods are running
kubectl get pods -n actionmindai

# 2. Check services
kubectl get svc -n actionmindai

# 3. Check ingress
kubectl get ingress -n actionmindai
kubectl describe ingress actionmindai-ingress -n actionmindai

# 4. Port forward to test locally (optional)
kubectl port-forward -n actionmindai svc/actionmindai-frontend 3000:3000

# 5. Test health endpoints
kubectl exec -n actionmindai deployment/actionmindai-backend -- curl http://localhost:8000/health
```

## Rollback Procedure

```bash
# List Helm releases
helm list -n actionmindai

# View revision history
helm history actionmindai -n actionmindai

# Rollback to previous version
helm rollback actionmindai 1 -n actionmindai

# Or rollback to specific revision
helm rollback actionmindai <revision> -n actionmindai
```

## Anti-Patterns to Avoid

- ❌ Using `latest` tag in production - Pin specific versions
- ❌ Hardcoding secrets in values.yaml - Use Kubernetes secrets
- ❌ Running containers as root - Use non-root security contexts
- ❌ No resource limits - Pods can consume unlimited resources
- ❌ Missing health probes - Pods won't restart on failure
- ❌ Committing secrets.yaml to git - Use .gitignore and example files
- ❌ Disabling PodDisruptionBudget - Risk of downtime during updates

## Additional Resources

- **AIOps Documentation**: `helm/ActionMindAI/docs/aiops.md`
- **Helm Best Practices**: https://helm.sh/docs/chart_best_practices/
- **Kubernetes Security**: https://kubernetes.io/docs/concepts/security/
- **Pod Security Standards**: https://kubernetes.io/docs/concepts/security/pod-security-standards/
