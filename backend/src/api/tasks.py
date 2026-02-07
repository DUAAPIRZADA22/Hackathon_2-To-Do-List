"""
Tasks API routes - Using Phase I/II sync database for compatibility

This module uses the sync database from Phase I/II to ensure compatibility
with the existing authentication system. Tasks created by the chatbot (which uses
async database) will need to be synced or the chatbot needs to be updated to use
the sync database.
"""

from typing import List
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
import re

# Use Phase I/II dependencies and services
from src.core.database import get_db
from src.auth.jwt import get_current_active_user
from src.models.user import User
from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.services.task import TaskService

# Import MCP tools for direct chat functionality
from src.mcp.tools.task_tools import (
    AddTaskTool,
    ListTasksTool,
    CompleteTaskTool,
    DeleteTaskTool,
    SetTaskStatusTool,
    SetTaskPriorityTool
)


router = APIRouter()


# =====================================================
# Direct Chat Endpoint (Working Solution)
# =====================================================

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Direct chat endpoint that calls MCP tools directly.
    This bypasses the complex AgentRunner → OpenAI flow.
    """
    message = request.message.lower().strip()
    user_id_str = str(current_user.id)

    # Initialize tools
    add_tool = AddTaskTool()
    list_tool = ListTasksTool()
    complete_tool = CompleteTaskTool()
    delete_tool = DeleteTaskTool()

    # Pattern matching
    for pattern in [r"add task (.+)", r"create task (.+)", r"new task (.+)"]:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            priority = "medium"
            for p in ["urgent", "high", "low"]:
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
                return ChatResponse(response=f"✓ Task '{title}' created with {priority} priority!")
            return ChatResponse(response=f"Error: {result.error}")

    for pattern in [r"list task", r"show task", r"my task", r"all task"]:
        if re.search(pattern, message):
            result = await list_tool.execute(user_id=user_id_str)
            if result.success and result.data:
                tasks = result.data.get("tasks", [])
                count = result.data.get("count", 0)
                if count == 0:
                    return ChatResponse(response="You don't have any tasks yet.")
                task_list = "\n".join([f"• {t['title']}" for t in tasks[:5]])
                return ChatResponse(response=f"Your tasks ({count}):\n{task_list}")
            return ChatResponse(response=f"Error: {result.error}")

    for pattern in [r"complete task (.+)", r"finish task (.+)", r"done with task (.+)"]:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            result = await complete_tool.execute(user_id=user_id_str, title=title)
            if result.success:
                return ChatResponse(response=f"✓ Task '{title}' completed!")
            return ChatResponse(response=f"Error: {result.error}")

    for pattern in [r"delete task (.+)", r"remove task (.+)"]:
        match = re.search(pattern, message)
        if match:
            title = match.group(1).strip()
            result = await delete_tool.execute(user_id=user_id_str, title=title)
            if result.success:
                return ChatResponse(response=f"✓ Task '{title}' deleted!")
            return ChatResponse(response=f"Error: {result.error}")

    # Default help message
    return ChatResponse(
        response="I can help you manage tasks!\n\n"
        "Try:\n"
        "• Add task [title]\n"
        "• Show tasks\n"
        "• Complete task [title]\n"
        "• Delete task [title]"
    )


@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for the current user

    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum number of tasks to return (max 100)
    """
    return TaskService.get_all_tasks(db, current_user.id, skip, limit)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID

    - **task_id**: ID of the task to retrieve
    """
    return TaskService.get_task(db, task_id, current_user.id)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task

    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional)
    - **status**: Task status - 'todo', 'in_progress', or 'done' (default: 'todo')
    - **priority**: Task priority - 'low', 'medium', 'high', or 'urgent' (default: 'medium')
    - **due_date**: Due date for the task (optional, ISO format)
    """
    return TaskService.create_task(db, task_data, current_user.id)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task

    - **task_id**: ID of the task to update
    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **status**: New task status (optional)
    - **priority**: New task priority (optional)
    - **due_date**: New due date (optional)
    """
    return TaskService.update_task(db, task_id, task_data, current_user.id)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task

    - **task_id**: ID of the task to delete
    """
    TaskService.delete_task(db, task_id, current_user.id)
