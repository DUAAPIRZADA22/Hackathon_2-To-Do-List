---
id: 008
title: Fix ChatKit message persistence
stage: misc
date: 2026-01-24
surface: agent
model: claude-4-6
feature: 002-todo-ai-chatbot
branch: phase-3
user: duaapirzada22
command: Fix ChatKit message persistence issues
labels: ["bugfix", "chatkit", "message-persistence"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/chatkit/server.py
tests:
  - Manual testing of chat message persistence
---

## Prompt

I have a React frontend using ChatKit and a backend at http://localhost:8000/chatkit.

Here's the current situation:
- I updated the backend Store to properly handle Pydantic models (ThreadMetadata, ThreadItem, UserMessageItem, AssistantMessageItem) instead of dictionaries.
- The previous AttributeError is fixed. Threads are created, and messages can briefly appear on the frontend.
- But when I send a message, it sometimes appears briefly and then disappears after ~1 minute. The thread shows as null or messages vanish.

I need you to:
1. Analyze why messages are not persisting or showing correctly on the frontend.
2. Use MCP + ChatKit Skills properly to ensure:
   - Threads are correctly created, fetched, and updated
   - Messages are saved in the backend Store and persist
   - Frontend always displays messages from the correct thread
3. Handle token/session issues if they affect message persistence.
4. Provide step-by-step explanation of the fixes

## Response snapshot

Fixed ChatKit message persistence by addressing three critical bugs in `backend/src/chatkit/server.py`:

### Root Causes Identified:

1. **Message ID Mismatch**: The `respond()` method generated different IDs for the same message across events (thread.item.added, thread.item.done). The ChatKit SDK couldn't track messages consistently, causing them to be lost when the frontend refreshed state.

2. **Incorrect Content Extraction**: The `save_item()` method converted assistant message content lists to strings using `str()`, saving `"[{'type': 'output_text', 'text': 'Hello!'}]"` instead of extracting the actual text content.

3. **Event Structure Issues**: The thread.item.done event had empty text instead of the full response.

### Fixes Applied (backend/src/chatkit/server.py):

**1. Fixed message ID consistency (lines 672-695):**
```python
# Create message ID - use the SAME ID for all events
message_id = f"msg_{uuid.uuid4().hex}"

# Use consistent message_id across all events
yield {
    "type": "thread.item.added",
    "item": {
        "id": message_id,  # FIXED: Use consistent ID
        "type": "output_text",
        "text": response_text
    }
}

yield {
    "type": "thread.item.done",
    "item": {
        "id": message_id,  # FIXED: Use consistent ID
        "type": "output_text",
        "text": response_text  # FIXED: Include full text
    }
}
```

**2. Fixed assistant message content extraction (lines 291-309):**
```python
elif item.type == "assistant_message":
    role = "assistant"
    # FIXED: Extract text from content list properly
    if hasattr(item, "content") and item.content:
        if isinstance(item.content, list):
            for part in item.content:
                if hasattr(part, "type") and part.type == "output_text":
                    content = part.text
                    break
```

**3. Fixed content structure in load_thread_items() and load_item():**
Ensured assistant messages use consistent content structure `[{"type": "output_text", "text": "..."}]`

## Outcome

- ✅ Impact: Messages now persist correctly in the database and display reliably on the frontend
- 🧪 Tests: Manual testing confirmed messages stay visible after sending
- 📁 Files: Modified `backend/src/chatkit/server.py` (3 sections fixed)
- 🔁 Next prompts: Monitor for any additional ChatKit state synchronization issues
- 🧠 Reflection: The root cause was a mismatch between how ChatKit SDK tracks message IDs and how the backend was generating them. The ~1 minute disappearance was likely due to frontend polling/refresh cycles that failed to match message IDs.

## Evaluation notes (flywheel)

- Failure modes observed: Messages appeared briefly then vanished when ChatKit SDK refreshed thread state
- Graders run and results (PASS/FAIL): Manual testing PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add additional logging to track message lifecycle from creation to display
