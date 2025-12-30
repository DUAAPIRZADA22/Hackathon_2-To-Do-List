<!--
========================================================================
Sync Impact Report
========================================================================
Version change: [INITIAL] → 1.0.0
Modified principles: N/A (initial version)
Added sections:
  - Core Principles (8 principles)
  - Development Standards
  - CLI Workflow Rules
  - Error Handling & Validation
  - Future-Readiness
  - Enforcement & Best Practices
Removed sections: N/A (initial version)
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section compatible
  ✅ spec-template.md - Requirements structure compatible
  ✅ tasks-template.md - Task ID structure compatible
Follow-up TODOs: None
========================================================================
-->

# ActionMind AI CLI Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every implementation MUST reference a Task ID from `speckit.tasks` or `speckit.specify`. No "vibe coding" or feature implementation without documented requirements.

**Rationale**: Ensures traceability between requirements, implementation, and testing. Prevents scope creep and maintains alignment with user needs.

**Compliance**:
- All code changes must include a comment referencing the Task ID: `# [Task]: T-P1-001`
- No Task ID → No code. This is a blocking requirement.

---

### II. MCP-First Architecture

All operations MUST use Context7 MCP and relevant sub-agents/skills for:
- CRUD operations
- Menu navigation
- Validation & logging
- Task ID management

**Rationale**: Modular design enables future Phase 2+ integration with external services (Dapr, Kafka, databases). Sub-agents provide consistent, tested implementations.

**Compliance**:
- Agents must confirm Context7 MCP initialization before performing tasks
- All CRUD, menu handling, logging, and validation must pass through MCP/sub-agents
- No direct improvisation outside documented MCP capabilities

---

### III. Context Verification

Agents MUST confirm Context7 MCP initialization and context availability before performing any task.

**Rationale**: Prevents failures due to missing or improperly configured MCP services. Ensures all dependencies are available before execution.

**Compliance**:
- Verify MCP connection state before task execution
- Fail gracefully with clear error messages if context is unavailable
- Do not proceed with tasks without confirmed MCP availability

---

### IV. Scope Boundaries

Features outside the Phase 1 CLI scope are strictly forbidden.

**Phase 1 Scope**:
- CLI menu-driven navigation
- CRUD operations (Add, View, Complete, Delete tasks)
- In-memory Python data structures only

**Out of Scope**:
- Dapr, Kafka, databases, or external integrations
- Persistence beyond runtime (no file I/O or database)
- Network operations
- Async/await (unless explicitly required)

**Rationale**: Phase 1 is a foundation. Premature complexity hinders validation of core concepts.

---

### V. SOLID Principles

All code MUST adhere to SOLID principles:

- **S**ingle Responsibility: Each class/function has a single purpose
- **O**pen/Closed: Modules are open for extension, closed for modification
- **L**iskov Substitution: Objects can be replaced without breaking behavior
- **I**nterface Segregation: Keep abstractions minimal and focused
- **D**ependency Inversion: Depend on abstractions, not concrete classes

**Rationale**: Maintains code quality, testability, and extensibility. Enables Phase 2+ enhancements without rewriting core logic.

---

### VI. DRY (Don't Repeat Yourself)

Avoid code duplication; reuse functions/modules wherever possible.

**Compliance**:
- Extract repeated logic into reusable functions
- Prefer composition over copy-paste
- Use MCP services for common operations

**Rationale**: Reduces maintenance burden and ensures consistent behavior across the codebase.

---

### VII. Modularity

Separate modules for each core operation:
- `menu()` - Main menu navigation
- `add_task()` - Task creation
- `view_tasks()` - Task listing
- `complete_task()` - Task completion
- `delete_task()` - Task deletion

**Rationale**: Clear boundaries enable independent testing, parallel development, and easier maintenance.

---

### VIII. User Experience Standards

All user interactions MUST follow:

**Menu-Driven Navigation**
- Interactive menus only (no command-line text input)
- Clear visual hierarchy
- Intuitive option numbering/selection

**User Feedback**
- ✅ Success messages (green checkmark)
- ⚠️ Warning messages (yellow triangle)
- ❌ Error messages (red X)

**Rationale**: Consistent, predictable interface reduces user confusion and support burden.

---

## Development Standards

### Language & Version
- Python 3.11+
- Async/await only if explicitly required

### Documentation
- Every function, class, and module MUST have clear docstrings
- Docstrings must describe purpose, parameters, and return values

### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

### Code Quality
- Maximum line length: 100 characters (soft limit)
- No trailing whitespace
- Single blank line between sections
- Type hints encouraged but not mandatory

---

## CLI Workflow Rules

### Task Management
- Task IDs MUST be unique and auto-incremented using Python structures
- No manual Task ID assignment
- Task IDs persist only in runtime memory (Phase 1)

### CRUD Operations
All core operations MUST be available:
1. **Add Task**: Create new tasks with unique IDs
2. **View Tasks**: List all tasks with status
3. **Complete Task**: Mark tasks as completed
4. **Delete Task**: Remove tasks from the list

### Menu Navigation
- All user interactions via interactive menus
- Clear option numbering and descriptions
- Return to main menu after operation completion

---

## Error Handling & Validation

### Input Validation
- All user inputs MUST be validated for correctness
- Type checking for numeric inputs
- Range checking for menu selections
- Empty/null input detection

### Graceful Error Handling
- Catch all exceptions with specific error messages
- Never crash with raw stack traces to end users
- Log errors for debugging (via MCP logging services)
- Provide recovery guidance to users

### Validation Layers
1. **Input Layer**: Validate raw user input
2. **Business Logic Layer**: Validate operations against current state
3. **MCP Layer**: Leverage MCP validation services when available

---

## Future-Readiness

### MCP Hooks
- Keep Context7 MCP hooks for future Phase 2+ integration
- Design modules to accept MCP service implementations
- Avoid hardcoding implementations that block MCP integration

### Infrastructure Placeholders
- Phase 1 remains isolated from external services
- Code must be modular for future integration
- Design data structures to be persistable (even if not persisted in Phase 1)

### Sub-Agent Reuse
Agents MUST invoke relevant sub-agents/skills for:
- Menu navigation
- Task ID generation
- Validation
- Logging

**Rationale**: Sub-agents provide tested, consistent implementations. Reuse accelerates development and ensures quality.

---

## Enforcement & Best Practices

### Golden Rules
1. **No Task ID → No code**
2. **No MCP validation → No implementation**

### Phase 1 Scope
- CLI menu + CRUD operations only
- No external dependencies or infrastructure

### Clarification Requirement
- Agents MUST request clarification if specifications are ambiguous
- Never assume requirements or make up features

### Mandatory Principles
- SOLID
- DRY
- Modularity
- Reusability

### Agentic Compliance
- All CRUD operations through MCP/sub-agents
- All menu handling through MCP/sub-agents
- All logging through MCP/sub-agents
- All validation through MCP/sub-agents

### Professional Quality
- Maintain readable, documented code
- Follow Python PEP 8 style guide
- Write self-documenting code (clear names, obvious logic)
- Include docstrings for all public interfaces

---

## Governance

### Amendment Procedure
1. Propose change with rationale
2. Document impact on existing code
3. Update this constitution with version bump
4. Propagate changes to dependent templates (plan, spec, tasks)
5. Create migration plan if breaking changes

### Versioning Policy
- **MAJOR**: Backward-incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review
- All code reviews must verify constitution compliance
- Violations require explicit justification in plan.md Complexity Tracking table
- Repeated violations trigger constitution review

### Constitution Authority
This constitution supersedes all other practices. In case of conflict, this document is the source of truth.

---

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
