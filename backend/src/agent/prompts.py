"""
Agent System Prompts for Todo AI Chatbot (Phase III)

System prompts and intent detection examples for OpenAI agent.
Guides AI behavior for natural language task management.

Architecture Principles:
- Clear instructions: Unambiguous behavior guidelines
- Intent detection: Examples for all user intents
- User-focused: Friendly, helpful persona
- Tool-aware: Instructions for when/how to use MCP tools
"""

from typing import List, Dict, Any, Optional

# =====================================================
# System Prompt
# =====================================================

SYSTEM_PROMPT = """You are ActionMind, an AI assistant for task management.

CRITICAL RULE: When user says "add a task [title]", you are in TASK CREATION MODE.

TASK CREATION MODE - PRIORITY FIRST:
1. User: "add a task [title]"
   → Extract title="[title]"
   → Ask: "What priority? (Low, Medium, High, or Urgent)"
   → Store the priority value

2. User: [provides priority like "High"/"Low"/"Medium"/"Urgent"]
   → Store it
   → Ask: "What status? (To Do, In Progress, or Done)"

3. User: [provides status like "To Do"/"In Progress"/"Done"]
   → Store it
   → IMMEDIATELY call: add_task(title="[title]", status="[status]", priority="[priority]")
   → Show confirmation

IMPORTANT STATUS VALUE MAPPING:
- "To Do" → status="todo"
- "In Progress" → status="in_progress"
- "Done" or "Completed" → status="done"

CRITICAL: In TASK CREATION MODE, "Done" is a STATUS VALUE, not a command!
- If user is creating a task and selects "Done" as status, CREATE THE TASK
- DO NOT call set_task_status - call add_task instead

WHEN NOT IN TASK CREATION MODE:
- "mark [task] as done" → call set_task_status
- "set priority [level] for [task]" → call set_task_priority

TOOL PARAMETERS:
- add_task(title, status, priority) - ALL 3 required
- status must be: "todo", "in_progress", or "done"
- priority must be: "low", "medium", "high", or "urgent"

=== TASK LIST DISPLAY FORMAT (STRICT RULES) ===

After calling list_tasks tool, you MUST format the output EXACTLY as follows:

1. Start with: "Here is your task list:" followed by a blank line
2. Each task on its OWN line with bullet point "•"
3. Use clean spacing with proper indentation
4. Format EXACTLY like this example:

Here is your task list:

• Title: nn
  Status: To Do
  Completed: No

• Title: hyl
  Status: Done
  Completed: Yes

STRICTLY FORBIDDEN:
- DO NOT show all tasks in a single paragraph
- DO NOT use format like: "1. Title: nn - Status: To Do - Completed: No"
- DO NOT combine tasks into one line
- Each task must have clear spacing and be on separate lines
"""

# =====================================================
# Intent Detection Examples
# =====================================================

INTENT_EXAMPLES = {
    "create": [
        "Add a task to buy groceries",
        "Remember to call mom on Saturday",
        "Create a task for the meeting tomorrow",
        "I need to finish the report by Friday",
        "Add: Pick up dry cleaning",
        "New task: submit the project",
        # Combined commands
        "Add a task hackathon submission and mark it complete",
        "Add a task call mom urgent",
        "Create a task buy groceries as high priority",
        "Add task review code and mark it in progress",
    ],
    "list": [
        "Show me my tasks",
        "What do I need to do?",
        "What's pending?",
        "List all my tasks",
        "Show me completed tasks",
        "What have I finished?",
    ],
    "set_status": [
        "Mark 'buy groceries' as done",
        "Move this task to in progress",
        "Set task as completed",
        "Change status to to-do",
        "Mark as in progress",
        "Mark as completed",
        "Move to to-do",
        "Mark this task as done",
        "Move this task to in progress",
        "Move this task to to-do",
    ],
    "set_priority": [
        "Set priority high for buy groceries",
        "Make this task urgent",
        "Change priority to low",
        "Mark as high priority",
        "Set priority to medium",
    ],
    "complete": [
        "Mark 'buy groceries' as done",
        "I finished the report",
        "Complete the meeting task",
        "Mark task 3 as done",
        "The grocery task is finished",
    ],
    "update": [
        "Change the task title to 'Buy milk'",
        "Update the grocery description",
        "Rename the meeting task",
        "Change task 5 to be about the project",
    ],
    "delete": [
        "Delete the grocery task",
        "Remove the old task",
        "Delete task 2",
        "Get rid of the completed tasks",
    ],
}


# =====================================================
# Helper Functions
# =====================================================

def get_system_prompt() -> str:
    """
    Get the system prompt for the agent.

    Returns:
        System prompt string
    """
    return SYSTEM_PROMPT


def get_intent_examples(intent: str) -> List[str]:
    """
    Get intent detection examples for a specific intent.

    Args:
        intent: Intent type (create, list, complete, update, delete)

    Returns:
        List of example phrases for the intent
    """
    return INTENT_EXAMPLES.get(intent, [])


def get_all_intent_examples() -> dict:
    """
    Get all intent detection examples.

    Returns:
        Dictionary mapping intent types to example phrases
    """
    return INTENT_EXAMPLES


def format_conversation_history(messages: List[dict]) -> List[dict]:
    """
    Format conversation history for OpenAI API.

    Args:
        messages: Raw message list from database

    Returns:
        Formatted message list for OpenAI API
    """
    formatted = []

    for msg in messages:
        formatted.append({
            "role": msg.role,
            "content": msg.content
        })

    return formatted


# =====================================================
# Prompt Builders
# =====================================================

def build_system_message() -> dict:
    """
    Build system message for OpenAI API.

    Returns:
        System message dictionary
    """
    return {
        "role": "system",
        "content": SYSTEM_PROMPT
    }


def build_user_message(content: str) -> dict:
    """
    Build user message for OpenAI API.

    Args:
        content: User message content

    Returns:
        User message dictionary
    """
    return {
        "role": "user",
        "content": content
    }


def build_assistant_message(content: str, tool_calls: Optional[List[dict]] = None) -> dict:
    """
    Build assistant message for OpenAI API.

    Args:
        content: Assistant response content
        tool_calls: Optional list of tool calls made

    Returns:
        Assistant message dictionary
    """
    message = {
        "role": "assistant",
        "content": content or ""
    }

    if tool_calls:
        message["tool_calls"] = tool_calls

    return message


def build_tool_message(tool_call_id: str, content: str) -> dict:
    """
    Build tool result message for OpenAI API.

    Args:
        tool_call_id: Tool call ID from assistant message
        content: Tool result content

    Returns:
        Tool message dictionary
    """
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content
    }
