"""Quiz retention."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timedelta


optional_datetime = datetime | None
SKIP_INTERVAL_GROWTH_FACTOR = 5  # Cf. https://artofmemory.com/blog/the-pimsleur-language-method/


@dataclass
class Retention:
    """Class to keep track of the retention of one quiz."""

    start: optional_datetime = None  # Start of the retention period, i.e. the period in which all answers were correct
    end: optional_datetime = None  # End of the retention period, i.e. the datetime of the most recent correct answer
    skip_until: optional_datetime = None  # Don't quiz this again until after the datetime
    count: int = 0  # Number of times the quiz was presented

    def update(self, correct: bool) -> None:
        """Update the retention of the quiz."""
        now = datetime.now()
        self.count += 1
        if correct:
            self.end = now
            if self.start is None:
                self.start = now
            if self.count == 1:
                self.skip_until = now + timedelta(days=1)  # User already knows the answer, skip ahead
            elif now > self.start:
                self.skip_until = now + (now - self.start) * SKIP_INTERVAL_GROWTH_FACTOR
            else:
                self.skip_until = None
        else:
            self.skip_until = self.start = self.end = None

    @property
    def length(self) -> timedelta:
        """Return the length of the retention."""
        return self.end - self.start if self.start and self.end else timedelta()

    def is_silenced(self) -> bool:
        """Return whether the quiz is silenced."""
        return self.skip_until > datetime.now() if self.skip_until else False

    def as_dict(self) -> dict[str, str | int]:
        """Return the retention as dict."""
        result = {}
        for field in fields(self):
            key = field.name
            if value := getattr(self, key):
                result[key] = value.isoformat(timespec="seconds") if str(field.type) == "optional_datetime" else value
        return result

    @classmethod
    def from_dict(cls, retention_dict: dict[str, str | int]) -> Retention:
        """Instantiate a retention from a dict."""
        start = cls.__get_datetime(retention_dict, "start")
        end = cls.__get_datetime(retention_dict, "end")
        skip_until = cls.__get_datetime(retention_dict, "skip_until")
        count = int(retention_dict.get("count", 0))
        return cls(start, end, skip_until, count)

    @staticmethod
    def __get_datetime(retention_dict: dict[str, str | int], key: str) -> optional_datetime:
        """Get a datetime from the Retention dict."""
        return datetime.fromisoformat(str(retention_dict.get(key))) if retention_dict.get(key) else None
