# [Task]: T006
"""
Shared utilities and libraries for ActionMind AI.

This module contains reusable components such as validation functions
and placeholder interfaces for future extensibility.
"""

from src.lib.validation import (
    validate_menu_selection,
    validate_task_id,
    validate_description,
)

__all__ = [
    "validate_menu_selection",
    "validate_task_id",
    "validate_description",
]
