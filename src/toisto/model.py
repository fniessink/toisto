"""Model classes."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import random

from .match import match


@dataclass
class Entry:
    """Class representing one word or phrase question/answer pair with a specific direction."""
    question_language: str
    answer_language: str
    question: str | list[str]
    answer: str | list[str]

    def is_correct(self, guess: str) -> bool:
        """Return whether the guess is correct."""
        answers = self.answer if isinstance(self.answer, list) else [self.answer]
        return match(guess, *answers)

    def reversed(self) -> "Entry":
        """Return the reversed version of this entry."""
        return self.__class__(self.answer_language, self.question_language, self.answer, self.question)

    def get_answer(self) -> str:
        """Return the answer. If answer is a list, return the first answer."""
        return self.answer[0] if isinstance(self.answer, list) else self.answer

    def get_question(self) -> str:
        """Return the question. If question is a list, return the first question."""
        return self.question[0] if isinstance(self.question, list) else self.question


@dataclass
class EntryProgress:
    """Class to keep track of progress on one entry."""

    count: int = 0  # The number of consecutive correct guesses
    silence_until: datetime | None = None  # Don't quiz the entry again until after the datetime

    def update(self, correct: bool) -> None:
        """Update the progress of the entry."""
        if correct:
            self.count += 1
        else:
            self.count = 0
        self.silence_until = self.__calculate_next_quiz() if self.count > 1 else None

    def is_silenced(self):
        """Return whether the entry can be quizzed."""
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
        """Return the progress entry as dict."""
        result: dict[str, int | str] = dict(count=self.count)
        if self.silence_until:
            result["silence_until"] = self.silence_until.isoformat()
        return result

    @classmethod
    def from_dict(cls, entry_progress_dict: dict[str, int | str]) -> "EntryProgress":
        """Instantiate a entry progress from a dict."""
        count = int(entry_progress_dict.get("count", 0))
        silence_until_text = str(entry_progress_dict.get("silence_until", ""))
        silence_until = datetime.fromisoformat(silence_until_text) if silence_until_text else None
        return cls(count, silence_until)


class Progress:
    """Keep track of progress on entries."""
    def __init__(self, progress_dict: dict[str, dict[str, int | str]]) -> None:
        self.progress_dict = {key: EntryProgress.from_dict(value) for key, value in progress_dict.items()}

    def update(self, entry: Entry, correct: bool) -> None:
        """Update the progress of the entry."""
        key = str(entry)
        self.progress_dict.setdefault(key, EntryProgress()).update(correct)

    def get_progress(self, entry: Entry) -> EntryProgress:
        """Return the progress of the entry."""
        key = str(entry)
        return self.progress_dict.get(key, EntryProgress())

    def next_entry(self, entries: list[Entry]) -> Entry | None:
        """Return the next entry to quiz the user with."""
        eligible_entries = [entry for entry in entries if not self.get_progress(entry).is_silenced()]
        if not eligible_entries:
            return None
        min_progress = min(self.get_progress(entry).count for entry in eligible_entries)
        next_entries = [entry for entry in eligible_entries if self.get_progress(entry).count == min_progress]
        return random.choice(next_entries)

    def as_dict(self) -> dict[str, dict[str, int | str]]:
        """Return the progress as dict."""
        return {key: value.as_dict() for key, value in self.progress_dict.items()}
