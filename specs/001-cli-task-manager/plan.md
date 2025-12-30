# Implementation Plan: ActionMind AI CLI Task Manager (Phase 1)

**Branch**: `001-cli-task-manager` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cli-task-manager/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

---

## Summary

ActionMind AI Phase 1 is a menu-driven Python CLI application for task management. Users can create, view, complete, and delete tasks through an intuitive interface with visual feedback (✅⚠️❌). The application stores tasks in memory during a single session, with no persistence or external dependencies. This foundational phase validates core user interactions and establishes patterns for future AI-powered enhancements.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Standard library only (no external packages for Phase 1)
**Storage**: In-memory Python list/dictionary (no database, no file I/O)
**Testing**: Not required for Phase 1 (manual testing via CLI execution)
**Target Platform**: Cross-platform (Windows, macOS, Linux) - any system with Python 3.11+
**Project Type**: Single project (standalone CLI application)
**Performance Goals**:
  - Menu render: <100ms
  - Task operations: <200ms for up to 1000 tasks
  - Memory usage: <50MB for typical usage
**Constraints**:
  - No external dependencies (standard library only)
  - No file or database persistence
  - No network operations
  - No async/await (synchronous execution only)
  - Single-user, single-session
**Scale/Scope**:
  - Single user
  - Up to 1000 tasks in memory
  - 5 menu options
  - Single process, no threading

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Constitution Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | All implementation will reference Task IDs from tasks.md |
| II. MCP-First Architecture | ⚠️ DEFER | Phase 1 uses direct Python implementation; MCP hooks will be added as placeholders for Phase 2+ |
| III. Context Verification | ✅ PASS | No MCP services required for Phase 1 (in-memory operations) |
| IV. Scope Boundaries | ✅ PASS | No Dapr, database, cloud, or external services; in-memory only |
| V. SOLID Principles | ✅ PASS | Design follows SOLID (see Section 5) |
| VI. DRY | ✅ PASS | Reusable functions for common operations (see Section 5) |
| VII. Modularity | ✅ PASS | Separate modules for menu, add_task, view_tasks, complete_task, delete_task |
| VIII. User Experience Standards | ✅ PASS | Menu-driven with ✅⚠️❌ feedback indicators |

### Constitution Compliance Notes

**MCP-First Architecture (Principle II)**: Phase 1 defers full MCP integration because:
1. Constitution permits Phase 1 to use "Python data structures only"
2. MCP services are designed for Phase 2+ external integrations (Dapr, Kafka, databases)
3. Design includes abstraction layer for future MCP service injection

**No justification required** - this is an approved constitution exception for Phase 1.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-task-manager/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command - internal APIs)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py          # Package initialization
├── main.py              # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass/entity definition
├── services/
│   ├── __init__.py
│   ├── task_service.py  # Business logic for CRUD operations
│   └── storage.py       # In-memory storage abstraction
├── cli/
│   ├── __init__.py
│   ├── menu.py          # Main menu rendering and navigation
│   ├── handlers.py      # Menu option handlers (add, view, complete, delete)
│   └── display.py       # Display utilities (tables, borders, feedback)
└── lib/
    ├── __init__.py
    ├── validation.py    # Input validation utilities
    └── mcp_placeholder.py # Placeholder interfaces for future MCP integration

tests/
# Note: No automated tests for Phase 1 per spec
# Manual testing via CLI execution
```

**Structure Decision**: Single project structure (Option 1) is appropriate because:
- This is a standalone CLI application with no frontend/backend separation
- All code runs in a single process
- No web APIs, mobile apps, or distributed components
- Standard library dependencies only (no package management complexity)

---

## Complexity Tracking

> **No violations requiring justification**

All design decisions align with Constitution principles and Phase 1 scope boundaries.

---

## High-Level Architecture

### System Overview

ActionMind AI Phase 1 is a **single-process, event-loop CLI application** with layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface Layer                     │
│  (menu.py, handlers.py, display.py)                        │
│  - Renders main menu with styled heading                    │
│  - Captures user input (numeric menu selections)            │
│  - Routes to appropriate handlers                           │
│  - Displays formatted output (task lists, feedback)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Task Management Service                   │
│  (task_service.py)                                          │
│  - Validates business rules                                 │
│  - Coordinates CRUD operations                              │
│  - Enforces task ID uniqueness                              │
│  - Returns results to CLI layer                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  (storage.py + models/task.py)                              │
│  - In-memory task collection (list)                         │
│  - Task entity definition (dataclass)                       │
│  - Auto-incrementing ID generation                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Placeholder Layer                         │
│  (lib/mcp_placeholder.py)                                   │
│  - Abstract interfaces for future MCP services              │
│  - No-op implementations for Phase 1                        │
└─────────────────────────────────────────────────────────────┘
```

