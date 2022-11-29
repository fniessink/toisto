"""Quiz classes."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import cast, get_args, Literal

from toisto.metadata import Language, SUPPORTED_LANGUAGES

from ..language.grammar import GrammaticalCategory
from ..language.label import Label, Labels
from ..types import ConceptId
from .match import match


QuizType = Literal[
    "translate",
    "listen",
    "pluralize",
    "singularize",
    "masculinize",
    "feminize",
    "neuterize",
    "give positive degree",
    "give comparitive degree",
    "give superlative degree",
    "give first person",
    "give second person",
    "give third person",
]
INSTRUCTION: dict[QuizType, str] = {
    "translate": "Translate into",
    "listen": "Listen and write in",
    "pluralize": "Give the [underline]plural[/underline] in",
    "singularize": "Give the [underline]singular[/underline] in",
    "masculinize": "Give the [underline]male[/underline] form in",
    "feminize": "Give the [underline]female[/underline] form in",
    "neuterize": "Give the [underline]neuter[/underline] form in",
    "give positive degree": "Give the [underline]positive degree[/underline] in",
    "give comparitive degree": "Give the [underline]comparitive degree[/underline] in",
    "give superlative degree": "Give the [underline]superlative degree[/underline] in",
    "give first person": "Give the [underline]first person[/underline] in",
    "give second person": "Give the [underline]second person[/underline] in",
    "give third person": "Give the [underline]third person[/underline] in",
}


@dataclass(frozen=True)
class Quiz:  # pylint: disable=too-many-instance-attributes
    """Class representing a quiz."""

    concept_id: ConceptId
    question_language: Language
    answer_language: Language
    _question: Label
    _answers: Labels
    quiz_type: QuizType = "translate"
    uses: tuple[ConceptId, ...] = tuple()
    _meaning: Label = Label()

    def __str__(self) -> str:
        """Return a string version of the quiz that can be used as key in the progress dict."""
        return f"{self.question_language}:{self.answer_language}:{self._question}:{self.quiz_type}"

    def __hash__(self) -> int:
        """Return a hash using the same attributes as used for testing equality."""
        return hash((self.question_language, self.answer_language, self.question, self.quiz_type))

    def __eq__(self, other) -> bool:
        """Return whether this quiz is equal to the other."""
        if not isinstance(other, self.__class__):
            return False
        return (
            self.question_language == other.question_language and
            self.answer_language == other.answer_language and
            self.question == other.question and
            self.quiz_type == other.quiz_type
        )

    def __ne__(self, other) -> bool:
        """Return whether this quiz is not equal to the other."""
        return not self == other

    def is_correct(self, guess: Label) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    @property
    def question(self) -> Label:
        """Return the first spelling alternative of the question."""
        return self._question.first_spelling_alternative()

    @property
    def answer(self) -> Label:
        """Return the first spelling alternative of the first answer."""
        return self._answers[0].first_spelling_alternative()

    @property
    def answers(self) -> Labels:
        """Return all answers."""
        answers = [answer.spelling_alternatives() for answer in self._answers]
        return cast(Labels, tuple(chain(*answers)))

    @property
    def meaning(self) -> Label:
        """Return the first spelling alternative of the meaning."""
        return self._meaning.first_spelling_alternative()

    def other_answers(self, guess: Label) -> Labels:
        """Return the answers not equal to the guess."""
        return tuple(answer for answer in self.answers if not match(guess, answer))

    def instruction(self) -> str:
        """Generate the quiz instruction."""
        hint = self._question.hint()
        hint = f" ({hint})" if self.question_language != self.answer_language and hint else ""
        return f"{INSTRUCTION[self.quiz_type]} {SUPPORTED_LANGUAGES[self.answer_language]}{hint}"

    def has_same_concept(self, other) -> bool:
        """Return whether this quiz belongs to the same concept as the other quiz."""
        if not isinstance(other, self.__class__):
            return False
        return self.concept_id.split("/", maxsplit=1)[0] == other.concept_id.split("/", maxsplit=1)[0]


Quizzes = set[Quiz]


def quiz_factory(  # pylint: disable=too-many-arguments
    concept_id: ConceptId,
    language1: Language,
    language2: Language,
    labels1: Labels,
    labels2: Labels,
    quiz_type: QuizType = "translate",
    uses: tuple[ConceptId, ...] = tuple(),
    meaning: Label = Label()
) -> Quizzes:
    """Create quizzes."""
    if quiz_type == "translate" and labels1 and labels2:
        return (
            set(Quiz(concept_id, language1, language2, label, labels2, "translate", uses) for label in labels1) |
            set(Quiz(concept_id, language2, language1, label, labels1, "translate", uses) for label in labels2)
        )
    return set(
        Quiz(concept_id, language1, language2, label1, (label2,), quiz_type, uses, meaning)
        for label1, label2 in zip(labels1, labels2) if label1 != label2 or quiz_type == "listen"
    )


def quiz_type_factory(grammatical_categories: tuple[GrammaticalCategory, ...]) -> tuple[QuizType, ...]:
    """Generate the quiz types from the grammatical categories."""
    match grammatical_categories:
        case ("singular", "plural"):
            return ("pluralize", "singularize")
        case ("female", "male", "neuter"):
            return ("masculinize", "neuterize", "feminize", "neuterize", "feminize", "masculinize")
        case ("female", "male"):
            return ("masculinize", "feminize")
        case ("positive_degree", "comparitive_degree", "superlative_degree"):
            return (
                "give comparitive degree", "give superlative degree", "give positive degree",
                "give superlative degree", "give positive degree", "give comparitive degree"
            )
        case ("first_person", "second_person", "third_person"):
            return (
                "give second person", "give third person", "give first person",
                "give third person", "give first person", "give second person"
            )
        case _:
            raise NotImplementedError(f"Don't know how to generate guizzes for {grammatical_categories}")


def easiest_quizzes(quizzes: Quizzes) -> Quizzes:
    """Return the easiest quizzes."""
    for quiz_type in get_args(QuizType):
        if quizzes_subset := set(quiz for quiz in quizzes if quiz.quiz_type == quiz_type):
            return quizzes_subset
    return quizzes
