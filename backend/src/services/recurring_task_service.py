"""
Recurring Task Service for User Story 2
Consumes task_completed events and creates next instance of recurring tasks
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid

from src.models.event import EventType, TaskEvent, TaskEventData, RecurrenceRule, RecurrenceFrequency
from src.db.models import Task
from src.db.session import get_db_session

logger = logging.getLogger(__name__)


class RecurringTaskService:
    """
    Service for handling recurring task automation.

    Listens for task_completed events and automatically creates the next
    instance of a recurring task based on its recurrence_rule configuration.
    """

    @staticmethod
    def validate_recurrence_rule(rule: Dict[str, Any]) -> bool:
        """
        Validate a recurrence rule configuration

        Args:
            rule: Recurrence rule dictionary

        Returns:
            True if valid, False otherwise
        """
        try:
            # Required field: frequency
            frequency = rule.get("frequency")
            if not frequency:
                return False

            if frequency not in ["daily", "weekly", "monthly"]:
                return False

            # For weekly: days array is required
            if frequency == "weekly":
                days = rule.get("days")
                if not days or not isinstance(days, list):
                    return False

            # For monthly: month_day is required
            if frequency == "monthly":
                month_day = rule.get("month_day")
                if month_day is None or not (1 <= month_day <= 31):
                    return False

            # Validate end_date if provided
            end_date = rule.get("end_date")
            if end_date:
                try:
                    datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                except ValueError:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating recurrence rule: {e}")
            return False

    @staticmethod
    def calculate_next_occurrence(
        completed_date: datetime,
        recurrence_rule: Dict[str, Any]
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date for a recurring task

        Args:
            completed_date: When the current task was completed
            recurrence_rule: Recurrence configuration

        Returns:
            Next occurrence datetime, or None if recurrence has ended
        """
        try:
            frequency = recurrence_rule.get("frequency")
            interval = recurrence_rule.get("interval", 1)

            # Check if recurrence has ended
            end_date_str = recurrence_rule.get("end_date")
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                if completed_date >= end_date:
                    logger.info(f"Recurrence ended: completed_date {completed_date} >= end_date {end_date}")
                    return None

            # Calculate next occurrence based on frequency
            if frequency == "daily":
                # Add interval days
                next_date = completed_date + timedelta(days=interval)

            elif frequency == "weekly":
                # Find the next occurrence day
                days = recurrence_rule.get("days", [])
                if not days:
                    return None

                # Map day names to weekday numbers (Monday=0, Sunday=6)
                day_map = {
                    "monday": 0,
                    "tuesday": 1,
                    "wednesday": 2,
                    "thursday": 3,
                    "friday": 4,
                    "saturday": 5,
                    "sunday": 6
                }

                # Get target weekdays
                target_weekdays = [day_map.get(d.lower()) for d in days if d.lower() in day_map]
                if not target_weekdays:
                    return None

                # Find next occurrence
                next_date = completed_date + timedelta(days=1)
                max_weeks = 52  # Prevent infinite loop
                weeks_checked = 0

                while next_date.weekday() not in target_weekdays and weeks_checked < max_weeks:
                    next_date += timedelta(days=1)
                    if next_date.weekday() == completed_date.weekday():
                        weeks_checked += 1

                if weeks_checked >= max_weeks:
                    return None

            elif frequency == "monthly":
                # Add interval months, keeping the same day of month
                month_day = recurrence_rule.get("month_day", completed_date.day)

                # Handle edge case where day doesn't exist in target month
                next_date = completed_date
                for _ in range(interval):
                    # Add one month
                    next_date = next_date + relativedelta(months=1)
                    # Adjust day if needed
                    last_day_of_month = (next_date.replace(day=28) + timedelta(days=4)).day
                    next_date = next_date.replace(day=min(month_day, last_day_of_month))

            else:
                logger.warning(f"Unknown recurrence frequency: {frequency}")
                return None

            # Final end_date check
            if end_date_str and next_date > datetime.fromisoformat(end_date_str.replace("Z", "+00:00")):
                return None

            return next_date

        except Exception as e:
            logger.error(f"Error calculating next occurrence: {e}")
            return None

    @staticmethod
    async def handle_task_completed_event(event: TaskEvent) -> bool:
        """
        Handle a task_completed event and create next instance if recurring

        Args:
            event: Task event with event_type=TASK_COMPLETED

        Returns:
            True if next instance was created, False otherwise
        """
        try:
            # Extract recurrence rule from event data
            if not event.data or not event.data.recurrence_rule:
                logger.debug(f"Task {event.task_id} is not recurring, skipping")
                return False

            recurrence_rule = event.data.recurrence_rule

            # Validate recurrence rule
            if not RecurringTaskService.validate_recurrence_rule(recurrence_rule):
                logger.warning(f"Invalid recurrence rule for task {event.task_id}: {recurrence_rule}")
                return False

            # Calculate next occurrence
            completed_date = event.timestamp
            next_occurrence = RecurringTaskService.calculate_next_occurrence(
                completed_date,
                recurrence_rule
            )

            if not next_occurrence:
                logger.info(f"Recurrence ended for task {event.task_id}, no next occurrence")
                return False

            # Create next task instance
            async with get_db_session() as db:
                # Get original task data
                # Note: In a real implementation, we'd fetch from database
                # For now, use event data
                title = event.data.title or "Recurring Task"
                description = event.data.description
                due_date = next_occurrence
                user_id = int(event.user_id) if event.user_id.isdigit() else 1

                new_task = Task(
                    title=title,
                    description=description,
                    due_date=due_date,
                    status="todo",
                    completed=False,
                    user_id=user_id,
                    recurrence_rule=recurrence_rule,
                    # Don't copy reminder_settings - user may want different reminders
                    reminder_settings=event.data.reminder_settings
                )

                db.add(new_task)
                await db.commit()
                await db.refresh(new_task)

                logger.info(
                    f"Created next recurring task instance: {new_task.id} "
                    f"(from {event.task_id}) due at {next_occurrence}"
                )

                # Publish task_created event for the new instance
                from src.services.dapr_client import get_dapr_client
                dapr_client = get_dapr_client()

                new_event = TaskEvent(
                    event_type=EventType.TASK_CREATED,
                    task_id=str(new_task.id),
                    user_id=event.user_id,
                    data=TaskEventData(
                        title=title,
                        description=description,
                        status="todo",
                        recurrence_rule=recurrence_rule,
                        reminder_settings=event.data.reminder_settings,
                        due_date=next_occurrence.isoformat()
                    )
                )

                await dapr_client.publish_task_event(new_event)

            return True

        except Exception as e:
            logger.error(f"Error handling recurring task completion: {e}")
            return False


# Global service instance
_recurring_task_service: Optional[RecurringTaskService] = None


def get_recurring_task_service() -> RecurringTaskService:
    """
    Get or create the global RecurringTaskService instance

    Returns:
        RecurringTaskService instance
    """
    global _recurring_task_service
    if _recurring_task_service is None:
        _recurring_task_service = RecurringTaskService()
    return _recurring_task_service