### Execution Flow (Program Start to Exit)

1. **Initialization** (`main.py`)
   - Import all modules
   - Initialize in-memory storage (empty task list)
   - Generate first Task ID seed (1)

2. **Main Menu Display** (`cli/menu.py`)
   - Clear screen (optional, platform-dependent)
   - Render styled heading with decorative borders
   - Display 5 numbered menu options
   - Prompt for user input

3. **Input Capture** (`cli/menu.py`)
   - Read user input from stdin
   - Validate numeric range (1-5)
   - Handle non-numeric input gracefully

4. **Action Routing** (`cli/handlers.py`)
   - Route to handler based on selection:
     - Option 1 → `add_task_handler()`
     - Option 2 → `view_tasks_handler()`
     - Option 3 → `complete_task_handler()`
     - Option 4 → `delete_task_handler()`
     - Option 5 → Exit (break loop)

5. **Handler Execution** (`cli/handlers.py` + `services/task_service.py`)
   - Prompt for additional input if needed (task ID, description)
   - Call Task Service method
   - Display feedback (✅⚠️❌) via `cli/display.py`

6. **Return to Menu** (`cli/menu.py`)
   - After handler completes, pause for user acknowledgment
   - Loop back to step 2

7. **Exit** (`main.py`)
   - On option 5, display farewell message
   - Terminate program (tasks lost, no persistence)

---

## Component Breakdown

### Core Components

#### 1. CLI Interface Layer

**Responsibilities**: All user interaction, display rendering, input capture

**Modules**:
- `cli/menu.py` - Main menu orchestration
- `cli/handlers.py` - Menu option handlers
- `cli/display.py` - Display formatting utilities

**Key Functions**:
```python
# cli/menu.py
def display_main_menu() -> None:
    """Render styled main menu with heading and 5 options."""

def get_menu_selection() -> int:
    """Capture and validate numeric menu input (1-5)."""

def main_menu_loop() -> None:
    """Primary event loop: display → capture → route → repeat."""

# cli/handlers.py
def add_task_handler(task_service: TaskService) -> None:
    """Handle 'Add Task' menu option: prompt, create, feedback."""

def view_tasks_handler(task_service: TaskService) -> None:
    """Handle 'View Tasks' menu option: display list with status."""

def complete_task_handler(task_service: TaskService) -> None:
    """Handle 'Complete Task' menu option: prompt, update, feedback."""

def delete_task_handler(task_service: TaskService) -> None:
    """Handle 'Delete Task' menu option: prompt, remove, feedback."""

# cli/display.py
def display_styled_heading(text: str) -> None:
    """Render decorative bordered heading (e.g., 'ActionMind AI')."""

def display_success(message: str) -> None:
    """Render success message with ✅ emoji."""

def display_warning(message: str) -> None:
    """Render warning message with ⚠️ emoji."""

def display_error(message: str) -> None:
    """Render error message with ❌ emoji."""

def display_task_table(tasks: List[Task]) -> None:
    """Render formatted task list with aligned columns."""

def prompt_for_input(prompt_text: str) -> str:
    """Display prompt and return user input."""
```

**Design Notes**:
- No CLI argument parsing (constitution requirement: menu-only)
- All prompts use `input()` built-in function
- Display functions separate from business logic (Single Responsibility)

---

#### 2. Task Management Service

**Responsibilities**: Business logic, validation, coordination of operations

**Module**: `services/task_service.py`

**Key Functions**:
```python
# services/task_service.py
class TaskService:
    def __init__(self, storage: StorageInterface):
        """Initialize with storage abstraction (dependency injection)."""

    def create_task(self, description: str) -> Task:
        """
        Create new task with auto-incremented ID.
        Validates: description not empty/whitespace.
        Raises: ValueError if validation fails.
        Returns: Created Task entity.
        """

    def get_all_tasks(self) -> List[Task]:
        """Return list of all tasks (empty list if none)."""

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Find task by ID.
        Returns: Task if found, None if not found.
        """

    def complete_task(self, task_id: int) -> bool:
        """
        Mark task as completed.
        Validates: task exists, not already complete.
        Returns: True if successful, False if task not found.
        Raises: ValueError if task already complete.
        """

    def delete_task(self, task_id: int) -> bool:
        """
        Remove task from storage.
        Returns: True if deleted, False if not found.
        """
```

