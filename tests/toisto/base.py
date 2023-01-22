"""Base class for unit tests."""

from typing import cast
import unittest

from toisto.metadata import Language
from toisto.model import Concept, ConceptFactory, Label, Labels, Quiz, Quizzes, QuizFactory
from toisto.model.language.concept_factory import ConceptDict
from toisto.model.model_types import ConceptId
from toisto.model.quiz.quiz import QuizType


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    @staticmethod
    def create_concept(concept_id: ConceptId, concept_dict: ConceptDict | None = None) -> Concept:
        """Create a concept from the concept dict."""
        return ConceptFactory(concept_id, concept_dict or cast(ConceptDict, {})).create_concept()

    @staticmethod
    def create_quizzes(concept: Concept, language: Language, source_language: Language) -> Quizzes:
        """Create quizzes for the concept."""
        return QuizFactory(language, source_language).create_quizzes(concept)

    @staticmethod
    def create_quiz(  # pylint: disable=too-many-arguments
        concept: Concept,
        question_language: str,
        answer_language: str,
        question: str,
        answers: list[str],
        quiz_type: str | tuple[str] = "translate",
        blocked_by: tuple[Quiz, ...] = tuple(),
        meanings: tuple[str, ...] = tuple(),
    ) -> Quiz:
        """Create a quiz."""
        quiz_type = cast(tuple[QuizType], (quiz_type,) if isinstance(quiz_type, str) else quiz_type)
        return Quiz(
            concept,
            cast(Language, question_language),
            cast(Language, answer_language),
            Label(question),
            tuple(Label(answer) for answer in answers),
            quiz_type,
            blocked_by,
            Labels(Label(meaning) for meaning in meanings),
        )
