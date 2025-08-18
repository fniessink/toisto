"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, FEMININE, INTERPRET, MASCULINE, NEUTER, PLURAL, READ, SINGULAR, WRITE

from .....base import NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalGenderQuizzesTest(QuizFactoryTestCase):
    """Unit tests for grammatical gender quizzes."""

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for feminine and masculine grammatical genders."""
        concept = self.create_noun_with_grammatical_gender()
        haar_kat, zijn_kat = concept.labels(NL)
        her_cat, his_cat = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, haar_kat, [her_cat], READ),
                self.create_quiz(concept, haar_kat, [haar_kat], DICTATE),
                self.create_quiz(concept, haar_kat, [her_cat], INTERPRET),
                self.create_quiz(concept, her_cat, [haar_kat], WRITE),
                self.create_quiz(concept, zijn_kat, [his_cat], READ),
                self.create_quiz(concept, zijn_kat, [zijn_kat], DICTATE),
                self.create_quiz(concept, zijn_kat, [his_cat], INTERPRET),
                self.create_quiz(concept, his_cat, [zijn_kat], WRITE),
                self.create_quiz(concept, haar_kat, [zijn_kat], MASCULINE),
                self.create_quiz(concept, zijn_kat, [haar_kat], FEMININE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different feminine, masculine, and neuter grammatical genders."""
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        haar_bot, zijn_bot, _ = concept.labels(NL)
        her_bone, his_bone, its_bone = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, haar_bot, [her_bone], READ),
                self.create_quiz(concept, haar_bot, [haar_bot], DICTATE),
                self.create_quiz(concept, haar_bot, [her_bone], INTERPRET),
                self.create_quiz(concept, her_bone, [haar_bot], WRITE),
                self.create_quiz(concept, zijn_bot, [his_bone], READ),
                self.create_quiz(concept, zijn_bot, [zijn_bot], DICTATE),
                self.create_quiz(concept, zijn_bot, [his_bone], INTERPRET),
                self.create_quiz(concept, his_bone, [zijn_bot], WRITE),
                self.create_quiz(concept, zijn_bot, [its_bone], READ),
                self.create_quiz(concept, zijn_bot, [zijn_bot], DICTATE),
                self.create_quiz(concept, zijn_bot, [its_bone], INTERPRET),
                self.create_quiz(concept, its_bone, [zijn_bot], WRITE),
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
        her_cat, her_cats, his_cat, his_cats = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, haar_kat, [her_cat], READ),
                self.create_quiz(concept, haar_kat, [haar_kat], DICTATE),
                self.create_quiz(concept, haar_kat, [her_cat], INTERPRET),
                self.create_quiz(concept, her_cat, [haar_kat], WRITE),
                self.create_quiz(concept, haar_katten, [her_cats], READ),
                self.create_quiz(concept, haar_katten, [haar_katten], DICTATE),
                self.create_quiz(concept, haar_katten, [her_cats], INTERPRET),
                self.create_quiz(concept, her_cats, [haar_katten], WRITE),
                self.create_quiz(concept, haar_kat, [haar_katten], PLURAL),
                self.create_quiz(concept, haar_katten, [haar_kat], SINGULAR),
                self.create_quiz(concept, zijn_kat, [his_cat], READ),
                self.create_quiz(concept, zijn_kat, [zijn_kat], DICTATE),
                self.create_quiz(concept, zijn_kat, [his_cat], INTERPRET),
                self.create_quiz(concept, his_cat, [zijn_kat], WRITE),
                self.create_quiz(concept, zijn_katten, [his_cats], READ),
                self.create_quiz(concept, zijn_katten, [zijn_katten], DICTATE),
                self.create_quiz(concept, zijn_katten, [his_cats], INTERPRET),
                self.create_quiz(concept, his_cats, [zijn_katten], WRITE),
                self.create_quiz(concept, zijn_kat, [zijn_katten], PLURAL),
                self.create_quiz(concept, zijn_katten, [zijn_kat], SINGULAR),
                self.create_quiz(concept, haar_kat, [zijn_kat], MASCULINE),
                self.create_quiz(concept, zijn_kat, [haar_kat], FEMININE),
                self.create_quiz(concept, haar_katten, [zijn_katten], MASCULINE),
                self.create_quiz(concept, zijn_katten, [haar_katten], FEMININE),
            },
            create_quizzes(NL_EN, (), concept),
        )
