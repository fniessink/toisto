"""Base class for unit tests."""

import unittest
from collections.abc import Sequence
from typing import Final, cast

from toisto.model.language import EN, FI, NL, Language, LanguagePair
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz import Quiz, QuizType

# Language pairs (target, source) used in the unit tests
EN_FI: Final[LanguagePair] = LanguagePair(EN, FI)
EN_NL: Final[LanguagePair] = LanguagePair(EN, NL)
FI_EN: Final[LanguagePair] = LanguagePair(FI, EN)
FI_NL: Final[LanguagePair] = LanguagePair(FI, NL)
NL_EN: Final[LanguagePair] = LanguagePair(NL, EN)
NL_FI: Final[LanguagePair] = LanguagePair(NL, FI)


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    def setUp(self) -> None:
        """Set up a default language pair."""
        self.language_pair = EN_FI

    def tearDown(self) -> None:
        """Clear the registries."""
        Concept.instances.clear()
        Concept.homonyms.clear()

    @staticmethod
    def create_concept(concept_id: str, concept_dict: dict[str, object]) -> Concept:
        """Create a concept."""
        return create_concept(cast(ConceptId, concept_id), cast(ConceptDict, concept_dict))

    def create_quiz(  # noqa: PLR0913
        self,
        concept: Concept,
        question: str,
        answers: Sequence[str],
        quiz_type: str | tuple[str, ...] = ("read",),
        blocked_by: tuple[Quiz, ...] = (),
        question_meanings: tuple[str, ...] = (),
        answer_meanings: tuple[str, ...] = (),
        language_pair: LanguagePair | None = None,
    ) -> Quiz:
        """Create a quiz."""
        quiz_type = cast(tuple[QuizType], (quiz_type,) if isinstance(quiz_type, str) else quiz_type)
        language_pair = self.language_pair if language_pair is None else language_pair
        question_language = self.question_language(language_pair, quiz_type)
        answer_language = self.answer_language(language_pair, quiz_type)
        return Quiz(
            concept,
            Label(question_language, question),
            Labels(Label(answer_language, answer) for answer in answers),
            quiz_type,
            blocked_by,
            Labels(Label(question_language, meaning) for meaning in question_meanings),
            Labels(Label(answer_language, meaning) for meaning in answer_meanings),
        )

    def copy_quiz(
        self,
        quiz: Quiz,
        question: str = "",
        answers: list[str] | None = None,
        quiz_type: str | tuple[str, ...] = "",
    ) -> Quiz:
        """Copy the quiz, overriding some of its parameters."""
        return self.create_quiz(
            quiz.concept,
            question=question or str(quiz.question),
            answers=answers or quiz.answers.as_strings,
            quiz_type=quiz_type or tuple(str(quiz_type) for quiz_type in quiz.quiz_types),
            blocked_by=quiz.blocked_by,
            question_meanings=quiz.question_meanings.as_strings,
            answer_meanings=quiz.answer_meanings.as_strings,
        )

    @staticmethod
    def question_language(language_pair: LanguagePair, quiz_types: tuple[QuizType, ...]) -> Language:
        """Return the question language for the quiz types, given the target and source languages."""
        return language_pair.source if "write" in quiz_types else language_pair.target

    @staticmethod
    def answer_language(language_pair: LanguagePair, quiz_types: tuple[QuizType, ...]) -> Language:
        """Return the answer language for the quiz types, given the target and source languages."""
        return language_pair.source if {"interpret", "read"} & set(quiz_types) else language_pair.target
