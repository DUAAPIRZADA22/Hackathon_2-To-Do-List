"""
MCP module for Todo AI Chatbot (Phase III)

Model Context Protocol implementation for tool abstraction.
Provides base tool classes, server management, and agent integration.

Exports:
- Base: BaseMCPTool, MCPToolRegistry, MCPToolResult
- Server: MCPServer, get_mcp_server, init_mcp_server
- Client: MCPAgentClient, OpenAIMCPAgent
"""

from src.mcp.tools.base import (
    BaseMCPTool,
    MCPToolRegistry,
    MCPToolResult,
    MCPToolSchema,
    MCPToolError,
    MCPToolPermissionError,
    MCPToolValidationError,
)

from src.mcp.server import (
    MCPServer,
    MCPServerConfig,
    get_mcp_server,
    init_mcp_server,
    format_tool_result_for_agent,
    format_tool_calls_for_logging,
)

from src.mcp.client import (
    MCPAgentClient,
    OpenAIMCPAgent,
    create_mcp_agent_client,
    create_openai_mcp_agent,
)

__all__ = [
    # Base
    "BaseMCPTool",
    "MCPToolRegistry",
    "MCPToolResult",
    "MCPToolSchema",
    "MCPToolError",
    "MCPToolPermissionError",
    "MCPToolValidationError",
    # Server
    "MCPServer",
    "MCPServerConfig",
    "get_mcp_server",
    "init_mcp_server",
    "format_tool_result_for_agent",
    "format_tool_calls_for_logging",
    # Client
    "MCPAgentClient",
    "OpenAIMCPAgent",
    "create_mcp_agent_client",
    "create_openai_mcp_agent",
]
