"""
Dapr subscription API routes
Handles event subscriptions from Dapr for event-driven microservices
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from src.models.event import (
    DaprSubscriptionRequest,
    DaprSubscriptionResponse,
    EventType,
    ReminderType,
    TaskEvent,
    ReminderEvent
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dapr", tags=["dapr"])


# Dapr health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for Dapr sidecar"""
    return {"status": "healthy", "service": "actionmindai-backend"}


# Dapr subscribe endpoint - Returns list of subscriptions
@router.get("/subscribe")
async def get_subscriptions() -> List[Dict[str, Any]]:
    """
    Dapr uses this endpoint to discover subscriptions
    Returns a list of topic subscriptions for this service
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "dapr/events/task-events",
            "metadata": {
                "service": "backend",
                "description": "Task CRUD events"
            }
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "dapr/events/reminders",
            "metadata": {
                "service": "backend",
                "description": "Due date reminder events"
            }
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "time-logged",
            "route": "dapr/events/time-logged",
            "metadata": {
                "service": "backend",
                "description": "Time logging events (future)"
            }
        }
    ]

    logger.info("Dapr subscription request received")
    return subscriptions


# Task events subscription handler
@router.post("/events/task-events")
async def handle_task_event(request: Request, background_tasks: BackgroundTasks):
    """
    Handle task events from Kafka via Dapr
    This endpoint receives events published to the task-events topic

    Routes events to appropriate services:
    - RecurringTaskService: handles task_completed events
    - RealtimeSyncService: handles all task events (future)
    """
    try:
        # Get event data from request body
        event_data = await request.json()

        logger.info(f"Received task event: {event_data.get('event_type')} for task {event_data.get('task_id')}")

        # Validate event structure
        event_type = event_data.get("event_type")
        task_id = event_data.get("task_id")

        if not event_type or not task_id:
            raise HTTPException(status_code=400, detail="Invalid event: missing event_type or task_id")

        # Process task_completed events for recurring tasks (T038-T039)
        if event_type == "task_completed":
            try:
                from src.services.recurring_task_service import get_recurring_task_service
                from src.models.event import TaskEvent

                # Parse event
                task_event = TaskEvent(
                    event_type=EventType.TASK_COMPLETED,
                    task_id=task_id,
                    user_id=event_data.get("user_id"),
                    timestamp=event_data.get("timestamp"),
                    correlation_id=event_data.get("correlation_id"),
                    project_id=event_data.get("project_id")
                )

                # Add data if present
                if event_data.get("data"):
                    from src.models.event import TaskEventData
                    task_event.data = TaskEventData(**event_data["data"])

                # Handle in background task for non-blocking processing
                service = get_recurring_task_service()
                background_tasks.add_task(service.handle_task_completed_event, task_event)

                logger.info(f"Task completed event routed to RecurringTaskService: {task_id}")

            except Exception as e:
                logger.error(f"Error processing recurring task: {e}")
                # Continue - don't block on recurring task errors

        logger.info(f"Task event processed successfully: {event_type}")

        return {"status": "success", "message": "Event processed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        # Return success to Dapr even on error to avoid redelivery
        # (events are at-least-once, so idempotency is handled by consumers)
        return {"status": "error", "message": str(e)}


# Reminder events subscription handler
@router.post("/events/reminders")
async def handle_reminder_event(request: Request):
    """
    Handle reminder events from Kafka via Dapr
    This endpoint receives events published to the reminders topic
    """
    try:
        # Get event data from request body
        event_data = await request.json()

        logger.info(f"Received reminder event: {event_data.get('reminder_type')} for task {event_data.get('task_id')}")

        # Validate event structure
        reminder_type = event_data.get("reminder_type")
        task_id = event_data.get("task_id")

        if not reminder_type or not task_id:
            raise HTTPException(status_code=400, detail="Invalid event: missing reminder_type or task_id")

        # Process reminder event
        # The NotificationService handles the actual notification sending

        logger.info(f"Reminder event processed successfully: {reminder_type}")

        return {"status": "success", "message": "Event processed"}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        return {"status": "error", "message": str(e)}


# Time logged events subscription handler (future feature)
@router.post("/events/time-logged")
async def handle_time_logged_event(request: Request):
    """
    Handle time logged events from Kafka via Dapr
    This endpoint receives events published to the time-logged topic
    """
    try:
        event_data = await request.json()
        logger.info(f"Received time-logged event: {event_data}")

        return {"status": "success", "message": "Event processed"}

    except Exception as e:
        logger.error(f"Error processing time-logged event: {e}")
        return {"status": "error", "message": str(e)}


# Dapr topic subscription confirmation
@router.post("/subscribe/confirm")
async def confirm_subscription(sub: DaprSubscriptionRequest) -> DaprSubscriptionResponse:
    """
    Confirm subscription to a topic
    Called by Dapr to validate subscription
    """
    valid_topics = ["task-events", "reminders", "time-logged"]

    if sub.topic in valid_topics:
        logger.info(f"Subscription confirmed for topic: {sub.topic}")
        return DaprSubscriptionResponse(success=True, message=f"Subscribed to {sub.topic}")
    else:
        logger.warning(f"Invalid subscription request for topic: {sub.topic}")
        return DaprSubscriptionResponse(success=False, message=f"Unknown topic: {sub.topic}")


# Event publishing status endpoint
@router.get("/events/status")
async def get_event_status():
    """
    Get event publishing statistics
    """
    from src.services.dapr_client import get_dapr_client

    dapr_client = get_dapr_client()
    stats = dapr_client.get_stats()

    return {
        "status": "operational",
        "pubsub_name": "kafka-pubsub",
        "statistics": stats
    }
