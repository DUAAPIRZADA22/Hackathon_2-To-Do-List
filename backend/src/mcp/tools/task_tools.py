"""
MCP Tools for Task Management (User Story 1)

Concrete MCP tool implementations for task operations.
All tools enforce user ownership and follow MCP protocol.

User Story 1 (MVP): add_task tool for natural language task creation.

Future stories will add:
- list_tasks (US2)
- complete_task (US2)
- update_task (US3)
- delete_task (US4)
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from backend.src.mcp.tools.base import (
        BaseMCPTool,
        MCPToolResult,
        MCPToolError,
    )
    from backend.src.db.repository import TaskRepository, _to_int
    from backend.src.db.models import Task
    from sqlalchemy import update as sql_update
except ImportError:
    from src.mcp.tools.base import (
        BaseMCPTool,
        MCPToolResult,
        MCPToolError,
    )
    from src.db.repository import TaskRepository, _to_int
    from src.db.models import Task
    from sqlalchemy import update as sql_update


# =====================================================
# Add Task Tool (User Story 1 - MVP)
# =====================================================

class AddTaskTool(BaseMCPTool):
    """
    MCP tool for creating new tasks.

    User Story 1 (MVP): Enables natural language task creation.

    IMPORTANT: This tool should be called AFTER asking the user for status and priority.
    The system prompt instructs the AI to have a conversation before calling this tool.

    Example:
        User: "Add a task to buy groceries"
        AI: "What should the status be? (To-Do, In-Progress, or Completed)"
        User: "to-do"
        AI: "And the priority? (Low, Medium, or High)"
        User: "medium"
        AI: Invokes add_task(title="Buy groceries", status="todo", priority="medium")
    """

    def __init__(self):
        """Initialize add_task tool."""
        super().__init__(
            name="add_task",
            description=(
                "Create a new task for the user. "
                "Use this when the user wants to add, create, or remember a task. "
                "IMPORTANT: Ask for status and priority BEFORE calling this tool. "
                "Only call this tool after collecting all information from the user."
            )
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for add_task parameters.

        Returns:
            JSON Schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (required, must not be empty)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description with additional details"
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "done"],
                    "description": "Task status: 'todo', 'in_progress', or 'done'. You MUST ask the user for this if not provided."
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Task priority: 'low', 'medium', 'high', or 'urgent'. You MUST ask the user for this if not provided."
                }
            },
            "required": ["title", "status", "priority"]
        }

    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute add_task tool.

        Args:
            user_id: User ID (from JWT, enforces ownership)
            **kwargs: Tool parameters (title, description, status, priority)

        Returns:
            MCPToolResult with created task data

        Example:
            result = await tool.execute(
                user_id="123",
                title="Buy groceries",
                status="todo",
                priority="medium"
            )

            assert result.success is True
            assert result.data["task_id"] == 123
        """
        # Extract parameters (all are now required)
        title = kwargs.get("title")
        description = kwargs.get("description")
        status = kwargs.get("status")
        priority = kwargs.get("priority")

        # Validate required fields
        if not title:
            return MCPToolResult(
                success=False,
                error="Title is required and cannot be empty",
                user_id=user_id
            )

        if not status:
            return MCPToolResult(
                success=False,
                error="Status is required (todo, in_progress, or done)",
                user_id=user_id
            )

        if not priority:
            return MCPToolResult(
                success=False,
                error="Priority is required (low, medium, high, or urgent)",
                user_id=user_id
            )

        if not isinstance(title, str):
            return MCPToolResult(
                success=False,
                error="Title must be a string",
                user_id=user_id
            )

        title = title.strip()
        if len(title) == 0:
            return MCPToolResult(
                success=False,
                error="Title cannot be empty or whitespace only",
                user_id=user_id
            )

        if len(title) > 255:
            return MCPToolResult(
                success=False,
                error="Title cannot exceed 255 characters",
                user_id=user_id
            )

        # CRITICAL FIX: Run sync database operations in a thread pool
        # This prevents async/sync context issues that cause transactions to not commit properly
        import asyncio

        def _create_task_in_sync_context():
            """Synchronous function to create task - runs in thread pool"""
            try:
                from src.services.task import TaskService
                from src.core.database import SessionLocal
                from src.models.schemas import TaskCreate
                from src.models.task import Task as TaskModel

                # Use sync database session
                db = SessionLocal()
                print(f"[DEBUG ADD_TASK] Creating sync session, connection: {db.bind.url if hasattr(db, 'bind') and db.bind else 'no bind'}")

                try:
                    # Create task data schema
                    task_create = TaskCreate(
                        title=title,
                        description=description,
                        status=status,
                        priority=priority,
                        completed=(status == "done")
                    )

                    print(f"[DEBUG ADD_TASK] About to call TaskService.create_task with user_id={_to_int(user_id)}")

                    # Create task using TaskService (same as tasks API)
                    user_id_int = _to_int(user_id)
                    task = TaskService.create_task(db, task_create, user_id_int)

                    print(f"[DEBUG ADD_TASK] Task created with ID={task.id}, title={task.title}")
                    print(f"[DEBUG ADD_TASK] Session in_transaction: {db.in_transaction()}")

                    # CRITICAL: Verify the task was actually persisted
                    # Create a NEW session to verify (to avoid cached data)
                    verification_db = SessionLocal()
                    try:
                        verified_task = verification_db.query(TaskModel).filter(TaskModel.id == task.id).first()
                        print(f"[DEBUG ADD_TASK] VERIFICATION using new session: task exists = {verified_task is not None}")
                        if verified_task:
                            print(f"[DEBUG ADD_TASK] VERIFIED: task.title={verified_task.title}, task.status={verified_task.status}")
                    finally:
                        verification_db.close()

                    # Store task data for return (convert all to simple types for JSON serialization)
                    task_data = {
                        "task_id": str(task.id),
                        "user_id": str(task.user_id),
                        "title": task.title,
                        "description": task.description or "",
                        "completed": bool(task.completed),
                        "status": task.status or "todo",
                        "priority": task.priority or "medium",
                        "created_at": task.created_at.isoformat() if task.created_at else "",
                        "updated_at": task.updated_at.isoformat() if task.updated_at else None
                    }

                    print(f"[DEBUG ADD_TASK] Returning success with task_data: {task_data}")

                    # Return both success flag and data
                    return (True, task_data, None)

                except Exception as inner_e:
                    print(f"[DEBUG ADD_TASK] Exception in sync context: {type(inner_e).__name__}: {str(inner_e)}")
                    import traceback
                    traceback.print_exc()
                    # Rollback to ensure no partial state
                    db.rollback()
                    return (False, None, f"Database error: {str(inner_e)}")
                finally:
                    print(f"[DEBUG ADD_TASK] Closing database session")
                    db.close()

            except Exception as outer_e:
                print(f"[DEBUG ADD_TASK] Exception in sync wrapper: {type(outer_e).__name__}: {str(outer_e)}")
                import traceback
                traceback.print_exc()
                return (False, None, f"Setup error: {str(outer_e)}")

        # Run the sync database operation in a thread pool
        # This is critical when calling sync code from async context
        try:
            success, data, error = await asyncio.to_thread(_create_task_in_sync_context)

            if success:
                return MCPToolResult(
                    success=True,
                    data=data,
                    user_id=data.get("user_id", user_id) if data else user_id
                )
            else:
                return MCPToolResult(
                    success=False,
                    error=error or "Unknown error occurred",
                    user_id=user_id
                )
        except Exception as e:
            print(f"[DEBUG ADD_TASK] Exception in to_thread: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return MCPToolResult(
                success=False,
                error=f"Failed to execute database operation: {str(e)}",
                user_id=user_id
            )


