"""Quiz factory filter unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    DICTATE,
    FEMININE,
    INTERPRET,
    MASCULINE,
    PLURAL,
    READ,
    SINGULAR,
    WRITE,
)

from ....base import FI_NL, NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class FilterByQuizTypeTest(QuizFactoryTestCase):
    """Unit tests for limiting the quiz types created."""

    def test_filter_quizzes(self):
        """Test that quizzes can be limited to certain quiz types."""
        concept = self.create_concept(
            "english", labels=[{"label": "English", "language": EN}, {"label": "Engels", "language": NL}]
        )
        (english,) = concept.labels(EN)
        (engels,) = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, engels, [english], READ),
                self.create_quiz(concept, english, [engels], WRITE),
            },
            create_quizzes(NL_EN, (READ, WRITE), concept),
        )
        self.assertSetEqual(
            {
                self.create_quiz(concept, engels, [engels], DICTATE),
                self.create_quiz(concept, engels, [english], INTERPRET),
            },
            create_quizzes(NL_EN, (DICTATE, INTERPRET), concept),
        )

    def test_filter_grammatical_number(self):
        """Test that quizzes can be filtered for plural and singular quiz types."""
        concept = self.create_noun_with_grammatical_number()
        aamu, aamut = concept.labels(FI)
        self.assertSetEqual(
            {self.create_quiz(concept, aamut, [aamu], SINGULAR)},
            create_quizzes(FI_NL, (SINGULAR,), concept),
        )
        self.assertSetEqual(
            {self.create_quiz(concept, aamu, [aamut], PLURAL)},
            create_quizzes(FI_NL, (PLURAL,), concept),
        )

    def test_filter_grammatical_gender(self):
        """Test that quizzes can be generated for feminine and masculine grammatical genders."""
        concept = self.create_noun_with_grammatical_gender()
        haar_kat, zijn_kat = concept.labels(NL)
        self.assertSetEqual(
            {self.create_quiz(concept, haar_kat, [zijn_kat], MASCULINE)},
            create_quizzes(NL_EN, (MASCULINE,), concept),
        )
        self.assertSetEqual(
            {self.create_quiz(concept, zijn_kat, [haar_kat], FEMININE)},
            create_quizzes(NL_EN, (FEMININE,), concept),
        )
