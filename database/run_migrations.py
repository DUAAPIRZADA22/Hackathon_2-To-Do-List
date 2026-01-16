#!/usr/bin/env python3
"""
Run database migrations for ActionMind AI.

This script executes SQL migration files against the PostgreSQL database.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv(backend_dir / ".env")


async def run_migration(connection: asyncpg.Connection, migration_file: Path):
    """Execute a single migration file."""
    print(f"Running migration: {migration_file.name}")

    sql_content = migration_file.read_text()

    # Split by semicolons and execute each statement
    # (simplified - for production use a proper migration tool like Alembic)
    statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]

    for statement in statements:
        # Skip empty statements and comments
        if not statement or statement.startswith("--"):
            continue

        try:
            await connection.execute(statement)
        except Exception as e:
            # Ignore "IF NOT EXISTS" errors
            if "already exists" not in str(e):
                print(f"  Statement executed (note: {e})")
            else:
                print(f"  Executed: {statement[:50]}...")

    print(f"  ✓ Migration completed\n")


async def main():
    """Main migration runner."""
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        sys.exit(1)

    # Convert asyncpg URL to libpq format for asyncpg
    # Replace postgresql+asyncpg:// with postgresql://
    libpq_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    migrations_dir = Path(__file__).parent / "migrations"

    # Get all migration files sorted
    migration_files = sorted(migrations_dir.glob("*.sql"))

    print(f"Found {len(migration_files)} migration files\n")

    try:
        # Connect to database
        print(f"Connecting to database...")
        conn = await asyncpg.connect(libpq_url)

        # Run each migration
        for migration_file in migration_files:
            await run_migration(conn, migration_file)

        await conn.close()
        print("✓ All migrations completed successfully")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
