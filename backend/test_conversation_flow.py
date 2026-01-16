"""
Test conversation context persistence
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import async_session_maker
from src.db.repository import ConversationRepository
from src.agent.context import ConversationContextBuilder


async def test_conversation_persistence():
    """Test that conversation_id persists across messages"""
    print("\n=== Testing Conversation Context Persistence ===\n")

    # Create context builder
    builder = ConversationContextBuilder()

    async with async_session_maker() as session:
        user_id = "6"  # Test user ID

        # Message 1: "add a task test"
        print("Message 1: 'add a task test123'")
        print("-" * 50)

        # First message - should create new conversation
        conv1 = await ConversationRepository.get_or_create_conversation(
            session, user_id, None
        )
        conv_id_1 = conv1.id
        print(f"Created conversation: {conv_id_1}")

        # Save first message
        await ConversationRepository.add_message(
            session, user_id, conv_id_1,
            "user", "add a task test123"
        )

        # Build context for first message
        context1 = await builder.build_context(
            user_id=user_id,
            conversation_id=conv_id_1,
            user_message="add a task test123",
            db_session=session
        )
        print(f"Context 1 message count: {len(context1)}")

        # Save assistant response
        await ConversationRepository.add_message(
            session, user_id, conv_id_1,
            "assistant", "What priority? (Low, Medium, High, or Urgent)"
        )

        # Commit to ensure data is persisted
        await session.commit()

    # Create NEW session to simulate a new request (like in the actual API)
    async with async_session_maker() as session:
        print(f"\nMessage 2: 'High' (priority selection)")
        print("-" * 50)

        # Second message - should use existing conversation
        print(f"Using conversation_id: {conv_id_1}")

        # Build context for second message (priority selection)
        context2 = await builder.build_context(
            user_id=user_id,
            conversation_id=conv_id_1,
            user_message="High",
            db_session=session
        )
        print(f"Context 2 message count: {len(context2)}")

        # Check if history was loaded
        if len(context2) > 2:  # System + current message = 2 minimum
            print("✅ SUCCESS: Conversation history was preserved!")
            print(f"   - System message: 1")
            print(f"   - History messages: {len(context2) - 2}")
            print(f"   - Current user message: 1")
        else:
            print("❌ FAILURE: Conversation history was NOT preserved!")
            print(f"   - Only {len(context2)} messages in context")

        # Save second message and response
        await ConversationRepository.add_message(
            session, user_id, conv_id_1,
            "user", "High"
        )
        await ConversationRepository.add_message(
            session, user_id, conv_id_1,
            "assistant", "What status? (To Do, In Progress, or Done)"
        )
        await session.commit()

    print("\n=== Test Complete ===\n")


if __name__ == "__main__":
    asyncio.run(test_conversation_persistence())
