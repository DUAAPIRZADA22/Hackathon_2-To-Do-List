"""
Reminder Scheduler Service for User Story 3
Periodically scans for tasks with due dates and publishes reminder events
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dateutil import parser as date_parser

from src.models.event import ReminderEvent, ReminderType, ReminderEventData
from src.db.models import Task
from src.db.session import get_db_session
from src.services.dapr_client import get_dapr_client

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Scheduler for checking due dates and publishing reminder events.

    Runs periodically (typically every 5 minutes via Dapr cron binding)
    to scan for tasks with due dates approaching or overdue.
    """

    # Parse reminder time string (e.g., "1h", "1d", "15m")
    @staticmethod
    def parse_reminder_time(time_str: str) -> timedelta:
        """
        Parse a reminder time string into a timedelta

        Args:
            time_str: Time string like "1h", "1d", "15m", "1w"

        Returns:
            Timedelta representing the time before due date
        """
        time_str = time_str.lower().strip()

        # Extract number and unit
        import re
        match = re.match(r'^(\d+)([mhdw])$', time_str)
        if not match:
            raise ValueError(f"Invalid reminder time format: {time_str}")

        value = int(match.group(1))
        unit = match.group(2)

        # Map units to timedelta parameters
        unit_map = {
            'm': ('minutes', value),
            'h': ('hours', value),
            'd': ('days', value),
            'w': ('weeks', value)
        }

        unit_name, unit_value = unit_map[unit]
        return timedelta(**{unit_name: unit_value})

    @staticmethod
    async def get_tasks_with_reminders() -> List[Task]:
        """
        Fetch all tasks that have reminder settings configured

        Returns:
            List of tasks with reminder_settings
        """
        async with get_db_session() as db:
            from sqlalchemy import select

            # Query tasks with reminder_settings
            query = select(Task).where(
                Task.reminder_settings.isnot(None)
            ).where(
                # Only active tasks
                Task.completed == False
            ).where(
                # Must have a due date
                Task.due_date.isnot(None)
            )

            result = await db.execute(query)
            return result.scalars().all()

    @staticmethod
    def should_send_reminder(task: Task, current_time: datetime) -> List[str]:
        """
        Check if a task should have reminders sent now

        Args:
            task: Task to check
            current_time: Current datetime

        Returns:
            List of reminder times to send (e.g., ["1h", "1d"])
        """
        if not task.reminder_settings:
            return []

        # Check if reminders are enabled
        if not task.reminder_settings.get('enabled', True):
            return []

        reminder_times = task.reminder_settings.get('reminder_times', [])
        if not reminder_times:
            return []

        due_date = task.due_date
        if not due_date:
            return []

        # Ensure timezone-aware comparison
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=current_time.tzinfo)

        times_to_send = []

        for reminder_time_str in reminder_times:
            try:
                reminder_delta = ReminderScheduler.parse_reminder_time(reminder_time_str)
                reminder_time = due_date - reminder_delta

                # Check if current time is past the reminder time
                # But within the reminder window (to avoid sending old reminders)
                window_start = reminder_time
                window_end = reminder_time + timedelta(minutes=10)  # 10-minute window

                if window_start <= current_time <= window_end:
                    times_to_send.append(reminder_time_str)

            except Exception as e:
                logger.warning(f"Error parsing reminder time {reminder_time_str}: {e}")

        return times_to_send

    @staticmethod
    def is_overdue(task: Task, current_time: datetime) -> bool:
        """
        Check if a task is overdue

        Args:
            task: Task to check
            current_time: Current datetime

        Returns:
            True if task is overdue, False otherwise
        """
        if not task.due_date:
            return False

        due_date = task.due_date
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=current_time.tzinfo)

        return current_time > due_date and not task.completed

    @staticmethod
    async def scan_and_publish_reminders() -> int:
        """
        Scan all tasks and publish reminder events for those due soon

        Returns:
            Number of reminder events published
        """
        logger.info("Starting reminder scan")
        current_time = datetime.utcnow()
        events_published = 0

        try:
            # Get all tasks with reminder settings
            tasks = await ReminderScheduler.get_tasks_with_reminders()

            for task in tasks:
                try:
                    # Check for due_approaching reminders
                    reminder_times = ReminderScheduler.should_send_reminder(task, current_time)

                    for reminder_time in reminder_times:
                        # Parse and format the reminder time
                        reminder_delta = ReminderScheduler.parse_reminder_time(reminder_time)

                        # Create appropriate message
                        if reminder_delta.total_seconds() < 3600:
                            message = f"Task is due in {reminder_delta.seconds // 60} minutes"
                        elif reminder_delta.total_seconds() < 86400:
                            hours = reminder_delta.total_seconds() // 3600
                            message = f"Task is due in {hours} hour{'s' if hours > 1 else ''}"
                        else:
                            days = reminder_delta.total_seconds() // 86400
                            message = f"Task is due in {days} day{'s' if days > 1 else ''}"

                        # Publish reminder event (T051)
                        event = ReminderEvent(
                            reminder_type=ReminderType.DUE_APPROACHING,
                            task_id=str(task.id),
                            due_date=task.due_date.isoformat(),
                            user_id=str(task.user_id),
                            data=ReminderEventData(
                                task_title=task.title,
                                message=message,
                                reminder_time=reminder_time
                            )
                        )

                        dapr_client = get_dapr_client()
                        await dapr_client.publish_reminder_event(event)
                        events_published += 1
                        logger.info(f"Published due_approaching reminder for task {task.id} ({reminder_time})")

                    # Check for overdue tasks
                    if ReminderScheduler.is_overdue(task, current_time):
                        event = ReminderEvent(
                            reminder_type=ReminderType.OVERDUE,
                            task_id=str(task.id),
                            due_date=task.due_date.isoformat(),
                            user_id=str(task.user_id),
                            data=ReminderEventData(
                                task_title=task.title,
                                message="This task is now overdue!",
                                reminder_time="overdue"
                            )
                        )

                        dapr_client = get_dapr_client()
                        await dapr_client.publish_reminder_event(event)
                        events_published += 1
                        logger.info(f"Published overdue reminder for task {task.id}")

                except Exception as e:
                    logger.error(f"Error processing reminders for task {task.id}: {e}")

            logger.info(f"Reminder scan complete: {events_published} events published")
            return events_published

        except Exception as e:
            logger.error(f"Error during reminder scan: {e}")
            return events_published


# Global scheduler instance
_reminder_scheduler: Optional[ReminderScheduler] = None


def get_reminder_scheduler() -> ReminderScheduler:
    """
    Get or create the global ReminderScheduler instance

    Returns:
        ReminderScheduler instance
    """
    global _reminder_scheduler
    if _reminder_scheduler is None:
        _reminder_scheduler = ReminderScheduler()
    return _reminder_scheduler
