"""
Migration script to add missing columns to tasks table.

This script adds the following columns:
- status (varchar(50), default 'todo')
- priority (varchar(20), default 'medium')
- due_date (timestamp, nullable)
"""

import asyncio
from sqlalchemy import text
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.src.db.session import async_session_maker
except ImportError:
    from src.db.session import async_session_maker


async def migrate():
    """Add missing columns to tasks table."""
    print("Starting migration: Adding missing columns to tasks table...")

    async with async_session_maker() as session:
        try:
            # Check if columns already exist
            print("Checking existing columns...")

            # Check status column
            result = await session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name = 'status'
            """))
            status_exists = result.first() is not None

            # Check priority column
            result = await session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name = 'priority'
            """))
            priority_exists = result.first() is not None

            # Check due_date column
            result = await session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name = 'due_date'
            """))
            due_date_exists = result.first() is not None

            print(f"Status column exists: {status_exists}")
            print(f"Priority column exists: {priority_exists}")
            print(f"Due_date column exists: {due_date_exists}")

            # Add status column if it doesn't exist
            if not status_exists:
                print("Adding status column...")
                await session.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN status VARCHAR(50) DEFAULT 'todo'
                """))
                print("✓ Status column added")
            else:
                print("- Status column already exists, skipping")

            # Add priority column if it doesn't exist
            if not priority_exists:
                print("Adding priority column...")
                await session.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'
                """))
                print("✓ Priority column added")
            else:
                print("- Priority column already exists, skipping")

            # Add due_date column if it doesn't exist
            if not due_date_exists:
                print("Adding due_date column...")
                await session.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN due_date TIMESTAMP WITH TIME ZONE
                """))
                print("✓ Due_date column added")
            else:
                print("- Due_date column already exists, skipping")

            # Commit all changes
            await session.commit()
            print("\n✓ Migration completed successfully!")

            # Verify the columns were added
            print("\nVerifying columns...")
            result = await session.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name IN ('status', 'priority', 'due_date')
                ORDER BY column_name
            """))
            columns = result.fetchall()
            print("\nCurrent columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (default: {col[2]})")

        except Exception as e:
            await session.rollback()
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(migrate())
