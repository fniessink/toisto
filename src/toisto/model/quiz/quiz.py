"""Quiz classes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property

from toisto.tools import first

from ..language import Language, LanguagePair
from ..language.concept import Concept
from ..language.iana_language_subtag_registry import ALL_LANGUAGES
from ..language.label import Label, Labels
from .evaluation import Evaluation
from .quiz_type import QuizAction, QuizType


@dataclass(frozen=True)
class Quiz:
    """Class representing a quiz."""

    language_pair: LanguagePair
    concept: Concept
    _question: Label
    _answers: Labels
    quiz_type: QuizType
    action: QuizAction

    def __repr__(self) -> str:
        """Return a representation of the quiz for test purposes."""
        return self.key

    def __hash__(self) -> int:
        """Return a hash using the same attributes as used for testing equality."""
        return hash(self.key)

    def __eq__(self, other: object) -> bool:
        """Return whether this quiz is equal to the other."""
        return self.key == other.key if isinstance(other, self.__class__) else False

    def __ne__(self, other: object) -> bool:
        """Return whether this quiz is not equal to the other."""
        return self.key != other.key if isinstance(other, self.__class__) else True

    @cached_property
    def key(self) -> str:
        """Return a string version of the quiz that can be used as key in the progress dict."""
        question = self._question.first_spelling_alternative
        return f"{self.question.language}:{self.answer.language}:{question}:{self.answer}:{self.action}"

    def has_quiz_type(self, quiz_type: QuizType | type[QuizType]) -> bool:
        """Return whether this quiz has the specified quiz type."""
        return self.quiz_type.is_quiz_type(quiz_type)

    def evaluate(self, guess: str, source_language: Language, attempt: int) -> Evaluation:
        """Evaluate the user's guess."""
        if self.is_correct(guess, source_language):
            return Evaluation.CORRECT
        if guess == "?":
            return Evaluation.SKIPPED
        if attempt == 1:
            return Evaluation.TRY_AGAIN
        return Evaluation.INCORRECT

    def is_correct(self, guess: str, source_language: Language) -> bool:
        """Return whether the guess is correct."""
        return any(self.answers.matching(guess, case_sensitive=self.answer.language != source_language))

    def is_question(self, guess: str) -> bool:
        """Return whether the guess is not the answer, but the question (common user error with listening quizzes)."""
        question_meanings = self.quiz_type.question_meanings(self.language_pair, self.concept, self.question)
        questions = Labels((self._question, *question_meanings))
        return any(questions.spelling_alternatives.matching(guess))

    @property
    def question(self) -> Label:
        """Return the first spelling alternative of the question."""
        return self.quiz_type.question(self._question.first_spelling_alternative)

    @property
    def answer(self) -> Label:
        """Return the first spelling alternative of the first answer."""
        return first(self._answers).first_spelling_alternative

    @property
    def answers(self) -> Labels:
        """Return all answers."""
        return self._answers.spelling_alternatives

    @property
    def non_generated_answers(self) -> Labels:
        """Return all non-generated answers."""
        return self._answers.non_generated_spelling_alternatives

    @property
    def question_meanings(self) -> Labels:
        """Return the first spelling alternative of the question meanings."""
        question_meanings = self.quiz_type.question_meanings(self.language_pair, self.concept, self.question)
        return question_meanings.first_spelling_alternatives

    @property
    def answer_meanings(self) -> Labels:
        """Return the first spelling alternative of the answer meanings."""
        answer_meanings = self.quiz_type.answer_meanings(self.language_pair, self.concept, self.answer)
        return answer_meanings.first_spelling_alternatives

    def other_answers(self, guess: str) -> Labels:
        """Return the answers not equal to the guess."""
        return self.quiz_type.other_answers(guess, self.non_generated_answers)

    @property
    def instruction(self) -> str:
        """Generate the quiz instruction."""
        instruction_text = self.quiz_type.instruction(self.question, self.action)
        if self.question.is_complete_sentence:
            instruction_text = instruction_text.replace("write ", "write a complete sentence ")
        return f"{instruction_text} {ALL_LANGUAGES[self.answer.language]}{self._tips}"

    @property
    def notes(self) -> Sequence[str]:
        """Return the notes to be shown after the quiz has been answered."""
        return self.quiz_type.notes(self._question, self._answers)

    def is_blocked_by(self, quizzes: Quizzes) -> bool:
        """Return whether this quiz should come after any of the given quizzes."""
        return any(self.quiz_type.blocked_by(quiz_type) for quiz_type in quizzes.quiz_types)

    @property
    def _tips(self) -> str:
        """Return the tip(s) to be shown as part of the question, if applicable."""
        tips = self.quiz_type.tips(self.concept, self._question, self._answers)
        return f" ({'; '.join(tips)})" if tips else ""


class Quizzes(frozenset[Quiz]):
    """Set of quizzes."""

    def __or__(self, other: Quizzes) -> Quizzes:  # type: ignore[override]
        """Return the union of self and other."""
        return self.__class__(super().__or__(other))

    def by_concept(self, concept: Concept) -> Quizzes:
        """Return the quizzes for the concept."""
        return self.__quizzes_by_concept.get(concept, Quizzes())

    @cached_property
    def __quizzes_by_concept(self) -> dict[Concept, Quizzes]:
        """Return the quizzes by concept."""
        mapping: dict[Concept, Quizzes] = {}
        for quiz in self:
            mapping[quiz.concept] = mapping.get(quiz.concept, Quizzes()) | Quizzes({quiz})
        return mapping

    def by_label(self, label: Label) -> Quizzes:
        """Return the quizzes for the label."""
        return self.__quizzes_by_label.get(label, Quizzes())

    @cached_property
    def __quizzes_by_label(self) -> dict[Label, Quizzes]:
        """Return the quizzes by label."""
        mapping: dict[Label, Quizzes] = {}
        for quiz in self:
            for label in {quiz.question, *quiz.answers}:
                mapping[label] = mapping.get(label, Quizzes()) | Quizzes({quiz})
        return mapping

    def related_quizzes(self, quiz: Quiz) -> Quizzes:
        """Return the quizzes related to the quiz, meaning quizzes for the same concept and quizzes for examples."""
        quizzes = self.by_concept(quiz.concept)
        for example in quiz.concept.get_related_concepts("example"):
            quizzes |= self.by_concept(example)
        return quizzes

    @property
    def colloquial(self) -> Quizzes:
        """Return the colloquial quizzes."""
        return self.__class__(quiz for quiz in self if quiz.question.colloquial)

    @cached_property
    def quiz_types(self) -> set[QuizType]:
        """Return the quiz types of the quizzes."""
        return {quiz.quiz_type for quiz in self}
