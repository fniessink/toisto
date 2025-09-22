"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import FEMININE, MASCULINE, NEUTER, PLURAL, SINGULAR

from .....base import NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalGenderQuizzesTest(QuizFactoryTestCase):
    """Unit tests for grammatical gender quizzes."""

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for feminine and masculine grammatical genders."""
        concept = self.create_noun_with_grammatical_gender()
        haar_kat, zijn_kat = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, haar_kat, [zijn_kat], MASCULINE),
                self.create_quiz(concept, zijn_kat, [haar_kat], FEMININE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different feminine, masculine, and neuter grammatical genders."""
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        haar_bot, zijn_bot, _ = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, haar_bot, [zijn_bot], MASCULINE),
                self.create_quiz(concept, haar_bot, [zijn_bot], NEUTER),
                self.create_quiz(concept, zijn_bot, [haar_bot], FEMININE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        concept = self.create_concept(
            "cat",
            labels=[
                {
                    "label": {
                        "feminine": {"singular": "her cat", "plural": "her cats"},
                        "masculine": {"singular": "his cat", "plural": "his cats"},
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "feminine": {"singular": "haar kat", "plural": "haar katten"},
                        "masculine": {"singular": "zijn kat", "plural": "zijn katten"},
                    },
                    "language": NL,
                },
            ],
        )
        haar_kat, haar_katten, zijn_kat, zijn_katten = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, haar_kat, [haar_katten], PLURAL),
                self.create_quiz(concept, haar_katten, [haar_kat], SINGULAR),
                self.create_quiz(concept, zijn_kat, [zijn_katten], PLURAL),
                self.create_quiz(concept, zijn_katten, [zijn_kat], SINGULAR),
                self.create_quiz(concept, haar_kat, [zijn_kat], MASCULINE),
                self.create_quiz(concept, zijn_kat, [haar_kat], FEMININE),
                self.create_quiz(concept, haar_katten, [zijn_katten], MASCULINE),
                self.create_quiz(concept, zijn_katten, [haar_katten], FEMININE),
            },
            create_quizzes(NL_EN, (), concept),
        )
