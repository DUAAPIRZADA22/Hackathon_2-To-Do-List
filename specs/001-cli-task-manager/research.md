# Research: ActionMind AI CLI Task Manager (Phase 1)

**Feature**: 001-cli-task-manager
**Date**: 2025-12-30
**Purpose**: Document technology decisions and best practices for Phase 1 implementation

---

## Python CLI Best Practices

### Menu-Driven Interfaces

**Decision**: Use `input()` for all user interaction with menu-driven navigation

**Rationale**:
- Constitution requirement: "Menu-driven navigation (no command-line text input)"
- Python's built-in `input()` is sufficient for Phase 1 needs
- No external dependencies required
- Cross-platform compatible (Windows, macOS, Linux)

**Alternatives Considered**:
- `argparse` - Rejected: Constitution prohibits command-line arguments
- `click` or `typer` - Rejected: External dependencies not needed for simple menu
- `curses` - Rejected: Over-engineered for 5-option menu

**Best Practice Reference**: Python official documentation recommends `input()` for simple interactive CLI applications.

---

### Stylish CLI Output

**Decision**: Use Python f-strings with emoji characters (✅, ⚠️, ❌) for visual feedback

**Rationale**:
- UTF-8 encoding standard in Python 3.11+
- Emoji characters provide immediate visual feedback
- No external dependencies (no `rich`, `colorama`, or `blessed` needed)
- Constitution requirement: "Success (✅), Warning (⚠️), Error (❌) messages"

**Alternatives Considered**:
- `rich` library - Rejected: External dependency, Phase 1 scope is simple text
- `colorama` - Rejected: Emoji feedback is clearer than color alone
- ANSI escape codes - Rejected: More complex, not needed for emoji feedback

**Best Practice**: Keep formatting simple - consistent spacing, aligned columns, clear borders.

---

### Data Structures for In-Memory Storage

**Decision**: Use Python `list` for task storage, `dataclass` for Task entity

**Rationale**:
- `list` provides O(1) append, O(n) lookup (acceptable for <1000 tasks)
- `dataclass` (Python 3.7+) provides clean, minimal boilerplate for entities
- Type hints enable better code clarity
- Built-in `datetime` for timestamps

**Alternatives Considered**:
- `dict` with task ID as key - Rejected: Adds complexity for minimal benefit (O(1) lookup not needed for Phase 1 scale)
- `pydantic` - Rejected: External dependency, `dataclass` is sufficient
- SQLAlchemy - Rejected: Database not in Phase 1 scope (in-memory only)

**Best Practice**: Use `dataclass` with `__post_init__` for validation.

---

### Input Validation

**Decision**: Multi-layer validation (Input → Business Logic → Storage)

**Rationale**:
- Separation of concerns (Constitution requirement)
- Each layer validates what it controls
- Graceful error handling with user-friendly messages

**Validation Layers**:
1. **Input Layer** (`lib/validation.py`): Type checking, range validation
2. **Business Logic** (`services/task_service.py`): Business rules (empty description, length limits)
3. **Storage** (`services/storage.py`): Existence checks (returns `None` if not found)

**Best Practice**: Raise `ValueError` with user-friendly messages, catch in handlers for display.

---

## Standard Library Capabilities

### `dataclasses` Module (Python 3.7+)

**Usage**: Task entity definition

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class Task:
    id: int
    description: str
    status: TaskStatus
    created_at: datetime
```

**Capabilities**:
- Automatic `__init__`, `__repr__`, `__eq__` generation
- Type hints support
- `__post_init__` hook for validation

**Why Not Custom Class**: `dataclass` reduces boilerplate while maintaining clarity.

---

### `abc` Module (Abstract Base Classes)

**Usage**: Storage interface for Phase 2+ extensibility

```python
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def add(self, task: Task) -> None: pass

    @abstractmethod
    def get_all(self) -> List[Task]: pass
```

**Capabilities**:
- Enforces interface contract
- Enables dependency inversion (SOLID principle)
- Supports Phase 2+ MCP integration

**Why Not Protocols**: `ABC` is clearer for this use case, `Protocol` would be over-engineering.

---

### `datetime` Module

**Usage**: Task creation timestamp

```python
from datetime import datetime

created_at = datetime.now()
```

**Capabilities**:
- Built-in timestamp support
- ISO 8601 formatting via `isoformat()`
- Timezone-aware options (not needed for Phase 1)

**Best Practice**: Use `datetime.now()` for local timestamps (sufficient for single-user CLI).

---

### `typing` Module

**Usage**: Type hints throughout codebase

```python
from typing import List, Optional

