# [Task]: T005
"""
CLI interface layer for ActionMind AI.

This module contains all user-facing CLI components including menus,
handlers, and display utilities.
"""

from src.cli.menu import main_menu_loop
from src.cli.handlers import (
    add_task_handler,
    view_tasks_handler,
    complete_task_handler,
    delete_task_handler,
)
from src.cli.display import (
    display_styled_heading,
    display_success,
    display_warning,
    display_error,
    display_task_table,
    prompt_for_input,
    pause_for_acknowledgment,
)

__all__ = [
    "main_menu_loop",
    "add_task_handler",
    "view_tasks_handler",
    "complete_task_handler",
    "delete_task_handler",
    "display_styled_heading",
    "display_success",
    "display_warning",
    "display_error",
    "display_task_table",
    "prompt_for_input",
    "pause_for_acknowledgment",
]
