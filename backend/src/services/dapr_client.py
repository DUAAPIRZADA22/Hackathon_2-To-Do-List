"""
Dapr Client for event publishing with retry logic and queuing
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import json

from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem

from src.models.event import TaskEvent, ReminderEvent

logger = logging.getLogger(__name__)


class DaprEventClient:
    """
    Dapr client wrapper for event publishing with retry logic and queuing
    """

    def __init__(
        self,
        pubsub_name: str = "kafka-pubsub",
        max_retries: int = 3,
        retry_delay_ms: int = 1000,
        queue_size: int = 1000,
        enabled: bool = True
    ):
        """
        Initialize Dapr event client

        Args:
            pubsub_name: Name of the pub/sub component (default: kafka-pubsub)
            max_retries: Maximum number of retry attempts
            retry_delay_ms: Initial delay between retries in milliseconds (exponential backoff)
            queue_size: Maximum size of in-memory event queue for Kafka unavailability
            enabled: Whether Dapr is enabled (can be disabled for local development)
        """
        self.pubsub_name = pubsub_name
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms
        self.enabled = enabled

        # In-memory queue for events when Kafka is unavailable
        self._event_queue: deque = deque(maxlen=queue_size)
        self._queue_lock = asyncio.Lock()

        # Track publishing statistics
        self._publish_count = 0
        self._failure_count = 0
        self._retry_count = 0

    def _should_retry(self, attempt: int, error: Exception) -> bool:
        """
        Determine if a request should be retried

        Args:
            attempt: Current attempt number
            error: The exception that occurred

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False

        # Retry on connection errors and timeouts
        error_str = str(error).lower()
        retryable_errors = [
            "connection",
            "timeout",
            "unavailable",
            "temporary",
            "network",
            "broker"
        ]

        return any(err in error_str for err in retryable_errors)

    async def _publish_with_retry(
        self,
        topic_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish event with exponential backoff retry

        Args:
            topic_name: Kafka topic name
            data: Event data to publish
            metadata: Optional metadata for the event

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping event publish to {topic_name}")
            return True

        data_json = json.dumps(data)

        for attempt in range(self.max_retries):
            try:
                with DaprClient() as dapr_client:
                    # Publish event via Dapr
                    dapr_client.publish_event(
                        pubsub_name=self.pubsub_name,
                        topic_name=topic_name,
                        data=data_json,
                        metadata=metadata or {}
                    )

                self._publish_count += 1
                logger.info(f"Published event to {topic_name} (attempt {attempt + 1})")
                return True

            except Exception as e:
                logger.warning(f"Failed to publish to {topic_name} (attempt {attempt + 1}): {e}")
                self._failure_count += 1

                if self._should_retry(attempt, e):
                    self._retry_count += 1
                    # Exponential backoff: 2^attempt * retry_delay_ms
                    delay_ms = (2 ** attempt) * self.retry_delay_ms
                    await asyncio.sleep(delay_ms / 1000)
                    continue
                else:
                    logger.error(f"Failed to publish to {topic_name} after {attempt + 1} attempts: {e}")
                    return False

        return False

    async def queue_event(
        self,
        topic_name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ):
        """
        Queue an event for later retry when Kafka is unavailable

        Args:
            topic_name: Kafka topic name
            data: Event data to queue
            metadata: Optional metadata for the event
        """
        async with self._queue_lock:
            if self._event_queue.maxlen > 0 and len(self._event_queue) >= self._event_queue.maxlen:
                logger.warning(f"Event queue full ({self._event_queue.maxlen}), dropping oldest event")
                self._event_queue.popleft()

            queued_event = {
                "topic_name": topic_name,
                "data": data,
                "metadata": metadata,
                "queued_at": datetime.utcnow().isoformat()
            }
            self._event_queue.append(queued_event)
            logger.info(f"Queued event to {topic_name}. Queue size: {len(self._event_queue)}")

    async def process_queue(self, batch_size: int = 10) -> int:
        """
        Process queued events and retry publishing

        Args:
            batch_size: Number of events to process in one batch

        Returns:
            Number of successfully processed events
        """
        processed = 0

        async with self._queue_lock:
            batch = min(batch_size, len(self._event_queue))

        for _ in range(batch):
            async with self._queue_lock:
                if not self._event_queue:
                    break
                queued_event = self._event_queue.popleft()

            # Retry publishing the queued event
            success = await self._publish_with_retry(
                topic_name=queued_event["topic_name"],
                data=queued_event["data"],
                metadata=queued_event.get("metadata")
            )

            if success:
                processed += 1
            else:
                # Re-queue if failed
                await self.queue_event(
                    topic_name=queued_event["topic_name"],
                    data=queued_event["data"],
                    metadata=queued_event.get("metadata")
                )

        if processed > 0:
            logger.info(f"Processed {processed} queued events. Queue size: {len(self._event_queue)}")

        return processed

    async def publish_task_event(self, event: TaskEvent) -> bool:
        """
        Publish a task event to Kafka

        Args:
            event: TaskEvent to publish

        Returns:
            True if published successfully, False otherwise
        """
        # Publish to task-events topic
        success = await self._publish_with_retry(
            topic_name="task-events",
            data=event.to_kafka_message(),
            metadata={"event_type": event.event_type.value}
        )

        # Queue for retry if failed
        if not success:
            await self.queue_event(
                topic_name="task-events",
                data=event.to_kafka_message(),
                metadata={"event_type": event.event_type.value}
            )

        return success

    async def publish_reminder_event(self, event: ReminderEvent) -> bool:
        """
        Publish a reminder event to Kafka

        Args:
            event: ReminderEvent to publish

        Returns:
            True if published successfully, False otherwise
        """
        # Publish to reminders topic
        success = await self._publish_with_retry(
            topic_name="reminders",
            data=event.to_kafka_message(),
            metadata={"reminder_type": event.reminder_type.value}
        )

        # Queue for retry if failed
        if not success:
            await self.queue_event(
                topic_name="reminders",
                data=event.to_kafka_message(),
                metadata={"reminder_type": event.reminder_type.value}
            )

        return success

    def get_stats(self) -> Dict[str, Any]:
        """
        Get publishing statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "publish_count": self._publish_count,
            "failure_count": self._failure_count,
            "retry_count": self._retry_count,
            "queue_size": len(self._event_queue),
            "queue_capacity": self._event_queue.maxlen
        }


# Global Dapr client instance
_dapr_client: Optional[DaprEventClient] = None


def get_dapr_client() -> DaprEventClient:
    """
    Get or create the global Dapr client instance

    Returns:
        DaprEventClient instance
    """
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprEventClient()
    return _dapr_client
