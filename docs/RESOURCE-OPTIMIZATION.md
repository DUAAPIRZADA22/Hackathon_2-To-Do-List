# 💪 Resource Optimization Guide
## Run ActionMindAI on Resource-Constrained Systems

**Current Constraints:**
- Docker Desktop: 1.8GB RAM allocated
- C: Drive: 100% capacity (CRITICAL)

---

## 🎯 Immediate Actions

### 1. Free Up Disk Space (CRITICAL - Do This First)

```bash
# PowerShell (Run as Administrator)
# Step 1: Clean Docker system (frees GBs)
docker system prune -a --volumes -f

# Step 2: Remove Windows temporary files
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue

# Step 3: Empty recycle bin
Clear-RecycleBin -Force

# Step 4: Check available space
docker system df
```

**Expected Results:**
- Free 5-10GB disk space
- Docker images removed (will rebuild on deploy)
- System temporary files cleared

### 2. Optimize Docker Desktop Settings

**Open Docker Desktop → Settings → Resources:**

**Memory (RAM):**
- Current: 1.8GB (TOO LOW)
- Minimum Recommended: 4GB
- Ideal: 8GB

**Disk:**
- Current: Unknown
- Minimum: 20GB free
- Ideal: 50GB free

**Action:** If you can't increase resources, use Docker Compose (recommended) instead of Minikube.

---

## 📊 Resource Requirements Comparison

### Docker Compose (Recommended for You)

| Component | Min | Ideal | Your Situation |
|-----------|-----|-------|----------------|
| RAM | 2GB | 4GB | ❌ 1.8GB (need 200MB more) |
| Disk | 2GB | 5GB | ❌ 0GB (100% full) |
| CPU | 2 cores | 4 cores | Unknown |

**Verdict:** With disk cleanup, Docker Compose will work!

### Minikube (NOT Recommended - Requires More Resources)

| Component | Min | Ideal | Your Situation |
|-----------|-----|-------|----------------|
| RAM | 4GB | 8GB | ❌ 1.8GB (impossible) |
| Disk | 20GB | 40GB | ❌ 0GB (impossible) |
| CPU | 2 cores | 4 cores | Unknown |

**Verdict:** Cannot run until you upgrade resources significantly.

---

## 🚀 Optimized Deployment Configuration

### Option 1: Ultra-Lightweight Docker Compose

**Created:** `docker-compose.yml` with optimized settings

**Resource Limits:**
```yaml
Frontend: 512MB limit, 128MB request
Backend:  1GB limit, 256MB request
Total:    1.5GB limit, ~450MB actual usage
```

**This fits in your 1.8GB allocation with ~300MB to spare!**

### Option 2: Further Reduced (If Needed)

**Edit docker-compose.yml:**

```yaml
frontend:
  deploy:
    resources:
      limits:
        memory: 256M  # Reduced from 512M
      reservations:
        memory: 64M   # Reduced from 128M

backend:
  deploy:
    resources:
      limits:
        memory: 512M  # Reduced from 1G
      reservations:
        memory: 128M  # Reduced from 256M
```

**New Total: ~768MB limit, ~250MB actual usage**

---

## 🔄 Docker Compose vs Kubernetes

### Docker Compose ✅ (Choose This)

**Pros:**
- ✅ Works with 1.8GB RAM
- ✅ Lower overhead (~200MB vs ~2GB)
- ✅ Simpler to use
- ✅ Production-ready
- ✅ Easy to debug
- ✅ Faster deployment

**Cons:**
- ❌ No auto-scaling
- ❌ No self-healing
- ❌ Manual service management

**Best For:** Your current situation, development, small deployments

### Kubernetes ❌ (Not Yet)

**Pros:**
- ✅ Auto-scaling
- ✅ Self-healing
- ✅ Advanced features
- ✅ Enterprise-ready

**Cons:**
- ❌ Requires 4GB+ RAM (you have 1.8GB)
- ❌ High overhead (~2GB)
- ❌ Complex to set up
- ❌ Overkill for small deployments

**Best For:** Production, large scale, when you upgrade resources

---

## 🛠️ Prerequisites Checklist

### Before You Deploy:

**Step 1: Free Disk Space**
```bash
docker system prune -a --volumes -f
```

**Step 2: Verify Docker Memory**
```bash
docker info --format "Memory: {{.MemTotal}}"
```

**Step 3: Get Required Services**
- [ ] Neon PostgreSQL (free): https://neon.tech
- [ ] OpenAI API Key: https://platform.openai.com/api-keys

**Step 4: Configure Environment**
```bash
cp .env.production .env
# Edit .env with your secrets
```

---

## 📈 Performance Optimization

### Build Optimization

**Your images are already optimized:**
- Frontend: 273.8 MB ✅ (excellent)
- Backend: 498.14 MB ✅ (good)

