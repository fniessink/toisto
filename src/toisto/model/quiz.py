"""Quiz classes."""

from dataclasses import dataclass

from ..match import match


@dataclass
class Quiz:
    """Class representing one question word or phrase question with one ore more correct answers."""
    question_language: str
    answer_language: str
    question: str
    answers: list[str]

    def is_correct(self, guess: str) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    def get_answer(self) -> str:
        """Return the first answer."""
        return self.answers[0]
