"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import CARDINAL, DICTATE, ORDINAL

from .....base import NL_EN, ToistoTestCase


class NumberTest(ToistoTestCase):
    """Unit tests for numbers."""

    def test_numbers(self):
        """Test that quizzes can be generated for numbers."""
        concept = self.create_concept(
            "one", labels=[{"label": {"cardinal": "een", "ordinal": "eerste"}, "language": NL}]
        )
        een, eerste = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(NL_EN, concept, een, [een], DICTATE),
                self.create_quiz(NL_EN, concept, eerste, [eerste], DICTATE),
                self.create_quiz(NL_EN, concept, een, [eerste], ORDINAL),
                self.create_quiz(NL_EN, concept, eerste, [een], CARDINAL),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_numbers_and_translations(self):
        """Test that quizzes can be generated for numbers."""
        concept = self.create_concept(
            "one",
            labels=[
                {"label": {"cardinal": "one", "ordinal": "first"}, "language": EN},
                {"label": {"cardinal": "een", "ordinal": "eerste"}, "language": NL},
            ],
        )
        een, eerste = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(NL_EN, concept)
            | {
                self.create_quiz(NL_EN, concept, eerste, [een], CARDINAL),
                self.create_quiz(NL_EN, concept, een, [eerste], ORDINAL),
            },
            create_quizzes(NL_EN, (), concept),
        )
