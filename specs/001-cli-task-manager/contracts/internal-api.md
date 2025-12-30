# Internal API Contracts: ActionMind AI CLI Task Manager (Phase 1)

**Feature**: 001-cli-task-manager
**Date**: 2025-12-30
**Purpose**: Define internal API contracts between layers

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface Layer                     │
│  (cli/menu.py, cli/handlers.py, cli/display.py)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Task Management Service                   │
│  (services/task_service.py)                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  (services/storage.py)                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Contract 1: CLI → TaskService

### Interface

```python
class TaskService:
    def create_task(self, description: str) -> Task:
        """Create a new task.

        Args:
            description: Task description (1-200 characters)

        Returns:
            Created Task object with auto-generated ID

        Raises:
            ValueError: If description is empty or >200 characters
        """

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks (empty list if none)
        """

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task was marked complete
            False if task was not found

        Raises:
            ValueError: If task is already completed
        """

    def delete_task(self, task_id: int) -> bool:
        """Delete a task.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task was deleted
            False if task was not found
        """
```

### Usage Example

```python
# CLI handler calls TaskService
task_service = TaskService(storage)

try:
    task = task_service.create_task("Buy groceries")
    display_success(f"Task created with ID: {task.id}")
except ValueError as e:
    display_error(str(e))
```

---

## Contract 2: TaskService → Storage

### Interface

```python
class StorageInterface(ABC):
    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a task to storage.

        Args:
            task: Task object to add

        Raises:
            None - this operation always succeeds
        """

    @abstractmethod
    def get_all(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks (empty list if none)
        """

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Find task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task if found, None if not found
        """

    @abstractmethod
    def update(self, task: Task) -> bool:
        """Replace an existing task.

        Args:
            task: Task object with updated data

        Returns:
            True if task was updated
            False if task ID was not found
        """

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            True if task was deleted
            False if task ID was not found
        """

    @abstractmethod
    def generate_id(self) -> int:
        """Generate next unique task ID.

        Returns:
            Unique integer ID
        """
```

### Usage Example

```python
# TaskService calls Storage
class TaskService:
    def __init__(self, storage: StorageInterface):
        self._storage = storage

    def create_task(self, description: str) -> Task:
        # Validation
        if not description or description.isspace():
            raise ValueError("Task description cannot be blank")

        # Create task
        task_id = self._storage.generate_id()
        task = Task(
            id=task_id,
            description=description.strip(),
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )

        # Store
        self._storage.add(task)
        return task
```

---

## Contract 3: Display Utilities

### Interface

```python
def display_styled_heading(text: str) -> None:
    """Display a styled heading with decorative borders.

    Args:
        text: Heading text to display
    """

def display_success(message: str) -> None:
    """Display a success message with ✅ emoji.

    Args:
        message: Success message text
    """

def display_warning(message: str) -> None:
    """Display a warning message with ⚠️ emoji.

    Args:
        message: Warning message text
    """

def display_error(message: str) -> None:
    """Display an error message with ❌ emoji.

    Args:
        message: Error message text
    """

def display_task_table(tasks: List[Task]) -> None:
    """Display tasks in a formatted table.

    Args:
        tasks: List of tasks to display
    """

def pause_for_acknowledgment() -> None:
    """Pause and wait for user to press Enter."""
```

### Usage Example

```python
# CLI handler uses display utilities
def add_task_handler(task_service: TaskService) -> None:
    description = prompt_for_input("Enter task description: ")

    try:
        task = task_service.create_task(description)
        display_success(f"Task created with ID: {task.id}")
    except ValueError as e:
        display_error(str(e))

    pause_for_acknowledgment()
```

---

## Contract 4: Validation Utilities

### Interface

```python
def validate_menu_selection(input_str: str) -> int:
    """Validate menu selection input.

    Args:
        input_str: Raw user input string

    Returns:
        Validated integer (1-5)

    Raises:
        ValueError: If input is not numeric or not in range 1-5
    """

def validate_task_id(input_str: str) -> int:
    """Validate task ID input.

    Args:
        input_str: Raw user input string

    Returns:
        Validated integer task ID (> 0)

    Raises:
        ValueError: If input is not numeric or not positive
    """

def validate_description(description: str) -> str:
    """Validate and normalize task description.

    Args:
        description: Raw task description

    Returns:
        Normalized description (trimmed)

    Raises:
        ValueError: If description is empty or too long
    """
```

