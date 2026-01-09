"""
Task repository for data access operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.task import Task
from src.models.schemas import TaskCreate, TaskUpdate


class TaskRepository:
    """Repository for Task model"""

    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_all_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks for a user with pagination"""
        return (
            db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, task_data: TaskCreate, user_id: int) -> Task:
        """Create a new task"""
        db_task = Task(**task_data.model_dump(), user_id=user_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def update(db: Session, task: Task, task_data: TaskUpdate) -> Task:
        """Update an existing task"""
        for field, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete(db: Session, task: Task) -> None:
        """Delete a task"""
        db.delete(task)
        db.commit()
