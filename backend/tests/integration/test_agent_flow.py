"""
Integration Tests for Agent Intent Detection (User Story 1)

Tests the agent's ability to detect "create task" intent and invoke add_task tool.
Validates end-to-end AI orchestration workflow.

TDD Approach: These tests FAIL until T036-T037 are implemented.
"""

import pytest


# Import after implementation
# from backend.src.agent.runner import AgentRunner
# from backend.src.mcp.server import get_mcp_server


class TestAgentIntentDetection:
    """
    Integration tests for agent intent detection.

    Tests:
    - Create intent detection
    - Tool invocation
    - Response formatting
    - Error handling
    """

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_detects_create_intent(self):
        """
        Test that agent detects "create task" intent from natural language.

        Given: A user says "Add a task to buy groceries"
        When: Agent processes the message
        Then: Agent should invoke add_task tool
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # result = await runner.chat(
        #     message="Add a task to buy groceries",
        #     conversation_history=None
        # )

        # # Should have tool calls
        # assert len(result["tool_calls"]) > 0
        # assert result["tool_calls"][0]["name"] == "add_task"
        # assert result["tool_calls"][0]["arguments"]["title"] == "Buy groceries"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_detects_remember_intent(self):
        """
        Test that agent detects "remember" as create intent.

        Given: A user says "Remember to call mom on Saturday"
        When: Agent processes the message
        Then: Agent should invoke add_task tool with correct title
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # result = await runner.chat(
        #     message="Remember to call mom on Saturday",
        #     conversation_history=None
        # )

        # assert len(result["tool_calls"]) > 0
        # assert result["tool_calls"][0]["name"] == "add_task"
        # # Extract task title from the message
        # assert "call mom" in result["tool_calls"][0]["arguments"]["title"].lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_extracts_task_details(self):
        """
        Test that agent extracts task title and description from message.

        Given: A user says "Add a task: buy groceries on Saturday afternoon"
        When: Agent processes the message
        Then: Agent should invoke add_task with title and description
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # result = await runner.chat(
        #     message="Add a task: buy groceries on Saturday afternoon",
        #     conversation_history=None
        # )

        # assert len(result["tool_calls"]) > 0
        # tool_call = result["tool_calls"][0]
        # assert tool_call["name"] == "add_task"
        # assert "title" in tool_call["arguments"]
        # # May or may not have description depending on AI interpretation

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_responds_confirmation(self):
        """
        Test that agent provides confirmation after creating task.

        Given: A user creates a task
        When: Agent completes the tool call
        Then: Agent should respond with confirmation message
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # result = await runner.chat(
        #     message="Add a task to buy groceries",
        #     conversation_history=None
        # )

        # # Should have text response
        # assert result["response"] is not None
        # assert len(result["response"]) > 0

        # # Should indicate task was created
        # response_lower = result["response"].lower()
        # assert any(word in response_lower for word in ["added", "created", "task", "done"])

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_handles_ambiguous_input(self):
        """
        Test that agent asks for clarification when intent is unclear.

        Given: A user says something ambiguous like "the thing"
        When: Agent processes the message
        Then: Agent should ask for clarification
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # result = await runner.chat(
        #     message="the thing",
        #     conversation_history=None
        # )

        # # Should not invoke tools
        # assert len(result["tool_calls"]) == 0

        # # Should ask for clarification
        # response_lower = result["response"].lower()
        # assert any(word in response_lower for word in ["what", "clarify", "mean", "which"])

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_handles_conversation_context(self):
        """
        Test that agent maintains context in multi-turn conversations.

        Given: A user creates a task, then asks to change it
        When: Agent processes second message with history
        Then: Agent should reference previous context
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # # First message
        # result1 = await runner.chat(
        #     message="Add a task to buy groceries",
        #     conversation_history=None
        # )

        # # Build conversation history
        # history = [
        #     {"role": "user", "content": "Add a task to buy groceries"},
        #     {"role": "assistant", "content": result1["response"]},
        # ]

        # # Second message
        # result2 = await runner.chat(
        #     message="Change it to buy milk",
        #     conversation_history=history
        # )

        # # Agent should understand "it" refers to the grocery task
        # # (This requires context awareness from conversation history)
        # assert result2["response"] is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_tool_error_handling(self):
        """
        Test that agent handles tool execution errors gracefully.

        Given: A tool execution fails (e.g., database error)
        When: Agent receives error from tool
        Then: Agent should respond with helpful error message
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # This would require mocking a tool failure scenario
        # For now, we verify the agent doesn't crash on tool errors

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_finished_flag(self):
        """
        Test that agent sets finished flag correctly.

        Given: A user sends a message
        When: Agent completes processing
        Then: finished flag should be True
        """
        # TODO: Implement after T036-T037
        pytest.skip("Test requires T036-T037 implementation")

        # from backend.src.agent.runner import AgentRunner

        # runner = AgentRunner(user_id="test_user_123")

        # result = await runner.chat(
        #     message="Add a task to buy groceries",
        #     conversation_history=None
        # )

        # assert result["finished"] is True
