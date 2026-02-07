"""
Simple Direct Chat API - Bypasses OpenAI Agent, calls MCP tools directly
This solves the issue where AgentRunner wasn't properly executing MCP tools
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import re

# Use Phase I/II authentication (same as tasks API)
from src.auth.jwt import get_current_active_user
from src.models.user import User
from src.mcp.tools.task_tools import (
    AddTaskTool,
    ListTasksTool,
    CompleteTaskTool,
    DeleteTaskTool,
    SetTaskStatusTool,
    SetTaskPriorityTool
)


router = APIRouter()


class SimpleChatRequest(BaseModel):
    message: str


class SimpleChatResponse(BaseModel):
    response: str


@router.post(
    "/api/direct-chat",
    response_model=SimpleChatResponse,
    tags=["Chat"],
    summary="Direct chat that calls MCP tools (working solution)",
)
async def direct_chat(
    request: SimpleChatRequest,
    current_user: User = Depends(get_current_active_user)
) -> SimpleChatResponse:
    """
    Direct chat endpoint that parses user intent and calls MCP tools directly.
    Bypasses the complex AgentRunner → OpenAI flow that wasn't working.
    """
    message = request.message.lower().strip()
    user_id_str = str(current_user.id)

    # Initialize tools
    add_tool = AddTaskTool()
    list_tool = ListTasksTool()
    complete_tool = CompleteTaskTool()
    delete_tool = DeleteTaskTool()
    set_status_tool = SetTaskStatusTool()
    set_priority_tool = SetTaskPriorityTool()

    # Pattern matching for task operations
    # 1. Add task patterns
    add_patterns = [
        r"add task (.+)",
        r"create task (.+)",
        r"new task (.+)",
        r"make a task (.+)",
    ]

    # 2. List tasks patterns
    list_patterns = [
        r"list task",
        r"show task",
        r"my task",
        r"all task",
        r"what task",
    ]

    # 3. Complete task patterns
    complete_patterns = [
        r"complete task (.+)",
        r"finish task (.+)",
        r"done with task (.+)",
        r"mark.*task.*done (.+)",
    ]

    # 4. Delete task patterns
    delete_patterns = [
        r"delete task (.+)",
        r"remove task (.+)",
        r"erase task (.+)",
    ]

    # Check for list tasks first
    for pattern in list_patterns:
        if re.search(pattern, message):
            result = await list_tool.execute(user_id=user_id_str)
            if result.success and result.data:
                tasks = result.data.get("tasks", [])
                count = result.data.get("count", 0)
                if count == 0:
                    return SimpleChatResponse(response="You don't have any tasks yet.")
                task_list = "\n".join([f"• {t['title']}" for t in tasks[:5]])
                return SimpleChatResponse(response=f"Your tasks ({count} total):\n{task_list}")
            else:
                return SimpleChatResponse(response=f"Error: {result.error}")

    # Check for add task
    for pattern in add_patterns:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            # Extract priority if mentioned
            priority = "medium"
            for p in ["urgent", "high", "medium", "low"]:
                if p in message:
                    priority = p
                    break

            result = await add_tool.execute(
                user_id=user_id_str,
                title=title,
                description="",
                priority=priority,
                status="todo"
            )
            if result.success:
                return SimpleChatResponse(
                    response=f"Task '{title}' created successfully with {priority} priority!"
                )
            else:
                return SimpleChatResponse(response=f"Error: {result.error}")

    # Check for complete task
    for pattern in complete_patterns:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            result = await complete_tool.execute(
                user_id=user_id_str,
                title=title
            )
            if result.success:
                return SimpleChatResponse(
                    response=f"Task '{title}' marked as done!"
                )
            else:
                return SimpleChatResponse(response=f"Error: {result.error}")

    # Check for delete task
    for pattern in delete_patterns:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            result = await delete_tool.execute(
                user_id=user_id_str,
                title=title
            )
            if result.success:
                return SimpleChatResponse(
                    response=f"Task '{title}' deleted!"
                )
            else:
                return SimpleChatResponse(response=f"Error: {result.error}")

    # Default: AI-style response using OpenAI (without tools)
    try:
        from src.agent.runner import AgentRunner
        agent = AgentRunner(user_id=user_id_str)
        ai_result = await agent.chat(
            message=request.message,
            conversation_history=[],
            stream=False
        )
        return SimpleChatResponse(response=ai_result.get("response", "I understand. How can I help you with your tasks?"))
    except Exception as e:
        # Fallback response
        return SimpleChatResponse(
            response="I can help you manage tasks! Try:\n"
                   "• 'Add task [title]' - Create a new task\n"
                   "• 'Show tasks' - List all your tasks\n"
                   "• 'Complete task [title]' - Mark a task as done\n"
                   "• 'Delete task [title]' - Remove a task"
        )


__all__ = ["router"]
