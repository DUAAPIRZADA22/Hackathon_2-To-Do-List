"""
OpenAI Agents SDK Client for Todo AI Chatbot (Phase III)

Implements agent runner with OpenAI Agents SDK and multiple LLM providers.
Provides AI orchestration with MCP tool calling, retry logic, and fallback.

Architecture Principles:
- LLM-agnostic: Works with Gemini, OpenRouter, or OpenAI
- Tool calling: Automatic function calling for MCP tools
- Retry logic: Handles rate limits with exponential backoff
- Fallback support: Multiple provider support for reliability
"""

import os
import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
from pathlib import Path

# Load environment variables from .env file before any other imports
from dotenv import load_dotenv

# Try to find .env file in the backend directory or parent directories
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to loading from current directory
    load_dotenv()

from openai import AsyncOpenAI
import httpx
import structlog

try:
    from backend.src.mcp.client import MCPAgentClient, OpenAIMCPAgent
    from backend.src.mcp.server import get_mcp_server
    from backend.src.agent.prompts import build_system_message
    from backend.src.agent.state_manager import get_state_manager
except ImportError:
    from src.mcp.client import MCPAgentClient, OpenAIMCPAgent
    from src.mcp.server import get_mcp_server
    from src.agent.prompts import build_system_message
    from src.agent.state_manager import get_state_manager


# =====================================================
# LLM Provider Configuration
# =====================================================

class LLMProvider:
    """Represents an LLM provider configuration."""

    def __init__(self, name: str, client: AsyncOpenAI, model: str):
        self.name = name
        self.client = client
        self.model = model


def get_available_providers() -> List[LLMProvider]:
    """
    Get list of available LLM providers in priority order.

    Priority: Gemini (direct) > OpenRouter > OpenAI

    Returns:
        List of LLMProvider instances
    """
    providers = []

    # Debug: Print environment variables
    print(f"[DEBUG] GEMINI_API_KEY set: {os.getenv('GEMINI_API_KEY') is not None}")
    print(f"[DEBUG] OPENROUTER_API_KEY set: {os.getenv('OPENROUTER_API_KEY') is not None}")
    print(f"[DEBUG] OPENAI_API_KEY set: {os.getenv('OPENAI_API_KEY') is not None}")
    if os.getenv('OPENAI_API_KEY'):
        print(f"[DEBUG] OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")

    # 1. Gemini API (direct, highest priority - your own key)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        # Use Gemini's OpenAI-compatible endpoint
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        # Create httpx client with connection limits
        http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10, keepalive_expiry=30),
            timeout=httpx.Timeout(60.0, connect=10.0)
        )
        client = AsyncOpenAI(api_key=gemini_key, base_url=base_url, http_client=http_client)
        providers.append(LLMProvider("Gemini", client, model))
        print(f"[DEBUG] Added Gemini provider")

    # 2. OpenRouter (fallback)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")
        # Create httpx client with connection limits
        http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10, keepalive_expiry=30),
            timeout=httpx.Timeout(60.0, connect=10.0)
        )
        client = AsyncOpenAI(api_key=openrouter_key, base_url=base_url, http_client=http_client)
        providers.append(LLMProvider("OpenRouter", client, model))
        print(f"[DEBUG] Added OpenRouter provider")

    # 3. OpenAI (fallback)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        # Create httpx client with connection limits and timeouts to prevent DNS errors
        http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30
            ),
            timeout=httpx.Timeout(60.0, connect=10.0)
        )
        client = AsyncOpenAI(api_key=openai_key, http_client=http_client)
        providers.append(LLMProvider("OpenAI", client, model))
        print(f"[DEBUG] Added OpenAI provider with model {model}")
    else:
        print(f"[DEBUG] OpenAI provider NOT added - OPENAI_API_KEY not set")

    print(f"[DEBUG] Total providers: {len(providers)}, names: {[p.name for p in providers]}")
    return providers


# =====================================================
# Agent Runner
# =====================================================

