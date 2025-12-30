# [Task]: T021, T022, T023, T024, T025, T026, T027
"""
Display utilities for ActionMind AI CLI with colors and styling.

This module provides functions for formatted output to the terminal,
including styled headings, feedback messages, task tables, and
user input prompts.
"""

import sys
import os
from typing import List, Optional
from src.models.task import Task


# ANSI Color Codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright foreground colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


# Detect if terminal supports colors
def _supports_colors() -> bool:
    """Check if the terminal supports ANSI colors."""
    return True  # Force colors on


USE_COLORS = _supports_colors()


# Styled text functions
def style(text: str, color: str = "", bold: bool = False) -> str:
    """Apply color and style to text.

    Args:
        text: The text to style
        color: ANSI color code
        bold: Whether to make text bold

    Returns:
        Styled text with color codes, or original text if colors not supported
    """
    if not USE_COLORS:
        return text

    styles = []
    if bold:
        styles.append(Colors.BOLD)
    if color:
        styles.append(color)

    if styles:
        return "".join(styles) + text + Colors.RESET
    return text


# Color helper functions
def cyan(text: str) -> str:
    """Apply cyan color to text."""
    return style(text, Colors.CYAN)

def green(text: str) -> str:
    """Apply green color to text."""
    return style(text, Colors.GREEN)

def red(text: str) -> str:
    """Apply red color to text."""
    return style(text, Colors.RED)

def yellow(text: str) -> str:
    """Apply yellow color to text."""
    return style(text, Colors.YELLOW)

def blue(text: str) -> str:
    """Apply blue color to text."""
    return style(text, Colors.BLUE)

def bright_cyan(text: str) -> str:
    """Apply bright cyan color to text."""
    return style(text, Colors.BRIGHT_CYAN)

def bright_green(text: str) -> str:
    """Apply bright green color to text."""
    return style(text, Colors.BRIGHT_GREEN)

def bright_yellow(text: str) -> str:
    """Apply bright yellow color to text."""
    return style(text, Colors.BRIGHT_YELLOW)

def bright_red(text: str) -> str:
    """Apply bright red color to text."""
    return style(text, Colors.BRIGHT_RED)

def bold(text: str) -> str:
    """Apply bold style to text."""
    return style(text, bold=True)


def display_styled_heading(text: str) -> None:
    """Display a styled heading with decorative borders and colors.

    The heading is centered within a box made of border characters.

    Args:
        text: Heading text to display
    """
    HEADING_BORDER_LENGTH = 40

    # Calculate padding to center the text
    text_length = len(text)
    padding = (HEADING_BORDER_LENGTH - text_length - 2) // 2

    # Create styled heading
    print()
    print(cyan("┌" + "─" * (HEADING_BORDER_LENGTH - 2) + "┐"))
    print(cyan("│") + bright_cyan(" " * padding + text + " " * (HEADING_BORDER_LENGTH - text_length - padding - 2)) + cyan("│"))
    print(cyan("└" + "─" * (HEADING_BORDER_LENGTH - 2) + "┘"))
    print()


def display_success(message: str) -> None:
    """Display a success message in green.

    Args:
        message: Success message text to display
    """
    print(bright_green("✓") + " " + green(message))


def display_warning(message: str) -> None:
    """Display a warning message in yellow.

    Args:
        message: Warning message text to display
    """
    print(bright_yellow("⚠") + " " + yellow(message))


def display_error(message: str) -> None:
    """Display an error message in red.

    Args:
        message: Error message text to display
    """
    print(bright_green("✗") + " " + red(message))


def display_info(message: str) -> None:
    """Display an informational message in cyan.

    Args:
        message: Info message text to display
    """
    print(cyan("○") + " " + cyan(message))


