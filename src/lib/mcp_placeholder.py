# [Task]: T010
"""
Placeholder interfaces for MCP (Model Context Protocol) integration.

This module provides abstract interfaces that enable Phase 2+ integration
with MCP services for state storage. In Phase 1, these are implemented
with in-memory storage only.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.models.task import Task


class StorageInterface(ABC):
    """Abstract base class defining the contract for task storage.

    This interface enables storage implementations to be swapped without
    changing business logic. Phase 1 uses InMemoryStorage; Phase 2+ may
    use MCP-backed storage, file storage, or database storage.

    All storage operations are synchronous and return immediately.
    """

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a task to storage.

        Args:
            task: Task object to add to storage

        This operation always succeeds in Phase 1 (in-memory storage).
        Future storage implementations may raise exceptions on failure.
        """

    @abstractmethod
    def get_all(self) -> List[Task]:
        """Get all tasks from storage.

        Returns:
            List of all tasks in storage (empty list if no tasks exist)

        The returned list is ordered by insertion order (oldest first).
        """

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Find a specific task by its ID.

        Args:
            task_id: Unique identifier of the task to retrieve

        Returns:
            Task object if found, None if no task with that ID exists
        """

    @abstractmethod
    def update(self, task: Task) -> bool:
        """Replace an existing task with updated data.

        Args:
            task: Task object containing updated data (must have valid ID)

        Returns:
            True if task was updated successfully
            False if no task with that ID exists in storage

        Note: This replaces the entire task, not partial updates.
        """

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task from storage.

        Args:
            task_id: Unique identifier of the task to delete

        Returns:
            True if task was deleted successfully
            False if no task with that ID exists in storage
        """

    @abstractmethod
    def generate_id(self) -> int:
        """Generate the next unique task ID.

        Returns:
            A unique integer ID that can be assigned to a new task

        The ID generation strategy is implementation-dependent.
        InMemoryStorage uses a simple counter; other implementations
        may use different strategies (UUIDs, database sequences, etc.).
        """


class MCPStateStoreInterface(ABC):
    """Placeholder interface for Phase 2+ MCP state store integration.

    This interface is defined for future extensibility but not used in Phase 1.
    Phase 2 may integrate with MCP servers that provide state storage capabilities.

    Example MCP integration patterns:
    - Dapr state store API
    - Key-value store via MCP tools
    - Cloud storage services (Azure Blob, AWS S3, GCS)
    """

    @abstractmethod
    def get_state(self, key: str) -> Optional[str]:
        """Retrieve state value by key from MCP state store.

        Args:
            key: State key to retrieve

        Returns:
            State value as string if found, None otherwise
        """

    @abstractmethod
    def set_state(self, key: str, value: str) -> None:
        """Store a state value in MCP state store.

        Args:
            key: State key to store
            value: State value to persist
        """

    @abstractmethod
    def delete_state(self, key: str) -> bool:
        """Delete a state value from MCP state store.

        Args:
            key: State key to delete

        Returns:
            True if deleted, False if key didn't exist
        """
