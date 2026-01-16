"""
MCP Client Wrapper for Todo AI Chatbot (Phase III)

Provides integration between OpenAI Agents SDK and MCP server.
Converts OpenAI function calls to MCP tool executions.

Architecture Principles:
- Abstraction: Hides MCP implementation details from agent
- User identity: Enforces user_id in all tool calls
- Error handling: Converts MCP errors to agent-friendly format
"""

from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

try:
    from backend.src.mcp.server import get_mcp_server, format_tool_result_for_agent
    from backend.src.mcp.tools.base import MCPToolResult
except ImportError:
    from src.mcp.server import get_mcp_server, format_tool_result_for_agent
    from src.mcp.tools.base import MCPToolResult


# =====================================================
# MCP Client for OpenAI Agents SDK
# =====================================================

class MCPAgentClient:
    """
    Client wrapper for integrating MCP tools with OpenAI Agents SDK.

    Handles tool registration, execution, and result formatting for
    seamless integration between MCP server and OpenAI agent.

    Example:
        client = MCPAgentClient(user_id="uuid-string")

        # Get tools for OpenAI function calling
        tools = client.get_openai_tools()

        # Execute function call from OpenAI
        result = await client.execute_function_call({
            "name": "add_task",
            "arguments": {"title": "Buy groceries"}
        })

        # Format result for agent response
        response = client.format_result(result)
    """

    def __init__(self, user_id: str):
        """
        Initialize MCP agent client.

        Args:
            user_id: User ID (string UUID, enforces ownership for all tool calls)
        """
        self.user_id = user_id
        self.server = get_mcp_server()

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Get MCP tools in OpenAI function calling format.

        Returns:
            List of tool schemas compatible with OpenAI API

        Example:
            tools = client.get_openai_tools()

            # Use with OpenAI SDK
            response = await openai.chat.completions.create(
                model="gpt-4",
                messages=[...],
                tools=tools
            )
        """
        mcp_schemas = self.server.get_tool_schemas()

        # Convert MCP schemas to OpenAI format
        openai_tools = []
        for schema in mcp_schemas:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "description": schema["description"],
                    "parameters": schema["parameters"]
                }
            })

        return openai_tools

    async def execute_function_call(self, call: Dict[str, Any]) -> MCPToolResult:
        """
        Execute a function call from OpenAI agent.

        Args:
            call: Function call dictionary from OpenAI
                {
                    "name": "tool_name",
                    "arguments": {...}
                }

        Returns:
            MCPToolResult from tool execution

        Example:
            call = {
                "name": "add_task",
                "arguments": {"title": "Buy groceries"}
            }

            result = await client.execute_function_call(call)
        """
        tool_name = call.get("name")
        arguments = call.get("arguments", {})

        if not tool_name:
            return MCPToolResult(
                success=False,
                error="Function call missing 'name' field",
                user_id=self.user_id
            )

        try:
            # Execute MCP tool
            return await self.server.execute_tool(
                tool_name,
                self.user_id,
                **arguments
            )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}",
                user_id=self.user_id
            )

    def format_result(self, result: MCPToolResult) -> str:
        """
        Format MCP tool result for agent response.

        Args:
            result: MCP tool execution result

        Returns:
            Formatted string for agent response

        Example:
            result = MCPToolResult(
                success=True,
                data={"task_id": 123},
                user_id="user123"
            )

            response = client.format_result(result)
            # Returns: "Task created successfully"
        """
        return format_tool_result_for_agent(result)

    async def execute_function_calls(
        self,
        calls: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Execute multiple function calls from OpenAI agent.

        Args:
            calls: List of function call dictionaries

        Returns:
            List of formatted result strings

        Example:
            calls = [
                {"name": "add_task", "arguments": {"title": "Buy groceries"}},
                {"name": "add_task", "arguments": {"title": "Call mom"}}
            ]

            results = await client.execute_function_calls(calls)
            # Returns: ["Task created: Buy groceries", "Task created: Call mom"]
        """
        results = []

        for call in calls:
            result = await self.execute_function_call(call)
            formatted = self.format_result(result)
            results.append(formatted)

        return results


# =====================================================
# OpenAI Agents SDK Integration Helper
# =====================================================