# =====================================================
# List Tasks Tool
# =====================================================

class ListTasksTool(BaseMCPTool):
    """
    MCP tool for listing all tasks.

    User Story 2: Enables viewing all user tasks.

    Example:
        User: "show my tasks" or "list all tasks"
        Agent: Invokes list_tasks()
        Tool: Returns all tasks for the user
    """

    def __init__(self):
        """Initialize list_tasks tool."""
        super().__init__(
            name="list_tasks",
            description=(
                "List all tasks for the user. "
                "Use this when the user wants to see, show, or list their tasks. "
                "Returns all tasks with their titles, descriptions, and completion status."
            )
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for list_tasks parameters.

        Returns:
            JSON Schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by status (optional: 'all', 'pending', or 'completed')"
                }
            }
        }

    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute list_tasks tool.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool parameters (status)

        Returns:
            MCPToolResult with list of tasks
        """
        status_filter = kwargs.get("status", "all")
        import asyncio

        def _list_tasks_sync():
            """Synchronous function to list tasks - runs in thread pool"""
            try:
                from src.services.task import TaskService
                from src.core.database import SessionLocal

                # Use sync database session
                db = SessionLocal()
                try:
                    user_id_int = _to_int(user_id)
                    tasks = TaskService.get_all_tasks(db, user_id_int, skip=0, limit=100)

                    # Filter by status if needed
                    if status_filter == "pending":
                        tasks = [t for t in tasks if not t.completed]
                    elif status_filter == "completed":
                        tasks = [t for t in tasks if t.completed]

                    # Format tasks for response (convert int IDs to strings)
                    task_list = []
                    for task in tasks:
                        task_list.append({
                            "task_id": str(task.id),
                            "title": task.title,
                            "description": task.description or "",
                            "completed": bool(task.completed),
                            "status": task.status or "todo",
                            "priority": task.priority or "medium",
                            "created_at": task.created_at.isoformat() if task.created_at else ""
                        })

                    result_data = {
                        "tasks": task_list,
                        "count": len(task_list)
                    }

                    return (True, result_data, None)
                finally:
                    db.close()
            except Exception as e:
                return (False, None, str(e))

        try:
            success, data, error = await asyncio.to_thread(_list_tasks_sync)
            if success:
                return MCPToolResult(success=True, data=data, user_id=user_id)
            else:
                return MCPToolResult(success=False, error=error, user_id=user_id)
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to list tasks: {str(e)}",
                user_id=user_id
            )


# =====================================================
# Delete Task Tool
# =====================================================

class DeleteTaskTool(BaseMCPTool):
    """
    MCP tool for deleting a task.

    User Story 4: Enables task deletion.

    Example:
        User: "delete task: buy groceries"
        Agent: Invokes delete_task(title="buy groceries")
        Tool: Deletes the task and returns confirmation
    """

    def __init__(self):
        """Initialize delete_task tool."""
        super().__init__(
            name="delete_task",
            description=(
                "Delete a task by title. "
                "Use this when the user wants to delete, remove, or get rid of a task. "
                "Matches tasks by title (exact or partial match)."
            )
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for delete_task parameters.

        Returns:
            JSON Schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the task to delete (required)"
                }
            },
            "required": ["title"]
        }

    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute delete_task tool.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool parameters (title)

        Returns:
            MCPToolResult with deletion confirmation
        """
        title = kwargs.get("title")

        if not title:
            return MCPToolResult(
                success=False,
                error="Title is required",
                user_id=user_id
            )

        import asyncio

        def _delete_task_sync():
            """Synchronous function to delete task - runs in thread pool"""
            try:
                from src.services.task import TaskService
                from src.core.database import SessionLocal

                # Use sync database session
                db = SessionLocal()
                try:
                    user_id_int = _to_int(user_id)

                    # Get all tasks for the user
                    tasks = TaskService.get_all_tasks(db, user_id_int, skip=0, limit=100)

                    # Try exact match first
                    matching_task = None
                    for task in tasks:
                        if task.title.lower() == title.lower():
                            matching_task = task
                            break

                    # If no exact match, try partial match
                    if not matching_task:
                        for task in tasks:
                            if title.lower() in task.title.lower():
                                matching_task = task
                                break

                    if not matching_task:
                        return (False, None, f"Task '{title}' not found")

                    # Delete the task
                    TaskService.delete_task(db, matching_task.id, user_id_int)

                    return (True, {
                        "deleted": True,
                        "title": matching_task.title,
                        "task_id": str(matching_task.id)
                    }, None)

                finally:
                    db.close()
            except Exception as e:
                return (False, None, str(e))

        try:
            success, data, error = await asyncio.to_thread(_delete_task_sync)
            if success:
                return MCPToolResult(success=True, data=data, user_id=user_id)
            else:
                return MCPToolResult(success=False, error=error, user_id=user_id)
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to delete task: {str(e)}",
                user_id=user_id
            )


