# Quickstart: Todo AI Chatbot

**Feature**: 002-todo-ai-chatbot
**Phase**: 1 (Design & Contracts)

This guide will help you set up and run the Todo AI Chatbot application from scratch.

## Prerequisites

### Required Software

- **Node.js** 20+ and **pnpm** (for frontend)
- **Python** 3.13+ and **uv** (for backend)
- **Docker** and **Docker Compose** (for local PostgreSQL)
- **Git** for version control

### Required Accounts

1. **Neon Database** (free tier): https://neon.tech
   - Sign up and create a new project
   - Save your connection string

2. **Google AI Studio** (free): https://aistudio.google.com
   - Get your Gemini API key
   - Enable Gemini 2.0 Flash Exp model

3. **OpenRouter** (optional fallback): https://openrouter.ai
   - For fallback LLM provider

## Project Structure

```
ActionMindAI/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── agent/          # AI agent and tools
│   │   ├── api/            # API endpoints
│   │   ├── auth/           # Authentication middleware
│   │   ├── db/             # Database models and repositories
│   │   ├── mcp/            # MCP tool implementations
│   │   └── main.py         # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.template
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities and auth
│   ├── package.json
│   └── .env.local.template
│
└── specs/002-todo-ai-chatbot/  # This specification
```

## Step 1: Backend Setup

### 1.1 Create Virtual Environment

```powershell
cd backend
python -m venv venv
.\\venv\\Scripts\\activate
```

### 1.2 Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Key dependencies**:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `sqlmodel` - ORM
- `openai` - OpenAI Agents SDK
- `openai-agents` - Agents framework
- `chatkit-python` - ChatKit integration
- `asyncpg` - PostgreSQL async driver
- `python-multipart` - Form data parsing
- `python-dotenv` - Environment variables

### 1.3 Configure Environment

```powershell
cp .env.template .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?sslmode=require

# LLM Provider (Gemini - Primary)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: OpenRouter Fallback
OPENROUTER_API_KEY=your_openrouter_key_here

# Better Auth Secret (generate one)
BETTER_AUTH_SECRET=your_random_secret_min_32_chars

# Better Auth URL (for production)
# BETTER_AUTH_URL=https://your-domain.com

# CORS Settings (for development)
FRONTEND_URL=http://localhost:3000
```

**Generate Better Auth Secret**:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 1.4 Initialize Database

```powershell
# Run database initialization
python -m src.db.init_db
```

This will:
- Create all tables (users, tasks, conversations, messages)
- Create all indexes
- Verify foreign key constraints

### 1.5 Start Backend Server

```powershell
# Development (with auto-reload)
python start_server.py

# Or with uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Verify it's running:
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok","timestamp":"2025-01-12T10:00:00Z"}
```

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```powershell
cd frontend
pnpm install
```

**Key dependencies**:
- `next` - React framework
- `@openai-chatkit/react` - ChatKit UI components
- `better-auth/react` - Authentication
- `@radix-ui/*` - UI primitives
- `tailwindcss` - Styling
- `typescript` - Type safety

### 2.2 Configure Environment

```powershell
cp .env.local.template .env.local
```

Edit `.env.local`:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=match_backend_secret
```

**IMPORTANT**: `BETTER_AUTH_SECRET` must match backend!

### 2.3 Start Development Server

```powershell
pnpm dev
```

Visit http://localhost:3000

## Step 3: Test the Application

### 3.1 Create Test Account

1. Click "Sign Up" on the frontend
2. Enter email and password
3. Verify you're redirected to dashboard

### 3.2 Test Natural Language Commands

Try these commands in the chat:

```
"Add a task to buy groceries"
"Show me my pending tasks"
"Mark the buy groceries task as complete"
"What tasks do I have?"
"Delete the groceries task"
```

### 3.3 Verify Database Operations

```sql
-- Check tasks were created
SELECT * FROM tasks ORDER BY created_at DESC LIMIT 5;

-- Check conversation history
SELECT c.title, m.role, m.content, m.created_at
FROM conversations c
JOIN messages m ON m.conversation_id = c.id
ORDER BY m.created_at ASC
LIMIT 20;
```

## Step 4: Docker Deployment (Optional)

### 4.1 Backend Docker

```powershell
cd backend
docker build -t todo-ai-chatbot-backend .
docker run -d -p 8000:8000 --env-file .env todo-ai-chatbot-backend
```

### 4.2 Docker Compose (Full Stack)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=todo_user
      - POSTGRES_PASSWORD=todo_pass
      - POSTGRES_DB=todo_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run:
```powershell
docker-compose up -d
```

## Step 5: Production Deployment

### Backend (Vercel/Railway/Render)

1. Set environment variables in platform
2. Deploy backend URL
3. Update frontend `NEXT_PUBLIC_API_URL`

### Frontend (Vercel)

```powershell
cd frontend
vercel --prod
```

### Database (Neon)

Neon is already production-ready. Just:
1. Use your production connection string
2. Enable connection pooling if needed

## Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```powershell
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Database connection failed**:
- Verify `DATABASE_URL` is correct
- Check Neon console for connection issues
- Ensure `sslmode=require` for Neon

**LLM API errors**:
- Verify `GEMINI_API_KEY` is set
- Check Google AI Studio quotas
- Try OpenRouter fallback if configured

### Frontend Issues

**CORS errors**:
- Ensure `FRONTEND_URL` in backend `.env` matches frontend URL
- Check backend CORS middleware configuration

**Authentication issues**:
- Ensure `BETTER_AUTH_SECRET` matches on both frontend and backend
- Clear cookies and try again

**Build errors**:
```powershell
rm -rf node_modules .next
pnpm install
pnpm build
```

## API Testing

### Test Chat Endpoint

```powershell
$headers = @{
  "x-session-token" = "your_session_token"
  "Content-Type" = "application/json"
}

$body = @{
  message = "Add a task to test the API"
  conversation_id = $null
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/test-user/chat" `
  -Method Post -Headers $headers -Body $body
```

### Test MCP Tools Directly

Tools are available at `/api/{user_id}/tools`:

```powershell
# Add task
Invoke-RestMethod -Uri "http://localhost:8000/api/test-user/tools/add_task" `
  -Method Post -Body '{"title":"Test task"}' -Headers $headers
```

## Development Tips

### Hot Reload

- **Backend**: Auto-reloads on file changes (uvicorn --reload)
- **Frontend**: Auto-reloads with Fast Refresh (Next.js dev)

### Debugging

**Backend logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend debug**:
- Open browser DevTools
- Network tab shows all API calls
- Console shows errors

### Database Access

```powershell
# Connect to Neon directly
psql $DATABASE_URL

# Or use DBeaver, pgAdmin, etc.
```

## Next Steps

After quickstart:

1. **Review architecture**: Read `plan.md` for system design
2. **Customize AI agent**: Modify `src/agent/agent.py` for custom behavior
3. **Add more tools**: Extend MCP tools in `src/mcp/tools/`
4. **Style customization**: Edit `frontend/src/app/globals.css`

## Resources

- **Project spec**: `specs/002-todo-ai-chatbot/spec.md`
- **Architecture plan**: `specs/002-todo-ai-chatbot/plan.md`
- **Data model**: `specs/002-todo-ai-chatbot/data-model.md`
- **API contracts**: `specs/002-todo-ai-chatbot/contracts/`
- **Research notes**: `specs/002-todo-ai-chatbot/research.md`

## Support

For issues or questions:
1. Check this quickstart's troubleshooting section
2. Review architecture plan for design decisions
3. Check logs in both backend and frontend
4. Verify all environment variables are set correctly