**If you need to rebuild smaller:**

```bash
# Use --no-cache for clean builds
docker build --no-cache -t ActionMindAI/frontend:1.0.0 -f frontend/Dockerfile frontend/
docker build --no-cache -t ActionMindAI/backend:1.0.0 -f backend/Dockerfile backend/
```

### Runtime Optimization

**Monitor resource usage:**
```bash
# Real-time stats
docker stats

# Check disk usage
docker system df

# List container sizes
docker ps -s
```

---

## 🎯 Deployment Success Path

### Phase 1: Immediate (Today)

**Action:** Deploy with Docker Compose

**Prerequisites:**
1. Free disk space: `docker system prune -a --volumes -f`
2. Get Neon database
3. Get OpenAI API key
4. Configure .env file

**Execute:**
```bash
./deploy-docker-compose.sh
```

**Time:** 5 minutes

**Resources Used:** ~450MB RAM, ~1GB disk

---

### Phase 2: Stabilization (This Week)

**Action:** Monitor and optimize

**Tasks:**
1. Monitor logs: `docker compose logs -f`
2. Check resource usage: `docker stats`
3. Test all features
4. Fix any issues

**Success Criteria:**
- App loads at http://localhost:3000
- API docs load at http://localhost:8000/docs
- No errors in logs
- Stable performance

---

### Phase 3: Scaling (Future - When Resources Available)

**Action:** Migrate to Kubernetes

**Prerequisites:**
- 8GB+ RAM
- 20GB+ free disk
- Minikube installed

**Execute:**
```bash
# Use existing Helm charts
helm install actionmindai helm/ActionMindAI/
```

**Benefits:**
- Auto-scaling
- Self-healing
- Production-ready
- Cloud migration path

---

## 🔍 Troubleshooting Resource Issues

### Issue: Out of Memory

**Symptoms:**
- Containers restart repeatedly
- "OOMKilled" in logs
- System sluggish

**Solutions:**
```bash
# 1. Check actual usage
docker stats

# 2. Reduce limits in docker-compose.yml
# 3. Stop other containers
docker compose down
docker system prune -f
docker compose up -d
```

### Issue: Out of Disk Space

**Symptoms:**
- "No space left on device"
- Docker build fails
- Can't pull images

**Solutions:**
```bash
# 1. Clean everything
docker system prune -a --volumes -f

# 2. Remove unused images
docker image prune -a -f

# 3. Check disk space
docker system df
```

### Issue: High CPU Usage

**Symptoms:**
- System sluggish
- High CPU in Task Manager

**Solutions:**
```bash
# 1. Check container stats
docker stats

# 2. Reduce CPU limits in docker-compose.yml
# 3. Disable unused features in .env
ENABLE_VOICE_INPUT=false
```

---

## 📊 Resource Monitoring

### Real-Time Monitoring

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Container sizes
docker ps -s

# Logs for errors
docker compose logs -f | grep -i error
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Service status
docker compose ps
```

---

## 🎯 Success Metrics

Your deployment is successful when:

**Resource Usage:**
- ✅ < 1.5GB RAM used
- ✅ < 2GB disk used
- ✅ < 50% CPU usage

**Application Health:**
- ✅ Both containers "Up" in `docker compose ps`
- ✅ Health checks pass
- ✅ No errors in logs
- ✅ App loads in browser

**Performance:**
- ✅ Frontend loads < 3 seconds
- ✅ API response < 1 second
- ✅ No memory leaks

---

## 🚀 Next Steps

1. **Immediate:** Free disk space and deploy with Docker Compose
2. **This Week:** Monitor and optimize
3. **Future:** Migrate to Kubernetes when resources available

**Your Path:**
```
Current State (1.8GB RAM)
    ↓
Docker Compose Deployment ← YOU ARE HERE
    ↓
Monitor & Optimize (This Week)
    ↓
Upgrade Resources (When Possible)
    ↓
Kubernetes Deployment (Future)
```

---

## 📞 Help & Resources

**Documentation:**
- [Deployment Blueprint](./DEPLOYMENT-BLUEPRINT.md)
- [Quick Deploy Guide](../QUICK-DEPLOY.md)

**External Resources:**
- Docker Compose: https://docs.docker.com/compose/
- Neon Database: https://neon.tech/docs
- OpenAI API: https://platform.openai.com/docs

**Critical Reminders:**
1. ⚠️ Free disk space FIRST (C: drive at 100%)
2. ⚠️ Use Docker Compose (NOT Minikube)
3. ⚠️ Monitor resource usage during deployment
4. ⚠️ Start with optimized docker-compose.yml

---

**Version:** 1.0.0
**Last Updated:** 2026-02-02
**Status:** Ready for Immediate Deployment
