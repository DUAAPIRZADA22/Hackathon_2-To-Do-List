# [Task]: T035, T036, T037, T042, T048
"""
Main menu implementation for ActionMind AI CLI.

This module provides the main menu loop and routing logic for the
CLI application. It handles user menu selection and dispatches
to appropriate handler functions.
"""

from typing import Optional, Callable
from src.cli.display import (
    display_styled_heading,
    display_main_menu_options,
    prompt_for_input,
    display_error,
)
from src.lib.validation import validate_menu_selection
from src.services.task_service import TaskService


def display_main_menu() -> None:
    """Display the main menu with styled heading and options.

    Shows the application heading followed by the 5 numbered menu options.
    """
    display_styled_heading("ActionMind AI")
    display_main_menu_options()


def get_menu_selection() -> int:
    """Prompt user for menu selection and validate input.

    Returns:
        Validated integer between 1 and 5

    Keeps prompting until valid input is received.

    Raises:
        ValueError: If input is not numeric or not in range 1-5
    """
    while True:
        try:
            selection_str = prompt_for_input("Choose an option")
            return validate_menu_selection(selection_str)
        except ValueError as e:
            display_error(str(e))


def main_menu_loop(
    task_service: TaskService,
    exit_handler: Optional[Callable[[], None]] = None
) -> None:
    """Run the main menu loop until user selects Exit.

    This is the primary event loop for the CLI application. It displays
    the menu, gets user selection, and dispatches to the appropriate
    handler function.

    Args:
        task_service: TaskService instance for business operations
        exit_handler: Optional callback function for graceful exit

    Menu options:
        1 - Add Task (dispatched to add_task_handler)
        2 - View Tasks (dispatched to view_tasks_handler)
        3 - Complete Task (dispatched to complete_task_handler)
        4 - Delete Task (dispatched to delete_task_handler)
        5 - Exit (terminates the loop)

    The loop continues until the user selects option 5 (Exit).

    Note: Handler functions are imported lazily to avoid circular imports.
    They will be wired in during user story implementation phases.
    """
    running = True

    while running:
        # Display the menu
        display_main_menu()

        # Get and validate user selection
        try:
            selection = get_menu_selection()
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully
            print()
            running = False
            break

        # Route to appropriate handler
        if selection == 1:
            # Add Task - will be wired in Phase 4 (User Story 2)
            _route_add_task(task_service)
        elif selection == 2:
            # View Tasks - will be wired in Phase 5 (User Story 3)
            _route_view_tasks(task_service)
        elif selection == 3:
            # Complete Task - will be wired in Phase 6 (User Story 4)
            _route_complete_task(task_service)
        elif selection == 4:
            # Delete Task - will be wired in Phase 7 (User Story 5)
            _route_delete_task(task_service)
        elif selection == 5:
            # Exit - terminate the loop
            running = False
            if exit_handler:
                exit_handler()


# Handler routing functions (wired in Phase 3-7)

def _route_add_task(task_service: TaskService) -> None:
    """Route to Add Task handler.

    Args:
        task_service: TaskService instance for business operations
    """
    from src.cli.handlers import add_task_handler
    add_task_handler(task_service)


def _route_view_tasks(task_service: TaskService) -> None:
    """Route to View Tasks handler.

    Args:
        task_service: TaskService instance for business operations
    """
    from src.cli.handlers import view_tasks_handler
    view_tasks_handler(task_service)


def _route_complete_task(task_service: TaskService) -> None:
    """Route to Complete Task handler.

    Args:
        task_service: TaskService instance for business operations
    """
    from src.cli.handlers import complete_task_handler
    complete_task_handler(task_service)


def _route_delete_task(task_service: TaskService) -> None:
    """Route to Delete Task handler.

    Args:
        task_service: TaskService instance for business operations
    """
    from src.cli.handlers import delete_task_handler
    delete_task_handler(task_service)
