"""
Agent module for Todo AI Chatbot (Phase III)

OpenAI Agents SDK integration with MCP tools.
Provides AI orchestration for natural language task management.

Exports:
- Runner: Agent execution with OpenAI SDK
- Prompts: System prompts and intent detection
- Context: Conversation history management
"""

try:
    from backend.src.agent.runner import (
        AgentRunner,
        create_agent_runner,
        create_openai_mcp_agent,
        get_available_providers,
    )

    from backend.src.agent.prompts import (
        get_system_prompt,
        get_intent_examples,
        get_all_intent_examples,
        format_conversation_history,
        build_system_message,
        build_user_message,
        build_assistant_message,
        build_tool_message,
        SYSTEM_PROMPT,
        INTENT_EXAMPLES,
    )

    from backend.src.agent.context import (
        ConversationContextBuilder,
        ConversationContextManager,
        create_context_builder,
        create_context_manager,
    )
except ImportError:
    from src.agent.runner import (
        AgentRunner,
        create_agent_runner,
        create_openai_mcp_agent,
        get_available_providers,
    )

    from src.agent.prompts import (
        get_system_prompt,
        get_intent_examples,
        get_all_intent_examples,
        format_conversation_history,
        build_system_message,
        build_user_message,
        build_assistant_message,
        build_tool_message,
        SYSTEM_PROMPT,
        INTENT_EXAMPLES,
    )

    from src.agent.context import (
        ConversationContextBuilder,
        ConversationContextManager,
        create_context_builder,
        create_context_manager,
    )

__all__ = [
    # Runner
    "AgentRunner",
    "create_agent_runner",
    "create_openai_mcp_agent",
    "get_available_providers",
    # Prompts
    "get_system_prompt",
    "get_intent_examples",
    "get_all_intent_examples",
    "format_conversation_history",
    "build_system_message",
    "build_user_message",
    "build_assistant_message",
    "build_tool_message",
    "SYSTEM_PROMPT",
    "INTENT_EXAMPLES",
    # Context
    "ConversationContextBuilder",
    "ConversationContextManager",
    "create_context_builder",
    "create_context_manager",
]
