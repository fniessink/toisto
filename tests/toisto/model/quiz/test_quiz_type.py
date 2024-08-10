"""Quiz type unit tests."""

from toisto.model.quiz.quiz_type import ANTONYM, PLURAL, THIRD_PERSON, GrammaticalQuizType

from ....base import ToistoTestCase


class GrammaticalQuizTypeTest(ToistoTestCase):
    """Unit tests for the grammatical quiz type."""

    def test_is_quiz_type(self):
        """Test that the grammatical quiz type is indeed a grammatical quiz type."""
        self.assertTrue(PLURAL.is_quiz_type(PLURAL))

    def test_is_not_quiz_type(self):
        """Test that the grammatical quiz type is not a semantical quiz type."""
        self.assertFalse(PLURAL.is_quiz_type(ANTONYM))

    def test_composite_is_quiz_type(self):
        """Test that a composite grammatical quiz type is indeed a grammatical quiz type."""
        self.assertTrue(GrammaticalQuizType(quiz_types=(PLURAL, THIRD_PERSON)).is_quiz_type(PLURAL))

    def test_composite_is_not_quiz_type(self):
        """Test a composite grammatical quiz type is not a semantical quiz type."""
        self.assertFalse(GrammaticalQuizType(quiz_types=(PLURAL, THIRD_PERSON)).is_quiz_type(ANTONYM))
