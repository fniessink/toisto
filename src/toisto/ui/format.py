"""Formatting."""

from collections.abc import Sequence
from datetime import datetime, timedelta

from toisto.model.language.label import Label
from toisto.ui.dictionary import linkified

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
    for unit, seconds_per_unit in (
        ("year", SECONDS_PER_YEAR),
        ("month", SECONDS_PER_MONTH),
        ("week", SECONDS_PER_WEEK),
        ("day", SECONDS_PER_DAY),
        ("hour", SECONDS_PER_HOUR),
        ("minute", SECONDS_PER_MINUTE),
    ):
        if (nr_units := round(seconds / seconds_per_unit)) > 1:
            return f"{nr_units} {unit}s"
    return f"{round(seconds)} second{'' if seconds == 1 else 's'}"


def format_datetime(date_time: datetime) -> str:
    """Return a human readable version of the datetime."""
    return date_time.replace(tzinfo=None).isoformat(sep=" ", timespec="minutes")


def quoted(text: str, quote: str = "'") -> str:
    """Return a quoted version of the text."""
    return f"{quote}{text}{quote}"


def punctuated(text: str) -> str:
    """Return the text with an added period, if it has no punctuation yet."""
    return text if set(text[-2:]) & set(Label.END_OF_SENTENCE_PUNCTUATION) else f"{text}."


def enumerated(*texts: str, min_enumeration_length: int = 2) -> str:
    """Return an enumerated version of the text."""
    match len(texts):
        case length if length > min_enumeration_length:
            comma_separated_texts = ", ".join(texts[:-1]) + ","
            return enumerated(comma_separated_texts, texts[-1])
        case length if length == min_enumeration_length:
            return " and ".join(texts)
        case length if length == 1:
            return texts[0]
        case _:
            return ""


def wrapped(text: str, *, style: str, postfix: str = "\n") -> str:
    """Return the text wrapped with the style."""
    return f"[{style}]{text}[/{style}]{postfix}"


def linkified_and_enumerated(*texts: str) -> str:
    """Return a linkified and enumerated version of the texts."""
    return enumerated(*(f"{quoted(linkified(text))}" for text in texts))


def bulleted_list(label: str, items: Sequence[str], style: str, *, bullet: str = "-") -> str:
    """Create a bulleted list of the items."""
    items = [punctuated(item) for item in items]
    match len(items):
        case 0:
            return ""
        case 1:
            text = f"{label}: {items[0]}"
        case _:
            text = f"{label}s:\n" + "\n".join(f"{bullet} {item}" for item in items)
    return wrapped(text, style=style)
