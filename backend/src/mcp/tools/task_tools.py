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

        # Create task in database
        try:
            try:
                from backend.src.db.session import async_session_maker
            except ImportError:
                from src.db.session import async_session_maker

            async with async_session_maker() as session:
                # Create task directly with all fields
                completed = (status == "done")

                task = Task(
                    user_id=_to_int(user_id),  # Use authenticated user ID
                    title=title,
                    description=description,
                    completed=completed,
                    status=status,
                    priority=priority
                )
                session.add(task)
                await session.flush()  # Get ID without committing

                # Commit the transaction
                await session.commit()

                # Store task data for return (convert int IDs to strings for API consistency)
                task_data = {
                    "task_id": str(task.id),
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }

                # Return success with task data
                return MCPToolResult(
                    success=True,
                    data=task_data,
                    user_id=str(task.user_id)
                )

        except Exception as e:
            # Handle database errors
            return MCPToolResult(
                success=False,
                error=f"Failed to create task: {str(e)}",
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
        status = kwargs.get("status", "all")
        try:
            try:
                from backend.src.db.session import async_session_maker
            except ImportError:
                from src.db.session import async_session_maker

            async with async_session_maker() as session:
                tasks = await TaskRepository.list_tasks(session, user_id, status)

                # Format tasks for response (convert int IDs to strings)
                task_list = []
                for task in tasks:
                    task_list.append({
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "status": task.status,
                        "priority": task.priority,
                        "created_at": task.created_at.isoformat()
                    })

                result_data = {
                    "tasks": task_list,
                    "count": len(task_list)
                }

                return MCPToolResult(
                    success=True,
                    data=result_data,
                    user_id=user_id
                )

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

        try:
            try:
                from backend.src.db.session import async_session_maker
            except ImportError:
                from src.db.session import async_session_maker

            async with async_session_maker() as session:
                # First, find the task by title
                tasks = await TaskRepository.list_tasks(session, user_id)
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
                    return MCPToolResult(
                        success=False,
                        error=f"Task '{title}' not found",
                        user_id=user_id
                    )

                # Delete the task
                deleted = await TaskRepository.delete_task(session, user_id, matching_task.id)

                # Commit the transaction
                await session.commit()

                if deleted:
                    return MCPToolResult(
                        success=True,
                        data={
                            "deleted": True,
                            "title": matching_task.title,
                            "task_id": str(matching_task.id)  # Convert int to string
                        },
                        user_id=user_id
                    )
                else:
                    return MCPToolResult(
                        success=False,
                        error=f"Failed to delete task '{title}'",
                        user_id=user_id
                    )

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

        try:
            try:
                from backend.src.db.session import async_session_maker
            except ImportError:
                from src.db.session import async_session_maker

            async with async_session_maker() as session:
                # If no title provided, get the most recent pending task
                if not title:
                    tasks = await TaskRepository.list_tasks(session, user_id, status="pending")
                    if tasks:
                        matching_task = tasks[0]  # Most recent pending task
                        title = matching_task.title
                    else:
                        return MCPToolResult(
                            success=False,
                            error="No pending tasks found to complete",
                            user_id=user_id
                        )
                else:
                    # Find the task by title
                    tasks = await TaskRepository.list_tasks(session, user_id)
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
                        return MCPToolResult(
                            success=False,
                            error=f"Task '{title}' not found",
                            user_id=user_id
                        )

                # Update task to completed (both completed and status fields)
                result = await session.execute(
                    sql_update(Task)
                    .where(Task.id == matching_task.id, Task.user_id == _to_int(user_id))
                    .values(completed=True, status="done")
                    .returning(Task)
                )

                # Commit the transaction
                await session.commit()

                updated_task = result.scalar_one_or_none()
                if updated_task:
                    return MCPToolResult(
                        success=True,
                        data={
                            "completed": True,
                            "status": "done",
                            "title": updated_task.title,
                            "task_id": str(updated_task.id),
                            "completed_at": updated_task.updated_at.isoformat()
                        },
                        user_id=user_id
                    )
                else:
                    return MCPToolResult(
                        success=False,
                        error=f"Failed to complete task '{title}'",
                        user_id=user_id
                    )

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

        try:
            try:
                from backend.src.db.session import async_session_maker
            except ImportError:
                from src.db.session import async_session_maker

            async with async_session_maker() as session:
                matching_task = None

                # PRIORITY 1: If task_id is provided, use it directly
                if task_id:
                    # Get task by ID
                    tasks = await TaskRepository.list_tasks(session, user_id)
                    for task in tasks:
                        if str(task.id) == str(task_id):
                            matching_task = task
                            break

                    if not matching_task:
                        return MCPToolResult(
                            success=False,
                            error=f"Task with ID '{task_id}' not found",
                            user_id=user_id
                        )

                # PRIORITY 2: If title is provided, find by title
                elif title:
                    # Find the task by title
                    tasks = await TaskRepository.list_tasks(session, user_id)

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
                        return MCPToolResult(
                            success=False,
                            error=f"Task '{title}' not found",
                            user_id=user_id
                        )

                # PRIORITY 3: Fallback to most recent task
                else:
                    tasks = await TaskRepository.list_tasks(session, user_id)
                    if tasks:
                        matching_task = tasks[0]  # Most recent task
                    else:
                        return MCPToolResult(
                            success=False,
                            error="No tasks found to update",
                            user_id=user_id
                        )

                # Update both completed and status fields in one operation
                completed = (status == "done")
                result = await session.execute(
                    sql_update(Task)
                    .where(Task.id == matching_task.id, Task.user_id == _to_int(user_id))
                    .values(completed=completed, status=status)
                    .returning(Task)
                )

                # Commit the transaction
                await session.commit()

                updated_task = result.scalar_one_or_none()
                if updated_task:
                    return MCPToolResult(
                        success=True,
                        data={
                            "updated": True,
                            "title": updated_task.title,
                            "task_id": str(updated_task.id),
                            "status": status,
                            "completed": completed,
                            "updated_at": updated_task.updated_at.isoformat()
                        },
                        user_id=user_id
                    )
                else:
                    return MCPToolResult(
                        success=False,
                        error=f"Failed to update task '{title}'",
                        user_id=user_id
                    )

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

        try:
            try:
                from backend.src.db.session import async_session_maker
            except ImportError:
                from src.db.session import async_session_maker

            async with async_session_maker() as session:
                matching_task = None

                # PRIORITY 1: If task_id is provided, use it directly
                if task_id:
                    # Get task by ID
                    tasks = await TaskRepository.list_tasks(session, user_id)
                    for task in tasks:
                        if str(task.id) == str(task_id):
                            matching_task = task
                            break

                    if not matching_task:
                        return MCPToolResult(
                            success=False,
                            error=f"Task with ID '{task_id}' not found",
                            user_id=user_id
                        )

                # PRIORITY 2: If title is provided, find by title
                elif title:
                    # Find the task by title
                    tasks = await TaskRepository.list_tasks(session, user_id)

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
                        return MCPToolResult(
                            success=False,
                            error=f"Task '{title}' not found",
                            user_id=user_id
                        )

                # PRIORITY 3: Fallback to most recent task
                else:
                    tasks = await TaskRepository.list_tasks(session, user_id)
                    if tasks:
                        matching_task = tasks[0]  # Most recent task
                    else:
                        return MCPToolResult(
                            success=False,
                            error="No tasks found to update",
                            user_id=user_id
                        )

                # Update task priority
                result = await session.execute(
                    sql_update(Task)
                    .where(Task.id == matching_task.id, Task.user_id == _to_int(user_id))
                    .values(priority=priority)
                    .returning(Task)
                )

                # Commit the transaction
                await session.commit()

                updated_task = result.scalar_one_or_none()
                if updated_task:
                    return MCPToolResult(
                        success=True,
                        data={
                            "updated": True,
                            "title": updated_task.title,
                            "task_id": str(updated_task.id),
                            "priority": priority,
                            "updated_at": updated_task.updated_at.isoformat()
                        },
                        user_id=user_id
                    )
                else:
                    return MCPToolResult(
                        success=False,
                        error=f"Failed to update task '{title}'",
                        user_id=user_id
                    )

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
