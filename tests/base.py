"""Base class for unit tests."""

import unittest
from typing import cast

from toisto.model.language import Language
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptDict, ConceptFactory
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz import Quiz, QuizType, Quizzes
from toisto.model.quiz.quiz_factory import QuizFactory


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
    def create_quiz(  # noqa: PLR0913
        concept: Concept,
        question_language: str,
        answer_language: str,
        question: str,
        answers: list[str],
        quiz_type: str | tuple[str, ...] = ("read",),
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
            quiz.meanings,
        )
