"""
Conversation Context Builder for Todo AI Chatbot (Phase III)

Implements context building with conversation history loading from database.
Provides conversation memory for multi-turn AI interactions.

Architecture Principles:
- Stateless: All state persisted in database
- History-aware: Loads conversation context for better responses
- Token-efficient: Truncates history to stay within model limits
- User-scoped: All conversation data scoped to user_id
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

try:
    from backend.src.db.repository import ConversationRepository
    from backend.src.agent.prompts import (
        build_system_message,
        format_conversation_history,
        SYSTEM_PROMPT,
    )
except ImportError:
    from src.db.repository import ConversationRepository
    from src.agent.prompts import (
        build_system_message,
        format_conversation_history,
        SYSTEM_PROMPT,
    )


# =====================================================
# Context Configuration
# =====================================================

# Maximum conversation history messages
MAX_HISTORY_MESSAGES = 100

# Token limit for context (adjust based on model)
MAX_CONTEXT_TOKENS = 8000

# Estimated tokens per message (rough approximation)
TOKENS_PER_MESSAGE = 100


# =====================================================
# Conversation Context Builder
# =====================================================

class ConversationContextBuilder:
    """
    Builds conversation context for AI agent.

    Loads conversation history from database and formats
    for OpenAI API with system prompt and user messages.

    Example:
        builder = ConversationContextBuilder()
        context = await builder.build_context(
            user_id="user123",
            conversation_id="uuid-or-None",
            db_session=session
        )
    """

    def __init__(self):
        """Initialize context builder."""
        self.logger = structlog.get_logger()

    async def build_context(
        self,
        user_id: str,
        conversation_id: Optional[UUID],
        user_message: str,
        db_session: AsyncSession,
        max_history: int = MAX_HISTORY_MESSAGES
    ) -> List[Dict[str, str]]:
        """
        Build conversation context for OpenAI API.

        Args:
            user_id: User ID (integer)
            conversation_id: Optional conversation UUID
            user_message: Current user message
            db_session: Database session
            max_history: Maximum history messages to load

        Returns:
            Formatted message list for OpenAI API

        Example:
            messages = await builder.build_context(
                user_id=123,
                conversation_id="uuid",
                user_message="Add a task",
                db_session=session
            )

            # Returns:
            # [
            #     {"role": "system", "content": "..."},
            #     {"role": "user", "content": "Previous message"},
            #     {"role": "assistant", "content": "Previous response"},
            #     {"role": "user", "content": "Add a task"}
            # ]
        """
        # DEBUG: Log incoming parameters
        print(f"[DEBUG BUILD CONTEXT] user_id={user_id}, conversation_id={conversation_id}, message={user_message[:50]}...")

        # Start with system message
        messages = [build_system_message()]

        # Load conversation history if conversation_id provided
        recent_task_id = None
        pending_task = None
        if conversation_id:
            print(f"[DEBUG BUILD CONTEXT] Loading history for conversation_id={conversation_id}")
            history = await self._load_conversation_history(
                user_id,
                conversation_id,
                db_session,
                max_history
            )

            # Extract most recently created task_id from tool results
            recent_task_id = self._extract_recent_task_id(history)

            # Detect pending task creation state
            pending_task = self._detect_pending_task_creation(history, user_message)

            # Add history messages
            messages.extend(history)
        else:
            print(f"[DEBUG BUILD CONTEXT] No conversation_id provided, starting fresh conversation")

        # Inject recent task context if available
        if recent_task_id:
            messages.append({
                "role": "system",
                "content": f"RECENT TASK CONTEXT: The most recently created task has ID '{recent_task_id}'. "
                          f"For ANY follow-up commands (mark as done, set priority, etc.), you MUST use task_id='{recent_task_id}'. "
                          f"DO NOT use the task title - use the task_id directly."
            })

        # Inject pending task creation context if detected
        if pending_task:
            messages.append({
                "role": "system",
                "content": self._format_pending_task_context(pending_task)
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Log context size
        self.logger.info(
            "Context built",
            user_id=user_id,
            conversation_id=str(conversation_id) if conversation_id else None,
            message_count=len(messages),
            recent_task_id=recent_task_id,
            pending_task=pending_task
        )

        return messages

    def _extract_recent_task_id(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Extract the most recently created task_id from conversation history.

        Looks for add_task tool results in assistant messages and returns the task_id.

        Args:
            messages: Conversation history messages

        Returns:
            Most recent task_id string or None
        """
        import json
        import re

        # Search in reverse order (most recent first)
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")

                # Look for tool results with task_id
                # Pattern 1: SUCCESS: {"task_id": "..."}
                match = re.search(r'SUCCESS:\s*\{[^}]*"task_id"\s*:\s*"([^"]+)"', content)
                if match:
                    return match.group(1)

                # Pattern 2: Direct JSON with task_id
                try:
                    # Look for JSON in the content
                    for json_match in re.finditer(r'\{[^{}]*"task_id"[^{}]*\}', content):
                        data = json.loads(json_match.group(0))
                        if "task_id" in data:
                            return data["task_id"]
                except json.JSONDecodeError:
                    pass

        return None

    def _detect_pending_task_creation(
        self,
        messages: List[Dict[str, str]],
        current_user_message: str
    ) -> Optional[Dict[str, str]]:
        """
        Detect if there's a pending task creation in progress.

        Scans conversation in chronological order to find:
        1. User initiated task creation (with title)
        2. Assistant asked for status/priority
        3. User provided some answers
        4. Task hasn't been created yet

        CRITICAL: Scans messages in ORDER to preserve state across turns.

        Args:
            messages: Conversation history messages (already in chronological order)
            current_user_message: Current user message to analyze

        Returns:
            Dict with pending task info {title, status?, priority?, stage?} or None
        """
        import re

        # Status and priority value mappings
        status_map = {
            "todo": "todo",
            "to-do": "todo",
            "to do": "todo",
            "in progress": "in_progress",
            "in-progress": "in_progress",
            "done": "done",
            "completed": "done",
            # Add capitalized versions
            "To Do": "todo",
            "To-Do": "todo",
            "In Progress": "in_progress",
            "In-Progress": "in_progress",
            "Done": "done",
            "Completed": "done"
        }
        status_values = list(status_map.keys())
        priority_values = ["low", "medium", "high", "urgent", "Low", "Medium", "High", "Urgent"]

        # Initialize state tracking
        task_title = None
        task_priority = None  # CHANGED: priority now comes before status
        task_status = None
        asked_priority = False  # CHANGED: priority now comes before status
        asked_status = False
        task_created = False
        stage = None  # "need_priority", "need_status", "ready_to_create", "complete", or None

        # First, check if current user message is a priority or status answer (CHANGED ORDER)
        current_lower = current_user_message.lower().strip()
        current_original = current_user_message.strip()  # Keep original case

        # Check for priority
        if current_lower in [p.lower() for p in priority_values]:
            task_priority = current_lower

        # Check for status - map display names to API values
        elif current_original in status_map:
            # Direct match with display name (e.g., "Done", "To Do", "In Progress")
            task_status = status_map[current_original]
        elif current_lower in status_map:
            # Lowercase match
            task_status = status_map[current_lower]
        # Also check common variations
        elif "done" in current_lower or "completed" in current_lower:
            task_status = "done"
        elif "in progress" in current_lower:
            task_status = "in_progress"
        elif "todo" in current_lower:
            task_status = "todo"

        # Track all messages in chronological order (append current message)
        all_messages = list(messages) + [{"role": "user", "content": current_user_message}]

        # Scan through conversation in ORDER
        # IMPORTANT: We need to handle the current message (last one) specially
        # because status/priority answers might come before we've fully detected the title
        for i, msg in enumerate(all_messages):
            role = msg.get("role", "")
            content = msg.get("content", "")
            content_lower = content.lower()
            is_last_message = (i == len(all_messages) - 1)

            if role == "user":
                # Check if this is a task creation request
                if not task_title and not task_created:
                    task_create_patterns = [
                        r'add\s+(?:a\s+)?task\s+(?:to\s+)?(.+?)(?:\.|$)',
                        r'create\s+(?:a\s+)?task\s+(?:for\s+)?(.+?)(?:\.|$)',
                        r'remember\s+to\s+(.+?)(?:\.|$)',
                        r'new\s+task\s*:\s*(.+?)(?:\.|$)',
                    ]
                    for pattern in task_create_patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            task_title = match.group(1).strip()
                            break

                # CHANGED: Check for PRIORITY first (before status)
                # For the current message (last one), check even if task_title isn't set yet
                should_check_priority = is_last_message or (task_title and not task_priority)
                if should_check_priority and not task_priority:
                    for priority_val in priority_values:
                        if priority_val in content_lower and len(content_lower.split()) <= 5:
                            task_priority = priority_val
                            break

                # CHANGED: Then check for STATUS (after priority)
                should_check_status = is_last_message or (task_title and task_priority and not task_status)
                if should_check_status and not task_status:
                    for status_val in status_values:
                        if status_val in content_lower and len(content_lower.split()) <= 5:
                            task_status = status_map.get(status_val, status_val)
                            break

            elif role == "assistant":
                # CHANGED: Check if assistant asked for PRIORITY first
                priority_question_patterns = [
                    "what priority",
                    "priority?",
                    "priority level",
                    "choose a priority",
                    "select priority"
                ]
                if any(q in content_lower for q in priority_question_patterns):
                    asked_priority = True
                    if task_title and not task_priority:
                        stage = "need_priority"

                # CHANGED: Then check if assistant asked for STATUS
                status_question_patterns = [
                    "what status",
                    "status?",
                    "status would",
                    "choose a status",
                    "select status"
                ]
                if any(q in content_lower for q in status_question_patterns):
                    asked_status = True
                    if task_title and task_priority and not task_status:
                        stage = "need_status"

                # Check if task was created (success message)
                if "task added" in content_lower or "successfully created" in content_lower or \
                   ("success" in content_lower and "task" in content_lower) or "task created" in content_lower:
                    task_created = True
                    stage = "complete"

                # Check if assistant asked for task/title (indicates we're starting over)
                if any(q in content_lower for q in ["what task", "what would you like", "task would you like"]):
                    # Assistant is asking for a new task - reset state
                    return None

        # Determine if we're still in the middle of task creation (CHANGED ORDER)
        if task_title and not task_created:
            # We have a task but haven't created it yet
            if not task_priority:
                stage = "need_priority"
            elif not task_status:
                stage = "need_status"
            else:
                stage = "ready_to_create"

            result = {
                "title": task_title,
                "priority": task_priority,  # CHANGED: priority first
                "status": task_status,
                "stage": stage,
                "asked_for_priority": asked_priority,  # CHANGED: priority first
                "asked_for_status": asked_status
            }
            # Debug logging
            print(f"[DEBUG PENDING TASK] Detected: title={task_title}, priority={task_priority}, status={task_status}, stage={stage}")
            return result

        print(f"[DEBUG PENDING TASK] No pending task detected. title={task_title}, task_created={task_created}")
        return None

    def _format_pending_task_context(self, pending_task: Dict[str, str]) -> str:
        """
        Format pending task state as a system message.

        Args:
            pending_task: Dict with pending task info

        Returns:
            Formatted system message string
        """
        title = pending_task.get("title", "")
        priority = pending_task.get("priority")
        status = pending_task.get("status")
        stage = pending_task.get("stage", "")

        parts = [f"TASK CREATION IN PROGRESS: '{title}'"]

        # Show what we have collected
        collected = []
        if priority:
            collected.append(f"priority={priority}")
        if status:
            collected.append(f"status={status}")

        if collected:
            parts.append(f"Have: {', '.join(collected)}")

        # Stage-specific instructions with CLEAR action
        if stage == "need_priority":
            parts.append("\nYOU MUST ASK: 'What priority? (Low, Medium, High, or Urgent)'")
            parts.append("DO NOT ask about status - that comes NEXT!")
            parts.append("DO NOT ask about title - you already have it!")
        elif stage == "need_status":
            parts.append("\nYOU MUST ASK: 'What status? (To Do, In Progress, or Done)'")
            parts.append("DO NOT ask about priority or title - you already have them!")
            parts.append("After user answers, IMMEDIATELY create the task!")
        elif stage == "ready_to_create":
            parts.append("\n🚨 CREATE THE TASK NOW - All information collected!")
            parts.append(f"IMMEDIATELY call: add_task(title='{title}', priority='{priority}', status='{status}')")
            parts.append("Map status display names to API values:")
            parts.append("- 'To Do' → status='todo'")
            parts.append("- 'In Progress' → status='in_progress'")
            parts.append("- 'Done' → status='done'")
            parts.append(f"\nTask to create: title='{title}', priority='{priority}', status='{status}'")
            parts.append("\nDO NOT ask any more questions - CREATE THE TASK NOW!")
            parts.append("DO NOT treat 'Done' as a command - it's the STATUS VALUE!")
            parts.append("Call add_task() immediately - do NOT call set_task_status!")

        parts.append("\n⚠️ CRITICAL: PRIORITY comes FIRST, then STATUS!")
        parts.append("⚠️ DO NOT treat 'Done' as a command - it's a status value!")
        parts.append("⚠️ DO NOT ask for task title again - you already have it!")

        return "\n".join(parts)

    async def _load_conversation_history(
        self,
        user_id: str,
        conversation_id: UUID,
        db_session: AsyncSession,
        max_history: int
    ) -> List[Dict[str, str]]:
        """
        Load conversation history from database.

        Args:
            user_id: User ID (integer)
            conversation_id: Conversation UUID
            db_session: Database session
            max_history: Maximum messages to load

        Returns:
            Formatted message list from database
        """
        try:
            # DEBUG: Log conversation_id details
            print(f"[DEBUG HISTORY] Loading history for conversation_id={conversation_id}, user_id={user_id}")

            # Get conversation history
            messages = await ConversationRepository.get_conversation_history(
                db_session,
                user_id,
                conversation_id,
                limit=max_history
            )

            print(f"[DEBUG HISTORY] Loaded {len(messages)} raw messages from database")

            # Format messages for OpenAI API
            formatted = []
            for i, msg in enumerate(messages):
                # Skip system messages (they're in the prompt)
                if msg.role == "system":
                    continue

                formatted_msg = {
                    "role": msg.role,
                    "content": msg.content
                }
                formatted.append(formatted_msg)
                print(f"[DEBUG HISTORY] Message {i+1}: role={msg.role}, content_preview={msg.content[:50]}...")

            self.logger.info(
                "History loaded",
                user_id=user_id,
                conversation_id=str(conversation_id),
                message_count=len(formatted)
            )

            return formatted

        except Exception as e:
            print(f"[DEBUG HISTORY] ERROR loading history: {str(e)}")
            import traceback
            traceback.print_exc()
            self.logger.error(
                "Failed to load history",
                user_id=user_id,
                conversation_id=str(conversation_id),
                error=str(e)
            )
            return []

    def truncate_context_if_needed(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> List[Dict[str, str]]:
        """
        Truncate context to fit within token limit.

        Keeps system message and recent messages.

        Args:
            messages: Message list to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated message list
        """
        # Estimate token count
        estimated_tokens = len(messages) * TOKENS_PER_MESSAGE

        if estimated_tokens <= max_tokens:
            return messages

        # Calculate how many messages to keep
        # Keep system message + recent messages
        system_message = messages[0] if messages and messages[0]["role"] == "system" else None

        # Calculate messages to keep (excluding system)
        available_tokens = max_tokens - (TOKENS_PER_MESSAGE if system_message else 0)
        messages_to_keep = available_tokens // TOKENS_PER_MESSAGE

        # Build truncated list
        truncated = []
        if system_message:
            truncated.append(system_message)

        # Keep most recent messages
        recent_messages = messages[1:] if system_message else messages
        truncated.extend(recent_messages[-messages_to_keep:])

        self.logger.info(
            "Context truncated",
            original_count=len(messages),
            truncated_count=len(truncated),
            estimated_tokens=estimated_tokens
        )

        return truncated


# =====================================================
# Context Manager
# =====================================================

class ConversationContextManager:
    """
    High-level context manager for conversation lifecycle.

    Handles conversation creation, context building, and
    message persistence throughout the conversation.
    """

    def __init__(self):
        """Initialize context manager."""
        self.builder = ConversationContextBuilder()
        self.logger = structlog.get_logger()

    async def prepare_conversation(
        self,
        user_id: str,
        conversation_id: Optional[UUID],
        user_message: str,
        db_session: AsyncSession
    ) -> tuple[UUID, List[Dict[str, str]]]:
        """
        Prepare conversation for agent execution.

        Gets or creates conversation and builds context.

        Args:
            user_id: User ID (integer)
            conversation_id: Optional conversation UUID
            user_message: User message content
            db_session: Database session

        Returns:
            Tuple of (conversation_id, context_messages)

        Example:
            conv_id, context = await manager.prepare_conversation(
                user_id=123,
                conversation_id=None,
                user_message="Add a task",
                db_session=session
            )
        """
        # Get or create conversation
        conversation = await ConversationRepository.get_or_create_conversation(
            db_session,
            user_id,
            conversation_id
        )

        # Build context
        context = await self.builder.build_context(
            user_id,
            conversation.id,
            user_message,
            db_session
        )

        # Truncate if needed
        context = self.builder.truncate_context_if_needed(context)

        self.logger.info(
            "Conversation prepared",
            user_id=user_id,
            conversation_id=str(conversation.id),
            context_length=len(context)
        )

        return conversation.id, context

    async def save_message(
        self,
        user_id: str,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[str] = None,
        db_session: AsyncSession = None
    ) -> None:
        """
        Save message to conversation.

        Args:
            user_id: User ID (integer)
            conversation_id: Conversation UUID
            role: Message role (user/assistant/system)
            content: Message content
            tool_calls: Optional tool calls JSON
            db_session: Database session
        """
        try:
            await ConversationRepository.add_message(
                db_session,
                user_id,
                conversation_id,
                role,
                content,
                tool_calls
            )

            self.logger.debug(
                "Message saved",
                user_id=user_id,
                conversation_id=str(conversation_id),
                role=role
            )

        except Exception as e:
            self.logger.error(
                "Failed to save message",
                user_id=user_id,
                conversation_id=str(conversation_id),
                error=str(e)
            )


# =====================================================
# Factory Functions
# =====================================================

def create_context_builder() -> ConversationContextBuilder:
    """
    Create conversation context builder.

    Returns:
        ConversationContextBuilder instance
    """
    return ConversationContextBuilder()


def create_context_manager() -> ConversationContextManager:
    """
    Create conversation context manager.

    Returns:
        ConversationContextManager instance
    """
    return ConversationContextManager()
