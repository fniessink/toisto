"""Base class for unit tests."""

from typing import cast
import unittest

from toisto.metadata import Language
from toisto.model import Label, Quiz
from toisto.model.quiz.quiz import QuizType


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    @staticmethod
    def create_quiz(
        question_language: str,
        answer_language: str,
        question: str,
        answers: list[str],
        quiz_type: str = "translate"
    ) -> Quiz:
        """Create a quiz."""
        return Quiz(
            cast(Language, question_language),
            cast(Language, answer_language),
            Label(question),
            tuple(Label(answer) for answer in answers),
            cast(QuizType, quiz_type)
        )
