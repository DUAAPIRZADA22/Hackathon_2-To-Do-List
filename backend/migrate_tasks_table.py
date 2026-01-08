"""
Migration script to drop and recreate the tasks table with correct schema.
Run this once to fix the schema mismatch.
"""

from sqlalchemy import text
from src.core.database import engine

def migrate_tasks_table():
    """Drop and recreate tasks table with correct schema"""

    with engine.begin() as conn:
        # Drop existing tasks table
        conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
        print("[OK] Dropped old tasks table")

    # Recreate table with correct schema using SQLAlchemy
    from src.models.task import Task
    from src.models.user import User
    from src.core.database import Base

    Base.metadata.create_all(bind=engine)
    print("[OK] Created tasks table with correct schema")

    print("\n[SUCCESS] Migration complete! Tasks table now has:")
    print("   - id, title, description")
    print("   - status (todo, in_progress, done)")
    print("   - priority (low, medium, high, urgent)")
    print("   - due_date, user_id")
    print("   - created_at, updated_at")

if __name__ == "__main__":
    migrate_tasks_table()
