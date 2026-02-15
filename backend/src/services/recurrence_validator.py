"""
Recurrence Rule Validator
Validates recurrence rule configurations for recurring tasks
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class RecurrenceRuleCreate(BaseModel):
    """Schema for creating a recurrence rule"""
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    interval: int = Field(default=1, ge=1, le=365)
    days: Optional[List[str]] = Field(default=None)
    month_day: Optional[int] = Field(default=None, ge=1, le=31)
    end_date: Optional[str] = None
    count: Optional[int] = Field(default=None, ge=1)

    @field_validator('days')
    @classmethod
    def validate_days(cls, v, info):
        if info.data.get('frequency') == 'weekly':
            if not v:
                raise ValueError("days array is required for weekly frequency")
            valid_days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
            if not all(d.lower() in valid_days for d in v):
                raise ValueError(f"Invalid day. Must be one of: {valid_days}")
        return v

    @field_validator('month_day')
    @classmethod
    def validate_month_day(cls, v, info):
        if info.data.get('frequency') == 'monthly':
            if v is None:
                raise ValueError("month_day is required for monthly frequency")
        return v

    @field_validator('end_date', 'count')
    @classmethod
    def validate_end_conditions(cls, v, values):
        # end_date and count are mutually exclusive
        data = values.data if hasattr(values, 'data') else values
        if v is not None and data.get('count') is not None:
            raise ValueError("end_date and count are mutually exclusive")

        # Validate end_date format
        if v and isinstance(v, str):
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("end_date must be a valid ISO 8601 datetime")

        return v


class RecurrenceValidator:
    """
    Validator for recurrence rule configurations
    """

    VALID_FREQUENCIES = ["daily", "weekly", "monthly"]
    VALID_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    @staticmethod
    def validate(rule: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a recurrence rule

        Args:
            rule: Recurrence rule dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check frequency
            frequency = rule.get("frequency")
            if not frequency:
                return False, "frequency is required"

            if frequency not in RecurrenceValidator.VALID_FREQUENCIES:
                return False, f"Invalid frequency: {frequency}. Must be one of {RecurrenceValidator.VALID_FREQUENCIES}"

            # Validate interval
            interval = rule.get("interval", 1)
            if not isinstance(interval, int) or interval < 1 or interval > 365:
                return False, "interval must be an integer between 1 and 365"

            # Validate based on frequency
            if frequency == "weekly":
                days = rule.get("days")
                if not days or not isinstance(days, list):
                    return False, "days array is required for weekly frequency"

                invalid_days = [d for d in days if d.lower() not in RecurrenceValidator.VALID_DAYS]
                if invalid_days:
                    return False, f"Invalid days: {invalid_days}. Must be one of {RecurrenceValidator.VALID_DAYS}"

            elif frequency == "monthly":
                month_day = rule.get("month_day")
                if month_day is None:
                    return False, "month_day is required for monthly frequency"
                if not isinstance(month_day, int) or month_day < 1 or month_day > 31:
                    return False, "month_day must be an integer between 1 and 31"

            # Validate end conditions
            end_date = rule.get("end_date")
            count = rule.get("count")

            if end_date and count:
                return False, "end_date and count are mutually exclusive"

            if end_date:
                try:
                    datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                except ValueError:
                    return False, "end_date must be a valid ISO 8601 datetime"

            if count is not None:
                if not isinstance(count, int) or count < 1:
                    return False, "count must be a positive integer"

            return True, None

        except Exception as e:
            logger.error(f"Error validating recurrence rule: {e}")
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def validate_and_create(rule: Dict[str, Any]) -> tuple[bool, Optional[RecurrenceRuleCreate], Optional[str]]:
        """
        Validate and create a RecurrenceRuleCreate object

        Args:
            rule: Recurrence rule dictionary

        Returns:
            Tuple of (is_valid, recurrence_rule_object, error_message)
        """
        is_valid, error_message = RecurrenceValidator.validate(rule)
        if not is_valid:
            return False, None, error_message

        try:
            recurrence_rule = RecurrenceRuleCreate(**rule)
            return True, recurrence_rule, None
        except Exception as e:
            return False, None, str(e)


# Global validator instance
_recurrence_validator: Optional[RecurrenceValidator] = None


def get_recurrence_validator() -> RecurrenceValidator:
    """
    Get or create the global RecurrenceValidator instance

    Returns:
        RecurrenceValidator instance
    """
    global _recurrence_validator
    if _recurrence_validator is None:
        _recurrence_validator = RecurrenceValidator()
    return _recurrence_validator
