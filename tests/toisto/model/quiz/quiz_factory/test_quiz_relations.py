"""Unit tests for quiz relations that the quiz factory creates."""

from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import GrammaticalQuizType, ListenOnlyQuizType, TranslationQuizType

from .....base import FI_NL
from .quiz_factory_test_case import QuizFactoryTestCase


class QuizRelationsTest(QuizFactoryTestCase):
    """Unit tests for the quiz relations that the quiz factory creates."""

    def test_translation_quizzes_block_listening_quizzes(self):
        """Test that translation quizzes block listening quizzes."""
        quizzes = create_quizzes(FI_NL, (), self.create_noun())
        translation_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(TranslationQuizType))
        listening_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(ListenOnlyQuizType))
        for quiz in listening_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(translation_quizzes)))

    def test_non_grammatical_quizzes_block_grammatical_quizzes(self):
        """Test that listening and translation quizzes block grammatical quizzes."""
        quizzes = create_quizzes(FI_NL, (), self.create_noun_with_grammatical_number())
        grammatical_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(GrammaticalQuizType))
        non_grammatical_quizzes = quizzes - grammatical_quizzes
        for quiz in grammatical_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(non_grammatical_quizzes)))

    def test_earlier_grammatical_quizzes_block_later_grammatical_quizzes(self):
        """Test that e.g. quizzes for singular forms are blocked by quizzes for plural forms."""
        quizzes = create_quizzes(FI_NL, (), self.create_noun_with_grammatical_number())
        singular_quizzes = {quiz for quiz in quizzes if "singular" in quiz.instruction}
        plural_quizzes = {quiz for quiz in quizzes if "plural" in quiz.instruction}
        for quiz in singular_quizzes:
            self.assertTrue(quiz.is_blocked_by(Quizzes(plural_quizzes)))