def get_task_by_id(self, task_id: int) -> Optional[Task]:
    ...
```

**Capabilities**:
- Type hints for function signatures
- `Optional` for nullable returns
- `List` for collection types

**Best Practice**: Use type hints for all public functions (Constitution requirement: "clear docstrings").

---

## Performance Considerations

### Menu Rendering

**Target**: <100ms per render

**Analysis**:
- Menu render involves ~10 `print()` calls (heading, 5 options, prompt)
- Python `print()` is fast (~0.1ms per call on modern hardware)
- String formatting (f-strings) is negligible
- **Conclusion**: Target easily achievable with standard library

**Optimization Not Needed**: No caching or pre-rendering required.

---

### Task Operations

**Target**: <200ms for CRUD operations up to 1000 tasks

**Analysis**:
- **Create**: O(1) list append - instant
- **Read**: O(n) linear search - ~0.1ms for 1000 tasks
- **Update**: O(n) find + O(1) update - ~0.1ms for 1000 tasks
- **Delete**: O(n) find + O(n) removal - ~0.2ms for 1000 tasks

**Conclusion**: All operations well under 200ms target even at maximum scale.

**Optimization Not Needed**: No indexing or data structure changes required.

---

### Memory Usage

**Target**: <50MB for typical usage (<1000 tasks)

**Analysis**:
- Single Task ~200 bytes (dataclass overhead + strings)
- 1000 tasks ~200 KB
- Python runtime overhead ~20 MB
- Total expected: ~20-25 MB

**Conclusion**: Well under 50 MB target.

**Optimization Not Needed**: No memory optimization required.

---

## Cross-Platform Compatibility

### Terminal Compatibility

**Consideration**: Different terminals (Windows cmd, PowerShell, macOS Terminal, Linux bash)

**Analysis**:
- UTF-8 emoji support (✅, ⚠️, ❌):
  - Windows 10+: Supported
  - macOS: Supported
  - Linux: Supported
- `input()` function: Universal across platforms
- `print()` function: Universal across platforms

**Conclusion**: Standard library functions provide cross-platform compatibility.

**Platform-Specific Code Not Needed**: No `os.name` checks or conditional imports required.

---

### Clearing Screen

**Consideration**: Clear screen between menu refreshes (optional)

**Options**:
1. **No clear screen** (simplest, consistent scrolling)
2. **OS-specific clear**:
   - Windows: `os.system('cls')`
   - Unix: `os.system('clear')`

**Decision**: No clear screen for Phase 1

**Rationale**:
- Keeps output scrollable for debugging
- Simpler implementation
- User can see history of actions

**Future Consideration**: Add optional clear screen in Phase 2+ if user feedback indicates preference.

---

## Error Handling Patterns

### KeyboardInterrupt (Ctrl+C)

**Scenario**: User presses Ctrl+C during any operation

**Best Practice**: Catch `KeyboardInterrupt` and exit gracefully

```python
try:
    # Main loop
except KeyboardInterrupt:
    print("\nGoodbye!")
    sys.exit(0)
```

**Decision**: Implement graceful Ctrl+C handling in main loop

---

### ValueError Handling

**Scenario**: Invalid user input (non-numeric, out of range)

**Best Practice**: Raise `ValueError` with user-friendly message, catch in handlers

```python
def validate_menu_selection(input_str: str) -> int:
    try:
        selection = int(input_str)
        if not 1 <= selection <= 5:
            raise ValueError("Invalid option. Please select 1-5")
        return selection
    except ValueError:
        raise ValueError("Please enter a number between 1 and 5")
```

**Decision**: Multi-layer validation with descriptive error messages

---

## Summary

| Decision | Rationale |
|----------|-----------|
| Use `input()` for menu interaction | Constitution requirement, no dependencies |
| f-strings with emoji | UTF-8 support, clear visual feedback |
| `list` for storage, `dataclass` for Task | Simple, sufficient for <1000 tasks |
| Multi-layer validation | Separation of concerns, SOLID principles |
| No external dependencies | Phase 1 scope, standard library sufficient |
| Type hints throughout | Code clarity, Constitution requirement |
| Graceful error handling | User experience, Constitution requirement |

**All decisions align with**:
- Constitution requirements (SOLID, DRY, modularity)
- Phase 1 scope (no external services, in-memory only)
- Success criteria (performance, usability, reliability)

---

**End of Research Document**
