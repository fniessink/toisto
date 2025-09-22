"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DECLARATIVE, IMPERATIVE, INTERROGATIVE

from .....base import NL_EN, ToistoTestCase


class GrammaticalMoodTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical moods."""

    def test_declarative_and_interrogative_moods(self):
        """Test that quizzes can be generated for the declarative and interrogative moods."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": {"declarative": "The car is black.", "interrogative": "Is the car black?"}, "language": EN},
                {"label": {"declarative": "De auto is zwart.", "interrogative": "Is de auto zwart?"}, "language": NL},
            ],
        )
        de_auto_is_zwart, is_de_auto_zwart = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, de_auto_is_zwart, [is_de_auto_zwart], INTERROGATIVE),
                self.create_quiz(concept, is_de_auto_zwart, [de_auto_is_zwart], DECLARATIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_declarative_and_imperative_moods(self):
        """Test that quizzes can be generated for the declarative and imperative moods."""
        concept = self.create_concept(
            "you run",
            labels=[
                {"label": {"declarative": "You run.", "imperative": "Run!"}, "language": EN},
                {"label": {"declarative": "Jij rent.", "imperative": "Ren!"}, "language": NL},
            ],
        )
        jij_rent, ren = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, jij_rent, [ren], IMPERATIVE),
                self.create_quiz(concept, ren, [jij_rent], DECLARATIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_declarative_interrogative_and_imperative_moods(self):
        """Test that quizzes can be generated for the declarative, interrogative, and imperative moods."""
        concept = self.create_concept(
            "you run",
            labels=[
                {
                    "label": {"declarative": "You run.", "interrogative": "Do you run?", "imperative": "Run!"},
                    "language": EN,
                },
                {
                    "label": {"declarative": "Jij rent.", "interrogative": "Ren jij?", "imperative": "Ren!"},
                    "language": NL,
                },
            ],
        )
        jij_rent, ren_jij, ren = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, jij_rent, [ren], IMPERATIVE),
                self.create_quiz(concept, jij_rent, [ren_jij], INTERROGATIVE),
                self.create_quiz(concept, ren, [jij_rent], DECLARATIVE),
                self.create_quiz(concept, ren, [ren_jij], INTERROGATIVE),
                self.create_quiz(concept, ren_jij, [ren], IMPERATIVE),
                self.create_quiz(concept, ren_jij, [jij_rent], DECLARATIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )
