"""Quiz retention."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Final

from toisto.persistence.progress_format import RetentionDict

optional_datetime = datetime | None
SKIP_INTERVAL_GROWTH_FACTOR: Final = 5  # Cf. https://artofmemory.com/blog/the-pimsleur-language-method/
SKIP_INTERVAL_WHEN_FIRST_ANSWER_IS_CORRECT: Final = timedelta(days=1)
SKIP_INTERVAL_WHEN_RELATED_QUIZ_IS_ANSWERED_CORRECTLY: Final = timedelta(minutes=5)


@dataclass
class Retention:
    """Class to keep track of the retention of one quiz."""

    start: optional_datetime = None  # Start of the retention period, i.e. the period in which all answers were correct
    end: optional_datetime = None  # End of the retention period, i.e. the datetime of the most recent correct answer
    skip_until: optional_datetime = None  # Don't quiz this again until after the datetime
    count: int = 0  # Number of times the quiz was presented

    def increase(self) -> None:
        """Increase the retention of the quiz after a correct answer."""
        self.count += 1
        self.end = now = datetime.now().astimezone()
        if self.start is None:
            self.start = now
        if self.count == 1:
            self.skip_until = now + SKIP_INTERVAL_WHEN_FIRST_ANSWER_IS_CORRECT
        elif now > self.start:
            self.skip_until = now + (now - self.start) * SKIP_INTERVAL_GROWTH_FACTOR
        else:
            self.skip_until = None

    def pause(self) -> None:
        """Pause this quiz for a brief while because a related quiz was answered correctly."""
        now = datetime.now().astimezone()
        current_skip_until = self.skip_until or now
        self.skip_until = max(current_skip_until, now + SKIP_INTERVAL_WHEN_RELATED_QUIZ_IS_ANSWERED_CORRECTLY)

    def reset(self) -> None:
        """Reset the retention of the quiz after an incorrect answer."""
        self.count += 1
        self.skip_until = self.start = self.end = None

    @property
    def length(self) -> timedelta:
        """Return the length of the retention."""
        return self.end - self.start if self.start and self.end else timedelta()

    def is_silenced(self) -> bool:
        """Return whether the quiz is silenced."""
        return self.skip_until > datetime.now().astimezone() if self.skip_until else False

    def as_dict(self) -> RetentionDict:
        """Return the retention as dict."""
        result = RetentionDict()
        if self.count:
            result["count"] = self.count
        if self.start:
            result["start"] = self.start.isoformat(timespec="seconds")
        if self.end:
            result["end"] = self.end.isoformat(timespec="seconds")
        if self.skip_until:
            result["skip_until"] = self.skip_until.isoformat(timespec="seconds")
        return result

    @classmethod
    def from_dict(cls, retention_dict: RetentionDict) -> Retention:
        """Instantiate a retention from a dict."""
        start = cls.__get_datetime(retention_dict, "start")
        end = cls.__get_datetime(retention_dict, "end")
        skip_until = cls.__get_datetime(retention_dict, "skip_until")
        count = int(retention_dict.get("count", 0))
        return cls(start, end, skip_until, count)

    @staticmethod
    def __get_datetime(retention_dict: RetentionDict, key: str) -> optional_datetime:
        """Get a datetime from the retention dict."""
        if value := retention_dict.get(key):
            dt = datetime.fromisoformat(str(value))
            # Progress used to be saved using naive datetimes (Toisto <= 0.35.0). Apply local timezone if needed:
            return dt.astimezone() if dt.tzinfo is None else dt
        return None
