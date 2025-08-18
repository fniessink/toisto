"""Quiz factory unit tests."""

from toisto.model.language import EN
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import ORDER
from toisto.tools import first

from .....base import EN_NL
from .quiz_factory_test_case import QuizFactoryTestCase


class OrderQuizTest(QuizFactoryTestCase):
    """Unit tests for generating order quizzes."""

    def test_generate_order_quiz_for_long_enough_sentences(self):
        """Test that order quizzes are generated for long enough sentences."""
        concept = self.create_concept(
            "breakfast", labels=[{"label": "We eat breakfast in the kitchen.", "language": EN}]
        )
        quizzes = create_quizzes(EN_NL, (ORDER,), concept)
        quiz = first(quizzes)
        self.assertEqual(ORDER, quiz.quiz_type)
