"""Formatting."""

from datetime import datetime, timedelta

DAYS_PER_YEAR = 365.25
MONTHS_PER_YEAR = 12
DAYS_PER_WEEK = 7
HOURS_PER_DAY = 24
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
DAYS_PER_MONTH = DAYS_PER_YEAR / MONTHS_PER_YEAR
SECONDS_PER_HOUR = MINUTES_PER_HOUR * SECONDS_PER_MINUTE
SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY
SECONDS_PER_WEEK = SECONDS_PER_DAY * DAYS_PER_WEEK
SECONDS_PER_MONTH = SECONDS_PER_DAY * DAYS_PER_MONTH
SECONDS_PER_YEAR = SECONDS_PER_DAY * DAYS_PER_YEAR


def format_duration(duration: timedelta) -> str:
    """Format the duration in a human friendly way.

    Uses a threshold of > 1 (not >= 1) to keep durations in their natural unit.

    Examples:
    - 18 months → "18 months" (not "2 years")
    - 10 days → "10 days" (not "1 week")
    - 25 hours → "25 hours" (not "1 day")

    Smallest unit used is second, largest unit is year.

    """
    seconds = abs(duration).total_seconds()
    if (years := round(seconds / SECONDS_PER_YEAR)) > 1:
        formatted_duration = f"{years} years"
    elif (months := round(seconds / SECONDS_PER_MONTH)) > 1:
        formatted_duration = f"{months} months"
    elif (weeks := round(seconds / SECONDS_PER_WEEK)) > 1:
        formatted_duration = f"{weeks} weeks"
    elif (days := round(seconds / SECONDS_PER_DAY)) > 1:
        formatted_duration = f"{days} days"
    elif (hours := round(seconds / SECONDS_PER_HOUR)) > 1:
        formatted_duration = f"{hours} hours"
    elif (minutes := round(seconds / SECONDS_PER_MINUTE)) > 1:
        formatted_duration = f"{minutes} minutes"
    else:
        formatted_duration = f"{round(seconds)} second{'' if seconds == 1 else 's'}"
    return formatted_duration


def format_datetime(date_time: datetime) -> str:
    """Return a human readable version of the datetime."""
    return date_time.replace(tzinfo=None).isoformat(sep=" ", timespec="minutes")
