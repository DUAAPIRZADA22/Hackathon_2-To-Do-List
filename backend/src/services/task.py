"""
Task service for business logic with event publishing
"""

import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.task import Task
from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.models.event import EventType, TaskEvent, TaskEventData
from src.repositories.task import TaskRepository
from src.services.dapr_client import get_dapr_client

logger = logging.getLogger(__name__)


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
        # Convert to response with explicit field mapping including Phase V fields
        result = []
        for task in tasks:
            result.append(TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,  # Explicitly include
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                recurrence_rule=task.recurrence_rule,
                reminder_settings=task.reminder_settings,
                user_id=task.user_id,
                created_at=task.created_at,
                updated_at=task.updated_at
            ))
        return result

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

        # Explicit field mapping including Phase V fields
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            recurrence_rule=task.recurrence_rule,
            reminder_settings=task.reminder_settings,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    @staticmethod
    async def assign_task(db: Session, task_id: int, assigned_to: int, user_id: int) -> TaskResponse:
        """
        Assign a task to a user and publish event (T031)

        Args:
            db: Database session
            task_id: Task ID
            assigned_to: User ID to assign task to
            user_id: Current user ID for authorization

        Returns:
            Updated task

        Raises:
            HTTPException: If task not found or not authorized
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
                detail="Not authorized to assign this task"
            )

        # Update task with assigned user (if we have assigned_to field)
        # For now, task is owned by user_id, so assignment might mean reassigning
        # This is a placeholder for future multi-user task assignment

        # Publish task_assigned event (T031)
        try:
            dapr_client = get_dapr_client()
            event = TaskEvent(
                event_type=EventType.TASK_ASSIGNED,
                task_id=str(task.id),
                user_id=str(user_id),
                data=TaskEventData(
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    assigned_to=str(assigned_to)
                )
            )
            await dapr_client.publish_task_event(event)
            logger.info(f"Published task_assigned event for task {task.id}")
        except Exception as e:
            logger.error(f"Failed to publish task_assigned event: {e}")
            # Continue even if event publishing fails

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            recurrence_rule=task.recurrence_rule,
            reminder_settings=task.reminder_settings,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    @staticmethod
    async def complete_task(db: Session, task_id: int, user_id: int) -> TaskResponse:
        """
        Mark a task as completed and publish event (T032)

        Args:
            db: Database session
            task_id: Task ID
            user_id: User ID for authorization

        Returns:
            Updated task

        Raises:
            HTTPException: If task not found or not authorized
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
                detail="Not authorized to complete this task"
            )

        # Update task to completed
        task.completed = True
        task.status = "done"
        db.commit()
        db.refresh(task)

        # Publish task_completed event (T032)
        try:
            dapr_client = get_dapr_client()
            event = TaskEvent(
                event_type=EventType.TASK_COMPLETED,
                task_id=str(task.id),
                user_id=str(user_id),
                data=TaskEventData(
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    recurrence_rule=task.recurrence_rule,
                    reminder_settings=task.reminder_settings,
                    due_date=task.due_date.isoformat() if task.due_date else None
                )
            )
            await dapr_client.publish_task_event(event)
            logger.info(f"Published task_completed event for task {task.id}")
        except Exception as e:
            logger.error(f"Failed to publish task_completed event: {e}")
            # Continue even if event publishing fails

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            recurrence_rule=task.recurrence_rule,
            reminder_settings=task.reminder_settings,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    @staticmethod
    async def create_task(db: Session, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """
        Create a new task and publish event

        Args:
            db: Database session
            task_data: Task creation data
            user_id: User ID

        Returns:
            Created task
        """
        task = TaskRepository.create(db, task_data, user_id)

        # Publish task_created event (T028)
        try:
            dapr_client = get_dapr_client()
            event = TaskEvent(
                event_type=EventType.TASK_CREATED,
                task_id=str(task.id),
                user_id=str(user_id),
                data=TaskEventData(
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    recurrence_rule=task.recurrence_rule,
                    reminder_settings=task.reminder_settings,
                    due_date=task.due_date.isoformat() if task.due_date else None
                )
            )
            await dapr_client.publish_task_event(event)
            logger.info(f"Published task_created event for task {task.id}")
        except Exception as e:
            logger.error(f"Failed to publish task_created event: {e}")
            # Continue even if event publishing fails

        # Explicit field mapping including Phase V fields
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            recurrence_rule=task.recurrence_rule,
            reminder_settings=task.reminder_settings,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    @staticmethod
    async def update_task(
        db: Session,
        task_id: int,
        task_data: TaskUpdate,
        user_id: int
    ) -> TaskResponse:
        """
        Update an existing task and publish event

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

        # Determine event type based on status change
        event_type = EventType.TASK_UPDATED
        is_completion = False
        is_uncompletion = False

        # Check if task is being completed
        if task_data.completed is True or (task_data.status == "done"):
            event_type = EventType.TASK_COMPLETED
            is_completion = True
        # Check if task is being uncompleted
        elif task_data.completed is False or (task_data.status in ["todo", "in_progress"] and task.completed):
            event_type = EventType.TASK_UNCOMPLETED
            is_uncompletion = True

        # Publish event (T029, T032)
        try:
            dapr_client = get_dapr_client()
            event = TaskEvent(
                event_type=event_type,
                task_id=str(updated_task.id),
                user_id=str(user_id),
                data=TaskEventData(
                    title=updated_task.title,
                    description=updated_task.description,
                    status=updated_task.status,
                    recurrence_rule=updated_task.recurrence_rule,
                    reminder_settings=updated_task.reminder_settings,
                    due_date=updated_task.due_date.isoformat() if updated_task.due_date else None
                )
            )
            await dapr_client.publish_task_event(event)
            logger.info(f"Published {event_type.value} event for task {updated_task.id}")
        except Exception as e:
            logger.error(f"Failed to publish {event_type.value} event: {e}")
            # Continue even if event publishing fails

        # Explicit field mapping including Phase V fields
        return TaskResponse(
            id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            completed=updated_task.completed,
            status=updated_task.status,
            priority=updated_task.priority,
            due_date=updated_task.due_date,
            recurrence_rule=updated_task.recurrence_rule,
            reminder_settings=updated_task.reminder_settings,
            user_id=updated_task.user_id,
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at
        )

    @staticmethod
    async def delete_task(db: Session, task_id: int, user_id: int) -> None:
        """
        Delete a task and publish event

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

        # Capture task data before deletion for event
        task_data = {
            "title": task.title,
            "status": task.status
        }

        TaskRepository.delete(db, task)

        # Publish task_deleted event (T030)
        try:
            dapr_client = get_dapr_client()
            event = TaskEvent(
                event_type=EventType.TASK_DELETED,
                task_id=str(task_id),
                user_id=str(user_id),
                data=TaskEventData(
                    title=task_data["title"],
                    status=task_data["status"]
                )
            )
            await dapr_client.publish_task_event(event)
            logger.info(f"Published task_deleted event for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to publish task_deleted event: {e}")
            # Continue even if event publishing fails
