"""Model classes."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass
class QuizProgress:
    """Class to keep track of progress on one quiz."""

    count: int = 0  # The number of consecutive correct guesses
    silence_until: datetime | None = None  # Don't quiz this again until after the datetime

    def update(self, correct: bool) -> None:
        """Update the progress of the quiz."""
        if correct:
            self.count += 1
        else:
            self.count = 0
        self.silence_until = self.__calculate_next_quiz() if self.count > 1 else None

    def is_silenced(self):
        """Return whether the quiz is silenced."""
        return self.silence_until > datetime.now() if self.silence_until else False

    def __calculate_next_quiz(self) -> datetime:
        """Calculate when to quiz again based on the number of correct guesses."""
        # Graph of function below: https://www.desmos.com/calculator/itvdhmh6ex
        max_timedelta = timedelta(days=90)  # How often do we quiz when user has perfect recall?
        slope = 0.25  # How fast do we get to the max timedelta?
        x_shift = -5.6  # Determines the minimum period at count = 2
        y_shift = 1  # Make zero the minimum y value instead of -1
        time_delta = (math.tanh(slope * self.count + x_shift) + y_shift) * (max_timedelta / 2)
        return datetime.now() + time_delta

    def as_dict(self) -> dict[str, int | str]:
        """Return the quiz progress as dict."""
        result: dict[str, int | str] = dict(count=self.count)
        if self.silence_until:
            result["silence_until"] = self.silence_until.isoformat()
        return result

    @classmethod
    def from_dict(cls, quiz_progress_dict: dict[str, int | str]) -> "QuizProgress":
        """Instantiate a quiz progress from a dict."""
        count = int(quiz_progress_dict.get("count", 0))
        silence_until_text = str(quiz_progress_dict.get("silence_until", ""))
        silence_until = datetime.fromisoformat(silence_until_text) if silence_until_text else None
        return cls(count, silence_until)
