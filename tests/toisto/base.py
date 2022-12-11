"""Base class for unit tests."""

from typing import cast
import unittest

from toisto.metadata import Language
from toisto.model import Label, Labels, Quiz
from toisto.model.model_types import ConceptId
from toisto.model.quiz.quiz import QuizType


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    @staticmethod
    def create_quiz(  # pylint: disable=too-many-arguments
        concept_id: ConceptId,
        question_language: str,
        answer_language: str,
        question: str,
        answers: list[str],
        quiz_type: str | tuple[str] = "translate",
        uses: tuple[ConceptId, ...] = tuple(),
        meanings: tuple[str, ...] = tuple()
    ) -> Quiz:
        """Create a quiz."""
        quiz_type = cast(tuple[QuizType], (quiz_type,) if isinstance(quiz_type, str) else quiz_type)
        return Quiz(
            concept_id,
            cast(Language, question_language),
            cast(Language, answer_language),
            Label(question),
            tuple(Label(answer) for answer in answers),
            quiz_type,
            uses,
            Labels(Label(meaning) for meaning in meanings)
        )
