---
id: 001
title: actionmind-ai-cli-constitution
stage: constitution
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: (cli-user)
command: /sp.constitution
labels: ["constitution","governance","sdd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

# speckit.constitution - Phase 1 (ActionMind AI CLI)

## 1. Purpose
This Constitution establishes **mandatory standards, principles, and workflows** for Phase 1 of the ActionMind AI CLI project.
All AI agents (Claude, Copilot, Gemini, local LLMs, etc.) **must comply fully** before implementing any code.

It ensures:

- **Spec-driven development** (no "vibe coding")
- **Traceability** between requirements, tasks, and implementation
- **Maintainability, readability, and testability**
- **Future extensibility** for Phase 2+

---

## 2. Core Agent Rules

1. **No Code Without Task ID**
   - Every implementation must reference a Task ID from `speckit.tasks` or `speckit.specify`.

2. **Mandatory Sub-agent / Skill Usage**
   - All operations must use **Context7 MCP** and relevant **sub-agents/skills** for:
     - CRUD operations
     - Menu navigation
     - Validation & logging
     - Task ID management

3. **Context Verification**
   - Agents must confirm **Context7 MCP initialization and context availability** before performing any task.

4. **No Improvisation**
   - Features outside the Phase 1 CLI scope are strictly forbidden.

5. **Infrastructure Restrictions**
   - Phase 1 excludes Dapr, Kafka, database, or external integrations. Only **Python data structures** are allowed.

---

## 3. Coding Standards

1. **Language & Version**
   - Python 3.11+ (async/await only if required).

2. **Documentation**
   - Every function, class, and module must have **clear docstrings**.

3. **Naming**
   - Use **snake_case** for functions/variables, **PascalCase** for classes.

4. **Task ID Reference**
   - Every code block must include the Task ID as a comment:
     ```python
     # [Task]: T-P1-001
     ```

5. **SOLID Principles**
   - **S**ingle Responsibility: Each class/function has a single purpose
   - **O**pen/Closed: Modules are open for extension, closed for modification
   - **L**iskov Substitution: Objects can be replaced without breaking behavior
   - **I**nterface Segregation: Keep abstractions minimal and focused
   - **D**ependency Inversion: Depend on abstractions, not concrete classes

6. **DRY (Don't Repeat Yourself)**
   - Avoid code duplication; reuse functions/modules wherever possible.

7. **Modularity**
   - Separate modules for:
     - `menu()`
     - `add_task()`
     - `view_tasks()`
     - `complete_task()`
     - `delete_task()`

---

## 4. CLI Workflow Rules

1. **Menu-Driven Navigation**
   - All user interactions must be via **interactive menus**. Command-line text inputs are not allowed.

2. **CRUD Operations**
   - Add, view, complete, and delete tasks.

3. **Task IDs**
   - Task IDs must be **unique and auto-incremented** using Python structures.

4. **User Feedback**
   - Success, error, and warning messages must be **clear and visually distinct**:
     - ✅ Success
     - ⚠ Warning
     - ❌ Error

---

## 5. Error Handling & Validation

1. **Input Validation**
   - All user inputs must be checked for correctness.

2. **Graceful Error Handling**
   - Catch all exceptions. Future-Readiness

1. **MCP Hooks**
   - Keep Context7 MCP hooks for future Phase 2+ integration.

2. **Infrastructure Placeholders**
   - Phase 1 must remain isolated from external services, but code must be modular for future integration.

3. **Sub-agent / Skill Reuse**
   - Agents **must invoke relevant sub-agents/skills** whenever possible for:
     - Menu navigation
     - Task ID generation
     - Validation
     - Logging

---

## 8. Enforcement & Best Practices

1. **Golden Rule**
   - **No Task ID → No code**
   - **No MCP validation → No implementation**

2. **Phase 1 Scope**
   - CLI menu + CRUD operations only

3. **Clarification Requirement**
   - Agents must request clarification if specifications are ambiguous.

4. **Mandatory Principles**
   - SOLID, DRY, Modularity, Reusability

5. **Agentic Compliance**
   - All CRUD, menu handling, logging, and validation **must pass through Context7 MCP and available sub-agents/skills**

6. **Professional Quality**
   - Maintain read

## Response snapshot

Successfully created the ActionMind AI CLI Constitution v1.0.0 with:
- 8 Core Principles (Spec-Driven Development, MCP-First Architecture, Context Verification, Scope Boundaries, SOLID, DRY, Modularity, User Experience Standards)
- Development Standards (Python 3.11+, naming conventions, documentation requirements)
- CLI Workflow Rules (menu-driven navigation, CRUD operations, task ID management)
- Error Handling & Validation (input validation, graceful error handling, validation layers)
- Future-Readiness (MCP hooks, infrastructure placeholders, sub-agent reuse)
- Enforcement & Best Practices (golden rules, compliance review, governance)
- Governance section (amendment procedure, versioning policy, compliance review)

The constitution includes a Sync Impact Report documenting:
- Version change from [INITIAL] to 1.0.0
- All added sections and principles
- Template compatibility verification (plan, spec, tasks templates)
- No follow-up TODOs required

## Outcome

- ✅ Impact: Constitution v1.0.0 established for ActionMind AI CLI Phase 1
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (created), history/prompts/constitution/001-actionmind-ai-cli-constitution.constitution.prompt.md (created)
- 🔁 Next prompts: /sp.specify to create feature specifications, /sp.plan for architecture design, /sp.tasks for implementation tasks
- 🧠 Reflection: Constitution provides clear guardrails for Phase 1 CLI development. Key emphasis on spec-driven development (no Task ID = no code), MCP-first architecture, and SOLID principles. Templates are already compatible with new governance.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding specific Context7 MCP service references when available
