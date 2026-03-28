---
id: 002
title: plan-phase-todo-ai-chatbot
stage: plan
date: 2025-01-09
surface: agent
model: glm-4.6
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: hackathon-participant
command: /sp.plan
labels: [planning, architecture, phase-3, mcp, openai-agents, chatbot]
links:
  spec: ../../specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-ai-chatbot/plan.md
  - specs/001-todo-ai-chatbot/research.md
  - specs/001-todo-ai-chatbot/data-model.md
  - specs/001-todo-ai-chatbot/contracts/chat-api.yaml
  - specs/001-todo-ai-chatbot/contracts/mcp-tools.yaml
  - specs/001-todo-ai-chatbot/quickstart.md
tests:
  - Constitution compliance: All 8 gates PASSED
  - Research phase: All 8 technical decisions resolved
  - Design artifacts: Complete (data model, API contracts, quickstart)
---

## Prompt

# sp.plan — Phase III: Todo AI Chatbot
Hackathon II — Spec-Kit Plus (Planning Phase)

==================================================================
PHASE CONFIRMATION
==================================================================

This plan strictly implements **Phase III only**:
➡️ Todo AI Chatbot

All work will:
- Be added to the **existing GitHub repository**
- Be implemented on the **phase-3 branch only**
- Start implementation ONLY after explicit approval

[... full planning prompt continues ...]

## Response snapshot

Created comprehensive implementation plan for Todo AI Chatbot (Phase III) with all design artifacts complete.

**Plan Location**: specs/001-todo-ai-chatbot/plan.md

**Phase 0: Research** ✅ COMPLETE
- Evaluated OpenAI Agents SDK + MCP integration patterns
- Resolved OpenRouter as OpenAI-compatible LLM provider
- Documented SSE streaming with FastAPI
- Researched SQLModel + Neon PostgreSQL best practices
- Designed stateless conversation loading strategy

**Phase 1: Design Artifacts** ✅ COMPLETE
- Created data-model.md with complete database schema (Task, Conversation, Message entities)
- Generated API contracts:
  - chat-api.yaml (OpenAPI 3.0 spec for chat endpoints)
  - mcp-tools.yaml (JSON Schema for all 5 MCP tools)
- Wrote quickstart.md with setup, testing, and deployment instructions
- Updated agent context (CLAUDE.md) with Python 3.11+ and PostgreSQL

**Constitution Compliance**: All 8 gates PASSED
- Spec-Driven Development: All 50 FRs documented with Task ID references
- MCP-First Architecture: All CRUD through MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
- Context Verification: MCP server initialization verification planned
- Scope Boundaries: Phase III scope clearly defined (chatbot, stateless backend, MCP tools)
- SOLID Principles: Clear layer separation (UI → API → Agent → MCP → DB)
- DRY Principle: Reusable chatbot-widget-creator skill, centralized validation
- Modularity: Backend organized by layer with clear module boundaries
- UX Standards: Conversational tone, confirmations, visual feedback

**Project Structure**:
- Web application (backend + frontend widget)
- Backend: Python 3.11+, FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel
- Frontend: JavaScript/TypeScript, React, chatbot-widget-creator skill
- Database: Neon PostgreSQL with SQLModel ORM

**Implementation Phases Defined**:
- Phase 0: Research ✅ COMPLETE
- Phase 1: Foundation ✅ COMPLETE
- Phase 2: Backend Implementation (next)
- Phase 3: Frontend Integration
- Phase 4: Integration & Testing
- Phase 5: Production Readiness

**Technology Decisions**:
| Component | Technology | Justification |
|-----------|-----------|---------------|
| Backend Framework | FastAPI | Async support, type-safe, OpenAPI auto-generation |
| AI Orchestration | OpenAI Agents SDK | Native tool calling, OpenAI-compatible |
| LLM Provider | OpenRouter (Claude/GPT) | OpenAI-compatible API, no subscription needed |
| Tool Protocol | Official MCP SDK | Standardized tool interface, stateless design |
| Database ORM | SQLModel | Type-safe, built on SQLAlchemy 2.0, Pydantic integration |
| Database | Neon PostgreSQL | Serverless, compatible with existing Phase I/II setup |
| Authentication | Better Auth | Existing integration from Phase I/II |
| Frontend Widget | chatbot-widget-creator Agent Skill | Production-ready, reusable, SSE support |
| Streaming | Server-Sent Events (SSE) | Simple, uni-directional, compatible with widget |
| Testing | pytest + httpx | Async test support, FastAPI compatibility |

**Risk Mitigation**:
- AI intent detection: Comprehensive system prompt, confirmation messages
- Performance: Pagination for >100 messages, 60s TTL cache, database indexes
- MCP+OpenAI integration: Early proof-of-concept, fallback pattern
- Statelessness: Streaming SSE for responsiveness, fast DB queries
- Database failures: Retry with exponential backoff, graceful errors

**Success Metrics**:
- Task operations < 10 seconds (SC-001)
- Chat responses < 5 seconds p95 (SC-008)
- DB queries < 500ms p95 (SC-010)
- Support 1000 concurrent users (SC-009)
- Zero cross-user data leakage (SC-012)
- SOLID principles compliance (SC-016)
- Production-ready error handling (SC-019)

## Outcome

- ✅ Impact: Complete architectural plan for Phase III Todo AI Chatbot ready for implementation
- 🧪 Tests: Constitution compliance verified (8/8 gates passed), research complete (8/8 decisions), design artifacts generated (6 files)
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, chat-api.yaml, mcp-tools.yaml, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation task breakdown, then await explicit approval before starting Phase 2: Backend Implementation
- 🧠 Reflection: Successfully created comprehensive architectural plan following Spec-Kit Plus methodology. All constitution gates passed without violations. Technology stack selected balances hackathon constraints (no subscriptions, production-grade) with architectural principles (SOLID, DRY, stateless). Clear roadmap defined for 5 implementation phases with measurable success criteria.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution compliance PASSED (8/8 gates)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run `/sp.tasks` to generate implementation task list with clear acceptance criteria for each development phase
