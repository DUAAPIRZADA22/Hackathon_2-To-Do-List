"""
MCP Server for Todo AI Chatbot (Phase III)

Implements MCP server with tool registry and initialization.
Provides centralized tool management for OpenAI Agents SDK integration.

Architecture Principles:
- Tool registry: Centralized tool management
- User identity: All tool executions enforce user ownership
- Extensible: Easy to add new tools
- Type-safe: JSON Schema for parameter validation
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel

try:
    from backend.src.mcp.tools.base import (
        BaseMCPTool,
        MCPToolRegistry,
        MCPToolResult,
        MCPToolError,
    )
except ImportError:
    from src.mcp.tools.base import (
        BaseMCPTool,
        MCPToolRegistry,
        MCPToolResult,
        MCPToolError,
    )


# =====================================================
# MCP Server Configuration
# =====================================================

class MCPServerConfig(BaseModel):
    """
    Configuration for MCP server.

    Attributes:
        server_name: Human-readable server name
        server_version: Server version string
        tools: List of registered tools
    """
    server_name: str = "actionmind-todo-chatbot"
    server_version: str = "1.0.0"
    tools: List[str] = []


# =====================================================
# MCP Server
# =====================================================

class MCPServer:
    """
    MCP Server for tool management and execution.

    Acts as the central hub for all MCP tools. Provides
    registration, discovery, and execution capabilities.

    Example:
        server = MCPServer()

        # Register tools
        server.register_tool(AddTaskTool())
        server.register_tool(ListTasksTool())

        # Get tool schemas for OpenAI
        schemas = server.get_tool_schemas()

        # Execute tool
        result = await server.execute_tool("add_task", user_id="123", title="Buy groceries")
    """

    def __init__(self, name: str = "actionmind-todo-chatbot", version: str = "1.0.0"):
        """
        Initialize MCP server.

        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.registry = MCPToolRegistry()

    def register_tool(self, tool: BaseMCPTool) -> None:
        """
        Register an MCP tool with the server.

        Args:
            tool: MCP tool instance to register

        Raises:
            ValueError: If tool name already registered
        """
        self.registry.register(tool)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get JSON schemas for all registered tools.

        Returns:
            List of tool schemas for OpenAI function calling

        Example:
            schemas = server.get_tool_schemas()
            # Returns:
            # [
            #     {
            #         "name": "add_task",
            #         "description": "Create a new task",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {...},
            #             "required": [...]
            #         }
            #     },
            #     ...
            # ]
        """
        return self.registry.get_all_schemas()

    async def execute_tool(
        self,
        name: str,
        user_id: str,
        **kwargs
    ) -> MCPToolResult:
        """
        Execute a tool by name.

        Args:
            name: Tool name to execute
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool-specific parameters

        Returns:
            MCPToolResult from tool execution

        Raises:
            ValueError: If tool not found

        Example:
            result = await server.execute_tool(
                "add_task",
                user_id="uuid-string",
                title="Buy groceries",
                description="Go to the store"
            )

            if result.success:
                print(f"Task created: {result.data}")
            else:
                print(f"Error: {result.error}")
        """
        return await self.registry.execute_tool(name, user_id, **kwargs)

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return self.registry.list_tools()

    def get_tool(self, name: str) -> Optional[BaseMCPTool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        return self.registry.get_tool(name)

    def get_config(self) -> MCPServerConfig:
        """
        Get server configuration.

        Returns:
            MCPServerConfig with server info and tools
        """
        return MCPServerConfig(
            server_name=self.name,
            server_version=self.version,
            tools=self.list_tools()
        )


# =====================================================
# Global MCP Server Instance
# =====================================================

# Global server instance (initialized on app startup)
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """
    Get the global MCP server instance.

    Returns:
        MCPServer instance

    Raises:
        RuntimeError: If server not initialized
    """
    global _mcp_server

    if _mcp_server is None:
        raise RuntimeError(
            "MCP server not initialized. "
            "Call init_mcp_server() during application startup."
        )

    return _mcp_server


def init_mcp_server(tools: Optional[List[BaseMCPTool]] = None) -> MCPServer:
    """
    Initialize the global MCP server with tools.

    Should be called during application startup.

    Args:
        tools: Optional list of MCP tools to register (if None, loads User Story 1 tools)

    Returns:
        Initialized MCPServer instance

    Example:
        from backend.src.mcp.tools.task_tools import get_user_story_1_tools

        server = init_mcp_server(get_user_story_1_tools())
    """
    global _mcp_server

    server = MCPServer()

    # If no tools provided, load User Story 1 tools (MVP)
    if tools is None:
        try:
            from backend.src.mcp.tools.task_tools import get_user_story_1_tools
        except ImportError:
            from src.mcp.tools.task_tools import get_user_story_1_tools
        tools = get_user_story_1_tools()

    for tool in tools:
        server.register_tool(tool)

    _mcp_server = server
    return server


def init_mcp_server_with_user_story_1() -> MCPServer:
    """
    Initialize MCP server with User Story 1 tools (MVP).

    Convenience function for MVP deployment.

    Returns:
        Initialized MCPServer with add_task tool
    """
    try:
        from backend.src.mcp.tools.task_tools import get_user_story_1_tools
    except ImportError:
        from src.mcp.tools.task_tools import get_user_story_1_tools
    return init_mcp_server(get_user_story_1_tools())


# =====================================================
# Helper Functions
# =====================================================

def format_tool_result_for_agent(result: MCPToolResult) -> str:
    """
    Format MCP tool result for AI agent response.

    Converts tool execution result into structured text that the AI agent
    can parse and use to construct accurate responses.

    Special handling for list_tasks results: Formats tasks in a clean,
    line-by-line format for better readability.

    Args:
        result: MCP tool execution result

    Returns:
        Formatted string for agent response with full data

    Example:
        result = MCPToolResult(
            success=True,
            data={"task_id": "uuid-string", "title": "Buy groceries"},
            user_id="user-uuid"
        )

        formatted = format_tool_result_for_agent(result)
        # Returns: "SUCCESS: {\"task_id\": \"...\", \"title\": \"Buy groceries\"}"
    """
    if result.success:
        if result.data:
            # Special handling for list_tasks results
            if "tasks" in result.data and isinstance(result.data["tasks"], list):
                return _format_task_list(result.data)

            # Return data as a structured string that the agent can parse
            # Use JSON-like format for easy parsing
            import json
            return f"SUCCESS: {json.dumps(result.data)}"
        else:
            return "SUCCESS: Operation completed successfully"
    else:
        return f"ERROR: {result.error or 'Unknown error'}"


def _format_task_list(data: dict) -> str:
    """
    Format task list result for clean display.

    Args:
        data: Dictionary with "tasks" list and "count" integer

    Returns:
        Formatted string with tasks in clean line-by-line format
    """
    from datetime import datetime

    tasks = data.get("tasks", [])
    count = data.get("count", len(tasks))

    if count == 0:
        return "SUCCESS: No tasks found"

    # Format each task
    formatted_tasks = []
    for task in tasks:
        title = task.get("title", "Untitled")
        status = task.get("status", "unknown")
        priority = task.get("priority", "unknown")

        # Format created_at date
        created_at = task.get("created_at", "")
        if created_at:
            try:
                # Parse ISO format and format nicely
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%B %d, %Y")
            except:
                date_str = created_at
        else:
            date_str = "Unknown"

        # Build formatted task entry
        formatted_tasks.append(f"**Title**: {title}\n**Status**: {status}\n**Priority**: {priority}\n**Created At**: {date_str}")

    # Combine all tasks with separator
    separator = "\n---\n"
    result = separator.join(formatted_tasks)

    return f"SUCCESS: Found {count} task{'s' if count != 1 else ''}\n\n{result}"


def format_tool_calls_for_logging(tool_calls: List[Dict[str, Any]]) -> str:
    """
    Format tool calls for logging.

    Args:
        tool_calls: List of tool call dictionaries

    Returns:
        Formatted string for logging

    Example:
        tool_calls = [
            {"name": "add_task", "arguments": {"title": "Buy groceries"}}
        ]

        formatted = format_tool_calls_for_logging(tool_calls)
        # Returns: "add_task(title='Buy groceries')"
    """
    if not tool_calls:
        return "No tool calls"

    formatted = []
    for call in tool_calls:
        name = call.get("name", "unknown")
        args = call.get("arguments", {})
        args_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
        formatted.append(f"{name}({args_str})")

    return ", ".join(formatted)
