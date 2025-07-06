"""Quiz classes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import cached_property

from toisto.tools import first

from ..language import LanguagePair
from ..language.concept import Concept, Concepts
from ..language.iana_language_subtag_registry import ALL_LANGUAGES
from ..language.label import Label, Labels
from .evaluation import Evaluation
from .match import match
from .quiz_type import ListenOnlyQuizType, QuizType


@dataclass(frozen=True)
class Quiz:
    """Class representing a quiz."""

    concept: Concept
    _question: Label
    _answers: Labels
    quiz_type: QuizType
    blocked_by: tuple[Quiz, ...]
    _question_meanings: Labels = field(default_factory=Labels)
    _answer_meanings: Labels = field(default_factory=Labels)

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
        return f"{self.question.language}:{self.answer.language}:{question}:{self.answer}:{self.quiz_type.action}"

    @property
    def old_key(self) -> str:
        """Return a string version of the quiz as it was used before."""
        concept_id = self.concept.base_concept.concept_id
        question = self._question.first_spelling_alternative
        return f"{concept_id}:{self.question.language}:{self.answer.language}:{question}:{self.quiz_type.action}"

    def has_quiz_type(self, quiz_type: QuizType | type[QuizType]) -> bool:
        """Return whether this quiz has the specified quiz type."""
        return self.quiz_type.is_quiz_type(quiz_type)

    def evaluate(self, guess: Label, language_pair: LanguagePair, attempt: int) -> Evaluation:
        """Evaluate the user's guess."""
        if self.is_correct(guess, language_pair):
            return Evaluation.CORRECT
        if str(guess) == "?":
            return Evaluation.SKIPPED
        if attempt == 1:
            return Evaluation.TRY_AGAIN
        return Evaluation.INCORRECT

    def is_correct(self, guess: Label, language_pair: LanguagePair) -> bool:
        """Return whether the guess is correct."""
        answers = self.answers
        if guess.language == language_pair.source:
            guess = guess.lower_case
            answers = answers.lower_case
        return match(str(guess), *answers.as_strings)

    def is_question(self, guess: Label) -> bool:
        """Return whether the guess is not the answer, but the question (common user error with listening quizzes)."""
        questions = Labels((self._question,)) + self._question_meanings
        return match(str(guess), *questions.spelling_alternatives.as_strings)

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
        return self._question_meanings.first_spelling_alternatives

    @property
    def answer_meanings(self) -> Labels:
        """Return the first spelling alternative of the answer meanings."""
        return self._answer_meanings.first_spelling_alternatives

    def other_answers(self, guess: Label) -> Labels:
        """Return the answers not equal to the guess."""
        return self.quiz_type.other_answers(guess, self.non_generated_answers)

    @property
    def instruction(self) -> str:
        """Generate the quiz instruction."""
        instruction_text = self.quiz_type.instruction(self.question)
        if self.question.is_complete_sentence:
            instruction_text = instruction_text.replace("write ", "write a complete sentence ")
        return f"{instruction_text} {ALL_LANGUAGES[self.answer.language]}{self._tips}"

    @property
    def notes(self) -> Sequence[str]:
        """Return the notes to be shown after the quiz has been answered."""
        return self.quiz_type.notes(self._question, self._answers)

    def is_blocked_by(self, quizzes: Quizzes) -> bool:
        """Return whether this quiz should come after any of the given quizzes."""
        return bool(Quizzes(self.blocked_by) & quizzes)

    @property
    def _tips(self) -> str:
        """Return the tip(s) to be shown as part of the question, if applicable."""
        question = self._question
        tips = self.quiz_type.tips(question, self._answers)
        if homographs := self.concept.get_homographs(question):
            tips.extend(self._homonym_tips(homographs))
        if isinstance(self.quiz_type, ListenOnlyQuizType) and (capitonyms := self.concept.get_capitonyms(question)):
            tips.extend(self._homonym_tips(capitonyms))
        return f" ({'; '.join(tips)})" if tips else ""

    def _homonym_tips(self, homonyms: Concepts) -> Sequence[str]:
        """Return the tip(s) to be shown as part of the question, if the question has one or more homonyms."""
        if self.concept.same_base_concept(*homonyms):
            return self.concept.grammatical_differences(*homonyms)
        language = self.question.language
        if hypernyms := self.concept.get_related_concepts("hypernym"):
            return [str(hypernym.labels(language)[0]) for hypernym in hypernyms[:1]]
        if holonyms := self.concept.get_related_concepts("holonym"):
            return [f"part of '{holonym.labels(language)[0]}'" for holonym in holonyms]
        if involved_concepts := self.concept.get_related_concepts("involves"):
            return [f"involves '{concept.labels(language)[0]}'" for concept in involved_concepts]
        return []


class Quizzes(set[Quiz]):
    """Set of quizzes."""

    def by_concept(self, concept: Concept) -> Quizzes:
        """Return the quizzes for the concept."""
        return self._quizzes_by_concept.get(concept.base_concept, Quizzes())

    def by_label(self, label: Label) -> Quizzes:
        """Return the quizzes for the label."""
        return self._quizzes_by_label.get(label, Quizzes())

    def related_quizzes(self, quiz: Quiz) -> Quizzes:
        """Return the quizzes related to the quiz, meaning quizzes for the same concept and quizzes for examples."""
        quizzes = Quizzes(self.by_concept(quiz.concept))
        for example in quiz.concept.get_related_concepts("example"):
            quizzes |= self.by_concept(example)
        return quizzes

    @property
    def colloquial(self) -> Quizzes:
        """Return the colloquial quizzes."""
        return self.__class__(quiz for quiz in self if quiz.question.colloquial)

    @cached_property
    def _quizzes_by_concept(self) -> dict[Concept, Quizzes]:
        """Return the quizzes by concept cache.

        Can't use functools.cache as Quizzes instances are not hashable, so use a dict as cache.
        Note that the cache is not updated when quizzes are added or removed after initialization.
        """
        quizzes_by_concept: dict[Concept, Quizzes] = {}
        for quiz in self:
            quizzes_by_concept.setdefault(quiz.concept.base_concept, Quizzes()).add(quiz)
        return quizzes_by_concept

    @cached_property
    def _quizzes_by_label(self) -> dict[Label, Quizzes]:
        """Return the quizzes by label cache.

        Can't use functools.cache as Quizzes instances are not hashable, so use a dict as cache.
        Note that the cache is not updated when quizzes are added or removed after initialization.
        """
        quizzes_by_label: dict[Label, Quizzes] = {}
        for quiz in self:
            for label in [quiz.question, *quiz.answers]:
                quizzes_by_label.setdefault(label, Quizzes()).add(quiz)
        return quizzes_by_label
