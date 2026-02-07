# 🚀 ActionMindAI Deployment Blueprint
## Cloud-Native Production Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2026-02-02
**Branch:** 001-kubernetes-deployment

---

## 📊 Executive Summary

### Current Situation
- **Constraint:** Docker Desktop allocated 1.8GB RAM (insufficient for Minikube)
- **Disk Space:** C: drive at 100% capacity (CRITICAL)
- **Images Built:** Frontend (273.8 MB), Backend (498.14 MB) ✅
- **Helm Charts:** Complete and ready for future Kubernetes deployment

### Recommended Approach: Docker Compose (Production-Ready)
- ✅ **Resource Efficient:** ~200MB overhead vs ~2GB for Minikube
- ✅ **Production Grade:** Used by thousands of companies in production
- ✅ **Cloud Native:** Follows container orchestration best practices
- ✅ **Immediate Value:** Deploy NOW without infrastructure changes
- ✅ **Future Proof:** Easy migration path to Kubernetes

---

## 🎯 Deployment Options Comparison

| Option | Resource Usage | Complexity | Production Ready | Time to Deploy | Best For |
|--------|---------------|------------|------------------|----------------|----------|
| **Docker Compose** | ~200MB RAM | Low | ✅ Yes | < 5 min | **Immediate deployment, resource-constrained environments** |
| Minikube | ~2GB RAM | Medium | ❌ Dev only | ~10 min | Local Kubernetes development |
| Cloud Kubernetes (AKS/GKE/EKS) | Variable | High | ✅ Yes | ~30 min | Production scaling, enterprise |

**Recommendation:** Start with Docker Compose, migrate to Kubernetes when resources available.

---

## 📋 Prerequisites Checklist

### Required
- [ ] Docker Desktop installed and running
- [ ] Git Bash or WSL2 (Windows) or Terminal (Mac/Linux)
- [ ] 2GB free disk space (you need to free up space on C: drive!)
- [ ] External PostgreSQL database (Neon recommended - free tier available)

### Required Services
- [ ] **Neon PostgreSQL** - Get free database at https://neon.tech
- [ ] **OpenAI API Key** - Get at https://platform.openai.com/api-keys

### Optional but Recommended
- [ ] Gemini API Key (alternative LLM) - https://aistudio.google.com/apikey
- [ ] ChatKit Workflow ID - https://platform.openai.com/agent-builder

---

## 🚀 Quick Start: Docker Compose Deployment

### Step 1: Free Up Disk Space (CRITICAL)

Your C: drive is at 100% capacity. You MUST free up space before deploying:

```bash
# On Windows, run these commands in PowerShell as Administrator:
# Clean temporary files
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue

# Clean Docker system (frees up GBs)
docker system prune -a --volumes

# Check available space after cleanup
docker system df
```

### Step 2: Configure Environment

```bash
# Copy the production environment template
cp .env.production .env

# Edit .env with your actual values
# REQUIRED VARIABLES:
# - DATABASE_URL (from Neon)
# - OPENAI_API_KEY (from OpenAI)
# - BETTER_AUTH_SECRET (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### Step 3: Deploy Application

```bash
# Make deployment script executable (Git Bash/WSL)
chmod +x deploy-docker-compose.sh

# Run deployment
./deploy-docker-compose.sh
```

**Or manually:**

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

### Step 4: Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🔧 Manual Deployment Steps

If the automated script fails, follow these steps:

### 1. Verify Docker Images

```bash
# List available images
docker images | grep ActionMindAI

# Expected output:
# ActionMindAI/frontend   1.0.0   273.8 MB
# ActionMindAI/backend    1.0.0   498.14 MB
```

### 2. Build Images if Missing

```bash
# Build frontend
docker build -t ActionMindAI/frontend:1.0.0 -f frontend/Dockerfile frontend/

# Build backend
docker build -t ActionMindAI/backend:1.0.0 -f backend/Dockerfile backend/
```

### 3. Create .env File

```bash
cat > .env << 'EOF'
# Database (get from https://neon.tech)
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# OpenAI (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Auth Secret (generate with python -c "import secrets; print(secrets.token_urlsafe(32))")
BETTER_AUTH_SECRET=your-random-secret-here

# URLs
FRONTEND_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ChatKit (optional)
CHATKIT_ENABLED=true
EOF
```

### 4. Start Services

```bash
# Start in detached mode
docker compose up -d

# Watch logs
docker compose logs -f

# Check health
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 🌐 Cloud Deployment Options

When you're ready for cloud deployment, here are your options:

### Option 1: Vercel + Railway (Easiest)

**Frontend → Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel
```

**Backend → Railway**
```bash
# Install Railway CLI
npm i -g railway

