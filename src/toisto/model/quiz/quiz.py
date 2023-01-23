"""Quiz classes."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import cast, Literal

from toisto.metadata import Language, SUPPORTED_LANGUAGES

from ..language.concept import Concept
from ..language.grammar import GrammaticalCategory
from ..language.label import Label, Labels
from ..model_types import ConceptId
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
    "give infinitive",
    "give present tense",
    "give past tense",
    "make declarative",
    "make interrogative",
    "affirm",
    "negate",
]
GRAMMATICAL_QUIZ_TYPES: dict[GrammaticalCategory, QuizType] = {
    "plural": "pluralize",
    "singular": "singularize",
    "male": "masculinize",
    "female": "feminize",
    "neuter": "neuterize",
    "positive degree": "give positive degree",
    "comparitive degree": "give comparitive degree",
    "superlative degree": "give superlative degree",
    "first person": "give first person",
    "second person": "give second person",
    "third person": "give third person",
    "infinitive": "give infinitive",
    "present tense": "give present tense",
    "past tense": "give past tense",
    "declarative": "make declarative",
    "interrogative": "make interrogative",
    "affirmative": "affirm",
    "negative": "negate",
}
QUIZ_TYPE_GRAMMATICAL_CATEGORIES = {value: key for key, value in GRAMMATICAL_QUIZ_TYPES.items()}
INSTRUCTIONS: dict[QuizType, str] = dict(translate="Translate into", listen="Listen and write in")


def instruction(*quiz_types: QuizType) -> str:
    """Return the instruction text for the quiz types."""
    if instruction_label := INSTRUCTIONS.get(quiz_types[0]):
        return instruction_label
    categories = " ".join(QUIZ_TYPE_GRAMMATICAL_CATEGORIES[quiz_type] for quiz_type in quiz_types)
    return f"Give the [underline]{categories}[/underline] form in"


@dataclass(frozen=True)
class Quiz:  # pylint: disable=too-many-instance-attributes
    """Class representing a quiz."""

    concept: Concept
    question_language: Language
    answer_language: Language
    _question: Label
    _answers: Labels
    quiz_types: tuple[QuizType, ...] = ("translate",)
    blocked_by: tuple[Quiz, ...] = tuple()
    _meanings: Labels = Labels()
    _hash: int = 0

    def __post_init__(self):
        """Initialize calculated attributes."""
        # The dataclass is frozen, so some magic is needed to set the hash attribute.
        super().__setattr__(
            "_hash", hash((self.question_language, self.answer_language, self.question, self.quiz_types))
        )

    def __str__(self) -> str:
        """Return a string version of the quiz that can be used as key in the progress dict."""
        quiz_types = "+".join(self.quiz_types)
        return f"{self.question_language}:{self.answer_language}:{self._question}:{quiz_types}"

    def __hash__(self) -> int:
        """Return a hash using the same attributes as used for testing equality."""
        return self._hash

    def __eq__(self, other) -> bool:
        """Return whether this quiz is equal to the other."""
        if not isinstance(other, self.__class__):
            return False
        return (
            self.question_language == other.question_language
            and self.answer_language == other.answer_language
            and self.question == other.question
            and self.quiz_types == other.quiz_types
        )

    def __ne__(self, other) -> bool:
        """Return whether this quiz is not equal to the other."""
        return not self == other

    def is_correct(self, guess: Label) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    @cached_property
    def question(self) -> Label:
        """Return the first spelling alternative of the question."""
        return self._question.spelling_alternatives[0]

    @property
    def answer(self) -> Label:
        """Return the first spelling alternative of the first answer."""
        return self._answers[0].spelling_alternatives[0]

    @property
    def answers(self) -> Labels:
        """Return all answers."""
        answers = [answer.spelling_alternatives for answer in self._answers]
        return cast(Labels, tuple(chain(*answers)))

    @property
    def meanings(self) -> Labels:
        """Return the first spelling alternative of the meanings."""
        return Labels(meaning.spelling_alternatives[0] for meaning in self._meanings)

    def other_answers(self, guess: Label) -> Labels:
        """Return the answers not equal to the guess."""
        if self.quiz_types == ("listen",):
            return Labels()  # Other answers doesn't make sense if the user has to type what is spoken
        return tuple(answer for answer in self.answers if not match(guess, answer))

    def instruction(self) -> str:
        """Generate the quiz instruction."""
        hint = self._question.hint
        hint = f" ({hint})" if self.question_language != self.answer_language and hint else ""
        return f"{instruction(*self.quiz_types)} {SUPPORTED_LANGUAGES[self.answer_language]}{hint}"

    def is_blocked_by(self, quizzes: Quizzes) -> bool:
        """Return whether this quiz should come after any of the given quizzes."""
        return bool(set(self.blocked_by) & quizzes)

    @property
    def concept_id(self) -> ConceptId:
        """Return the id of the quiz's concept."""
        return self.concept.concept_id

    @property
    def root_concept_id(self) -> ConceptId:
        """Return the root id of the quiz's concept."""
        return ConceptId(self.concept_id.split("/")[0])

    @property
    def used_concepts(self) -> tuple[ConceptId, ...]:
        """Return the ids of the concepts used by the concept that this quiz quizzes."""
        return self.concept.used_concepts(self.question_language)


Quizzes = set[Quiz]
