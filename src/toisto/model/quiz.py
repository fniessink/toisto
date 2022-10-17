"""Quiz classes."""

from dataclasses import dataclass
from typing import Literal

from ..match import match
from ..metadata import Language, SUPPORTED_LANGUAGES


QuizType = Literal["translate", "pluralize", "singularize"]
INSTRUCTION: dict[QuizType, str] = dict(
    translate="Translate into", pluralize="Give the plural in", singularize="Give the singular in"
)


@dataclass
class Quiz:
    """Class representing a quiz."""
    question_language: Language
    answer_language: Language
    question: str
    answers: list[str]
    quiz_type: QuizType = "translate"

    def is_correct(self, guess: str) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    def get_answer(self) -> str:
        """Return the first answer."""
        return self.answers[0]

    def other_answers(self, guess: str) -> list[str]:
        """Return the answers not equal to the guess."""
        assert self.is_correct(guess)
        return [answer for answer in self.answers if not match(guess, answer)]

    def instruction(self) -> str:
        """Generate the quiz instruction."""
        return f"{INSTRUCTION[self.quiz_type]} {SUPPORTED_LANGUAGES[self.answer_language]}"
