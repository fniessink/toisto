"""Quiz classes."""

from dataclasses import dataclass
from itertools import chain
from typing import cast, Literal

from toisto.match import match
from toisto.metadata import Language, SUPPORTED_LANGUAGES

from .label import Label, Labels


QuizType = Literal[
    "translate",
    "pluralize",
    "singularize",
    "masculinize",
    "feminize",
    "give positive degree",
    "give comparitive degree",
    "give superlative degree",
    "give first person",
    "give second person",
    "give third person",
]
INSTRUCTION: dict[QuizType, str] = {
    "translate": "Translate into",
    "pluralize": "Give the [underline]plural[/underline] in",
    "singularize": "Give the [underline]singular[/underline] in",
    "masculinize": "Give the [underline]male[/underline] form in",
    "feminize": "Give the [underline]female[/underline] form in",
    "give positive degree": "Give the [underline]positive degree[/underline] in",
    "give comparitive degree": "Give the [underline]comparitive degree[/underline] in",
    "give superlative degree": "Give the [underline]superlative degree[/underline] in",
    "give first person": "Give the [underline]first person[/underline] in",
    "give second person": "Give the [underline]second person[/underline] in",
    "give third person": "Give the [underline]third person[/underline] in",
}


@dataclass
class Quiz:
    """Class representing a quiz."""
    question_language: Language
    answer_language: Language
    _question: Label
    _answers: Labels
    quiz_type: QuizType = "translate"

    def is_correct(self, guess: Label) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    @property
    def question(self) -> Label:
        """Return the first spelling alternative of the question."""
        return self.__first_spelling_alternative(self._question)

    @property
    def answer(self) -> Label:
        """Return the first spelling alternative of the first answer."""
        return self.__first_spelling_alternative(self._answers[0])

    @property
    def answers(self) -> Labels:
        """Return all answers."""
        answers = [answer.split("|") for answer in self._answers]
        return cast(Labels, list(chain(*answers)))

    def other_answers(self, guess: Label) -> Labels:
        """Return the answers not equal to the guess."""
        assert self.is_correct(guess)
        return [answer for answer in self.answers if not match(guess, answer)]

    def instruction(self) -> str:
        """Generate the quiz instruction."""
        return f"{INSTRUCTION[self.quiz_type]} {SUPPORTED_LANGUAGES[self.answer_language]}"

    @staticmethod
    def __first_spelling_alternative(label: Label) -> Label:
        """Extract the first spelling alternative from the label."""
        return Label(label.split("|")[0])


def quiz_factory(  # pylint: disable=too-many-arguments
    language1: Language,
    language2: Language,
    labels1: Labels,
    labels2: Labels,
    quiz_type1: QuizType = "translate",
    quiz_type2: QuizType = "translate"
) -> list[Quiz]:
    """Create quizzes."""
    return (
        [Quiz(language1, language2, label, labels2, quiz_type1) for label in labels1] +
        [Quiz(language2, language1, label, labels1, quiz_type2) for label in labels2]
    )
