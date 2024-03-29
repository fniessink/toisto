"""Quiz classes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import Final, Literal, cast, get_args

from ..language import Language
from ..language.concept import Concept
from ..language.grammar import GrammaticalCategory
from ..language.iana_language_subtag_registry import ALL_LANGUAGES
from ..language.label import Label, Labels
from .match import match

TranslationQuizType = Literal["read", "write"]
ListenQuizType = Literal["dictate", "interpret"]
SemanticQuizType = Literal["answer", "antonym"]
GrammaticalQuizType = Literal[
    "pluralize",
    "singularize",
    "diminutize",
    "masculinize",
    "feminize",
    "neuterize",
    "give positive degree",
    "give comparative degree",
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
    "make cardinal",
    "make ordinal",
    "abbreviate",
    "give full form",
]
QuizType = Literal[TranslationQuizType, ListenQuizType, SemanticQuizType, GrammaticalQuizType]
GRAMMATICAL_QUIZ_TYPES: Final[dict[GrammaticalCategory, GrammaticalQuizType]] = {
    "plural": "pluralize",
    "singular": "singularize",
    "diminutive": "diminutize",
    "male": "masculinize",
    "female": "feminize",
    "neuter": "neuterize",
    "positive degree": "give positive degree",
    "comparative degree": "give comparative degree",
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
    "cardinal": "make cardinal",
    "ordinal": "make ordinal",
    "abbreviation": "abbreviate",
    "full form": "give full form",
}
QUIZ_TYPE_GRAMMATICAL_CATEGORIES: Final = {value: key for key, value in GRAMMATICAL_QUIZ_TYPES.items()}
INSTRUCTIONS: Final[dict[Literal[TranslationQuizType, ListenQuizType, SemanticQuizType], str]] = {
    "read": "Translate into",
    "write": "Translate into",
    "dictate": "Listen and write in",
    "interpret": "Listen and write in",
    "answer": "Answer the question in",
    "antonym": "Give the [underline]antonym[/underline] in",
}


@dataclass(frozen=True)
class Quiz:
    """Class representing a quiz."""

    concept: Concept
    question_language: Language
    answer_language: Language
    _question: Label
    _answers: Labels
    quiz_types: tuple[QuizType, ...]
    blocked_by: tuple[Quiz, ...]
    _question_meanings: Labels = ()
    _answer_meanings: Labels = ()

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
        concept_id = self.concept.base_concept.concept_id
        quiz_types = "+".join(self.quiz_types)
        return f"{concept_id}:{self.question_language}:{self.answer_language}:{self.question}:{quiz_types}"

    def is_correct(self, guess: Label) -> bool:
        """Return whether the guess is correct."""
        return match(guess, *self.answers)

    def is_question(self, guess: Label) -> bool:
        """Return whether the guess is not the answer, but the question (common user error with listening quizzes)."""
        return any(match(guess, *label.spelling_alternatives) for label in (self._question, *self._question_meanings))

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
    def non_generated_answers(self) -> Labels:
        """Return all non-generated answers."""
        answers = [answer.non_generated_spelling_alternatives for answer in self._answers]
        return cast(Labels, tuple(chain(*answers)))

    @property
    def question_meanings(self) -> Labels:
        """Return the first spelling alternative of the question meanings."""
        return Labels(meaning.spelling_alternatives[0] for meaning in self._question_meanings)

    @property
    def answer_meanings(self) -> Labels:
        """Return the first spelling alternative of the answer meanings."""
        return Labels(meaning.spelling_alternatives[0] for meaning in self._answer_meanings)

    def other_answers(self, guess: Label) -> Labels:
        """Return the answers not equal to the guess."""
        if self.quiz_types[0] in get_args(ListenQuizType):
            return Labels()  # Returning other answers doesn't make sense if the user has to type what is spoken
        return tuple(answer for answer in self.non_generated_answers if not match(guess, answer))

    @property
    def instruction(self) -> str:
        """Generate the quiz instruction."""
        if self.is_grammatical:
            categories = " ".join(
                QUIZ_TYPE_GRAMMATICAL_CATEGORIES[cast(GrammaticalQuizType, quiz_type)] for quiz_type in self.quiz_types
            )
            instruction_text = f"Give the [underline]{categories}[/underline] in"
        else:
            quiz_type = cast(Literal[TranslationQuizType, ListenQuizType, SemanticQuizType], self.quiz_types[0])
            if self.question.is_colloquial:
                instruction_text = f"Listen to the colloquial {ALL_LANGUAGES[self.question_language]} and write in"
                if quiz_type == "dictate":
                    instruction_text += " standard"
            else:
                instruction_text = INSTRUCTIONS[quiz_type]
            if self.question.is_complete_sentence:
                instruction_text = instruction_text.replace("write ", "write a complete sentence ")
        return f"{instruction_text} {ALL_LANGUAGES[self.answer_language]}{self._question_note}"

    @property
    def answer_notes(self) -> Sequence[str]:
        """Return the notes to be shown after the quiz has been answered."""
        if "write" in self.quiz_types:
            return tuple(chain.from_iterable(answer.answer_notes for answer in self._answers))
        return self._question.answer_notes

    def is_blocked_by(self, quizzes: Quizzes) -> bool:
        """Return whether this quiz should come after any of the given quizzes."""
        return bool(Quizzes(self.blocked_by) & quizzes)

    @property
    def _question_note(self) -> str:
        """Return the note to be shown as part of the question, if applicable."""
        note_applicable = self.question_language != self.answer_language or {"answer", "dictate"} & set(self.quiz_types)
        question_note = self._answers[0].question_note if "write" in self.quiz_types else self._question.question_note
        return f" ({question_note})" if (note_applicable and question_note) else ""

    @property
    def is_grammatical(self) -> bool:
        """Return whether this is a grammatical quiz."""
        return self.quiz_types[0] in get_args(GrammaticalQuizType)


class Quizzes(set[Quiz]):
    """Set of quizzes."""

    def by_concept(self, concept: Concept) -> Quizzes:
        """Return the quizzes for the concept."""
        return self._quizzes_by_concept.get(concept.base_concept, Quizzes())

    def related_quizzes(self, quiz: Quiz) -> Quizzes:
        """Return the quizzes related to the quiz, meaning quizzes for the same concept and quizzes for examples."""
        quizzes = Quizzes(self.by_concept(quiz.concept))
        for example in quiz.concept.get_related_concepts("example"):
            quizzes |= self.by_concept(example)
        return quizzes

    def by_quiz_type(self, quiz_type: QuizType) -> Quizzes:
        """Return the quizzes of the specified type."""
        return self.__class__(quiz for quiz in self if quiz_type in quiz.quiz_types)

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
