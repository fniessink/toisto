"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, INTERPRET

from .....base import EN_NL, FI_EN, FI_NL, ToistoTestCase


class MeaningsTest(ToistoTestCase):
    """Test that quizzes have the correct meaning."""

    def test_interpret_with_synonym(self):
        """Test that interpret quizzes show all synonyms as meaning."""
        concept = self.create_concept(
            "yes",
            labels=[
                {"label": "kylla", "language": FI},
                {"label": "joo", "language": FI},
                {"label": "yes", "language": EN},
            ],
        )
        interpret_quizzes = create_quizzes(FI_EN, (INTERPRET,), concept)
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kylla"), Label(FI, "joo")), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)

    def test_interpret_with_colloquial(self):
        """Test that interpret quizzes don't show colloquial labels as meaning."""
        concept = self.create_concept(
            "20",
            labels=[
                {"label": "kaksikymmentä", "language": FI},
                {"label": "kakskyt", "language": FI, "colloquial": True},
                {"label": "twintig", "language": NL},
            ],
        )
        interpret_quizzes = create_quizzes(FI_NL, (INTERPRET,), concept)
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kaksikymmentä"),), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)

    def test_dictate_with_plural(self):
        """Test that the meaning of a quiz that dictates a singular does not include plural."""
        concept = self.create_concept(
            "table",
            labels=[
                {"label": {"singular": "table", "plural": "tables"}, "language": EN},
                {"label": {"singular": "de tafel", "plural": "de tafels"}, "language": NL},
            ],
        )
        dictate_quizzes = create_quizzes(EN_NL, (DICTATE,), concept)
        for quiz in dictate_quizzes:
            self.assertEqual(
                ("de tafel",) if str(quiz.question) == "table" else ("de tafels",),
                tuple(str(meaning) for meaning in quiz.question_meanings),
            )
