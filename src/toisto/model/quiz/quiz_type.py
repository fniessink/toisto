"""Quiz types."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import chain
from typing import ClassVar, final

from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Label, Labels
from toisto.tools import Registry

from .match import match


@dataclass(frozen=True)
class QuizType:
    """Base quiz type."""

    _action: str = ""
    _instruction: str = ""  # Instruction telling the user what action(s) they need to perform to answer the quiz

    @property
    def action(self) -> str:
        """Return the quiz type action."""
        return self._action

    def instruction(self, question: Label) -> str:  # noqa: ARG002
        """Return the quiz type instruction."""
        return self._instruction if self._instruction else f"Give the [underline]{self.action}[/underline] in"

    def question(self, question: Label) -> Label:
        """Return the question for the quiz type. Can be overridden for quiz types that transform questions."""
        return question

    def question_notes(self, question: Label, answers: Labels, *homonym_notes: str) -> list[str]:  # noqa: ARG002
        """Return the notes to be shown before the quiz has been answered."""
        return (
            [question.question_note]
            if question.question_note and self.question_notes_applicable(question, answers[0])
            else []
        )

    def question_notes_applicable(self, question: Label, answer: Label) -> bool:
        """Return whether the question should get question notes."""
        return question.language != answer.language

    def answer_notes(self, question: Label, answers: Labels) -> Sequence[str]:  # noqa: ARG002
        """Return the notes to be shown after the quiz has been answered."""
        return question.answer_notes

    def other_answers(self, guess: Label, answers: Labels) -> Labels:
        """Return the answers not equal to the guess."""
        return Labels(
            answer
            for answer in answers
            if not match(str(guess.lower_case), str(answer.lower_case)) and guess not in answer.spelling_alternatives
        )

    def is_quiz_type(self, quiz_type: QuizType | type[QuizType]) -> bool:
        """Return whether this quiz type matches the given quiz type."""
        return quiz_type == self if isinstance(quiz_type, QuizType) else isinstance(self, quiz_type)


@dataclass(frozen=True)
class ListenOnlyQuizType(QuizType):
    """Listen-only quiz type."""

    def instruction(self, question: Label) -> str:
        """Override to return the quiz type instruction for listen-only quizzes."""
        colloquial_note = f"to the colloquial {ALL_LANGUAGES[question.language]} "
        return f"Listen {colloquial_note if question.is_colloquial else ''}and write in"

    def question_notes(self, question: Label, answers: Labels, *homonym_notes: str) -> list[str]:
        """Return the notes to be shown before the quiz has been answered."""
        return super().question_notes(question, answers) + list(homonym_notes)

    def other_answers(self, guess: Label, answers: Labels) -> Labels:  # noqa: ARG002
        """Override because returning other answers doesn't make sense if the user has to type what is spoken."""
        return Labels()


@dataclass(frozen=True)
class TranslationQuizType(QuizType):
    """Translation quiz type."""

    _instruction: str = "Translate into"


@dataclass(frozen=True)
class SemanticQuizType(QuizType):
    """Semantic quiz type."""

    def question_notes_applicable(self, question: Label, answer: Label) -> bool:  # noqa: ARG002
        """Override to return True because semantic quizzes should always get a question note."""
        return True


@dataclass(frozen=True)
class GrammaticalQuizType(QuizType):
    """Grammatical quiz type."""

    quiz_types: tuple[QuizType, ...] = ()  # Grammatical quizzes can be composite

    instances: ClassVar[Registry[str, GrammaticalQuizType]] = Registry[str, "GrammaticalQuizType"]()

    def __post_init__(self) -> None:
        """Add the quiz type to the grammatical quiz type registry."""
        self.instances.add_item(self._action, self)

    @property
    def action(self) -> str:
        """Return the quiz type action."""
        return "+".join(quiz_type.action for quiz_type in self.quiz_types) if self.quiz_types else super().action

    def instruction(self, question: Label) -> str:  # noqa: ARG002
        """Return the quiz type instruction."""
        actions = " ".join(quiz_type.action for quiz_type in self.quiz_types) if self.quiz_types else super().action
        return f"Give the [underline]{actions}[/underline] in"

    def is_quiz_type(self, quiz_type: QuizType | type[QuizType]) -> bool:
        """Extend to also check whether the constituent quiz types match the given quiz type."""
        if self.quiz_types:
            return any(constituent_quiz_type.is_quiz_type(quiz_type) for constituent_quiz_type in self.quiz_types)
        return super().is_quiz_type(quiz_type)


