# ⚡ Quick Deploy Guide
## Deploy ActionMindAI in 5 Minutes

**CRITICAL:** Your C: drive is at 100% capacity. Free up disk space FIRST!

---

## Step 1: Free Disk Space (2 min)

```bash
# Run in PowerShell as Administrator
docker system prune -a --volumes
```

---

## Step 2: Configure Environment (2 min)

```bash
# Get free database: https://neon.tech (free tier)
# Get API key: https://platform.openai.com/api-keys

# Copy environment template
cp .env.production .env

# Edit .env and set these 3 required values:
# 1. DATABASE_URL (from Neon)
# 2. OPENAI_API_KEY (from OpenAI)
# 3. BETTER_AUTH_SECRET (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
```

---

## Step 3: Deploy (1 min)

```bash
# Automated deployment
chmod +x deploy-docker-compose.sh
./deploy-docker-compose.sh
```

**Or manual:**
```bash
docker compose up -d
docker compose logs -f
```

---

## Step 4: Access

- **App:** http://localhost:3000
- **API:** http://localhost:8000/docs

---

## Troubleshooting

**No space left:**
```bash
docker system prune -a --volumes
```

**Services not starting:**
```bash
docker compose logs -f
```

**Port already in use:**
```bash
netstat -ano | findstr :3000
# Change ports in docker-compose.yml if needed
```

---

## Stop Services

```bash
docker compose down
```

---

## Full Documentation

See [docs/DEPLOYMENT-BLUEPRINT.md](./docs/DEPLOYMENT-BLUEPRINT.md) for complete guide.
