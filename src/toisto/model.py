"""Model classes."""

from dataclasses import dataclass

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
