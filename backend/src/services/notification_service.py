"""
Notification Service for User Story 3
Consumes reminder events and sends email notifications
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from email.utils import formatdate

from src.models.event import ReminderEvent, ReminderType, ReminderEventData
from src.db.models import Task
from src.db.session import get_db_session

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for handling due date reminder notifications.

    Sends email notifications for tasks approaching their due date
    or already overdue.
    """

    # Track sent reminders for deduplication (T047)
    _sent_reminders: Dict[str, datetime] = {}

    @staticmethod
    def _get_reminder_key(task_id: str, reminder_time: str) -> str:
        """Generate a unique key for reminder deduplication"""
        return f"{task_id}:{reminder_time}"

    @staticmethod
    def is_reminder_sent(task_id: str, reminder_time: str, within_hours: int = 24) -> bool:
        """
        Check if a reminder has already been sent recently

        Args:
            task_id: Task ID
            reminder_time: Reminder time string (e.g., "1h", "1d")
            within_hours: Hours to consider as duplicate (default: 24)

        Returns:
            True if reminder was sent recently, False otherwise
        """
        key = NotificationService._get_reminder_key(task_id, reminder_time)
        sent_at = NotificationService._sent_reminders.get(key)

        if not sent_at:
            return False

        # Check if reminder was sent within the deduplication window
        time_since_sent = datetime.utcnow() - sent_at
        return time_since_sent.total_seconds() < (within_hours * 3600)

    @staticmethod
    def mark_reminder_sent(task_id: str, reminder_time: str):
        """Mark a reminder as sent to prevent duplicates"""
        key = NotificationService._get_reminder_key(task_id, reminder_time)
        NotificationService._sent_reminders[key] = datetime.utcnow()

        # Clean up old entries
        cutoff = datetime.utcnow() - timedelta(hours=48)
        NotificationService._sent_reminders = {
            k: v for k, v in NotificationService._sent_reminders.items()
            if v > cutoff
        }

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email notification

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Import SendGrid (T046)
            import os
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content

            api_key = os.getenv("SENDGRID_API_KEY")
            if not api_key:
                logger.warning("SENDGRID_API_KEY not configured, skipping email send")
                return False

            sg = SendGridAPIClient(api_key)

            from_email = Email(os.getenv("SENDGRID_FROM_EMAIL", "noreply@actionmind.ai"))
            to_email_obj = To(to_email)

            # Create email content
            mail = Mail(from_email, to_email, subject)

            # Add HTML content
            mail.add_content(Content("text/html", html_body))

            # Add text content if provided
            if text_body:
                mail.add_content(Content("text/plain", text_body))

            # Send email
            response = sg.send(mail)

            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.warning(f"Email send failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    @staticmethod
    def _render_reminder_email(
        task_title: str,
        due_date: datetime,
        reminder_message: str
    ) -> tuple[str, str]:
        """
        Render HTML and plain text email for reminder

        Returns:
            Tuple of (html_body, text_body)
        """
        due_date_str = due_date.strftime("%B %d, %Y at %I:%M %p")

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9fafb; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                .task-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .due-date {{ color: #DC2626; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Task Due Soon</h1>
                </div>
                <div class="content">
                    <p class="task-title">📋 {task_title}</p>
                    <p>{reminder_message}</p>
                    <p>Due: <span class="due-date">{due_date_str}</span></p>
                    <p>Make sure to complete your task on time!</p>
                </div>
                <div class="footer">
                    <p>ActionMind AI - Your Smart Task Manager</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
⏰ TASK DUE SOON

Task: {task_title}
{reminder_message}
Due: {due_date_str}

Make sure to complete your task on time!

---
ActionMind AI - Your Smart Task Manager
        """

        return html_body, text_body

    @staticmethod
    async def handle_reminder_event(event: ReminderEvent, user_email: str) -> bool:
        """
        Handle a reminder event and send notification

        Args:
            event: Reminder event
            user_email: User's email address

        Returns:
            True if notification was sent, False otherwise
        """
        try:
            # Check for duplicate reminder (T047)
            reminder_time = event.data.reminder_time if event.data else "unknown"
            if NotificationService.is_reminder_sent(event.task_id, reminder_time):
                logger.debug(f"Reminder already sent recently for task {event.task_id}, skipping")
                return False

            # Render email
            due_date = datetime.fromisoformat(event.due_date.replace("Z", "+00:00"))
            html_body, text_body = NotificationService._render_reminder_email(
                event.data.task_title,
                due_date,
                event.data.message
            )

            # Send email
            subject = f"⏰ Reminder: {event.data.task_title}"
            sent = await NotificationService.send_email(
                to_email=user_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )

            if sent:
                # Mark as sent to prevent duplicates
                NotificationService.mark_reminder_sent(event.task_id, reminder_time)
                logger.info(f"Reminder notification sent for task {event.task_id}")
                return True
            else:
                logger.warning(f"Failed to send reminder notification for task {event.task_id}")
                return False

        except Exception as e:
            logger.error(f"Error handling reminder event: {e}")
            return False

    @staticmethod
    async def cancel_reminders(task_id: str):
        """
        Cancel pending reminders for a task (T048)
        Called when a task is completed or deleted

        Args:
            task_id: Task ID
        """
        # Remove from sent reminders cache
        keys_to_remove = [
            k for k in NotificationService._sent_reminders.keys()
            if k.startswith(f"{task_id}:")
        ]
        for key in keys_to_remove:
            del NotificationService._sent_reminders[key]

        logger.info(f"Cancelled reminders for task {task_id}")


# Global service instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """
    Get or create the global NotificationService instance

    Returns:
        NotificationService instance
    """
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
