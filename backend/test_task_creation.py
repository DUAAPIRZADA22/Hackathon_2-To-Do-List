"""Test script to debug Task creation"""
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.task import Task
from src.models.schemas import TaskCreate

# Create sync engine
database_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
engine = create_engine(database_url, echo=True)  # Enable SQL logging
SessionLocal = sessionmaker(bind=engine)

# Test 1: Check Task model metadata
print("\n=== Task Model Columns ===")
for col in Task.__table__.columns:
    print(f"  {col.name}: {col.type}")

# Test 2: Try creating a task
print("\n=== Creating Task ===")
with SessionLocal() as session:
    task_data = TaskCreate(
        title="Direct Test",
        description="Testing directly",
        completed=False,
        status="todo",
        priority="medium"
    )

    print(f"\nTask schema dump: {task_data.model_dump()}")

    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        user_id=5
    )

    print(f"\nTask object created: {task}")
    print(f"Task.completed value: {task.completed}")

    session.add(task)
    session.commit()
    print("\n✓ Task created successfully!")
