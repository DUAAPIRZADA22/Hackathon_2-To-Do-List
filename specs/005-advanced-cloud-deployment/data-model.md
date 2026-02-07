# Data Model: Advanced Cloud Deployment with Event-Driven Architecture

**Feature**: 005-advanced-cloud-deployment
**Date**: 2026-02-08
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data entities for the event-driven architecture, including database schema extensions, event schemas, and state management.

## Database Entities

### Extended Task Model

```python
# backend/src/models/task.py (modified)
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

class Task(Base):
    __tablename__ = "tasks"

    # Existing fields (from Phase IV)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # NEW: Phase V fields
    recurrence_rule = Column(JSONB, nullable=True)
    reminder_settings = Column(JSONB, nullable=True)
```

### Recurrence Rule Schema

```json
{
  "frequency": "daily" | "weekly" | "monthly",
  "interval": 1,           // Every N days/weeks/months (default: 1)
  "days": ["monday"],       // For weekly: which days
  "month_day": 15,          // For monthly: which day of month
  "end_date": "2026-12-31", // Optional: last occurrence
  "count": 10               // Optional: max occurrences (not used in initial impl)
}
```

**Validation Rules**:
- `frequency` is required: must be "daily", "weekly", or "monthly"
- `interval` defaults to 1 if not specified
- For `weekly` frequency, `days` array is required
- For `monthly` frequency, `month_day` is required (1-31)
- `end_date` and `count` are mutually exclusive

**Examples**:
```json
// Daily task
{"frequency": "daily"}

// Weekly task on Mondays and Wednesdays
{"frequency": "weekly", "days": ["monday", "wednesday"]}

// Monthly task on the 15th
{"frequency": "monthly", "month_day": 15}

// Weekly task ending on December 31
{"frequency": "weekly", "days": ["friday"], "end_date": "2026-12-31"}
```

### Reminder Settings Schema

```json
{
  "reminder_times": ["1h", "1d", "1w"],  // When to remind before due date
  "notification_method": "email",         // "email" or "push" (push not in initial impl)
  "enabled": true                         // Can be disabled without deleting settings
}
```

**Validation Rules**:
- `reminder_times` array: each value must match pattern `(\d+)(m|h|d|w)`
- Valid units: `m` (minutes), `h` (hours), `d` (days), `w` (weeks)
- Maximum: 5 reminder times per task
- `notification_method`: only "email" supported in Phase V

**Examples**:
```json
// Remind 1 hour before
{"reminder_times": ["1h"], "notification_method": "email", "enabled": true}

// Remind 1 day and 1 week before
{"reminder_times": ["1d", "1w"], "notification_method": "email", "enabled": true}

// Remind 15 minutes, 1 hour, and 1 day before
{"reminder_times": ["15m", "1h", "1d"], "notification_method": "email", "enabled": true}
```

## Event Schemas

### Task Event Schema

```yaml
# events/task-event.yaml
type: object
required:
  - event_type
  - task_id
  - user_id
  - timestamp
  - correlation_id
properties:
  event_type:
    type: string
    enum:
      - task_created
      - task_updated
      - task_deleted
      - task_assigned
      - task_completed
      - task_uncompleted
    description: Type of task event
  task_id:
    type: string
    format: uuid
    description: Unique identifier of the task
  project_id:
    type: string
    format: uuid
    description: Project identifier (optional)
  user_id:
    type: string
    format: uuid
    description: User who performed the action
  timestamp:
    type: string
    format: date-time
    description: When the event occurred (ISO 8601)
  correlation_id:
    type: string
    format: uuid
    description: Correlation ID for distributed tracing
  data:
    type: object
    description: Event-specific data
    properties:
      title:
        type: string
        description: Task title (for created/updated events)
      status:
        type: string
        description: Task status (for updated/completed events)
      assigned_to:
        type: string
        format: uuid
        description: User ID task is assigned to (for assigned events)
      recurrence_rule:
        type: object
        description: Recurrence rule (if task is recurring)
```

**Event Examples**:
```json
// task_created
{
  "event_type": "task_created",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-08T12:00:00Z",
  "correlation_id": "880e8400-e29b-41d4-a716-446655440000",
  "data": {
    "title": "Complete Phase 5 implementation",
    "status": "pending",
    "assigned_to": "990e8400-e29b-41d4-a716-446655440000",
    "recurrence_rule": null
  }
}

// task_completed (for recurring task)
{
  "event_type": "task_completed",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-08T14:00:00Z",
  "correlation_id": "880e8400-e29b-41d4-a716-446655440000",
  "data": {
    "recurrence_rule": {
      "frequency": "weekly",
      "days": ["monday"],
      "end_date": "2026-12-31"
    }
  }
}
```

### Reminder Event Schema

