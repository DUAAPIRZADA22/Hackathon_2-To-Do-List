"""
Task Creation State Manager for Todo AI Chatbot

Implements persistent state management for multi-step task creation.
Provides transactional state that persists across HTTP requests.

Architecture Principles:
- User-scoped: State keyed by user_id
- Transactional: State cleared only after task creation
- Simple: In-memory dictionary for fast access
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio


class TaskCreationState:
    """State for an in-progress task creation."""

    def __init__(self, title: str):
        self.title = title
        self.priority: Optional[str] = None
        self.status: Optional[str] = None
        self.step = "priority"  # "priority" → "status" → "complete"
        self.created_at = datetime.now()

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if state has expired."""
        return datetime.now() - self.created_at > timedelta(minutes=timeout_minutes)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
            "step": self.step,
            "created_at": self.created_at.isoformat()
        }


class TaskCreationStateManager:
    """
    Manages persistent state for multi-step task creation.

    Stores in-progress task creation state by user_id.
    Provides transactional state that persists across HTTP requests.

    Example:
        manager = TaskCreationStateManager()

        # Step 1: User initiates task creation
        state = manager.start_task_creation("user123", "Buy groceries")
        # state: {title: "Buy groceries", priority: None, status: None, step: "priority"}

        # Step 2: User provides priority
        state = manager.update_priority("user123", "high")
        # state: {title: "Buy groceries", priority: "high", status: None, step: "status"}

        # Step 3: User provides status - create task and clear state
        state = manager.update_status("user123", "done")
        # state: {title: "Buy groceries", priority: "high", status: "done", step: "complete"}
        manager.clear_task_creation("user123")
    """

    def __init__(self):
        """Initialize state manager with in-memory storage."""
        self._states: Dict[str, TaskCreationState] = {}
        self._lock = asyncio.Lock()

    async def get_state(self, user_id: str) -> Optional[TaskCreationState]:
        """
        Get current task creation state for a user.

        Args:
            user_id: User ID

        Returns:
            TaskCreationState if exists, None otherwise
        """
        async with self._lock:
            state = self._states.get(user_id)

            # Clean up expired states
            if state and state.is_expired():
                del self._states[user_id]
                return None

            return state

    async def start_task_creation(self, user_id: str, title: str) -> TaskCreationState:
        """
        Start a new task creation flow.

        Creates or replaces existing state with new task creation state.

        Args:
            user_id: User ID
            title: Task title

        Returns:
            Created TaskCreationState
        """
        async with self._lock:
            state = TaskCreationState(title)
            self._states[user_id] = state
            print(f"[STATE MANAGER] Started task creation for user {user_id}: {state.to_dict()}")
            return state

    async def update_priority(self, user_id: str, priority: str) -> Optional[TaskCreationState]:
        """
        Update priority and move to next step.

        Args:
            user_id: User ID
            priority: Priority value (low, medium, high, urgent)

        Returns:
            Updated TaskCreationState if exists, None otherwise
        """
        async with self._lock:
            state = self._states.get(user_id)
            if not state:
                print(f"[STATE MANAGER] No state found for user {user_id} when updating priority")
                return None

            state.priority = priority.lower()
            state.step = "status"
            print(f"[STATE MANAGER] Updated priority for user {user_id}: {state.to_dict()}")
            return state

    async def update_status(self, user_id: str, status: str) -> Optional[TaskCreationState]:
        """
        Update status and mark ready for creation.

        Args:
            user_id: User ID
            status: Status value (todo, in_progress, done)

        Returns:
            Updated TaskCreationState if exists, None otherwise
        """
        async with self._lock:
            state = self._states.get(user_id)
            if not state:
                print(f"[STATE MANAGER] No state found for user {user_id} when updating status")
                return None

            # Map display names to API values
            status_map = {
                "to do": "todo",
                "in progress": "in_progress",
                "done": "done",
                # Lowercase versions
                "todo": "todo",
                "in_progress": "in_progress",
                "done": "done",
            }
            state.status = status_map.get(status.lower(), status.lower())
            state.step = "complete"
            print(f"[STATE MANAGER] Updated status for user {user_id}: {state.to_dict()}")
            return state

    async def clear_task_creation(self, user_id: str) -> None:
        """
        Clear task creation state for a user.

        Called after task is successfully created.

        Args:
            user_id: User ID
        """
        async with self._lock:
            if user_id in self._states:
                del self._states[user_id]
                print(f"[STATE MANAGER] Cleared state for user {user_id}")

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active states (for debugging).

        Returns:
            Dictionary mapping user_id to state dict
        """
        return {
            user_id: state.to_dict()
            for user_id, state in self._states.items()
            if not state.is_expired()
        }


# =====================================================
# Global State Manager Instance
# =====================================================

_global_state_manager: Optional[TaskCreationStateManager] = None


def get_state_manager() -> TaskCreationStateManager:
    """
    Get the global state manager instance.

    Returns:
        TaskCreationStateManager singleton
    """
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = TaskCreationStateManager()
    return _global_state_manager
