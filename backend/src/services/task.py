"""
Task service for business logic
"""

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.task import Task
from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.repositories.task import TaskRepository


class TaskService:
    """Service for task operations"""

    @staticmethod
    def get_all_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        """
        Get all tasks for a user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tasks
        """
        tasks = TaskRepository.get_all_by_user(db, user_id, skip, limit)
        return [TaskResponse.model_validate(task) for task in tasks]

    @staticmethod
    def get_task(db: Session, task_id: int, user_id: int) -> TaskResponse:
        """
        Get a specific task by ID

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID for authorization

        Returns:
            Task data

        Raises:
            HTTPException: If task not found or doesn't belong to user
        """
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this task"
            )

        return TaskResponse.model_validate(task)

    @staticmethod
    def create_task(db: Session, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """
        Create a new task

        Args:
            db: Database session
            task_data: Task creation data
            user_id: User ID

        Returns:
            Created task
        """
        task = TaskRepository.create(db, task_data, user_id)
        return TaskResponse.model_validate(task)

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        task_data: TaskUpdate,
        user_id: int
    ) -> TaskResponse:
        """
        Update an existing task

        Args:
            db: Database session
            task_id: Task ID
            task_data: Task update data
            user_id: User ID for authorization

        Returns:
            Updated task

        Raises:
            HTTPException: If task not found or doesn't belong to user
        """
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task"
            )

        updated_task = TaskRepository.update(db, task, task_data)
        return TaskResponse.model_validate(updated_task)

    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> None:
        """
        Delete a task

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID for authorization

        Raises:
            HTTPException: If task not found or doesn't belong to user
        """
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )

        TaskRepository.delete(db, task)
