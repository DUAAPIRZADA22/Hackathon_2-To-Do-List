---
id: 006
title: Fix Chatbot Tool Execution
stage: misc
date: 2026-01-15
surface: agent
model: claude-opus-4-5
feature: 002-todo-ai-chatbot
branch: 002-todo-ai-chatbot
user: Acer
command: Fix chatbot task status updates and list tasks issues
labels: ["bug-fix","mcp","agent","chatbot"]
links:
  spec: specs/002-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/mcp/server.py
 - backend/src/agent/prompts.py
 - backend/test_task_operations.py
 - backend/test_mcp_tools.py
 - backend/test_agent_flow.py
 - backend/verify_db_state.py
tests:
 - backend/test_mcp_tools.py (PASSED - MCP tools execute correctly)
 - backend/test_agent_flow.py (PASSED - Agent flow works with fixes)
 - backend/verify_db_state.py (PASSED - Database updates persist correctly)
---

## Prompt

Fix issues where:
1. Task status updates (Completed / In-Progress / To-Do) through chatbot are not persisting to database
2. View task list does not show saved tasks

Context: Using OpenAI Agents SDK, ChatKit frontend, MCP tools for task actions.

## Response

Investigation completed. Root causes identified and fixes applied:

**Root Causes:**
1. Tool results were formatted as simple strings, limiting agent's ability to construct accurate responses
2. System prompt didn't explicitly instruct agent to always execute tools for status/priority updates
3. System prompt didn't prevent agent from hallucinating tasks instead of using actual tool results

**Fixes Applied:**

1. **backend/src/mcp/server.py** - Updated `format_tool_result_for_agent()`:
   - Changed from simple text format to structured JSON format
   - Returns `SUCCESS: {json_data}` instead of just "Success: title"
   - Allows agent to parse and use actual data in responses

2. **backend/src/agent/prompts.py** - Updated system prompt:
   - Added "CRITICAL: ALWAYS EXECUTE TOOLS FOR ACTIONS" section
   - Added "CRITICAL: USE TOOL RESULTS ACCURATELY" section
   - Explicitly forbids hallucinating tasks
   - Requires agent to use tool result data exactly as provided
   - Added explicit examples for list_tasks response format

**Verification Tests:**
- MCP tools execute correctly and update database ✅
- Agent calls tools for all actions ✅
- Agent uses actual task data in responses (no hallucination) ✅
- Status/priority updates persist correctly ✅

**Files Modified:**
- `backend/src/mcp/server.py`: format_tool_result_for_agent() returns JSON data
- `backend/src/agent/prompts.py`: System prompt with critical instructions

**Server Status:** Backend server restarted with fixes applied.

## Outcome

- ✅ Impact: Task status updates now persist correctly through chatbot. List tasks now shows actual saved tasks.
- 🧪 Tests: All verification tests passed. MCP tools execute and update database correctly. Agent flow works properly.
- 📁 Files: 2 files modified (server.py, prompts.py), 4 test files created
- 🔁 Next prompts: Monitor chatbot behavior in production to ensure fixes work across all scenarios
- 🧠 Reflection: The issue was not in the MCP tools or database layer (those worked correctly). The issue was in how tool results were formatted for the agent and how the agent was instructed to use those results.

## Evaluation notes (flywheel)

- The root cause analysis revealed that the MCP tools and database operations were working correctly
- The problem was in the presentation layer - how results were formatted for the LLM and what instructions the LLM received
- Tool result formatting should be structured (JSON) rather than simple text to enable accurate responses
- System prompts must explicitly forbid hallucination and require using actual tool data