# Deploy backend
railway login
railway init
railway up
```

### Option 2: Render (All-in-One)

```bash
# Deploy both frontend and backend
# Visit https://render.com and connect your repo
# Render automatically detects Dockerfile and deploys
```

### Option 3: AWS ECS (Production)

```bash
# Use existing Docker images
# Push to ECR (Elastic Container Registry)
# Deploy to ECS (Elastic Container Service)
# Requires AWS account setup
```

---

## 🔄 Migration Path to Kubernetes

When you have more resources (8GB+ RAM), migrate to Kubernetes:

### Prerequisites for Kubernetes
- 8GB+ RAM allocated to Docker Desktop
- 20GB+ free disk space
- Minikube or Kind installed

### Migration Steps

1. **Increase Docker Desktop Resources:**
   - Open Docker Desktop → Settings → Resources
   - Increase memory to 8GB
   - Increase disk to 50GB

2. **Start Minikube:**
   ```bash
   minikube start --driver=docker --memory=6144 --cpus=2
   ```

3. **Use Existing Helm Charts:**
   ```bash
   # Your Helm charts are already ready at helm/ActionMindAI/
   helm install actionmindai helm/ActionMindAI/ \
     --set secrets.databaseUrl="$DATABASE_URL" \
     --set secrets.openaiApiKey="$OPENAI_API_KEY" \
     --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET"
   ```

---

## 🧪 Troubleshooting

### Issue: Docker "No space left on device"

**Solution:**
```bash
# Clean Docker system
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Check disk usage
docker system df
```

### Issue: Services not starting

**Diagnose:**
```bash
# Check service status
docker compose ps

# View logs
docker compose logs frontend
docker compose logs backend

# Restart services
docker compose restart
```

### Issue: Database connection errors

**Check:**
1. DATABASE_URL is correctly set in .env
2. Neon database is active (check Neon console)
3. SSL mode is enabled (sslmode=require)
4. Network connectivity

```bash
# Test database connection
docker compose exec backend python -c "
from sqlalchemy import create_engine
engine = create_engine('DATABASE_URL')
conn = engine.connect()
print('Database connection successful!')
"
```

### Issue: Port already in use

**Solution:**
```bash
# Check what's using port 3000 or 8000
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Stop conflicting service or change ports in docker-compose.yml
```

---

## 📊 Resource Optimization

### Current Resource Usage (Docker Compose)

| Service | CPU Limit | Memory Limit | Actual Usage |
|---------|-----------|--------------|--------------|
| Frontend | 0.5 CPU | 512MB | ~150MB |
| Backend | 1.0 CPU | 1GB | ~300MB |
| **Total** | **1.5 CPU** | **1.5GB** | **~450MB** |

### Optimization Tips

1. **Reduce Memory Limits:**
   ```yaml
   # In docker-compose.yml, if needed
   deploy:
     resources:
       limits:
         memory: 256M  # Reduced from 512M
   ```

2. **Use Single Replica:**
   ```yaml
   # For development, remove replicas
   # (Docker Compose defaults to 1)
   ```

3. **Disable Unused Features:**
   ```bash
   # In .env
   ENABLE_VOICE_INPUT=false
   CHATKIT_ENABLED=false
   ```

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore (already configured)
.env
.env.local
.env.*.local
```

### 2. Use Environment Variables

```bash
# Pass secrets at runtime, not build time
docker compose run --rm backend env
```

### 3. Rotate Secrets Regularly

```bash
# Generate new auth secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env and restart
docker compose restart backend
```

---

## 📈 Monitoring and Observability

### View Logs

```bash
# Follow all logs
docker compose logs -f

# Specific service
docker compose logs -f frontend
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Docker health status
docker compose ps
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

---

## 🎯 Success Criteria

Deployment is successful when:

- [ ] Both containers are running: `docker compose ps` shows "Up"
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Frontend is accessible: http://localhost:3000 loads
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] No errors in logs: `docker compose logs` shows no ERROR/WARNING
- [ ] Database connectivity confirmed (check logs)

---

## 🆘 Getting Help

### Resources

- **Docker Compose Docs:** https://docs.docker.com/compose/
- **Neon Database Docs:** https://neon.tech/docs
- **OpenAI API Docs:** https://platform.openai.com/docs

### Common Issues

1. **Port conflicts:** Change ports in docker-compose.yml
2. **Memory issues:** Close other applications, increase Docker Desktop memory
3. **Network issues:** Check firewall settings
4. **Database errors:** Verify DATABASE_URL format

---

## 📝 Next Steps

After successful deployment:

1. ✅ Test application functionality
2. ✅ Set up monitoring/alerts
3. ✅ Configure backup strategy
4. ✅ Plan Kubernetes migration (when resources available)
5. ✅ Set up CI/CD pipeline

---

## 🔄 Rollback Procedure

If deployment fails:

```bash
# Stop all services
docker compose down

# Remove volumes (if needed)
docker compose down -v

# Restart previous version
docker compose up -d
```

---

**Deployment Blueprint Version:** 1.0.0
**Last Updated:** 2026-02-02
**Maintained By:** ActionMindAI Team
