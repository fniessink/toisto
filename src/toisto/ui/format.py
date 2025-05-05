"""Formatting."""

from datetime import datetime, timedelta


def format_duration(duration: timedelta) -> str:
    """Format the duration in a human friendly way."""
    if duration.days > 1:
        return f"{duration.days} days"
    seconds = duration.seconds + (24 * 3600 if duration.days else 0)
    if seconds >= 1.5 * 3600:  # 1.5 hours
        hours = round(seconds / 3600)
        return f"{hours} hours"
    if seconds >= 1.5 * 60:  # 1.5 minutes
        minutes = round(seconds / 60)
        return f"{minutes} minutes"
    return f"{seconds} seconds"


def format_datetime(date_time: datetime) -> str:
    """Return a human readable version of the datetime."""
    return date_time.replace(tzinfo=None).isoformat(sep=" ", timespec="minutes")
