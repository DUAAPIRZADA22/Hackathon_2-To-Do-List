"""Verify database state after agent tests"""
import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlalchemy import select
from src.db.session import async_session_maker
from src.db.models import Task

async def verify_state():
    """Verify the actual database state"""
    print("\n=== Verifying Database State ===\n")

    async with async_session_maker() as session:
        query = select(Task).where(Task.user_id == 7).order_by(Task.created_at.desc())
        result = await session.execute(query)
        tasks = result.scalars().all()

        print(f"Tasks in database for user_id=7: {len(tasks)}\n")
        for task in tasks:
            print(f"  Task {task.id}:")
            print(f"    Title: {task.title}")
            print(f"    Description: {task.description}")
            print(f"    Status: {task.status}")
            print(f"    Completed: {task.completed}")
            print(f"    Priority: {task.priority}")
            print(f"    Created: {task.created_at}")
            print(f"    Updated: {task.updated_at}")
            print()

    print("=== Verification Complete ===\n")

if __name__ == "__main__":
    asyncio.run(verify_state())
