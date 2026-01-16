# Quick Start Guide: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Phase**: III
**Last Updated**: 2025-01-09

This guide will help you set up and run the Todo AI Chatbot feature locally.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** installed (for frontend widget)
- **Git** installed
- **Access to Neon PostgreSQL** database
- **OpenRouter API key** (get from https://openrouter.ai/keys)
- **Better Auth** configured from Phase I/II

---

## 1. Environment Setup

### 1.1 Clone Repository

```bash
git clone <repository-url>
cd ActionMindAI
git checkout phase-3
```

### 1.2 Backend Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<database>?sslmode=require

# Better Auth
BETTER_AUTH_SECRET=<your-better-auth-secret>
BETTER_AUTH_URL=http://localhost:3000

# OpenRouter (LLM Provider)
OPENROUTER_API_KEY=sk-or-v1-<your-openrouter-key>
OPENROUTER_MODEL=anthropic/claude-3-haiku

# Application
APP_ENV=development
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000
```

**Get OpenRouter API Key**:
1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Navigate to API Keys
4. Create new key
5. Add to `.env`

### 1.3 Frontend Environment Variables

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

---

## 2. Database Setup

### 2.1 Run Migrations

```bash
cd backend
python -m uvicorn migrations.migrate:run_migrations
```

Or using Alembic:

```bash
cd backend
alembic upgrade head
```

### 2.2 Verify Tables

Connect to Neon PostgreSQL and verify tables exist:

```sql
-- Check tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('tasks', 'conversations', 'messages');

-- Should return:
-- tasks
-- conversations
-- messages
```

---

## 3. Backend Setup

### 3.1 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt** contents:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
asyncpg==0.29.0
alembic==1.13.0
pydantic==2.5.0
pydantic-settings==2.1.0
openai==1.3.0
mcp==0.1.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
httpx==0.25.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

### 3.2 Start Backend Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3.3 Verify Backend

Open browser: http://localhost:8000/docs

You should see FastAPI auto-generated documentation.

---

## 4. Frontend Setup

### 4.1 Install Dependencies

```bash
cd frontend
npm install
```

### 4.2 Integrate Chat Widget

The chatbot-widget-creator Agent Skill provides a production-ready widget.

**Install widget** (if not already integrated):

```bash
cd frontend
npm install @your-org/chatbot-widget
```

### 4.3 Add Chat Page

Create `frontend/src/pages/chat.tsx`:

```tsx
import { ChatWidget } from '@your-org/chatbot-widget';
import { useSession } from 'better-auth-react';

export default function ChatPage() {
  const { user } = useSession();

  if (!user) {
    return <div>Please log in</div>;
  }

  return (
    <ChatWidget
      apiUrl={process.env.NEXT_PUBLIC_API_URL}
      userId={user.id}
      theme="clean"
      streaming={true}
      placeholder="What would you like to remember?"
    />
  );
}
```

### 4.4 Start Frontend

```bash
cd frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 14.0.0
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

---

## 5. Testing the Complete Flow

### 5.1 Open Chat Interface

Navigate to: http://localhost:3000/chat

### 5.2 Authenticate

Sign in using Better Auth (credentials from Phase I/II)

### 5.3 Send Test Messages

Try these natural language commands:

**Create a task**:
```
Remember to buy groceries on Saturday
```

Expected response:
```
I've added "Buy groceries" to your task list with the note "on Saturday".
```

**List tasks**:
```
Show me my pending tasks
```

Expected response:
```
Here are your pending tasks:
1. Buy groceries (on Saturday)
```

**Complete a task**:
```
Mark "Buy groceries" as done
```

Expected response:
```
I've marked "Buy groceries" as complete!
```

**Update a task**:
```
Change the grocery task to include milk and eggs
```

Expected response:
```
I've updated "Buy groceries" with: milk and eggs
```

**Delete a task**:
```
Delete the grocery task
```

Expected response:
```
I've deleted "Buy groceries" from your task list.
```

---

## 6. Verify Statelessness

**Test 1: Refresh Page**
1. Create a task
2. Refresh the browser
3. Ask "What did I ask you to remember?"
4. ✅ Task should still be there (loaded from DB)

**Test 2: Restart Backend**
1. Create a task
2. Stop backend (Ctrl+C)
3. Start backend again
4. Ask "Show me my tasks"
5. ✅ Task should still be there (loaded from DB)

**Test 3: No In-Memory State**
1. Check logs - no "session created" messages
2. Each request should log "loading conversation from DB"
3. ✅ Confirms stateless architecture

---

## 7. Run Tests

### 7.1 Backend Tests

```bash
cd backend
pytest -v
```

Expected output:
```
collected 25 items

tests/unit/test_models.py::test_task_creation PASSED
tests/unit/test_task_tools.py::test_add_task PASSED
tests/integration/test_agent_flow.py::test_complete_flow PASSED
...
=== 25 passed in 3.45s ===
```

### 7.2 Frontend Tests

```bash
cd frontend
npm test
```

---

## 8. Performance Verification

### 8.1 Check Response Times

**Using browser DevTools**:
1. Open Network tab
2. Send a message
3. Check `TTFB` (Time To First Byte)
4. ✅ Should be < 5000ms (5 seconds)

### 8.2 Check Database Query Times

**Using backend logs**:
```
INFO:     Database query completed in 123ms
```
✅ Should be < 500ms

---

## 9. Troubleshooting

### Issue: "Database connection failed"

**Solution**:
1. Verify `DATABASE_URL` in `.env`
2. Check Neon PostgreSQL is accessible
3. Test connection: `psql $DATABASE_URL`

### Issue: "OpenRouter API error"

**Solution**:
1. Verify `OPENROUTER_API_KEY` is set
2. Check key is valid at https://openrouter.ai/keys
3. Check account has credits

### Issue: "CORS error"

**Solution**:
1. Verify `CORS_ORIGINS` in backend `.env`
2. Check frontend URL matches CORS origin
3. Restart backend after changing `.env`

### Issue: "User not authenticated"

**Solution**:
1. Verify Better Auth session cookie is set
2. Check browser cookies for `better-auth.session_token`
3. Verify `BETTER_AUTH_SECRET` matches between frontend/backend

### Issue: "Conversation not found"

**Solution**:
1. This is expected when starting new chat
2. System will create new conversation
3. Check `conversation_id` in response

---

## 10. Production Deployment

### 10.1 Backend Deployment

**Environment Variables** (set in hosting platform):
```bash
DATABASE_URL=<production-neon-url>
OPENROUTER_API_KEY=<production-key>
BETTER_AUTH_SECRET=<production-secret>
APP_ENV=production
LOG_LEVEL=warning
```

**Docker Build**:
```bash
docker build -t actionmind-backend:latest backend/
docker run -p 8000:8000 --env-file .env actionmind-backend:latest
```

### 10.2 Frontend Deployment

**Environment Variables** (set in Vercel/Netlify):
```bash
NEXT_PUBLIC_API_URL=https://api.actionmind.ai
NEXT_PUBLIC_BETTER_AUTH_URL=https://actionmind.ai
```

**Deploy to Vercel**:
```bash
cd frontend
vercel deploy --prod
```

---

## 11. Monitoring & Observability

### 11.1 Backend Logs

**Production**:
```bash
# View logs
docker logs -f actionmind-backend

# Check for errors
docker logs actionmind-backend 2>&1 | grep ERROR
```

### 11.2 Performance Metrics

Monitor these metrics:
- Chat response time p95 < 5s
- Database query time p95 < 500ms
- Error rate < 1%
- Concurrent users supported

---

## 12. Next Steps

After local setup is working:

1. ✅ Run `/sp.tasks` to generate implementation tasks
2. ✅ Review generated `tasks.md`
3. ✅ Begin implementation (after explicit approval)
4. ✅ Run tests for each user story (P1-P5)
5. ✅ Verify all success criteria met
6. ✅ Deploy to phase-3 branch

---

## Support

**Documentation**:
- [Spec](./spec.md) - Feature requirements
- [Plan](./plan.md) - Architecture decisions
- [Data Model](./data-model.md) - Database schema
- [API Contracts](./contracts/chat-api.yaml) - API documentation

**Issues**:
- Open an issue in the repository
- Tag with `phase-3` and `todo-ai-chatbot`

---

**Good luck with Phase III! 🚀**
