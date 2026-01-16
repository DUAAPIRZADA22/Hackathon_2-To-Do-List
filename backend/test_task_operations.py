"""Test script to verify task operations work correctly"""
import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlalchemy import select
from src.db.session import async_session_maker
from src.db.models import Task
from src.db.repository import TaskRepository

async def test_list_and_update_tasks():
    """Test that we can list and update tasks"""
    print("\n=== Testing Task Operations ===\n")

    async with async_session_maker() as session:
        # Test 1: List all tasks for user_id=7
        print("Test 1: List tasks for user_id=7")
        tasks = await TaskRepository.list_tasks(session, user_id=7, status="all")
        print(f"  Found {len(tasks)} tasks")
        for task in tasks:
            print(f"    - Task {task.id}: {task.title} (status={task.status}, completed={task.completed}, priority={task.priority})")

        # Test 2: Update first task to done
        if tasks:
            first_task = tasks[0]
            print(f"\nTest 2: Update task {first_task.id} to done")
            print(f"  Before: status={first_task.status}, completed={first_task.completed}")

            # Direct update using SQLAlchemy
            from sqlalchemy import update as sql_update
            result = await session.execute(
                sql_update(Task)
                .where(Task.id == first_task.id, Task.user_id == 7)
                .values(completed=True, status="done")
                .returning(Task)
            )
            await session.commit()

            updated_task = result.scalar_one_or_none()
            print(f"  After: status={updated_task.status}, completed={updated_task.completed}")

            # Verify update persisted
            await session.refresh(updated_task)
            print(f"  Refresh: status={updated_task.status}, completed={updated_task.completed}")

        # Test 3: Verify we can retrieve updated tasks
        print("\nTest 3: Verify update persisted")
        tasks = await TaskRepository.list_tasks(session, user_id=7, status="all")
        print(f"  Found {len(tasks)} tasks")
        for task in tasks:
            print(f"    - Task {task.id}: {task.title} (status={task.status}, completed={task.completed})")

    print("\n=== Tests Complete ===\n")

if __name__ == "__main__":
    asyncio.run(test_list_and_update_tasks())