**Design Notes**:
- Follows Single Responsibility (business logic only, no display)
- Depends on StorageInterface abstraction (Dependency Inversion)
- Returns boolean success indicators (no display logic)

---

#### 3. Task Model

**Responsibilities**: Data structure definition, validation rules

**Module**: `models/task.py`

**Key Definition**:
```python
# models/task.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class Task:
    """Represents a single todo item."""
    id: int                          # Unique identifier (auto-incremented)
    description: str                 # Task description (1-200 characters)
    status: TaskStatus               # PENDING or COMPLETED
    created_at: datetime             # Timestamp of creation

    def __post_init__(self):
        """Validate description length and strip whitespace."""
        # Enforce 1-200 character limit
        # Strip leading/trailing whitespace
```

**Design Notes**:
- Uses `dataclass` for clean, minimal boilerplate
- `Enum` for type-safe status values
- Validation in `__post_init__` ensures data integrity

---

#### 4. Storage Layer

**Responsibilities**: In-memory data storage, ID generation, lifecycle management

**Modules**: `services/storage.py`, `lib/mcp_placeholder.py`

**Key Definitions**:
```python
# services/storage.py
class InMemoryStorage(StorageInterface):
    """In-memory task storage using Python list."""

    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def add(self, task: Task) -> None:
        """Add task to storage."""

    def get_all(self) -> List[Task]:
        """Return all tasks (returns empty list if none)."""

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Find task by ID (returns None if not found)."""

    def update(self, task: Task) -> bool:
        """Replace existing task (returns False if ID not found)."""

    def delete(self, task_id: int) -> bool:
        """Remove task by ID (returns False if not found)."""

    def generate_id(self) -> int:
        """Return next auto-incremented ID."""

# lib/mcp_placeholder.py
class StorageInterface(ABC):
    """Abstract interface for storage implementations.

    NOTE: Phase 1 uses InMemoryStorage. Phase 2+ will replace with
    MCP-backed storage (Dapr state store, database, etc.).
    """
    @abstractmethod
    def add(self, task: Task) -> None: pass

    @abstractmethod
    def get_all(self) -> List[Task]: pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]: pass

    @abstractmethod
    def update(self, task: Task) -> bool: pass

    @abstractmethod
    def delete(self, task_id: int) -> bool: pass
```

**Design Notes**:
- `StorageInterface` abstraction enables Phase 2+ swap to MCP services
- `_next_id` counter ensures unique, auto-incrementing IDs
- No persistence - data lost on program exit (Phase 1 scope)

---

## Control Flow & Navigation

### Main Loop Behavior

```text
┌─────────────────────────────────────────────────────────────┐
│                    START (main.py)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Initialize: Storage, TaskService               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Main Menu Loop │ ◄──────────────────┐
                   └─────────────────┘                     │
                            │                               │
                            ▼                               │
              ┌────────────────────────┐                   │
              │   Display Main Menu    │                   │
              │   (styled heading)     │                   │
              └────────────────────────┘                   │
                            │                               │
                            ▼                               │
              ┌────────────────────────┐                   │
              │   Get User Input       │                   │
              │   (validate 1-5)       │                   │
              └────────────────────────┘                   │
                            │                               │
                            ▼                               │
              ┌────────────────────────┐                   │
              │   Route Selection      │                   │
              └────────────────────────┘                   │
                     │        │        │                    │
        ┌────────────┼────────┼────────┼────────────┐      │
        ▼            ▼        ▼        ▼               ▼      │
    [Add]       [View]  [Complete] [Delete]        [Exit]     │
        │            │        │        │               │      │
        ▼            ▼        ▼        ▼               ▼      │
   ┌─────────┐ ┌──────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
   │ Handler │ │Handler│ │ Handler │ │ Handler │ │ Exit    ││
   └─────────┘ └──────┘ └─────────┘ └─────────┘ └─────────┘│
        │            │        │        │               │      │
        └────────────┼────────┼────────┼───────────────┘      │
                     │        │        │                      │
                     ▼        ▼        ▼                      │
              ┌────────────────────────┐                   │
              │   Display Feedback      │                   │
              │   (✅⚠️❌)              │                   │
              └────────────────────────┘                   │
                     │                                      │
                     ▼                                      │
              ┌────────────────────────┐                   │
              │   Pause for Acknowledge │                   │
              │   ("Press Enter...")    │                   │
              └────────────────────────┘                   │
                     │                                      │
                     └──────────────────────────────────────┘
                            │
                            ▼ (if Exit)
┌─────────────────────────────────────────────────────────────┐
│              Display Farewell, Terminate                     │
└─────────────────────────────────────────────────────────────┘
```

