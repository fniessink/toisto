"""Base class for unit tests."""

import unittest
from typing import cast

from toisto.model.language import Language
from toisto.model.language.concept import Concept
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz import Quiz, QuizType


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    def setUp(self):
        """Override to reset the Concept instances registry."""
        Concept.instances.clear()

    @staticmethod
    def create_quiz(  # noqa: PLR0913
        concept: Concept,
        question_language: str,
        answer_language: str,
        question: str,
        answers: list[str],
        quiz_type: str | tuple[str, ...] = ("read",),
        blocked_by: tuple[Quiz, ...] = tuple(),
        question_meanings: tuple[str, ...] = tuple(),
        answer_meanings: tuple[str, ...] = tuple(),
    ) -> Quiz:
        """Create a quiz."""
        quiz_type = cast(tuple[QuizType], (quiz_type,) if isinstance(quiz_type, str) else quiz_type)
        question_language = cast(Language, question_language)
        answer_language = cast(Language, answer_language)
        return Quiz(
            concept,
            question_language,
            answer_language,
            Label(question_language, question),
            tuple(Label(answer_language, answer) for answer in answers),
            quiz_type,
            blocked_by,
            Labels(Label(question_language, meaning) for meaning in question_meanings),
            Labels(Label(answer_language, meaning) for meaning in answer_meanings),
        )

    @classmethod
    def copy_quiz(  # noqa: PLR0913
        cls,
        quiz: Quiz,
        question_language: str = "",
        answer_language: str = "",
        question: str = "",
        answers: list[str] | None = None,
        quiz_type: str | tuple[str, ...] = "",
    ) -> Quiz:
        """Copy the quiz, overriding some of its parameters."""
        return cls.create_quiz(
            quiz.concept,
            question_language or quiz.question_language,
            answer_language or quiz.answer_language,
            question or quiz.question,
            answers or [str(answer) for answer in quiz.answers],
            quiz_type or tuple(str(quiz_type) for quiz_type in quiz.quiz_types),
            quiz.blocked_by,
            quiz.answer_meanings,
            quiz.question_meanings,
        )