### Usage Example

```python
# CLI handler uses validation utilities
def complete_task_handler(task_service: TaskService) -> None:
    input_str = prompt_for_input("Enter task ID: ")

    try:
        task_id = validate_task_id(input_str)
        success = task_service.complete_task(task_id)

        if success:
            display_success("Task marked as completed")
        else:
            display_error("Task not found")
    except ValueError as e:
        display_error(str(e))
```

---

## Error Handling Contract

### Error Propagation

```text
┌─────────────────────────────────────────────────────────────┐
│ CLI Handler (catches ValueError, displays to user)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ (raises ValueError)
┌─────────────────────────────────────────────────────────────┐
│ TaskService (validates business rules)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ (returns None/False)
┌─────────────────────────────────────────────────────────────┐
│ Storage (graceful handling, no exceptions)                  │
└─────────────────────────────────────────────────────────────┘
```

### Error Messages

| Layer | Error Type | Message Format |
|-------|------------|----------------|
| Validation | ValueError | "Please enter a number between 1 and 5" |
| TaskService | ValueError | "Task description cannot be blank" |
| TaskService | ValueError | "Task is already completed" |
| Storage | (none) | Returns `None` or `False` |

---

## Data Transfer Objects (DTOs)

### Task Entity (Internal DTO)

```python
@dataclass
class Task:
    """Internal task representation."""
    id: int
    description: str
    status: TaskStatus
    created_at: datetime
```

**Note**: Phase 1 has no external DTOs (no API, no serialization).

---

## Method Signatures Summary

| Layer | Method | Input | Output | Raises |
|-------|--------|-------|--------|--------|
| CLI | `add_task_handler()` | None | None | None (catches errors) |
| CLI | `view_tasks_handler()` | None | None | None |
| CLI | `complete_task_handler()` | None | None | None (catches errors) |
| CLI | `delete_task_handler()` | None | None | None (catches errors) |
| Service | `create_task()` | description: str | Task | ValueError |
| Service | `get_all_tasks()` | None | List[Task] | None |
| Service | `complete_task()` | task_id: int | bool | ValueError |
| Service | `delete_task()` | task_id: int | bool | None |
| Storage | `add()` | task: Task | None | None |
| Storage | `get_all()` | None | List[Task] | None |
| Storage | `get_by_id()` | task_id: int | Optional[Task] | None |
| Storage | `update()` | task: Task | bool | None |
| Storage | `delete()` | task_id: int | bool | None |
| Storage | `generate_id()` | None | int | None |

---

## Testing Contracts (Manual)

### Manual Test Scenarios

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| Add task (valid) | description="Buy groceries" | ✅ Success with ID |
| Add task (empty) | description="" | ⚠️ Warning: blank |
| Add task (long) | description="a"*250 | ⚠️ Warning: too long |
| View tasks (empty) | (no tasks) | "No tasks found" |
| View tasks (populated) | (3 tasks exist) | Table with 3 rows |
| Complete (valid) | task_id=1 | ✅ Success |
| Complete (invalid) | task_id=999 | ❌ Error: not found |
| Delete (valid) | task_id=1 | ✅ Success |
| Delete (invalid) | task_id=999 | ❌ Error: not found |

---

## Summary

| Contract | Between | Purpose |
|----------|---------|---------|
| CLI → TaskService | Presentation → Business Logic | Execute user actions |
| TaskService → Storage | Business Logic → Data | Persist/retrieve tasks |
| Display Utilities | CLI → User | Show formatted output |
| Validation Utilities | CLI → Business Logic | Validate input |

**All contracts use**:
- Type hints for clarity
- Explicit return types
- `ValueError` for validation failures
- Boolean success indicators (not exceptions) for "not found" cases

---

**End of Internal API Contracts Document**