@final
@dataclass(frozen=True)
class WriteQuizType(TranslationQuizType):
    """Write a translation quiz type."""

    _action: str = "write"

    def question_notes(self, question: Label, answers: Labels, *homonym_notes: str) -> list[str]:  # noqa: ARG002
        """Return the note to be shown before the quiz has been answered."""
        return [answers[0].question_note] if answers[0].question_note else []

    def answer_notes(self, question: Label, answers: Labels) -> Sequence[str]:  # noqa: ARG002
        """Return the notes to be shown after the quiz has been answered."""
        return tuple(chain.from_iterable(answer.answer_notes for answer in answers))


@final
@dataclass(frozen=True)
class OrderQuizType(SemanticQuizType):
    """Order quiz type."""

    _action: str = "order"
    _instruction: str = "Give the [underline]right order[/underline] of the words in"

    def question(self, question: Label) -> Label:
        """Override to randomize the word order."""
        return question.random_order


@final
@dataclass(frozen=True)
class DictateQuizType(ListenOnlyQuizType):
    """Dictate quiz type."""

    _action: str = "dictate"

    def instruction(self, question: Label) -> str:
        """Extend to add "standard" for dictate quizzes."""
        instruction = super().instruction(question)
        return instruction + " standard" if question.is_colloquial else instruction

    def question_notes_applicable(self, question: Label, answer: Label) -> bool:  # noqa: ARG002
        """Override to return True because dictate quizzes should always get a question note."""
        return True


# Translate quiz types
READ = TranslationQuizType("read")
WRITE = WriteQuizType()

# Listen-only quiz types
DICTATE = DictateQuizType()
INTERPRET = ListenOnlyQuizType("interpret")

# Grammatical quiz types
PLURAL = GrammaticalQuizType("plural")
SINGULAR = GrammaticalQuizType("singular")
FIRST_PERSON = GrammaticalQuizType("first person")
SECOND_PERSON = GrammaticalQuizType("second person")
THIRD_PERSON = GrammaticalQuizType("third person")
MALE = GrammaticalQuizType("male")
FEMALE = GrammaticalQuizType("female")
NEUTER = GrammaticalQuizType("neuter")
PRESENT_TENSE = GrammaticalQuizType("present tense")
PAST_TENSE = GrammaticalQuizType("past tense")
PRESENT_PERFECT_TENSE = GrammaticalQuizType("present perfect tense")
PAST_PERFECT_TENSE = GrammaticalQuizType("past perfect tense")
INFINITIVE = GrammaticalQuizType("infinitive")
POSITIVE_DEGREE = GrammaticalQuizType("positive degree")
COMPARATIVE_DEGREE = GrammaticalQuizType("comparative degree")
SUPERLATIVE_DEGREE = GrammaticalQuizType("superlative degree")
INTERROGATIVE = GrammaticalQuizType("interrogative")
DECLARATIVE = GrammaticalQuizType("declarative")
IMPERATIVE = GrammaticalQuizType("imperative")
AFFIRMATIVE = GrammaticalQuizType("affirmative")
NEGATIVE = GrammaticalQuizType("negative")
DIMINUTIVE = GrammaticalQuizType("diminutive")
CARDINAL = GrammaticalQuizType("cardinal")
ORDINAL = GrammaticalQuizType("ordinal")
ABBREVIATION = GrammaticalQuizType("abbreviation")
FULL_FORM = GrammaticalQuizType("full form")

# Semantic quiz types
ANSWER = SemanticQuizType("answer")
ANTONYM = SemanticQuizType("antonym")
ORDER = OrderQuizType()