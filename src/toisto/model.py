"""Model classes."""

from dataclasses import asdict, dataclass
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

    def update(self, correct: bool) -> None:
        """Update the progress of the entry."""
        if correct:
            self.count += 1
        else:
            self.count = 0


class Progress:
    """Keep track of progress on entries."""
    def __init__(self, progress_dict: dict[str, dict[str, int]]) -> None:
        self.progress_dict = {key: EntryProgress(**value) for key, value in progress_dict.items()}

    def update(self, entry: Entry, correct: bool) -> None:
        """Update the progress of the entry."""
        key = str(entry)
        self.progress_dict.setdefault(key, EntryProgress()).update(correct)

    def get_progress(self, entry: Entry) -> int:
        """Return the progress of the entry."""
        key = str(entry)
        return self.progress_dict.get(key, EntryProgress()).count

    def next_entry(self, entries: list[Entry]) -> Entry:
        """Return the next entry to quiz the user with."""
        min_progress = min(self.get_progress(entry) for entry in entries)
        next_entries = [entry for entry in entries if self.get_progress(entry) == min_progress]
        return random.choice(next_entries)

    def as_dict(self) -> dict[str, dict[str, int]]:
        """Return the progress as dict."""
        return {key: asdict(value) for key, value in self.progress_dict.items()}