class OpenAIMCPAgent:
    """
    High-level wrapper for OpenAI Agents SDK with MCP integration.

    Combines OpenAI client with MCP tools for seamless agent orchestration.

    Example:
        agent = OpenAIMCPAgent(
            user_id="uuid-string",
            openai_api_key="sk-...",
            model="gpt-4"
        )

        response = await agent.chat(
            message="Add a task to buy groceries",
            conversation_id="uuid-or-None"
        )
    """

    def __init__(
        self,
        user_id: str,
        openai_api_key: str,
        model: str = "gpt-4",
        base_url: Optional[str] = None
    ):
        """
        Initialize OpenAI MCP agent.

        Args:
            user_id: User ID (UUID string, enforces ownership)
            openai_api_key: OpenAI API key (or OpenRouter key)
            model: Model name
            base_url: Optional base URL (for OpenRouter)
        """
        self.user_id = user_id
        self.model = model
        self.mcp_client = MCPAgentClient(user_id)

        # Initialize OpenAI client
        client_kwargs = {"api_key": openai_api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.openai_client = AsyncOpenAI(**client_kwargs)

    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Chat with agent, automatically handling tool calls.

        Args:
            message: User message
            conversation_history: Optional conversation history
            max_iterations: Maximum tool call iterations (default: 5)

        Returns:
            Dictionary with:
                - response: Agent text response
                - tool_calls: List of tool calls made
                - conversation_id: Updated conversation ID

        Example:
            result = await agent.chat("Add a task to buy groceries")

            print(result["response"])  # "I've added that task for you!"
            print(result["tool_calls"])  # [{"name": "add_task", ...}]
        """
        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        # Get MCP tools for OpenAI
        tools = self.mcp_client.get_openai_tools()

        # Track tool calls for response
        all_tool_calls = []

        # Execute with tool calling loop
        for iteration in range(max_iterations):
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,  # Only include if tools exist
                tool_choice="auto" if tools else None,
                max_tokens=1000
            )

            # Get assistant message
            assistant_message = response.choices[0].message

            # Check for tool calls
            tool_calls = assistant_message.tool_calls

            if not tool_calls:
                # No tool calls, return text response
                return {
                    "response": assistant_message.content or "",
                    "tool_calls": all_tool_calls,
                    "finished": True
                }

            # Process tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in tool_calls:
                # Parse arguments with better error handling
                import json
                raw_arguments = tool_call.function.arguments

                try:
                    arguments = json.loads(raw_arguments)
                except json.JSONDecodeError as je:
                    # Try to fix common JSON issues
                    try:
                        import re
                        fixed_args = raw_arguments.strip()
                        # Remove trailing commas before closing brackets/braces
                        fixed_args = re.sub(r',(\s*[}\]])', r'\1', fixed_args)
                        arguments = json.loads(fixed_args)
                    except Exception:
                        # If still fails, return error
                        return {
                            "response": f"I had trouble understanding your request. Could you rephrase it?",
                            "tool_calls": all_tool_calls,
                            "finished": True
                        }

                call_info = {
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": arguments
                }
                all_tool_calls.append(call_info)

                # Execute MCP tool
                result = await self.mcp_client.execute_function_call(call_info)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": self.mcp_client.format_result(result)
                })

        # Max iterations reached
        return {
            "response": "I need more information to complete your request.",
            "tool_calls": all_tool_calls,
            "finished": False
        }


# =====================================================
# Factory Functions
# =====================================================

def create_mcp_agent_client(user_id: str) -> MCPAgentClient:
    """
    Create MCP agent client for a user.

    Args:
        user_id: User ID

    Returns:
        MCPAgentClient instance
    """
    return MCPAgentClient(user_id)


def create_openai_mcp_agent(
    user_id: str,
    openai_api_key: str,
    model: str = "gpt-4",
    base_url: Optional[str] = None
) -> OpenAIMCPAgent:
    """
    Create OpenAI MCP agent for a user.

    Args:
        user_id: User ID
        openai_api_key: OpenAI API key
        model: Model name
        base_url: Optional base URL (for OpenRouter)

    Returns:
        OpenAIMCPAgent instance
    """
    return OpenAIMCPAgent(
        user_id=user_id,
        openai_api_key=openai_api_key,
        model=model,
        base_url=base_url
    )
