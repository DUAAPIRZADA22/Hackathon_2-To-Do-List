# Quickstart: ActionMind AI CLI Task Manager (Phase 1)

**Feature**: 001-cli-task-manager
**Date**: 2025-12-30
**Purpose**: Quick reference for running and testing the application

---

## Installation

### Prerequisites

- Python 3.11 or higher
- No external dependencies required (standard library only)

### Setup

```bash
# Clone repository (if applicable)
cd /path/to/ActionMindAI

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

---

## Running the Application

### Start the CLI

```bash
# From repository root
python -m src.main
```

### Expected Output

```
╔═══════════════════════════════╗
║     ActionMind AI v1.0        ║
╚═══════════════════════════════╝

Main Menu:
1. Add Task
2. View Tasks
3. Complete Task
4. Delete Task
5. Exit

Enter your choice (1-5):
```

---

## User Guide

### Adding a Task

1. Select option `1` from the main menu
2. Enter a task description when prompted
3. See success message with the new task ID

**Example**:
```
Enter your choice (1-5): 1
Enter task description: Buy groceries
✅ Task created successfully with ID: 1
Press Enter to continue...
```

---

### Viewing All Tasks

1. Select option `2` from the main menu
2. See a formatted table of all tasks

**Example**:
```
Enter your choice (1-5): 2
┌────┬─────────────────────┬────────────┬────────────────────┐
│ ID │ Description         │ Status     │ Created At         │
├────┼─────────────────────┼────────────┼────────────────────┤
│  1 │ Buy groceries       │ PENDING    │ 2025-12-30 10:30   │
│  2 │ Write code          │ COMPLETED  │ 2025-12-30 11:15   │
└────┴─────────────────────┴────────────┴────────────────────┘
Press Enter to continue...
```

**If no tasks exist**:
```
Enter your choice (1-5): 2
ℹ️ No tasks found. Press Enter to continue...
```

---

### Completing a Task

1. Select option `3` from the main menu
2. Enter the task ID
3. See confirmation or error message

**Example** (success):
```
Enter your choice (1-5): 3
Enter task ID: 1
✅ Task marked as completed
Press Enter to continue...
```

**Example** (already completed):
```
Enter your choice (1-5): 3
Enter task ID: 2
⚠️ Task is already completed
Press Enter to continue...
```

**Example** (not found):
```
Enter your choice (1-5): 3
Enter task ID: 999
❌ Task not found
Press Enter to continue...
```

---

### Deleting a Task

1. Select option `4` from the main menu
2. Enter the task ID
3. See confirmation or error message

**Example** (success):
```
Enter your choice (1-5): 4
Enter task ID: 1
✅ Task deleted successfully
Press Enter to continue...
```

**Example** (not found):
```
Enter your choice (1-5): 4
Enter task ID: 999
❌ Task not found
Press Enter to continue...
```

---

### Exiting the Application

1. Select option `5` from the main menu
2. See farewell message
3. Application terminates (tasks are NOT saved)

**Example**:
```
Enter your choice (1-5): 5
Thank you for using ActionMind AI!
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Exit application immediately |
| `Enter` | Confirm input / Continue to menu |

---

## Error Handling

### Invalid Menu Selection

```
Enter your choice (1-5): abc
❌ Please enter a number between 1 and 5

Enter your choice (1-5): 9
❌ Invalid option. Please select 1-5
```

### Empty Task Description

```
Enter your choice (1-5): 1
Enter task description:
⚠️ Task description cannot be blank
Press Enter to continue...
```

### Invalid Task ID

```
Enter your choice (1-5): 3
Enter task ID: xyz
❌ Please enter a valid task ID
Press Enter to continue...
```

---

## Session Management

### Data Persistence

**Phase 1 Limitation**: Tasks are stored in memory only and are **lost when the application exits**.

**Example**:
```
# Session 1:
- Create task with ID 1
- Exit application

# Session 2:
- Task list is empty (ID counter resets to 1)
```

**Future Phases**:
- Phase 2: File-based persistence (JSON)
- Phase 3: Database persistence
- Phase 4: Cloud synchronization

---

## Troubleshooting

### Issue: Application won't start

**Check Python version**:
```bash
python --version
# Should be 3.11 or higher
```

**Check file structure**:
```
ActionMindAI/
├── src/
│   ├── __init__.py
│   └── main.py
```

---

### Issue: Emoji not displaying correctly

**Cause**: Terminal doesn't support UTF-8

**Solution**: Ensure terminal encoding is UTF-8
```bash
# Windows PowerShell:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# macOS/Linux terminal:
export LANG=en_US.UTF-8
```

---

### Issue: Tasks disappear on restart

**Expected behavior**: Phase 1 does not persist data (see "Data Persistence" above)

---

## Performance Expectations

| Operation | Expected Time |
|-----------|---------------|
| Menu render | < 100ms |
| Add task | < 100ms |
| View tasks (1000 tasks) | < 200ms |
| Complete task | < 100ms |
| Delete task | < 100ms |

---

## Development Quick Reference

### Project Structure

```
src/
├── __init__.py
├── main.py              # Entry point
├── models/
│   └── task.py          # Task entity
├── services/
│   ├── task_service.py  # Business logic
│   └── storage.py       # In-memory storage
├── cli/
│   ├── menu.py          # Main menu loop
│   ├── handlers.py      # Menu handlers
│   └── display.py       # Display utilities
└── lib/
    ├── validation.py    # Input validation
    └── mcp_placeholder.py # MCP placeholders (Phase 2+)
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `Task` | `models/task.py` | Task data entity |
| `TaskService` | `services/task_service.py` | Business logic |
| `InMemoryStorage` | `services/storage.py` | In-memory storage |

### Key Functions

| Function | File | Purpose |
|----------|------|---------|
| `main_menu_loop()` | `cli/menu.py` | Main event loop |
| `add_task_handler()` | `cli/handlers.py` | Handle "Add Task" |
| `view_tasks_handler()` | `cli/handlers.py` | Handle "View Tasks" |
| `complete_task_handler()` | `cli/handlers.py` | Handle "Complete Task" |
| `delete_task_handler()` | `cli/handlers.py` | Handle "Delete Task" |

---

## Next Steps

After running the application:

1. **Test all user stories** (see `spec.md` for acceptance scenarios)
2. **Verify error handling** (try invalid inputs)
3. **Check performance** (add 100+ tasks)
4. **Report issues** (if found)

For implementation details, see:
- `plan.md` - Architecture and design
- `data-model.md` - Data structures
- `contracts/internal-api.md` - API contracts

---

**End of Quickstart Guide**
