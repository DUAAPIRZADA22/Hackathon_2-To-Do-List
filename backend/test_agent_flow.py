"""Test agent flow to identify issues with tool execution"""
import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.agent.runner import AgentRunner
from src.mcp.server import init_mcp_server_with_user_story_1

async def test_agent_flow():
    """Test that agent correctly executes tools"""
    print("\n=== Testing Agent Flow ===\n")

    # Initialize MCP server first
    init_mcp_server_with_user_story_1()
    print("MCP Server initialized")

    # Test user_id
    user_id = "7"

    # Create agent runner
    agent = AgentRunner(user_id=user_id)

    # Test 1: List tasks
    print("Test 1: 'show my tasks'")
    result = await agent.chat(message="show my tasks", stream=False)
    print(f"  Response: {result['response'][:200]}")
    print(f"  Tool calls: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"    - {tc['name']}: {tc['arguments']}")
        if tc.get('result'):
            print(f"      Result: {tc['result']}")

    # Test 2: Mark task as done
    print("\nTest 2: 'mark Test Task from API as done'")
    result = await agent.chat(message="mark Test Task from API as done", stream=False)
    print(f"  Response: {result['response'][:200]}")
    print(f"  Tool calls: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"    - {tc['name']}: {tc['arguments']}")
        if tc.get('result'):
            print(f"      Result: {tc['result']}")

    # Test 3: Verify update persisted
    print("\nTest 3: Verify update by listing tasks again")
    result = await agent.chat(message="show my tasks", stream=False)
    print(f"  Response: {result['response'][:300]}")
    print(f"  Tool calls: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"    - {tc['name']}: {tc['arguments']}")
        if tc.get('result'):
            result_data = tc['result']
            if result_data.get('success'):
                data = result_data.get('data', {})
                tasks = data.get('tasks', [])
                for task in tasks:
                    print(f"      Task: {task.get('title')} (completed={task.get('completed')}, status={task.get('status')})")

    # Test 4: Set priority
    print("\nTest 4: 'set priority urgent for Test Task from API'")
    result = await agent.chat(message="set priority urgent for Test Task from API", stream=False)
    print(f"  Response: {result['response'][:200]}")
    print(f"  Tool calls: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"    - {tc['name']}: {tc['arguments']}")
        if tc.get('result'):
            print(f"      Result: {tc['result']}")

    # Test 5: Move to in progress
    print("\nTest 5: 'move Test Task from API to in progress'")
    result = await agent.chat(message="move Test Task from API to in progress", stream=False)
    print(f"  Response: {result['response'][:200]}")
    print(f"  Tool calls: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"    - {tc['name']}: {tc['arguments']}")
        if tc.get('result'):
            print(f"      Result: {tc['result']}")

    print("\n=== Agent Flow Tests Complete ===\n")

if __name__ == "__main__":
    asyncio.run(test_agent_flow())
