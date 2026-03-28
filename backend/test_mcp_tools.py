"""Test MCP tools directly to verify they work"""
import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.mcp.server import init_mcp_server_with_user_story_1
from src.mcp.tools.task_tools import ListTasksTool, SetTaskStatusTool, SetTaskPriorityTool

async def test_mcp_tools():
    """Test MCP tools execute correctly"""
    print("\n=== Testing MCP Tools ===\n")

    # Initialize MCP server
    server = init_mcp_server_with_user_story_1()
    print(f"MCP Server initialized with {len(server.list_tools())} tools")

    # Test user_id
    user_id = "7"

    # Test 1: List tasks
    print("\nTest 1: list_tasks tool")
    list_tool = ListTasksTool()
    result = await list_tool.execute(user_id=user_id)
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Tasks found: {result.data.get('count', 0)}")
        for task in result.data.get('tasks', []):
            print(f"    - {task['task_id']}: {task['title']} (completed={task.get('completed')})")
    else:
        print(f"  Error: {result.error}")

    # Test 2: Set task status to "done"
    print("\nTest 2: set_task_status tool")
    status_tool = SetTaskStatusTool()
    result = await status_tool.execute(user_id=user_id, title="Test Task from API", status="done")
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Result: {result.data}")
    else:
        print(f"  Error: {result.error}")

    # Test 3: List tasks again to verify update
    print("\nTest 3: list_tasks after update")
    result = await list_tool.execute(user_id=user_id)
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Tasks found: {result.data.get('count', 0)}")
        for task in result.data.get('tasks', []):
            print(f"    - {task['task_id']}: {task['title']} (completed={task.get('completed')})")

    # Test 4: Set task priority
    print("\nTest 4: set_task_priority tool")
    priority_tool = SetTaskPriorityTool()
    result = await priority_tool.execute(user_id=user_id, title="Test Task from API", priority="high")
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Result: {result.data}")
    else:
        print(f"  Error: {result.error}")

    # Test 5: List tasks again to verify priority update
    print("\nTest 5: list_tasks after priority update")
    result = await list_tool.execute(user_id=user_id)
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Tasks found: {result.data.get('count', 0)}")
        for task in result.data.get('tasks', []):
            print(f"    - {task['task_id']}: {task['title']} (completed={task.get('completed')})")

    print("\n=== MCP Tool Tests Complete ===\n")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
