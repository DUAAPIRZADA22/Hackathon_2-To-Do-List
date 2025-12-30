# [Task]: T007, T008, T009
"""
Task entity for ActionMind AI.

This module defines the core Task dataclass and TaskStatus enum
used throughout the application.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    """Enumeration of possible task states.

    A task can be in one of two states:
    - PENDING: Task is not yet completed
    - COMPLETED: Task has been marked as completed
    """

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


@dataclass
class Task:
    """Represents a task in the task management system.

    Attributes:
        id: Unique identifier for the task (auto-generated)
        description: Human-readable description of what the task entails
        status: Current state of the task (PENDING or COMPLETED)
        created_at: Timestamp when the task was created

    Raises:
        ValueError: If description is empty or only whitespace after validation
    """

    id: int
    description: str
    status: TaskStatus
    created_at: datetime

    def __post_init__(self):
        """Validate task data after initialization.

        Ensures the task description is not blank (empty or whitespace only).
        This validation enforces business rule that tasks must have meaningful
        descriptions.

        Raises:
            ValueError: If description is empty or contains only whitespace
        """
        # Trim whitespace from description
        self.description = self.description.strip()

        # Validate description is not empty
        if len(self.description) == 0:
            raise ValueError("Task description cannot be blank")

    def __str__(self) -> str:
        """Return string representation of task for display.

        Returns:
            A formatted string showing task ID and description
        """
        status_symbol = "✓" if self.status == TaskStatus.COMPLETED else " "
        return f"[{self.id}] {status_symbol} {self.description}"

    def __repr__(self) -> str:
        """Return detailed representation for debugging.

        Returns:
            String with all task attributes
        """
        return (
            f"Task(id={self.id}, description='{self.description}', "
            f"status={self.status.value}, created_at={self.created_at})"
        )
