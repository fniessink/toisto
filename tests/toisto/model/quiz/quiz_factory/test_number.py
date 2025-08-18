"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import CARDINAL, DICTATE, INTERPRET, ORDINAL, READ, WRITE

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
                self.create_quiz(concept, een, [een], DICTATE),
                self.create_quiz(concept, eerste, [eerste], DICTATE),
                self.create_quiz(concept, een, [eerste], ORDINAL),
                self.create_quiz(concept, eerste, [een], CARDINAL),
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
        one, first_ = concept.labels(EN)
        een, eerste = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, een, [one], READ),
                self.create_quiz(concept, een, [een], DICTATE),
                self.create_quiz(concept, een, [one], INTERPRET),
                self.create_quiz(concept, one, [een], WRITE),
                self.create_quiz(concept, eerste, [first_], READ),
                self.create_quiz(concept, eerste, [eerste], DICTATE),
                self.create_quiz(concept, eerste, [first_], INTERPRET),
                self.create_quiz(concept, first_, [eerste], WRITE),
                self.create_quiz(concept, eerste, [een], CARDINAL),
                self.create_quiz(concept, een, [eerste], ORDINAL),
            },
            create_quizzes(NL_EN, (), concept),
        )
