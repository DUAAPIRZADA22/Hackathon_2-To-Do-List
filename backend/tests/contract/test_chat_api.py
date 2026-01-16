"""
Contract Tests for Chat API (User Story 1)

Tests the POST /api/{user_id}/chat endpoint contract.
Validates request/response schema compliance.

TDD Approach: These tests FAIL until T038-T040 are implemented.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError


# Import after implementation
# from backend.src.main import app
# from backend.src.api.models import ChatRequest, ChatResponse


class TestChatAPIContract:
    """
    Contract tests for chat endpoint.

    Tests:
    - Request schema validation
    - Response schema validation
    - Required fields
    - Field constraints
    """

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_request_schema_valid(self):
        """
        Test that valid chat request passes schema validation.

        Given: A valid chat request with message and optional conversation_id
        When: Request is validated
        Then: Validation should pass
        """
        # TODO: Implement after T038-T040
        from backend.src.api.models import ChatRequest

        # Valid request with message only
        request = ChatRequest(
            message="Add a task to buy groceries"
        )
        assert request.message == "Add a task to buy groceries"
        assert request.conversation_id is None

        # Valid request with conversation_id
        request = ChatRequest(
            message="Show my tasks",
            conversation_id="12345678-1234-5678-1234-567812345678"
        )
        assert request.message == "Show my tasks"
        assert request.conversation_id == "12345678-1234-5678-1234-567812345678"

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_request_message_required(self):
        """
        Test that chat request requires message field.

        Given: A chat request without message
        When: Request is validated
        Then: Validation should fail with missing field error
        """
        # TODO: Implement after T038-T040
        from backend.src.api.models import ChatRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(conversation_id="uuid")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("message",) for error in errors)

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_request_message_min_length(self):
        """
        Test that chat request message has minimum length.

        Given: A chat request with empty message
        When: Request is validated
        Then: Validation should fail with min_length error
        """
        # TODO: Implement after T038-T040
        from backend.src.api.models import ChatRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("message",) for error in errors)

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_request_message_max_length(self):
        """
        Test that chat request message has maximum length.

        Given: A chat request with message exceeding 5000 chars
        When: Request is validated
        Then: Validation should fail with max_length error
        """
        # TODO: Implement after T038-T040
        from backend.src.api.models import ChatRequest
        from pydantic import ValidationError

        # Create message with 5001 characters
        long_message = "x" * 5001

        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message=long_message)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("message",) for error in errors)

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_response_schema_valid(self):
        """
        Test that chat response matches expected schema.

        Given: A valid chat response
        When: Response is validated
        Then: Validation should pass with correct fields
        """
        # TODO: Implement after T038-T040
        from backend.src.api.models import ChatResponse, ToolCall

        # Valid response without tool calls
        response = ChatResponse(
            conversation_id="12345678-1234-5678-1234-567812345678",
            response="I've added that task for you!",
            tool_calls=[]
        )
        assert response.conversation_id == "12345678-1234-5678-1234-567812345678"
        assert response.response == "I've added that task for you!"
        assert response.tool_calls == []

        # Valid response with tool calls
        response = ChatResponse(
            conversation_id="12345678-1234-5678-1234-567812345678",
            response="Task created successfully",
            tool_calls=[
                ToolCall(
                    tool="add_task",
                    parameters={"title": "Buy groceries"},
                    result="Task created successfully"
                )
            ]
        )
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].tool == "add_task"
        assert response.tool_calls[0].parameters["title"] == "Buy groceries"

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_endpoint_returns_200(self):
        """
        Test that chat endpoint returns 200 on valid request.

        Given: A valid chat request
        When: POST /api/{user_id}/chat is called
        Then: Response should be 200 OK
        """
        # TODO: Implement after T038-T040
        # This test requires the actual endpoint to be implemented
        pytest.skip("Test requires T038-T040 implementation")

        # client = TestClient(app)
        # response = client.post(
        #     "/api/user123/chat",
        #     json={"message": "Add a task to buy groceries"}
        # )
        # assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_endpoint_returns_conversation_id(self):
        """
        Test that chat endpoint returns conversation_id in response.

        Given: A chat request without conversation_id
        When: POST /api/{user_id}/chat is called
        Then: Response should include a new conversation_id
        """
        # TODO: Implement after T038-T040
        pytest.skip("Test requires T038-T040 implementation")

        # client = TestClient(app)
        # response = client.post(
        #     "/api/user123/chat",
        #     json={"message": "Add a task to buy groceries"}
        # )
        # data = response.json()
        # assert "conversation_id" in data
        # assert data["conversation_id"] is not None

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_endpoint_returns_response_text(self):
        """
        Test that chat endpoint returns response text from AI.

        Given: A chat request
        When: POST /api/{user_id}/chat is called
        Then: Response should include assistant's response text
        """
        # TODO: Implement after T038-T040
        pytest.skip("Test requires T038-T040 implementation")

        # client = TestClient(app)
        # response = client.post(
        #     "/api/user123/chat",
        #     json={"message": "Add a task to buy groceries"}
        # )
        # data = response.json()
        # assert "response" in data
        # assert isinstance(data["response"], str)
        # assert len(data["response"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.contract
    async def test_chat_endpoint_returns_tool_calls(self):
        """
        Test that chat endpoint returns tool_calls when tools are used.

        Given: A chat request that triggers tool usage
        When: POST /api/{user_id}/chat is called
        Then: Response should include tool_calls array
        """
        # TODO: Implement after T038-T040
        pytest.skip("Test requires T038-T040 implementation")

        # client = TestClient(app)
        # response = client.post(
        #     "/api/user123/chat",
        #     json={"message": "Add a task to buy groceries"}
        # )
        # data = response.json()
        # assert "tool_calls" in data
        # assert isinstance(data["tool_calls"], list)
        # # For "add task" intent, should have tool_calls
        # if "add" in data["response"].lower():
        #     assert len(data["tool_calls"]) > 0
