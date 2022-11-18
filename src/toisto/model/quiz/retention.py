"""Quiz retention."""

from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta


@dataclass
class Retention:
    """Class to keep track of the retention of one quiz."""

    start: datetime | None = None  # Start of the retention period, i.e. the period in which all answers were correct
    end: datetime | None = None  # End of the retention period, i.e. the datetime of the more recent correct answer
    skip_until: datetime | None = None  # Don't quiz this again until after the datetime

    def update(self, correct: bool) -> None:
        """Update the retention of the quiz."""
        now = datetime.now()
        if correct:
            self.end = now
            if self.start is None:
                self.start = now
                self.skip_until = None
            else:
                self.skip_until = now + (now - self.start) * 5
        else:
            self.skip_until = self.start = self.end = None

    @property
    def length(self) -> timedelta:
        """Return the length of the retention."""
        return self.end - self.start if self.start and self.end else timedelta()

    def is_silenced(self) -> bool:
        """Return whether the quiz is silenced."""
        return self.skip_until > datetime.now() if self.skip_until else False

    def as_dict(self) -> dict[str, str]:
        """Return the retention as dict."""
        return {key: value.isoformat(timespec="seconds") for key, value in asdict(self).items() if value}

    @classmethod
    def from_dict(cls, retention_dict: dict[str, str]) -> "Retention":
        """Instantiate a retention from a dict."""
        values = []
        for field in fields(cls):
            text = str(retention_dict.get(field.name, ""))
            values.append(datetime.fromisoformat(text) if text else None)
        return cls(*values)
