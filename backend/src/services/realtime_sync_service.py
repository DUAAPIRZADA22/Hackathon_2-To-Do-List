"""
Real-Time Sync Service for User Story 4
Consumes all task events and broadcasts to WebSocket clients
"""

import logging
from typing import Dict, Any
from datetime import datetime

from src.models.event import TaskEvent, EventType
from src.api.websocket import get_connection_manager

logger = logging.getLogger(__name__)


class RealtimeSyncService:
    """
    Service for real-time task update synchronization.

    Consumes all task events from Kafka and broadcasts them
    to connected WebSocket/SSE clients.
    """

    @staticmethod
    def format_event_message(event: TaskEvent) -> Dict[str, Any]:
        """
        Format a task event for WebSocket/SSE broadcast

        Args:
            event: Task event

        Returns:
            Formatted message dictionary
        """
        return {
            "type": "task_update",
            "event_type": event.event_type.value,
            "task_id": event.task_id,
            "user_id": event.user_id,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data.model_dump() if event.data else None,
            "correlation_id": event.correlation_id
        }

    @staticmethod
    async def handle_task_event(event: TaskEvent) -> bool:
        """
        Handle a task event and broadcast to relevant users

        Args:
            event: Task event

        Returns:
            True if broadcast was successful, False otherwise
        """
        try:
            manager = get_connection_manager()

            # Format message
            message = RealtimeSyncService.format_event_message(event)

            # Get user ID as integer
            try:
                user_id = int(event.user_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id in event: {event.user_id}")
                return False

            # Broadcast to user's connections (T060-T061)
            await manager.broadcast_to_user(user_id, message)

            logger.info(
                f"Broadcast task event {event.event_type.value} "
                f"to user {user_id} (task {event.task_id})"
            )

            return True

        except Exception as e:
            logger.error(f"Error handling task event for realtime sync: {e}")
            return False

    @staticmethod
    async def handle_reminder_event(event: Dict[str, Any]) -> bool:
        """
        Handle a reminder event and broadcast to user

        Args:
            event: Reminder event dictionary

        Returns:
            True if broadcast was successful, False otherwise
        """
        try:
            manager = get_connection_manager()

            # Format message for reminders
            message = {
                "type": "reminder",
                "reminder_type": event.get("reminder_type"),
                "task_id": event.get("task_id"),
                "user_id": event.get("user_id"),
                "timestamp": event.get("timestamp"),
                "data": event.get("data")
            }

            # Get user ID
            user_id_str = event.get("user_id")
            if not user_id_str:
                logger.warning("Reminder event missing user_id")
                return False

            try:
                user_id = int(user_id_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id in reminder event: {user_id_str}")
                return False

            # Broadcast to user
            await manager.broadcast_to_user(user_id, message)

            logger.info(f"Broadcast reminder to user {user_id} (task {event.get('task_id')})")

            return True

        except Exception as e:
            logger.error(f"Error handling reminder event for realtime sync: {e}")
            return False

    @staticmethod
    async def broadcast_system_message(user_id: int, message: str, level: str = "info"):
        """
        Broadcast a system message to a user

        Args:
            user_id: User ID
            message: Message content
            level: Message level (info, warning, error)
        """
        manager = get_connection_manager()

        await manager.broadcast_to_user(user_id, {
            "type": "system_message",
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })


# Global service instance
_realtime_sync_service = None


def get_realtime_sync_service() -> RealtimeSyncService:
    """
    Get or create the global RealtimeSyncService instance

    Returns:
        RealtimeSyncService instance
    """
    global _realtime_sync_service
    if _realtime_sync_service is None:
        _realtime_sync_service = RealtimeSyncService()
    return _realtime_sync_service
