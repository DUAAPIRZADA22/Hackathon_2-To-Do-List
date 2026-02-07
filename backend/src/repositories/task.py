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
        # Extract data from schema (now includes completed)
        task_dict = task_data.model_dump()

        print(f"[DEBUG TASK_REPO] Creating task with data: {task_dict}")
        print(f"[DEBUG TASK_REPO] Session before add - in_transaction: {db.in_transaction()}, dirty: {db.dirty}, new: {db.new}")

        # Create task object with all fields including completed
        db_task = Task(
            title=task_dict.get('title'),
            description=task_dict.get('description'),
            completed=task_dict.get('completed', False),  # Get from schema
            status=task_dict.get('status'),
            priority=task_dict.get('priority'),
            due_date=task_dict.get('due_date'),
            user_id=user_id
        )

        db.add(db_task)
        print(f"[DEBUG TASK_REPO] Task added to session - pending: {db.new}, dirty: {db.dirty}")

        db.commit()
        print(f"[DEBUG TASK_REPO] Commit completed - task.id: {db_task.id}")

        db.refresh(db_task)
        print(f"[DEBUG TASK_REPO] Refresh completed - verified task in DB")
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