### Menu Option Routing

| Selection | Handler Function | Service Method | User Flow |
|-----------|------------------|----------------|-----------|
| 1 (Add Task) | `add_task_handler()` | `task_service.create_task()` | Prompt description → Validate → Create → ✅ Success with ID |
| 2 (View Tasks) | `view_tasks_handler()` | `task_service.get_all_tasks()` | Display table → "No tasks" if empty → Pause → Return |
| 3 (Complete) | `complete_task_handler()` | `task_service.complete_task()` | Prompt ID → Validate → Update → ✅ Success or ⚠️ Already complete |
| 4 (Delete) | `delete_task_handler()` | `task_service.delete_task()` | Prompt ID → Validate → Remove → ✅ Success or ❌ Not found |
| 5 (Exit) | (break loop) | (none) | Display farewell → Terminate |

### Return to Menu Mechanism

After every handler completes:
1. Handler displays feedback (✅⚠️❌) via `cli/display.py`
2. Handler calls `pause_for_acknowledge()` - displays "Press Enter to continue..."
3. `input()` blocks until user presses Enter
4. Control returns to `main_menu_loop()`
5. Loop repeats: menu displays again

---

## Error Handling Strategy

### Error Categories & Responses

| Error Type | Example | Detection | User Message | Recovery |
|------------|---------|-----------|--------------|----------|
| Invalid menu input | User enters "abc" | Non-numeric input | ❌ "Please enter a number between 1 and 5" | Re-prompt for input |
| Out of range menu | User enters "9" | Not in 1-5 | ❌ "Invalid option. Please select 1-5" | Re-prompt for input |
| Empty task description | User presses Enter without text | Empty/whitespace string | ⚠️ "Task description cannot be blank" | Re-prompt for description |
| Invalid task ID | User enters "xyz" for task ID | Non-numeric input | ❌ "Please enter a valid task ID" | Re-prompt for ID |
| Task not found | User enters ID 999 | ID not in storage | ❌ "Task not found" | Return to menu |
| Already complete | User marks already-complete task | Status is COMPLETED | ⚠️ "Task is already completed" | Return to menu |
| Description too long | User enters 250+ characters | Length > 200 | ⚠️ "Description too long (max 200 characters)" | Re-prompt with truncated or new input |
| Ctrl+C interruption | User presses Ctrl+C | KeyboardInterrupt | (optional) Display graceful exit message | Terminate program |

### Validation Layers

**Layer 1: Input Validation** (`cli/handlers.py` + `lib/validation.py`)
```python
def validate_menu_selection(input_str: str) -> int:
    """
    Validate menu input is numeric and in range 1-5.
    Raises: ValueError with user-friendly message.
    """
    try:
        selection = int(input_str)
        if not 1 <= selection <= 5:
            raise ValueError("Please select 1-5")
        return selection
    except ValueError:
        raise ValueError("Please enter a number between 1 and 5")
```

**Layer 2: Business Logic Validation** (`services/task_service.py`)
```python
def create_task(self, description: str) -> Task:
    """Validate business rules before creation."""
    if not description or description.isspace():
        raise ValueError("Task description cannot be blank")
    if len(description) > 200:
        raise ValueError("Description too long (max 200 characters)")
    # Proceed with creation
```

**Layer 3: Storage Validation** (`services/storage.py`)
```python
def get_by_id(self, task_id: int) -> Optional[Task]:
    """Returns None if not found (graceful handling)."""
    for task in self._tasks:
        if task.id == task_id:
            return task
    return None  # Not an error, just "not found"
```

### User-Friendly CLI Messages

**Success (✅)**:
- "Task created successfully with ID: {id}"
- "Task marked as completed"
- "Task deleted successfully"

**Warning (⚠️)**:
- "Task description cannot be blank"
- "Description too long (max 200 characters). Truncating..."
- "Task is already completed"

**Error (❌)**:
- "Invalid option. Please select 1-5"
- "Please enter a valid task ID"
- "Task not found"

**Recovery Guidance**:
- After error: "Press Enter to try again"
- After success: "Press Enter to return to menu"

---

## Design Principles (Mandatory)

### SOLID Principles Compliance

