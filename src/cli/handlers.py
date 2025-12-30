# [Task]: T041, T047, T053, T059
"""
CLI handler functions for user actions.

This module contains handler functions that are called from the main menu
to execute specific user actions (add, view, complete, delete tasks).

Each handler follows a consistent pattern:
1. Prompt for input (if applicable)
2. Call service layer
3. Display feedback
4. Pause for user acknowledgment
"""

from src.services.task_service import TaskService
from src.cli.display import (
    prompt_for_input,
    display_success,
    display_warning,
    display_error,
    display_info,
    display_task_table,
    pause_for_acknowledgment,
)
from src.lib.validation import validate_task_id


# [Task]: T041, T043, T044, T045, T046
def add_task_handler(task_service: TaskService) -> None:
    """Handle the "Add Task" menu option.

    Prompts user for task description, creates the task, and displays feedback.

    Args:
        task_service: TaskService instance for business operations

    Flow:
        1. Prompt user for task description
        2. Validate description is not empty
        3. Call task_service.create_task()
        4. Display success message with new task ID
        5. Pause for user acknowledgment
    """
    # Prompt for task description
    description = prompt_for_input("Enter task description: ")

    # Check if description is empty
    if not description or description.strip() == "":
        display_warning("Task description cannot be blank")
        pause_for_acknowledgment()
        return

    # Create the task via service
    try:
        task = task_service.create_task(description)
        display_success(f"Task created successfully with ID: {task.id}")
    except ValueError as e:
        display_error(str(e))

    # Pause before returning to menu
    pause_for_acknowledgment()


# [Task]: T047, T049, T050, T051, T052
def view_tasks_handler(task_service: TaskService) -> None:
    """Handle the "View Tasks" menu option.

    Displays all tasks in a formatted table.

    Args:
        task_service: TaskService instance for business operations

    Flow:
        1. Call task_service.get_all_tasks()
        2. Handle empty list with friendly message
        3. Display task table
        4. Pause for user acknowledgment
    """
    # Get all tasks from service
    tasks = task_service.get_all_tasks()

    # Handle empty task list
    if not tasks:
        display_info("No tasks found")
        pause_for_acknowledgment()
        return

    # Display the task table
    display_task_table(tasks)

    # Pause before returning to menu
    pause_for_acknowledgment()


# [Task]: T053, T055, T056, T057, T058
def complete_task_handler(task_service: TaskService) -> None:
    """Handle the "Complete Task" menu option.

    Prompts user for task ID and marks the task as completed.

    Args:
        task_service: TaskService instance for business operations

    Flow:
        1. Prompt user for task ID
        2. Validate task ID format
        3. Call task_service.complete_task()
        4. Display appropriate feedback (success/already completed/not found)
        5. Pause for user acknowledgment
    """
    # Prompt for task ID
    input_str = prompt_for_input("Enter task ID: ")

    # Validate task ID format
    try:
        task_id = validate_task_id(input_str)
    except ValueError as e:
        display_error(str(e))
        pause_for_acknowledgment()
        return

    # Attempt to complete the task
    try:
        success = task_service.complete_task(task_id)
        if success:
            display_success("Task marked as completed")
        else:
            display_error("Task not found")
    except ValueError as e:
        # Handle "already completed" case
        display_warning(str(e))

    # Pause before returning to menu
    pause_for_acknowledgment()


# [Task]: T059, T061, T062, T063, T064
def delete_task_handler(task_service: TaskService) -> None:
    """Handle the "Delete Task" menu option.

    Prompts user for task ID and deletes the task.

    Args:
        task_service: TaskService instance for business operations

    Flow:
        1. Prompt user for task ID
        2. Validate task ID format
        3. Call task_service.delete_task()
        4. Display appropriate feedback (success/not found)
        5. Pause for user acknowledgment
    """
    # Prompt for task ID
    input_str = prompt_for_input("Enter task ID: ")

    # Validate task ID format
    try:
        task_id = validate_task_id(input_str)
    except ValueError as e:
        display_error(str(e))
        pause_for_acknowledgment()
        return

    # Attempt to delete the task
    success = task_service.delete_task(task_id)
    if success:
        display_success("Task deleted successfully")
    else:
        display_error("Task not found")

    # Pause before returning to menu
    pause_for_acknowledgment()