def display_task_table(tasks: List[Task]) -> None:
    """Display tasks in a beautifully formatted table with colors.

    The table shows ID, description, status, and creation time for each task.

    Args:
        tasks: List of tasks to display

    If the task list is empty, displays a friendly "No tasks found" message.
    """
    # Handle empty list
    if not tasks:
        display_info("No tasks found")
        return

    # Define column widths
    id_width = 6
    desc_width = 40
    status_width = 14
    created_width = 18

    # Format created_at timestamp for display
    def format_timestamp(task: Task) -> str:
        """Format task creation timestamp for display."""
        return task.created_at.strftime("%Y-%m-%d %H:%M")

    # Truncate description if too long
    def truncate_description(desc: str, max_len: int) -> str:
        """Truncate description to fit column width."""
        if len(desc) <= max_len:
            return desc
        return desc[:max_len - 3] + "..."

    # Helper to get colored status
    def get_colored_status(status: str) -> str:
        """Return status with appropriate color."""
        if status == "PENDING":
            return yellow(status)
        elif status == "COMPLETED":
            return green(status)
        return status

    # Helper to safely print Unicode/box characters
    def safe_print(text: str) -> None:
        """Print text, falling back if encoding fails."""
        try:
            print(text)
        except UnicodeEncodeError:
            # Strip ANSI codes and replace box chars for terminals that don't support them
            clean = text
            for code in [Colors.RESET, Colors.BOLD, Colors.CYAN, Colors.BRIGHT_CYAN]:
                clean = clean.replace(code, "")
            print(clean.encode('ascii', 'replace').decode('ascii'))

    # Print table header with colors
    safe_print(cyan("┌" + "─" * id_width + "┬" + "─" * desc_width + "┬" +
                     "─" * status_width + "┬" + "─" * created_width + "┐"))

    # Column headers
    print(
        cyan("│") + bold(f" {'ID':<{id_width}}") + cyan("│") +
        bold(f" {'Description':<{desc_width}}") + cyan("│") +
        bold(f" {'Status':<{status_width}}") + cyan("│") +
        bold(f" {'Created At':<{created_width}}") + cyan("│")
    )

    # Separator
    safe_print(cyan("├" + "─" * id_width + "┼" + "─" * desc_width + "┼" +
               "─" * status_width + "┼" + "─" * created_width + "┤"))

    # Print each task row
    for task in tasks:
        desc = truncate_description(task.description, desc_width)
        status_colored = get_colored_status(task.status.value)
        created = format_timestamp(task)

        print(
            cyan("│") + f" {task.id:<{id_width}}" + cyan("│") +
            f" {desc:<{desc_width}}" + cyan("│") +
            f" {status_colored:<{status_width}}" + cyan("│") +
            f" {created:<{created_width}}" + cyan("│")
        )

    # Print bottom border
    safe_print(cyan("└" + "─" * id_width + "┴" + "─" * desc_width + "┴" +
               "─" * status_width + "┴" + "─" * created_width + "┘"))

    # Show task count
    task_count = len(tasks)
    completed_count = sum(1 for t in tasks if t.status.value == "COMPLETED")
    print(f"\n{cyan('Total:')} {task_count} tasks  |  {green('Completed:')} {completed_count}  |  {yellow('Pending:')} {task_count - completed_count}\n")


def prompt_for_input(prompt_text: str) -> str:
    """Prompt the user for input and return their response.

    Args:
        prompt_text: The prompt message to display

    Returns:
        The user's input as a string (may be empty)
    """
    return input(bold(cyan("➤ ") + prompt_text))


def pause_for_acknowledgment() -> None:
    """Pause and wait for user to press Enter.

    This function displays a prompt and waits for the user to press Enter
    before continuing.
    """
    input(cyan("\nPress Enter to continue...") + " ")


def clear_screen() -> None:
    """Clear the terminal screen.

    This is a utility function for clearing the screen between
    menu displays. Works across platforms (Windows, macOS, Linux).
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def display_main_menu_options() -> None:
    """Display the main menu options with colors and icons.

    Shows the 5 numbered menu options for user selection.
    """
    print()
    print(f"  {cyan('1.')} Add Task")
    print(f"  {green('2.')} View Tasks")
    print(f"  {yellow('3.')} Complete Task")
    print(f"  {blue('4.')} Delete Task")
    print(f"  {red('5.')} Exit")
    print()