#### Single Responsibility Principle (SRP)
- **Each module has ONE reason to change**:
  - `cli/menu.py` → Menu display/navigation logic changes
  - `cli/handlers.py` → User interaction flow changes
  - `cli/display.py` → Visual formatting changes
  - `services/task_service.py` → Business rule changes
  - `services/storage.py` → Storage mechanism changes
  - `models/task.py` → Task data structure changes

- **Each function has ONE job**:
  - `display_main_menu()` only displays (doesn't capture input)
  - `validate_menu_selection()` only validates (doesn't display)
  - `create_task()` only creates (doesn't display result)

#### Open/Closed Principle (OCP)
- **Open for extension**:
  - `StorageInterface` allows new storage backends (MCP, database) without modifying `TaskService`
  - Menu handlers can be added without modifying `main_menu_loop()` (using dict-based routing)
  - Display formats can be extended by adding functions to `cli/display.py`

- **Closed for modification**:
  - Core logic in `TaskService` doesn't change when storage swaps
  - Menu rendering doesn't change when new options added (uses loop)

#### Liskov Substitution Principle (LSP)
- **`InMemoryStorage` can replace `StorageInterface`** without breaking `TaskService`
- Future `MCPStorage` will also implement `StorageInterface` and be substitutable

#### Interface Segregation Principle (ISP)
- **`StorageInterface` is minimal** - only methods actually used:
  - No unused methods like `bulk_import()` or `search_by_tags()`
  - Keeps implementation simple for Phase 1

#### Dependency Inversion Principle (DIP)
- **`TaskService` depends on abstraction** (`StorageInterface`), not concrete `InMemoryStorage`
- **CLI layer depends on `TaskService` abstraction**, not internal storage details
- Enables Phase 2+ swap to MCP-backed storage without rewriting handlers

---

### DRY (Don't Repeat Yourself)

**Reusable Display Utilities** (`cli/display.py`):
```python
# Don't repeat this in every handler:
def display_task_table(tasks: List[Task]) -> None:
    """Centralized table rendering with consistent formatting."""
```

**Reusable Validation Functions** (`lib/validation.py`):
```python
# Don't repeat validation logic:
def validate_task_id(input_str: str) -> int:
    """Centralized task ID validation."""
```

**Reusable Feedback Functions** (`cli/display.py`):
```python
# Don't repeat emoji formatting:
def display_success(message: str) -> None:
    print(f"✅ {message}")

def display_warning(message: str) -> None:
    print(f"⚠️ {message}")

def display_error(message: str) -> None:
    print(f"❌ {message}")
```

---

### Separation of Concerns

| Layer | Concern | Does NOT Handle |
|-------|---------|-----------------|
| CLI (`cli/`) | User interaction, display | Business rules, storage |
| Service (`services/`) | Business logic, validation | Display, storage implementation |
| Storage (`services/storage.py`) | Data persistence (in-memory) | Display, business rules |
| Model (`models/`) | Data structure, validation | Display, storage mechanism |

**Key Separation**:
- CLI handlers NEVER call storage directly (always through `TaskService`)
- Service NEVER displays (returns results, lets CLI display)
- Storage NEVER validates business rules (stores/retrieves only)

---

### Readability Over Cleverness

**Clear Naming**:
- `display_main_menu()` not `render()`
- `validate_menu_selection()` not `check()`
- `task_service.create_task()` not `task_service.add()`

**Explicit Logic**:
```python
# Prefer this (clear):
def generate_id(self) -> int:
    next_id = self._next_id
    self._next_id += 1
    return next_id

# Over this (clever but opaque):
def generate_id(self) -> int:
    return self._next_id + 1  # Bug: doesn't increment!
```

**No Premature Optimization**:
- Use `list` for storage (not optimizing for 1M+ tasks - Phase 1 is <1000)
- Use linear search for `get_by_id()` (not indexing - not needed for Phase 1)
- Synchronous execution (not async - not needed for single-user CLI)

---

## Extensibility Plan

### Phase 2 Backend Replacement

**Current (Phase 1)**:
```python
# services/storage.py
class InMemoryStorage(StorageInterface):
    def __init__(self):
        self._tasks: List[Task] = []
```

**Phase 2 (MCP Integration)**:
```python
# services/mcp_storage.py
class MCPStorage(StorageInterface):
    """Dapr-backed state store via Context7 MCP."""
    def __init__(self, mcp_client):
        self._mcp = mcp_client

    def add(self, task: Task) -> None:
        self._mcp.save_state(key=f"task-{task.id}", value=task)

    # ... other methods
```

**Swap Mechanism** (no changes to `TaskService`):
```python
# main.py Phase 1:
storage = InMemoryStorage()

# main.py Phase 2:
storage = MCPStorage(mcp_client=context7.get_client())

# TaskService works with either:
task_service = TaskService(storage)
```

---

### Dapr Integration Later

**Placeholder Interfaces** (`lib/mcp_placeholder.py`):
```python
class MCPStateStoreInterface(ABC):
    """Abstract interface for Dapr state store.

    Phase 1: No-op implementation
    Phase 2+: Real Dapr integration via Context7 MCP
    """
    @abstractmethod
    def save_state(self, key: str, value: any) -> None: pass

    @abstractmethod
    def get_state(self, key: str) -> any: pass

    @abstractmethod
    def delete_state(self, key: str) -> None: pass
```

**Phase 1 No-Op**:
```python
class NoOpMCPStateStore(MCPStateStoreInterface):
    """Phase 1 placeholder - does nothing."""
    def save_state(self, key: str, value: any) -> None:
        pass  # No-op - in-memory storage handles data

    def get_state(self, key: str) -> any:
        return None  # No-op
```

**Phase 2+ Implementation**:
```python
class DaprMCPStateStore(MCPStateStoreInterface):
    """Real Dapr state store via Context7 MCP."""
    def __init__(self, dapr_client):
        self._dapr = dapr_client

    def save_state(self, key: str, value: any) -> None:
        self._dapr.save_state(store_name="tasks", key=key, value=value)
```

---

### Persistence Layer Swap

**Current** (Phase 1):
- `InMemoryStorage` with Python `list`
- Data lost on exit

**Future Options** (Phase 2+):
- **File-based**: `JSONFileStorage` - serialize to `tasks.json`
- **SQLite**: `SQLiteStorage` - local database
- **Dapr**: `DaprStorage` - distributed state store
- **PostgreSQL**: `PostgresStorage` - cloud database

**All implement `StorageInterface`** - zero changes to:
- `TaskService`
- CLI handlers
- Display logic

---

### MCP Service Injection Points

**Current Code** (Phase 1):
```python
# Direct instantiation
storage = InMemoryStorage()
task_service = TaskService(storage)
```

**Future Code** (Phase 2+):
```python
# MCP-backed services
storage = MCPStorage(mcp_client=context7.get_client())
validator = MCPValidator(mcp_client=context7.get_client())
logger = MCPLogger(mcp_client=context7.get_client())

task_service = TaskService(storage, validator, logger)
```

**Key Design Elements**:
1. `StorageInterface` abstraction
2. Constructor injection (not hardcoded dependencies)
3. No direct MCP calls in Phase 1 (all through placeholders)
4. Single-line changes in `main.py` to enable MCP

---

## Constitution Check (Post-Design)

### Design Phase Constitution Compliance

| Principle | Status | Verification |
|-----------|--------|--------------|
| I. Spec-Driven Development | ✅ PASS | All design traced to spec.md requirements (FR-001 to FR-020) |
| II. MCP-First Architecture | ✅ PASS | MCP placeholder interfaces added for Phase 2+ integration |
| III. Context Verification | ✅ PASS | No MCP services required (Phase 1 uses direct Python) |
| IV. Scope Boundaries | ✅ PASS | No external dependencies, in-memory only, no persistence |
| V. SOLID Principles | ✅ PASS | Documented in Section 5 (all 5 principles applied) |
| VI. DRY | ✅ PASS | Reusable functions in display.py, validation.py |
| VII. Modularity | ✅ PASS | Separate modules: menu, handlers, task_service, storage, model |
| VIII. User Experience Standards | ✅ PASS | Menu-driven with ✅⚠️❌ feedback, no CLI arguments |

**MCP-First Architecture (Principle II) - Re-evaluated**:
- **Phase 1 Design**: Uses direct Python implementation with MCP placeholder interfaces
- **Constitution Compliance**: Approved for Phase 1 (see Constitution Check section above)
- **Phase 2+ Readiness**: `StorageInterface`, `MCPStateStoreInterface` abstractions enable seamless MCP integration
- **No Violation**: Constitution explicitly permits Phase 1 "Python data structures only"

---

## Next Steps

This plan is complete. Proceed to:

1. **Phase 0**: Generate `research.md` (Python CLI best practices, standard library capabilities)
2. **Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. **Phase 2**: Run `/sp.tasks` to generate actionable implementation task list

---

**End of Implementation Plan**
