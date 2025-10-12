"""Quiz factory unit tests."""

from toisto.model.language import NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import ABBREVIATION, DICTATE, FULL_FORM

from .....base import NL_EN, ToistoTestCase


class AbbreviationQuizzesTest(ToistoTestCase):
    """Unit tests for abbreviation quizzes."""

    def test_abbreviations(self):
        """Test that quizzes can be generated for abbreviations."""
        concept = self.create_concept(
            "llc", labels=[{"label": {"full form": "naamloze vennootschap", "abbreviation": "NV"}, "language": NL}]
        )
        naamloze_vennootschap, nv = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(NL_EN, concept, naamloze_vennootschap, [naamloze_vennootschap], DICTATE),
                self.create_quiz(NL_EN, concept, nv, [nv], DICTATE),
                self.create_quiz(NL_EN, concept, naamloze_vennootschap, [nv], ABBREVIATION),
                self.create_quiz(NL_EN, concept, nv, [naamloze_vennootschap], FULL_FORM),
            },
            create_quizzes(NL_EN, (), concept),
        )
