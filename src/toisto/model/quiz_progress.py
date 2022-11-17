"""Model classes."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class QuizProgress:
    """Class to keep track of progress on one quiz."""

    streak: int = 0  # The number of consecutive correct guesses
    start: datetime | None = None  # Start of the retention period, i.e. the period in which all answers were correct
    end: datetime | None = None  # End of the retention period, i.e. the datetime of the more recent correct answer
    skip_until: datetime | None = None  # Don't quiz this again until after the datetime

    def update(self, correct: bool) -> None:
        """Update the progress of the quiz."""
        now = datetime.now()
        if correct:
            self.streak += 1
            self.end = now
            if self.start is None:
                self.start = now
                self.skip_until = None
            else:
                self.skip_until = now + (now - self.start) * 5
        else:
            self.streak = 0
            self.skip_until = self.start = self.end = None

    def is_silenced(self):
        """Return whether the quiz is silenced."""
        return self.skip_until > datetime.now() if self.skip_until else False

    def as_dict(self) -> dict[str, int | str]:
        """Return the quiz progress as dict."""
        result: dict[str, int | str] = dict(streak=self.streak)
        if self.skip_until:
            result["skip_until"] = self.skip_until.isoformat(timespec="seconds")
        if self.start:
            result["start"] = self.start.isoformat(timespec="seconds")
        if self.end:
            result["end"] = self.end.isoformat(timespec="seconds")
        return result

    @classmethod
    def from_dict(cls, quiz_progress_dict: dict[str, int | str]) -> "QuizProgress":
        """Instantiate a quiz progress from a dict."""
        streak = int(quiz_progress_dict.get("streak", 0))
        skip_until_text = str(quiz_progress_dict.get("skip_until", ""))
        skip_until = datetime.fromisoformat(skip_until_text) if skip_until_text else None
        start_text = str(quiz_progress_dict.get("start", ""))
        start = datetime.fromisoformat(start_text) if start_text else None
        end_text = str(quiz_progress_dict.get("end", ""))
        end = datetime.fromisoformat(end_text) if end_text else None
        return cls(streak, start, end, skip_until)
