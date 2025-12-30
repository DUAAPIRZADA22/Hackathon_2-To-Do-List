# [Task]: T011, T012, T013, T014, T015, T016, T017
"""
In-memory storage implementation for ActionMind AI tasks.

This module provides the Phase 1 storage implementation using a Python list.
Tasks are stored in memory and are lost when the application exits.

Phase 2+ may replace this with MCP-backed storage, file storage, or database.
"""

from typing import List, Optional
from src.models.task import Task
from src.lib.mcp_placeholder import StorageInterface


class InMemoryStorage(StorageInterface):
    """In-memory storage implementation for tasks.

    This implementation stores tasks in a Python list. All operations are
    O(n) time complexity where n is the number of tasks. This is acceptable
    for Phase 1 where task counts are expected to be <1000.

    Attributes:
        _tasks: Internal list storing Task objects
        _next_id: Counter for generating unique task IDs

    Note: Data is NOT persisted between application runs.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory storage."""
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def add(self, task: Task) -> None:
        """Add a task to storage.

        Args:
            task: Task object to add

        The task is appended to the end of the internal list.
        """
        self._tasks.append(task)

    def get_all(self) -> List[Task]:
        """Get all tasks from storage.

        Returns:
            List of all tasks in insertion order (oldest first)

            Returns an empty list if no tasks exist.
        """
        return self._tasks.copy()

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by its ID.

        Args:
            task_id: Unique identifier of the task to find

        Returns:
            Task if found, None if not found

        Time complexity: O(n) where n is the number of tasks
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update(self, task: Task) -> bool:
        """Replace an existing task with updated data.

        Args:
            task: Task object with updated data (ID must match existing task)

        Returns:
            True if task was updated
            False if no task with that ID exists

        Time complexity: O(n) where n is the number of tasks

        Note: This replaces the entire task object in the list.
        """
        for i, existing_task in enumerate(self._tasks):
            if existing_task.id == task.id:
                self._tasks[i] = task
                return True
        return False

    def delete(self, task_id: int) -> bool:
        """Delete a task from storage.

        Args:
            task_id: Unique identifier of the task to delete

        Returns:
            True if task was deleted
            False if no task with that ID exists

        Time complexity: O(n) where n is the number of tasks
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                self._tasks.pop(i)
                return True
        return False

    def generate_id(self) -> int:
        """Generate the next unique task ID.

        Returns:
            A unique integer ID

        The ID counter increments with each call, starting from 1.
        IDs are not reused even after tasks are deleted.
        """
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def count(self) -> int:
        """Get the total number of tasks stored.

        Returns:
            Number of tasks in storage

        This is a convenience method not required by StorageInterface.
        """
        return len(self._tasks)

    def clear(self) -> None:
        """Remove all tasks from storage.

        This is a convenience method for testing purposes.
        Not required by StorageInterface.
        """
        self._tasks.clear()
        self._next_id = 1