class AgentRunner:
    """
    Agent runner for orchestrating AI conversations with MCP tools.

    Features:
    - Multiple LLM provider support with automatic fallback
    - Retry logic with exponential backoff for rate limits
    - Tool calling with automatic execution
    """

    def __init__(self, user_id: str):
        """
        Initialize agent runner for a user.

        Args:
            user_id: User ID (UUID string, enforces ownership)
        """
        self.user_id = user_id
        self.logger = structlog.get_logger().bind(user_id=user_id)

        # Get MCP client for tool integration
        self.mcp_client = MCPAgentClient(user_id)

        # Get available providers
        self.providers = get_available_providers()

        # Debug logging for provider configuration
        openai_key_set = os.getenv("OPENAI_API_KEY") is not None
        self.logger.info(
            "Provider configuration check",
            gemini_key_set=os.getenv("GEMINI_API_KEY") is not None,
            openrouter_key_set=os.getenv("OPENROUTER_API_KEY") is not None,
            openai_key_set=openai_key_set,
            total_providers=len(self.providers),
            provider_names=[p.name for p in self.providers]
        )

        if not self.providers:
            self.logger.warning("No LLM providers configured")
            self.primary_provider = None
        else:
            self.primary_provider = self.providers[0]
            self.logger.info(
                "LLM providers configured",
                primary=self.primary_provider.name,
                total_providers=len(self.providers),
                all_providers=[p.name for p in self.providers]
            )

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get MCP tools in OpenAI function calling format.

        Returns:
            List of tool schemas for OpenAI function calling
        """
        return self.mcp_client.get_openai_tools()

    async def _call_llm_with_retry(
        self,
        provider: LLMProvider,
        messages: List[Dict],
        tools: List[Dict],
        max_retries: int = 3
    ) -> Any:
        """
        Call LLM API with retry logic for rate limits.

        Args:
            provider: LLM provider to use
            messages: Conversation messages
            tools: Tool definitions
            max_retries: Maximum number of retries

        Returns:
            API response
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(
                    "Calling LLM",
                    provider=provider.name,
                    model=provider.model,
                    attempt=attempt + 1,
                    tool_count=len(tools) if tools else 0
                )

                # OpenAI requires max_completion_tokens, other providers use max_tokens
                token_param = "max_completion_tokens" if provider.name == "OpenAI" else "max_tokens"
                kwargs = {
                    "model": provider.model,
                    "messages": messages,
                    token_param: 500
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = await provider.client.chat.completions.create(**kwargs)

                self.logger.info(
                    "LLM call successful",
                    provider=provider.name,
                    response_tokens=response.usage.total_tokens if hasattr(response, 'usage') else "N/A"
                )
                return response

            except Exception as e:
                error_str = str(e)
                import traceback
                error_traceback = traceback.format_exc()

                # Check for rate limit (429) errors
                is_rate_limit = "429" in error_str or "rate" in error_str.lower()
                is_not_found = "404" in error_str

                print(f"[DEBUG] LLM call failed for {provider.name}:")
                print(f"[DEBUG] Error type: {type(e).__name__}")
                print(f"[DEBUG] Error message: {error_str[:500]}")
                print(f"[DEBUG] Traceback: {error_traceback[:1000]}")

                self.logger.error(
                    "LLM call failed",
                    provider=provider.name,
                    model=provider.model,
                    attempt=attempt + 1,
                    error=str(e)[:500],
                    error_type=type(e).__name__,
                    is_rate_limit=is_rate_limit,
                    is_not_found=is_not_found
                )

                if is_rate_limit and attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        "Rate limit hit, retrying with backoff",
                        provider=provider.name,
                        attempt=attempt + 1,
                        wait_seconds=wait_time
                    )
                    await asyncio.sleep(wait_time)
                    continue

                # For other errors or final retry attempt, re-raise
                if attempt == max_retries - 1:
                    raise
                else:
                    # Non-rate-limit errors, don't retry (especially 404)
                    raise

    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Chat with agent, handling tool calls automatically.

        Tries all available providers with fallback on failure.

        Args:
            message: User message
            conversation_history: Optional conversation history
            stream: Whether to stream response tokens

        Returns:
            Dictionary with:
                - response: Agent text response
                - tool_calls: List of tool calls made
                - finished: Whether conversation is complete
        """
        self.logger.info("Agent chat started", message_length=len(message))

        # Get state manager
        state_manager = get_state_manager()

        # Check if user has active task creation state
        state = await state_manager.get_state(self.user_id)

        # DEBUG: Log state check
        print(f"[STATE MANAGER] Checking state for user {self.user_id}")
        print(f"[STATE MANAGER] Current state: {state.to_dict() if state else None}")

        # Priority and status value mappings
        priority_values = ["low", "medium", "high", "urgent", "Low", "Medium", "High", "Urgent"]
        status_map = {
            "to do": "todo",
            "in progress": "in_progress",
            "done": "done",
            "todo": "todo",
            "in_progress": "in_progress",
            "done": "done",
            "To Do": "todo",
            "In Progress": "in_progress",
            "Done": "done",
        }

        message_lower = message.lower().strip()

        # CASE 1: Active state in "status" step - complete task creation
        if state and state.step == "status" and message_lower in [s.lower() for s in status_map.keys()]:
            print(f"[STATE MANAGER] Completing task creation for user {self.user_id}")

            # Update status
            status_value = status_map.get(message, status_map.get(message_lower, "todo"))
            await state_manager.update_status(self.user_id, status_value)

            # Create the task using MCP tool
            try:
                result = await self.mcp_client.execute_function_call({
                    "id": "call_" + str(hash(message)),
                    "name": "add_task",
                    "arguments": {
                        "title": state.title,
                        "priority": state.priority,
                        "status": state.status
                    }
                })

                # Clear the state
                await state_manager.clear_task_creation(self.user_id)

                # Return success response
                return {
                    "response": f"Task '{state.title}' has been created with {state.priority} priority and {status_value} status.",
                    "tool_calls": [{
                        "id": "call_" + str(hash(message)),
                        "name": "add_task",
                        "arguments": {
                            "title": state.title,
                            "priority": state.priority,
                            "status": state.status
                        },
                        "result": {"success": True, "data": result.data} if result.success else {"error": result.error}
                    }],
                    "finished": True
                }
            except Exception as e:
                self.logger.error("Failed to create task", error=str(e))
                return {
                    "response": f"Sorry, I couldn't create the task. Error: {str(e)}",
                    "tool_calls": [],
                    "finished": True
                }

        # CASE 2: Active state in "priority" step - update priority
        elif state and state.step == "priority" and message_lower in [p.lower() for p in priority_values]:
            print(f"[STATE MANAGER] Updating priority for user {self.user_id}")

            # Update priority
            priority_value = message_lower
            await state_manager.update_priority(self.user_id, priority_value)

            # Ask for status
            return {
                "response": "What status? (To Do, In Progress, or Done)",
                "tool_calls": [],
                "finished": False
            }

        # CASE 3: New task creation - "add a task <title>"
        elif not state and any(pattern in message_lower for pattern in [
            "add a task ", "add task ", "create a task ", "remember to "
        ]):
            import re
            # Extract task title
            match = re.search(r'add\s+(?:a\s+)?task\s+(?:to\s+)?(.+?)(?:\.|$)|create\s+(?:a\s+)?task\s+(?:for\s+)?(.+?)(?:\.|$)|remember\s+to\s+(.+?)(?:\.|$)', message, re.IGNORECASE)
            if match:
                title = next(g for g in match.groups() if g).strip()
                print(f"[STATE MANAGER] Starting task creation for user {self.user_id} with title: {title}")

                # Start new state
                await state_manager.start_task_creation(self.user_id, title)

                # Ask for priority
                return {
                    "response": "What priority? (Low, Medium, High, or Urgent)",
                    "tool_calls": [],
                    "finished": False
                }

        # Check if any LLM provider is configured
        if not self.providers:
            self.logger.warning("No LLM providers configured")
            return {
                "response": "AI assistant is not configured. Please set GEMINI_API_KEY or OPENROUTER_API_KEY.",
                "tool_calls": [],
                "finished": True
            }

        # Build messages with system prompt
        messages = [build_system_message()]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": message})

        # Get MCP tools
        try:
            mcp_server = get_mcp_server()
            tools = self.mcp_client.get_openai_tools()
            self.logger.debug("MCP tools loaded", tool_count=len(tools))
        except RuntimeError:
            self.logger.warning("MCP server not initialized, tool calling disabled")
            tools = []

        # Track tool calls
        all_tool_calls = []

        # Try each provider until one succeeds
        last_error = None

        print(f"[DEBUG] chat(): About to try {len(self.providers)} providers: {[p.name for p in self.providers]}")

        for i, provider in enumerate(self.providers):
            print(f"[DEBUG] chat(): Loop iteration {i+1}/{len(self.providers)}, trying provider: {provider.name}")
            self.logger.info("Trying provider", provider=provider.name, index=i+1, total=len(self.providers))

            try:
                # Execute conversation loop with this provider
                result = await self._chat_with_provider(
                    provider, messages, tools, all_tool_calls
                )

                # If successful, log and return
                print(f"[DEBUG] chat(): Provider {provider.name} succeeded!")
                self.logger.info(
                    "Provider succeeded",
                    provider=provider.name,
                    tool_calls=len(result["tool_calls"])
                )
                return result

            except Exception as e:
                last_error = e
                print(f"[DEBUG] chat(): Provider {provider.name} failed: {type(e).__name__}: {str(e)[:100]}")
                self.logger.warning(
                    "Provider failed",
                    provider=provider.name,
                    error=str(e)[:200],
                    error_type=type(e).__name__
                )
                # Continue to next provider
                continue

        # All providers failed
        print(f"[DEBUG] chat(): All {len(self.providers)} providers failed!")
        self.logger.error("All providers failed", last_error=str(last_error))
        return {
            "response": f"Service temporarily unavailable. Please try again in a moment. (Error: {str(last_error)})",
            "tool_calls": all_tool_calls,
            "finished": True
        }

    async def _chat_with_provider(
        self,
        provider: LLMProvider,
        messages: List[Dict],
        tools: List[Dict],
        all_tool_calls: List[Dict]
    ) -> Dict[str, Any]:
        """
        Execute chat loop with a specific provider.

        Args:
            provider: LLM provider to use
            messages: Conversation messages
            tools: Tool definitions
            all_tool_calls: Accumulated tool calls

        Returns:
            Response dictionary
        """
        # Execute conversation loop
        max_iterations = 5
        for iteration in range(max_iterations):
            # Call LLM with retry logic
            response = await self._call_llm_with_retry(provider, messages, tools)

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
                # Parse arguments
                import json
                raw_arguments = tool_call.function.arguments
                self.logger.info("Parsing tool arguments", tool=tool_call.function.name)

                try:
                    arguments = json.loads(raw_arguments)
                except json.JSONDecodeError:
                    # Try to fix JSON issues
                    import re
                    fixed_args = re.sub(r',(\s*[}\]])', r'\1', raw_arguments.strip())
                    arguments = json.loads(fixed_args)

                call_info = {
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": arguments
                }
                all_tool_calls.append(call_info)

                self.logger.info("Executing tool", tool=tool_call.function.name)

                # Execute MCP tool
                result = await self.mcp_client.execute_function_call(call_info)

                # Store tool result data for frontend (success, data, error)
                if result.success:
                    call_info["result"] = {
                        "success": True,
                        "data": result.data
                    }
                else:
                    call_info["result"] = {
                        "success": False,
                        "error": result.error
                    }

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

    async def chat_stream(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Chat with streaming response.

        Yields response tokens as they arrive.

        Args:
            message: User message
            conversation_history: Optional conversation history

        Yields:
            Response tokens (strings)
        """
        self.logger.info("Agent chat stream started")

        # For now, use non-streaming and yield complete response
        result = await self.chat(message, conversation_history)
        yield result["response"]


# =====================================================
# Factory Functions
# =====================================================

def create_agent_runner(user_id: str) -> AgentRunner:
    """
    Create agent runner for a user.

    Args:
        user_id: User ID (UUID string)

    Returns:
        AgentRunner instance
    """
    return AgentRunner(user_id)


def create_openai_mcp_agent(user_id: str) -> "OpenAIMCPAgent":
    """
    Create OpenAI MCP agent for a user.

    Args:
        user_id: User ID (UUID string)

    Returns:
        OpenAIMCPAgent instance
    """
    providers = get_available_providers()
    if providers:
        provider = providers[0]
        return OpenAIMCPAgent(
            user_id=user_id,
            openai_api_key="",  # Not used, client already configured
            model=provider.model,
            base_url=provider.client.base_url
        )
    else:
        raise RuntimeError("No LLM provider configured")

