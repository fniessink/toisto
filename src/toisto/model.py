"""Model classes."""

from dataclasses import dataclass
import random

from .match import match

@dataclass
class Entry:
    """Class representing one word or phrase question/answer pair with a specific direction."""
    question_language: str
    answer_language: str
    question: str
    answer: str

    def is_correct(self, guess: str) -> bool:
        """Return whether the guess is correct."""
        return match(self.answer, guess)

    def reversed(self) -> "Entry":
        """Return the reversed version of this entry."""
        return self.__class__(self.answer_language, self.question_language, self.answer, self.question)


class Progress:
    """Keep track of progress on entries."""
    def __init__(self, progress_dict: dict[str, int]) -> None:
        self.progress_dict = progress_dict

    def update(self, entry: Entry, correct: bool) -> None:
        """Update the progress of the entry."""
        key = str(entry)
        self.progress_dict[key] = self.progress_dict.setdefault(key, 0) + (2 if correct else -1)

    def get_progress(self, entry: Entry) -> int:
        """Return the progress of the entry."""
        key = str(entry)
        return self.progress_dict.get(key, 0)

    def next_entry(self, entries: list[Entry]) -> Entry:
        """Return the next entry to quiz the user with."""
        min_progress = min(self.get_progress(entry) for entry in entries)
        next_entries = [entry for entry in entries if self.get_progress(entry) == min_progress]
        return random.choice(next_entries)

    def as_dict(self) -> dict[str, int]:
        """Return the progress as dict."""
        return self.progress_dict