```yaml
# events/reminder-event.yaml
type: object
required:
  - reminder_type
  - task_id
  - due_date
  - user_id
  - timestamp
  - correlation_id
properties:
  reminder_type:
    type: string
    enum:
      - due_approaching
      - overdue
    description: Type of reminder
  task_id:
    type: string
    format: uuid
    description: Unique identifier of the task
  due_date:
    type: string
    format: date-time
    description: Task due date (ISO 8601)
  user_id:
    type: string
    format: uuid
    description: User to receive the reminder
  timestamp:
    type: string
    format: date-time
    description: When the reminder was triggered (ISO 8601)
  correlation_id:
    type: string
    format: uuid
    description: Correlation ID for distributed tracing
  data:
    type: object
    properties:
      task_title:
        type: string
        description: Task title for notification
      message:
        type: string
        description: Reminder message
      reminder_time:
        type: string
        description: Original reminder time setting (e.g., "1h", "1d")
```

**Event Examples**:
```json
// due_approaching reminder
{
  "reminder_type": "due_approaching",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "due_date": "2026-02-08T17:00:00Z",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-08T16:00:00Z",
  "correlation_id": "880e8400-e29b-41d4-a716-446655440000",
  "data": {
    "task_title": "Complete Phase 5 implementation",
    "message": "Task is due in 1 hour",
    "reminder_time": "1h"
  }
}
```

## State Transitions

### Task Status State Machine

```
                    ┌─────────────┐
                    │   pending   │
                    └──────┬──────┘
                           │ assign/start
                           ▼
                    ┌─────────────┐
           complete  │ in_progress │
           ┌─────────┴─────────────┴─────────┐
           │                                 │
           ▼                                 │
    ┌─────────────┐                         │
    │  completed  │─────────────────────────┘
    └─────────────┘
           │ (recurring only)
           │ complete recurring task
           ▼
    ┌─────────────┐
    │ new instance│
    │  (pending)  │
    └─────────────┘
```

**State Transitions with Events**:

| Current State | Action | Next State | Event Published |
|---------------|--------|------------|-----------------|
| pending | assign | pending | task_assigned |
| pending | start | in_progress | task_updated |
| in_progress | complete | completed | task_completed |
| completed | uncomplete | pending | task_uncompleted |
| pending | delete | - | task_deleted |
| any | update | same | task_updated |

**Recurring Task Special Case**:
- When a recurring task is completed, a `task_completed` event is published
- Recurring Task Service consumes this event
- If `recurrence_rule` exists and conditions met, creates new task instance
- New task is created with `pending` status
- Original task remains in `completed` state

## Relationships

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │───────┤    Task     │───────│  Project    │
│             │ 1:N   │             │ N:1   │             │
│ - id        │       │ - id        │       │ - id        │
│ - email     │       │ - title     │       │ - name      │
│ - name      │       │ - status    │       │             │
└─────────────┘       │ - user_id   │       └─────────────┘
                      │ - project_id│
                      │ - assigned_to│
                      └─────────────┘
                            │
                            │ event-driven
                            ▼
                      ┌─────────────┐
                      │ Task Event  │
                      │             │
                      │ - event_type│
                      │ - task_id   │
                      │ - data      │
                      └─────────────┘
```

## Indexes

```sql
-- Performance indexes for event-driven queries
CREATE INDEX idx_tasks_status ON tasks(status) WHERE status != 'completed';
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;

-- Recurrence rule index for filtering recurring tasks
CREATE INDEX idx_tasks_recurrence_frequency ON tasks((recurrence_rule->>'frequency'))
WHERE recurrence_rule IS NOT NULL;

-- Reminder settings index for tasks with reminders
CREATE INDEX idx_tasks_reminder_enabled ON tasks(id)
WHERE reminder_settings->>'enabled' = 'true';

-- Compound index for reminder queries
CREATE INDEX idx_tasks_reminder_due ON tasks(assigned_to, due_date)
WHERE reminder_settings IS NOT NULL
AND due_date IS NOT NULL;
```

## Data Migration

### Migration Steps (Phase IV → Phase V)

```sql
-- Step 1: Add new columns
ALTER TABLE tasks
ADD COLUMN recurrence_rule JSONB DEFAULT NULL,
ADD COLUMN reminder_settings JSONB DEFAULT NULL;

-- Step 2: Create indexes
CREATE INDEX idx_tasks_recurrence_frequency ON tasks((recurrence_rule->>'frequency'))
WHERE recurrence_rule IS NOT NULL;

CREATE INDEX idx_tasks_reminder_due ON tasks(assigned_to, due_date)
WHERE reminder_settings IS NOT NULL
AND due_date IS NOT NULL;

-- Step 3: Validate
SELECT COUNT(*) FROM tasks
WHERE recurrence_rule IS NOT NULL;  -- Should be 0 initially
```

### Rollback Strategy

```sql
-- Rollback migration
DROP INDEX IF EXISTS idx_tasks_reminder_due;
DROP INDEX IF EXISTS idx_tasks_recurrence_frequency;
ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_settings;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_rule;
```

## Summary

| Entity | Type | Purpose |
|--------|------|---------|
| Task | Database | Extended with recurrence_rule and reminder_settings |
| Recurrence Rule | JSONB | Defines task recurrence pattern |
| Reminder Settings | JSONB | Configures due date reminders |
| Task Event | Kafka | Published on task CRUD operations |
| Reminder Event | Kafka | Published when reminders are due |
