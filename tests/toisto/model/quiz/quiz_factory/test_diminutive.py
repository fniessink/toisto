"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, DIMINUTIVE, INTERPRET, READ, WRITE

from .....base import NL_EN, NL_FI, ToistoTestCase


class DiminutiveTest(ToistoTestCase):
    """Unit tests for diminutive forms."""

    def test_diminutive_one_language(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = self.create_concept(
            "car", labels=[{"label": {"root": "de auto", "diminutive": "het autootje"}, "language": NL}]
        )
        auto, autootje = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, auto, [auto], DICTATE),
                self.create_quiz(concept, autootje, [autootje], DICTATE),
                self.create_quiz(concept, auto, [autootje], DIMINUTIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_diminutive_two_languages(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": {"root": "de auto", "diminutive": "het autootje"}, "language": NL},
                {"label": {"root": "auto", "diminutive": "pikkuauto"}, "language": FI},
            ],
        )
        de_auto, autootje = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, FI) | {self.create_quiz(concept, de_auto, [autootje], DIMINUTIVE)},
            create_quizzes(NL_FI, (), concept),
        )

    def test_diminutive_in_one_language_but_not_the_other(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": "car", "language": EN},
                {"label": {"root": "de auto", "diminutive": "het autootje"}, "language": NL},
            ],
        )
        (car,) = concept.labels(EN)
        auto, autootje = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, auto, [car], READ),
                self.create_quiz(concept, auto, [auto], DICTATE),
                self.create_quiz(concept, auto, [car], INTERPRET),
                self.create_quiz(concept, car, [auto], WRITE),
                self.create_quiz(concept, autootje, [autootje], DICTATE),
                self.create_quiz(concept, autootje, [car], READ),
                self.create_quiz(concept, auto, [autootje], DIMINUTIVE),
                self.create_quiz(concept, autootje, [car], INTERPRET),
            },
            create_quizzes(NL_EN, (), concept),
        )
