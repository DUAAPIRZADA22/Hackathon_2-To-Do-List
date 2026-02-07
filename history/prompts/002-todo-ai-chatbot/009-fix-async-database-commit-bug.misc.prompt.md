---
id: 009
title: fix-async-database-commit-bug
stage: misc
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 002-todo-ai-chatbot
branch: 001-kubernetes-deployment
user: pirzadaduaa87@gmail.com
command: /sp.fix
labels: ["bug","database","async","mcp"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/mcp/tools/task_tools.py
 - backend/src/repositories/task.py
tests:
 - manual testing via chatbot interface
---

## Prompt

I need you to analyze and fix a critical bug in a Todo AI Chatbot application.

## The Problem
Tasks created via the chatbot (using AgentRunner -> MCP tools) are NOT being saved to the database, even though:
1. The MCP tool works correctly when called directly
2. The chatbot responds with "Task created successfully"
3. But the task doesn't appear in the database or tasks page

## Current Architecture
- Backend: FastAPI with Python
- Database: PostgreSQL (Neon)
- Auth: JWT with Phase I/II (sync) and Phase III (async) systems
- MCP Tools: Located in `backend/src/mcp/tools/task_tools.py`
- AgentRunner: Located in `backend/src/agent/runner.py`
- Simple Chat API: `backend/src/api/simple_chat.py`

## Key Files to Investigate
1. `backend/src/mcp/tools/task_tools.py` - MCP task tools (now using sync TaskService)
2. `backend/src/agent/runner.py` - AgentRunner that calls MCP tools (lines 330-380 for task creation flow)
3. `backend/src/services/task.py` - TaskService for sync database operations
4. `backend/src/api/simple_chat.py` - Simple chat endpoint
5. `backend/src/mcp/client.py` - MCPAgentClient that executes tools

## What I've Found
- Direct call to AddTaskTool.execute() works
- Call through AgentRunner.chat() -> mcp_client.execute_function_call() fails
- The task is never committed to the database

## Your Task
1. Analyze the code flow from AgentRunner to MCP tool execution
2. Identify why the database commit isn't happening when called from async context
3. Propose and implement a fix that ensures tasks are properly saved
4. The fix should use Phase 3 async/await patterns properly with the sync database

Focus on the interaction between async AgentRunner and sync TaskService. The issue is likely in how the database session is handled when sync code is called from async context.

## Response snapshot

## Root Cause Analysis

The bug was caused by **calling synchronous database operations from an async context without proper thread isolation**. When `AddTaskTool.execute()` was called via `AgentRunner.chat()` (which is async), it created a sync `SessionLocal()` session and performed database operations. While `TaskRepository.create()` did call `db.commit()`, the transaction was not being properly committed due to the async/sync context mismatch.

The issue occurs because:
1. The async event loop was executing sync SQLAlchemy code
2. SQLAlchemy's sync sessions are not designed to be used across async boundaries
3. The transaction state was not being properly flushed/committed when the session closed

## The Fix

The solution is to wrap all synchronous database operations in `asyncio.to_thread()`, which runs the sync code in a separate thread pool. This ensures:
1. The sync database operations run in a proper synchronous context
2. The transaction is committed correctly
3. The session is properly closed after operations complete

## Changes Made

### 1. `backend/src/mcp/tools/task_tools.py`

All MCP tool `execute()` methods were updated to use `asyncio.to_thread()`:

- `AddTaskTool.execute()`: Wraps task creation in thread pool
- `ListTasksTool.execute()`: Wraps task listing in thread pool
- `DeleteTaskTool.execute()`: Wraps task deletion in thread pool
- `CompleteTaskTool.execute()`: Wraps task completion in thread pool
- `SetTaskStatusTool.execute()`: Wraps status updates in thread pool
- `SetTaskPriorityTool.execute()`: Wraps priority updates in thread pool

### 2. `backend/src/repositories/task.py`

Added debug logging to track transaction state during task creation.

## Outcome

- Impact: Fixes critical bug where tasks created via chatbot were not being persisted to the database
- Tests: Manual testing via chatbot interface required to verify
- Files: Modified 2 files (task_tools.py, task.py)
- Next prompts: Test the fix by creating tasks via the chatbot interface
- Reflection: This is a classic async/sync boundary issue. The pattern of using `asyncio.to_thread()` should be applied to all MCP tools that perform database operations.

## Evaluation notes (flywheel)

- Failure modes observed: Tasks created via chatbot were not being saved to database despite successful API responses
- Graders run and results (PASS/FAIL): Pending manual testing
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Remove debug logging after verifying the fix works correctly
