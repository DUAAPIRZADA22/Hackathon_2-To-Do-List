"""
Tasks API routes
"""

from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.auth.jwt import get_current_active_user
from src.models.user import User
from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.services.task import TaskService


router = APIRouter()


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
