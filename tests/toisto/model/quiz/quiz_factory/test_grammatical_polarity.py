"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import AFFIRMATIVE, DICTATE, INTERPRET, NEGATIVE, ORDER, READ, WRITE

from .....base import NL_EN, ToistoTestCase


class GrammaticalPolarityTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical polarities."""

    def test_affirmative_and_negative_polarities(self):
        """Test that quizzes can be generated for the affirmative and negative polarities."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": {"affirmative": "The car is black.", "negative": "The car is not black."}, "language": EN},
                {"label": {"affirmative": "De auto is zwart.", "negative": "De auto is niet zwart."}, "language": NL},
            ],
        )
        de_auto_is_zwart, de_auto_is_niet_zwart = concept.labels(NL)
        the_car_is_black, the_car_is_not_black = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, de_auto_is_zwart, [the_car_is_black], READ),
                self.create_quiz(concept, de_auto_is_zwart, [de_auto_is_zwart], DICTATE),
                self.create_quiz(concept, de_auto_is_zwart, [the_car_is_black], INTERPRET),
                self.create_quiz(concept, the_car_is_black, [de_auto_is_zwart], WRITE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [the_car_is_not_black], READ),
                self.create_quiz(concept, de_auto_is_niet_zwart, [de_auto_is_niet_zwart], DICTATE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [the_car_is_not_black], INTERPRET),
                self.create_quiz(concept, the_car_is_not_black, [de_auto_is_niet_zwart], WRITE),
                self.create_quiz(concept, de_auto_is_zwart, [de_auto_is_niet_zwart], NEGATIVE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [de_auto_is_zwart], AFFIRMATIVE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [de_auto_is_niet_zwart], ORDER),
            },
            create_quizzes(NL_EN, (), concept),
        )
