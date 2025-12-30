# [Task]: T038, T039, T040, T065, T066
"""
Main entry point for ActionMind AI CLI Task Manager (Phase 1).

This module initializes the application and starts the main menu loop.
"""

import sys
import io


def _configure_output_encoding() -> None:
    """Configure UTF-8 output for better cross-platform compatibility.

    On Windows, attempts to set console to UTF-8 mode for proper
    display of box-drawing characters and emojis.
    Falls back gracefully if configuration fails.
    """
    if sys.platform == 'win32':
        try:
            # Try to configure Windows console for UTF-8
            import codecs
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except:
            # If configuration fails, application will still work
            # with ASCII fallbacks in display.py
            pass


def graceful_exit() -> None:
    """Display farewell message and exit.

    Called when user selects option 5 (Exit) from the main menu.
    """
    print()
    print("Thank you for using ActionMind AI!")
    print()


def main() -> int:
    """Main entry point for the CLI application.

    Initializes storage, task service, and starts the main menu loop.

    Returns:
        Exit code (0 for successful exit, 1 for errors)

    Application flow:
        1. Configure output encoding
        2. Initialize InMemoryStorage for task persistence
        3. Initialize TaskService with storage dependency injection
        4. Display welcome message
        5. Start main menu loop
        6. Handle graceful exit on menu selection 5 or Ctrl+C
    """
    # Configure UTF-8 output for better display on Windows
    _configure_output_encoding()

    try:
        # Import here to avoid circular imports
        from src.services.storage import InMemoryStorage
        from src.services.task_service import TaskService
        from src.cli.menu import main_menu_loop

        # Initialize storage (Phase 1: in-memory only)
        storage = InMemoryStorage()

        # Initialize task service with dependency injection
        task_service = TaskService(storage)

        # Start the main menu loop with graceful exit handler
        main_menu_loop(task_service, exit_handler=graceful_exit)

        return 0

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print()
        print("Exiting gracefully...")
        return 0

    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    """Allow running the module directly with: python -m src.main"""
    sys.exit(main())
