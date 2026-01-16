"""
Base MCP Tool Class for Todo AI Chatbot (Phase III)

Implements the foundation for all MCP tools with user identity enforcement,
error handling, and standardized response format.

Architecture Principles:
- User identity: All tools require and validate user_id parameter
- Error handling: Descriptive user-friendly error messages
- Type-safe: Uses JSON Schema for parameter validation
- Extensible: Easy to create new tools by inheriting from base class
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# =====================================================
# MCP Tool Response Models
# =====================================================

class MCPToolResult(BaseModel):
    """
    Standardized result format for MCP tool execution.

    Attributes:
        success: Whether the tool execution succeeded
        data: Result data (if successful)
        error: Error message (if failed)
        user_id: User who executed the tool (for audit/logging)
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    user_id: str


class MCPToolSchema(BaseModel):
    """
    JSON Schema for MCP tool parameters.

    Used by OpenAI Agents SDK for function calling.
    """
    name: str
    description: str
    parameters: Dict[str, Any]


# =====================================================
# Base MCP Tool Class
# =====================================================

class BaseMCPTool(ABC):
    """
    Abstract base class for all MCP tools.

    All tools must inherit from this class and implement the execute method.

    Example:
        class AddTaskTool(BaseMCPTool):
            def __init__(self):
                super().__init__(
                    name="add_task",
                    description="Create a new task for the user"
                )

            def get_parameters_schema(self) -> Dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["title"]
                }

            async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
                # Implementation here
                pass
    """

    def __init__(self, name: str, description: str):
        """
        Initialize MCP tool.

        Args:
            name: Tool name (used for function calling)
            description: Tool description (shown to AI agent)
        """
        self.name = name
        self.description = description

    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get JSON Schema for tool parameters.

        Returns:
            JSON Schema dictionary defining tool parameters

        Example:
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        """
        pass

    @abstractmethod
    async def execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute the tool with given parameters.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool-specific parameters

        Returns:
            MCPToolResult with success status and data/error

        Example:
            try:
                task = await create_task(user_id, kwargs["title"])
                return MCPToolResult(
                    success=True,
                    data={"task_id": task.id},
                    user_id=user_id
                )
            except Exception as e:
                return MCPToolResult(
                    success=False,
                    error=str(e),
                    user_id=user_id
                )
        """
        pass

    def get_tool_schema(self) -> MCPToolSchema:
        """
        Get complete tool schema for OpenAI function calling.

        Returns:
            MCPToolSchema with name, description, and parameters
        """
        return MCPToolSchema(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters_schema()
        )

    def validate_user_id(self, user_id: str) -> None:
        """
        Validate user_id parameter.

        Args:
            user_id: User ID to validate

        Raises:
            ValueError: If user_id is missing or invalid
        """
        if not user_id:
            raise ValueError("user_id is required and cannot be empty")
        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")

    async def safe_execute(self, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute tool with error handling and validation.

        Wraps execute() method with try-catch for consistent error handling.

        Args:
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool-specific parameters

        Returns:
            MCPToolResult with success status and data/error
        """
        try:
            # Validate user_id
            self.validate_user_id(user_id)

            # Execute tool
            return await self.execute(user_id, **kwargs)

        except ValueError as e:
            # Validation errors (user_id, parameters)
            return MCPToolResult(
                success=False,
                error=f"Validation error: {str(e)}",
                user_id=user_id
            )

        except PermissionError as e:
            # Permission errors (ownership)
            return MCPToolResult(
                success=False,
                error=f"Permission denied: {str(e)}",
                user_id=user_id
            )

        except Exception as e:
            # Unexpected errors
            return MCPToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                user_id=user_id
            )


# =====================================================
# MCP Tool Registry
# =====================================================

class MCPToolRegistry:
    """
    Registry for managing MCP tools.

    Provides centralized tool management for the MCP server.
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, BaseMCPTool] = {}

    def register(self, tool: BaseMCPTool) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: MCP tool instance to register

        Raises:
            ValueError: If tool name already registered
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")

        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseMCPTool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Get JSON schemas for all registered tools.

        Returns:
            List of tool schemas for OpenAI function calling
        """
        return [
            tool.get_tool_schema().model_dump()
            for tool in self._tools.values()
        ]

    async def execute_tool(self, name: str, user_id: str, **kwargs) -> MCPToolResult:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            user_id: User ID (string UUID, enforces ownership)
            **kwargs: Tool parameters

        Returns:
            MCPToolResult from tool execution

        Raises:
            ValueError: If tool not found
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        return await tool.safe_execute(user_id, **kwargs)


# =====================================================
# Common Errors
# =====================================================

class MCPToolError(Exception):
    """Base exception for MCP tool errors."""

    def __init__(self, message: str, user_id: str):
        """
        Initialize MCP tool error.

        Args:
            message: Error message
            user_id: User who triggered the error
        """
        self.message = message
        self.user_id = user_id
        super().__init__(f"[{user_id}] {message}")


class MCPToolPermissionError(MCPToolError):
    """Exception raised when user lacks permission for an operation."""

    def __init__(self, message: str, user_id: str):
        super().__init__(f"Permission denied: {message}", user_id)


class MCPToolValidationError(MCPToolError):
    """Exception raised when tool parameters are invalid."""

    def __init__(self, message: str, user_id: str):
        super().__init__(f"Validation error: {message}", user_id)
