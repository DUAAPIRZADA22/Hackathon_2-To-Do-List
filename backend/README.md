# ActionMind AI - Todo AI Chatbot Backend

**Phase III**: AI-powered conversational todo management with MCP (Model Context Protocol) and OpenAI Agents SDK.

## Architecture Overview

```
Frontend (ChatKit) → FastAPI → OpenAI Agent → MCP Tools → Neon PostgreSQL
```

### Key Technologies

- **FastAPI 0.104.1**: Async Python web framework
- **SQLModel 0.0.14**: Type-safe ORM (SQLAlchemy 2.0 + Pydantic)
- **Neon PostgreSQL**: Serverless PostgreSQL database
- **OpenAI Agents SDK 1.3.0**: AI orchestration with tool calling
- **OpenRouter API**: OpenAI-compatible LLM provider (Claude/GPT)
- **MCP Protocol**: Model Context Protocol for tool abstraction
- **Better Auth**: Authentication integration (from Phase I/II)

## Project Structure

```
backend/
├── src/
│   ├── api/           # FastAPI endpoints (chat.py, dependencies.py)
│   ├── agent/         # OpenAI Agents SDK integration
│   ├── mcp/           # MCP server and tools
│   │   └── tools/     # Individual MCP tools (task_tools.py)
│   ├── db/            # Database models and repositories
│   └── auth/          # Authentication middleware
├── tests/             # pytest test suite
│   ├── contract/      # API contract tests
│   ├── integration/   # Integration tests
│   └── unit/          # Unit tests
├── requirements.txt   # Python dependencies
├── pytest.ini         # Test configuration
├── Dockerfile         # Production deployment
└── .env.template      # Environment variables template
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Neon PostgreSQL account (free tier available)
- OpenRouter API key ([https://openrouter.ai](https://openrouter.ai))
- Better Auth configuration (from Phase I/II)

### 2. Environment Setup

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your values:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - OPENROUTER_API_KEY: Your OpenRouter API key
# - BETTER_AUTH_SECRET: Your auth secret (from Phase I/II)
# - CORS_ORIGINS: Frontend URLs (default: http://localhost:3000)
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Run database migrations
# (See database/migrations/ directory)
```

### 5. Run Development Server

```bash
# Start FastAPI with auto-reload
uvicorn src.main:app --reload --port 8000
```

API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Redoc**: http://localhost:8000/redoc

## API Endpoints

### Chat Endpoint (Main)

```http
POST /api/{user_id}/chat
Content-Type: application/json

{
  "message": "Remember to buy groceries on Saturday",
  "conversation_id": "uuid-or-null"
}
```

**Response** (SSE streaming):
```json
{
  "conversation_id": "uuid",
  "response": "I've added that task for you!",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Buy groceries", "description": "..."}
    }
  ]
}
```

### Health Check

```http
GET /health
```

## MCP Tools

All task operations go through MCP tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create new task | user_id, title, description (optional) |
| `list_tasks` | List tasks | user_id, status (all/pending/completed) |
| `complete_task` | Mark task complete | user_id, task_id |
| `update_task` | Update task | user_id, task_id, title (optional), description (optional) |
| `delete_task` | Delete task | user_id, task_id |

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Contract tests (API schemas)
pytest -m contract

# With coverage report
pytest --cov=src --cov-report=html
```

### Test Organization

- **Unit Tests**: `tests/unit/` - Isolated component tests
- **Integration Tests**: `tests/integration/` - Multi-component tests
- **Contract Tests**: `tests/contract/` - API schema validation

## Deployment

### Docker (Production)

```bash
# Build image
docker build -t actionmind-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENROUTER_API_KEY="sk-or-..." \
  actionmind-backend
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key |
| `OPENROUTER_MODEL` | No | Model to use (default: anthropic/claude-3-haiku) |
| `BETTER_AUTH_SECRET` | Yes | Auth secret key |
| `BETTER_AUTH_URL` | Yes | Auth service URL |
| `CORS_ORIGINS` | No | Allowed CORS origins (comma-separated) |
| `APP_ENV` | No | Environment (development/production) |
| `LOG_LEVEL` | No | Logging level (info/debug/error) |

## Troubleshooting

### Database Connection Issues

```bash
# Test Neon connection
psql $DATABASE_URL

# Check connection string format
# Should be: postgresql+asyncpg://user:password@host:port/database
```

### OpenRouter API Errors

- Verify API key at [OpenRouter Keys](https://openrouter.ai/keys)
- Check model name: `anthropic/claude-3-haiku` or similar
- Ensure sufficient credits in OpenRouter account

### MCP Tool Errors

- All MCP tools require `user_id` parameter
- Tools enforce user ownership (users can only access their own data)
- Check `backend/src/mcp/tools/task_tools.py` for error messages

### SSE Streaming Not Working

- Verify frontend uses `EventSource` or `fetch` with streaming
- Check CORS headers include frontend origin
- Ensure conversation_id is passed for existing conversations

## Development Notes

### Stateless Design

**IMPORTANT**: This backend is fully stateless. All conversation state is persisted in the Neon PostgreSQL database. No in-memory session storage.

### User Identity Enforcement

User identity is enforced at **ALL layers**:
1. API layer (FastAPI dependencies)
2. Agent layer (OpenAI Agents context)
3. MCP tool layer (all tools require user_id)

### MCP-First Architecture

All CRUD operations must go through MCP tools. The agent only orchestrates - it never accesses the database directly.

## Related Documentation

- [Specification](../specs/001-todo-ai-chatbot/spec.md)
- [Implementation Plan](../specs/001-todo-ai-chatbot/plan.md)
- [Data Model](../specs/001-todo-ai-chatbot/data-model.md)
- [API Contracts](../specs/001-todo-ai-chatbot/contracts/chat-api.yaml)
- [MCP Tools Schema](../specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml)
- [Quick Start Guide](../specs/001-todo-ai-chatbot/quickstart.md)

## License

MIT
