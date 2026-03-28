#!/usr/bin/env python3
"""
Startup script for ActionMind AI backend server.

Sets the correct PYTHONPATH and starts the FastAPI server.
Run from the project root (ActionMindAI directory).
"""

import os
import sys

# Add backend directory to PYTHONPATH
backend_dir = os.path.join(os.path.dirname(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Set fallback environment variables (only if not in .env)
os.environ.setdefault('PYTHONPATH', backend_dir)
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('BETTER_AUTH_SECRET', 'test-secret-key-for-development-only-change-in-production')

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
