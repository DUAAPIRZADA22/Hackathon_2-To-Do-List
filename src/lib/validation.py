# [Task]: T018, T019, T020
"""
Input validation utilities for ActionMind AI CLI.

This module provides validation functions for user input throughout
the application. All validation functions raise ValueError with
descriptive messages for invalid input.
"""

from typing import Optional


def validate_menu_selection(input_str: str) -> int:
    """Validate menu selection input from user.

    Args:
        input_str: Raw user input from menu prompt

    Returns:
        Validated integer between 1 and 5

    Raises:
        ValueError: If input is not a valid number or not in range 1-5

    Valid selections:
        1 - Add Task
        2 - View Tasks
        3 - Complete Task
        4 - Delete Task
        5 - Exit
    """
    # Check if input is empty
    if not input_str or input_str.strip() == "":
        raise ValueError("Please enter a number between 1 and 5")

    # Try to convert to integer
    try:
        selection = int(input_str.strip())
    except ValueError:
        raise ValueError("Please enter a number between 1 and 5")

    # Validate range
    if selection < 1 or selection > 5:
        raise ValueError("Invalid option. Please select 1-5")

    return selection


def validate_task_id(input_str: str) -> int:
    """Validate task ID input from user.

    Args:
        input_str: Raw user input for task ID

    Returns:
        Validated positive integer task ID

    Raises:
        ValueError: If input is not a valid positive integer
    """
    # Check if input is empty
    if not input_str or input_str.strip() == "":
        raise ValueError("Please enter a valid task ID")

    # Try to convert to integer
    try:
        task_id = int(input_str.strip())
    except ValueError:
        raise ValueError("Please enter a valid task ID")

    # Validate positive
    if task_id <= 0:
        raise ValueError("Task ID must be a positive number")

    return task_id


def validate_description(description: str) -> str:
    """Validate and normalize task description.

    Args:
        description: Raw task description input

    Returns:
        Normalized description with whitespace trimmed

    Raises:
        ValueError: If description is empty or only whitespace
    """
    # Trim whitespace
    normalized = description.strip()

    # Validate not empty
    if len(normalized) == 0:
        raise ValueError("Task description cannot be blank")

    # Validate maximum length (200 characters per spec)
    if len(normalized) > 200:
        raise ValueError(
            f"Task description is too long ({len(normalized)} characters). "
            "Maximum is 200 characters."
        )

    return normalized


def validate_non_empty(input_str: str, field_name: str = "Input") -> str:
    """Validate that input is not empty or whitespace only.

    This is a generic validation helper for any input that must
    not be blank.

    Args:
        input_str: Raw user input
        field_name: Name of the field being validated (for error message)

    Returns:
        Trimmed input string

    Raises:
        ValueError: If input is empty or whitespace only
    """
    normalized = input_str.strip()

    if len(normalized) == 0:
        raise ValueError(f"{field_name} cannot be blank")

    return normalized