# =====================================================
# Complete Task Tool
# =====================================================

class CompleteTaskTool(BaseMCPTool):
    """
    MCP tool for marking a task as completed.

    User Story 2: Enables task completion.

    Example:
        User: "mark task buy groceries as done" or "complete this task"
        Agent: Invokes complete_task(title="buy groceries")
        Tool: Marks the task as completed and returns confirmation
    """

    def __init__(self):
        """Initialize complete_task tool."""
        super().__init__(
            name="complete_task",
            description=(
                "Mark a task as completed. "
                "Use this when the user wants to mark, complete, or finish a task. "
                "Matches tasks by title (exact or partial match). "
                "If no title is specified, attempts to complete the most recent pending task."
            )
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for complete_task parameters.

        Returns:
            JSON Schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the task to complete (optional - if not provided, completes the most recent pending task)"
                }
            }
        }

    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute complete_task tool.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool parameters (title)

        Returns:
            MCPToolResult with completion confirmation
        """
        title = kwargs.get("title")
        import asyncio

        def _complete_task_sync():
            """Synchronous function to complete task - runs in thread pool"""
            try:
                from src.services.task import TaskService
                from src.core.database import SessionLocal
                from src.models.schemas import TaskUpdate

                # Use sync database session
                db = SessionLocal()
                try:
                    user_id_int = _to_int(user_id)

                    # Get all tasks for the user
                    tasks = TaskService.get_all_tasks(db, user_id_int, skip=0, limit=100)

                    # If no title provided, get the most recent pending task
                    if not title:
                        matching_task = None
                        for task in tasks:
                            if not task.completed:
                                matching_task = task
                                break
                        if not matching_task:
                            return (False, None, "No pending tasks found to complete")
                    else:
                        # Find the task by title
                        matching_task = None
                        # Try exact match first
                        for task in tasks:
                            if task.title.lower() == title.lower():
                                matching_task = task
                                break

                        # If no exact match, try partial match
                        if not matching_task:
                            for task in tasks:
                                if title.lower() in task.title.lower():
                                    matching_task = task
                                    break

                        if not matching_task:
                            return (False, None, f"Task '{title}' not found")

                    # Update task to completed
                    update_data = TaskUpdate(
                        title=matching_task.title,
                        description=matching_task.description,
                        completed=True,
                        status="done",
                        priority=matching_task.priority
                    )
                    updated_task = TaskService.update_task(db, matching_task.id, update_data, user_id_int)

                    return (True, {
                        "completed": True,
                        "status": "done",
                        "title": updated_task.title,
                        "task_id": str(updated_task.id),
                        "completed_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                    }, None)

                finally:
                    db.close()
            except Exception as e:
                return (False, None, str(e))

        try:
            success, data, error = await asyncio.to_thread(_complete_task_sync)
            if success:
                return MCPToolResult(success=True, data=data, user_id=user_id)
            else:
                return MCPToolResult(success=False, error=error, user_id=user_id)
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to complete task: {str(e)}",
                user_id=user_id
            )


# =====================================================
# Set Task Status Tool
# =====================================================

class SetTaskStatusTool(BaseMCPTool):
    """
    MCP tool for changing task status.

    Allows marking tasks as done, in_progress, or todo.

    Example:
        User: "mark task buy groceries as done" or "set buy milk to in progress"
        Agent: Invokes set_task_status(title="buy groceries", status="done")
        Tool: Updates the task status and returns confirmation
    """

    def __init__(self):
        """Initialize set_task_status tool."""
        super().__init__(
            name="set_task_status",
            description=(
                "Change the status of a task (done, in_progress, or todo). "
                "Use this when the user wants to mark, set, or change a task's status. "
                "IMPORTANT: If a task was just created in the conversation, use task_id from the creation result. "
                "Otherwise, matches tasks by title (exact or partial match). "
                "If neither task_id nor title is specified, attempts to update the most recent task."
            )
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for set_task_status parameters.

        Returns:
            JSON Schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of the task to update (optional - use this when a task was just created in the conversation)"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the task to update (optional - use if user explicitly mentions task name)"
                },
                "status": {
                    "type": "string",
                    "enum": ["done", "in_progress", "todo"],
                    "description": "New status for the task (required): 'done', 'in_progress', or 'todo'"
                }
            },
            "required": ["status"]
        }

    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute set_task_status tool.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool parameters (task_id, title, status)

        Returns:
            MCPToolResult with status update confirmation
        """
        task_id = kwargs.get("task_id")
        title = kwargs.get("title")
        status = kwargs.get("status")

        if not status:
            return MCPToolResult(
                success=False,
                error="Status is required (done, in_progress, or todo)",
                user_id=user_id
            )

        if status not in ["done", "in_progress", "todo"]:
            return MCPToolResult(
                success=False,
                error=f"Invalid status '{status}'. Must be 'done', 'in_progress', or 'todo'",
                user_id=user_id
            )

        import asyncio

        def _set_status_sync():
            """Synchronous function to set task status - runs in thread pool"""
            try:
                from src.services.task import TaskService
                from src.core.database import SessionLocal
                from src.models.schemas import TaskUpdate

                # Use sync database session
                db = SessionLocal()
                try:
                    user_id_int = _to_int(user_id)

                    # Get all tasks for the user
                    tasks = TaskService.get_all_tasks(db, user_id_int, skip=0, limit=100)

                    matching_task = None

                    # PRIORITY 1: If task_id is provided, use it directly
                    if task_id:
                        for task in tasks:
                            if str(task.id) == str(task_id):
                                matching_task = task
                                break

                        if not matching_task:
                            return (False, None, f"Task with ID '{task_id}' not found")

                    # PRIORITY 2: If title is provided, find by title
                    elif title:
                        # Try exact match first
                        for task in tasks:
                            if task.title.lower() == title.lower():
                                matching_task = task
                                break

                        # If no exact match, try partial match
                        if not matching_task:
                            for task in tasks:
                                if title.lower() in task.title.lower():
                                    matching_task = task
                                    break

                        if not matching_task:
                            return (False, None, f"Task '{title}' not found")

                    # PRIORITY 3: Fallback to most recent task
                    else:
                        if tasks:
                            matching_task = tasks[0]  # Most recent task
                        else:
                            return (False, None, "No tasks found to update")

                    # Update task status
                    completed = (status == "done")
                    update_data = TaskUpdate(
                        title=matching_task.title,
                        description=matching_task.description,
                        completed=completed,
                        status=status,
                        priority=matching_task.priority,
                        due_date=matching_task.due_date
                    )
                    updated_task = TaskService.update_task(db, matching_task.id, update_data, user_id_int)

                    return (True, {
                        "updated": True,
                        "title": updated_task.title,
                        "task_id": str(updated_task.id),
                        "status": status,
                        "completed": completed,
                        "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                    }, None)

                finally:
                    db.close()
            except Exception as e:
                return (False, None, str(e))

        try:
            success, data, error = await asyncio.to_thread(_set_status_sync)
            if success:
                return MCPToolResult(success=True, data=data, user_id=user_id)
            else:
                return MCPToolResult(success=False, error=error, user_id=user_id)
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to update task status: {str(e)}",
                user_id=user_id
            )


# =====================================================
# Set Task Priority Tool
# =====================================================

class SetTaskPriorityTool(BaseMCPTool):
    """
    MCP tool for changing task priority.

    Allows setting task priority to urgent, high, medium, or low.

    Example:
        User: "set priority high for buy groceries" or "mark buy milk as high priority"
        Agent: Invokes set_task_priority(title="buy groceries", priority="high")
        Tool: Updates the task priority and returns confirmation
    """

    def __init__(self):
        """Initialize set_task_priority tool."""
        super().__init__(
            name="set_task_priority",
            description=(
                "Change the priority of a task (urgent, high, medium, or low). "
                "Use this when the user wants to set, mark, or change a task's priority. "
                "IMPORTANT: If a task was just created in the conversation, use task_id from the creation result. "
                "Otherwise, matches tasks by title (exact or partial match). "
                "If neither task_id nor title is specified, attempts to update the most recent task."
            )
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for set_task_priority parameters.

        Returns:
            JSON Schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of the task to update (optional - use this when a task was just created in the conversation)"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the task to update (optional - use if user explicitly mentions task name)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "medium", "low"],
                    "description": "New priority for the task (required): 'urgent', 'high', 'medium', or 'low'"
                }
            },
            "required": ["priority"]
        }

    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute set_task_priority tool.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool parameters (task_id, title, priority)

        Returns:
            MCPToolResult with priority update confirmation
        """
        task_id = kwargs.get("task_id")
        title = kwargs.get("title")
        priority = kwargs.get("priority")

        if not priority:
            return MCPToolResult(
                success=False,
                error="Priority is required (urgent, high, medium, or low)",
                user_id=user_id
            )

        if priority not in ["urgent", "high", "medium", "low"]:
            return MCPToolResult(
                success=False,
                error=f"Invalid priority '{priority}'. Must be 'urgent', 'high', 'medium', or 'low'",
                user_id=user_id
            )

        import asyncio

        def _set_priority_sync():
            """Synchronous function to set task priority - runs in thread pool"""
            try:
                from src.services.task import TaskService
                from src.core.database import SessionLocal
                from src.models.schemas import TaskUpdate

                # Use sync database session
                db = SessionLocal()
                try:
                    user_id_int = _to_int(user_id)

                    # Get all tasks for the user
                    tasks = TaskService.get_all_tasks(db, user_id_int, skip=0, limit=100)

                    matching_task = None

                    # PRIORITY 1: If task_id is provided, use it directly
                    if task_id:
                        for task in tasks:
                            if str(task.id) == str(task_id):
                                matching_task = task
                                break

                        if not matching_task:
                            return (False, None, f"Task with ID '{task_id}' not found")

                    # PRIORITY 2: If title is provided, find by title
                    elif title:
                        # Try exact match first
                        for task in tasks:
                            if task.title.lower() == title.lower():
                                matching_task = task
                                break

                        # If no exact match, try partial match
                        if not matching_task:
                            for task in tasks:
                                if title.lower() in task.title.lower():
                                    matching_task = task
                                    break

                        if not matching_task:
                            return (False, None, f"Task '{title}' not found")

                    # PRIORITY 3: Fallback to most recent task
                    else:
                        if tasks:
                            matching_task = tasks[0]  # Most recent task
                        else:
                            return (False, None, "No tasks found to update")

                    # Update task priority
                    update_data = TaskUpdate(
                        title=matching_task.title,
                        description=matching_task.description,
                        completed=matching_task.completed,
                        status=matching_task.status,
                        priority=priority,
                        due_date=matching_task.due_date
                    )
                    updated_task = TaskService.update_task(db, matching_task.id, update_data, user_id_int)

                    return (True, {
                        "updated": True,
                        "title": updated_task.title,
                        "task_id": str(updated_task.id),
                        "priority": priority,
                        "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                    }, None)

                finally:
                    db.close()
            except Exception as e:
                return (False, None, str(e))

        try:
            success, data, error = await asyncio.to_thread(_set_priority_sync)
            if success:
                return MCPToolResult(success=True, data=data, user_id=user_id)
            else:
                return MCPToolResult(success=False, error=error, user_id=user_id)
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to update task priority: {str(e)}",
                user_id=user_id
            )


# =====================================================
# Tool Registration Helper
# =====================================================

def get_user_story_1_tools():
    """
    Get all MCP tools for User Story 1 (MVP).

    Returns:
        List of MCP tool instances

    Example:
        tools = get_user_story_1_tools()
        # Returns: [AddTaskTool(), ListTasksTool(), CompleteTaskTool(), DeleteTaskTool(), SetTaskStatusTool(), SetTaskPriorityTool()]
    """
    return [
        AddTaskTool(),
        ListTasksTool(),
        CompleteTaskTool(),
        DeleteTaskTool(),
        SetTaskStatusTool(),
        SetTaskPriorityTool(),
    ]


# =====================================================
# Future Tools (Placeholder for US2-US5)
# =====================================================

# These will be implemented in future user stories:

# class ListTasksTool(BaseMCPTool):
#     """MCP tool for listing tasks (User Story 2)."""
#     pass

# class CompleteTaskTool(BaseMCPTool):
#     """MCP tool for completing tasks (User Story 2)."""
#     pass

# class UpdateTaskTool(BaseMCPTool):
#     """MCP tool for updating tasks (User Story 3)."""
#     pass

# class DeleteTaskTool(BaseMCPTool):
#     """MCP tool for deleting tasks (User Story 4)."""
#     pass
