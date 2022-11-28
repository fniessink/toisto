"""Base class for unit tests."""

from typing import cast
import unittest

from toisto.metadata import Language
from toisto.model import Label, Quiz
from toisto.model.types import ConceptId
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
        quiz_type: str = "translate",
        uses: tuple[ConceptId, ...] = tuple(),
        meaning: str = ""
    ) -> Quiz:
        """Create a quiz."""
        return Quiz(
            concept_id,
            cast(Language, question_language),
            cast(Language, answer_language),
            Label(question),
            tuple(Label(answer) for answer in answers),
            cast(QuizType, quiz_type),
            uses,
            Label(meaning)
        )
