"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    DICTATE,
    FEMININE,
    FIRST_PERSON,
    INTERPRET,
    MASCULINE,
    READ,
    SECOND_PERSON,
    THIRD_PERSON,
    WRITE,
    GrammaticalQuizType,
)

from .....base import FI_EN, NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalPersonQuizzesTest(QuizFactoryTestCase):
    """Unit tests for grammatical person quizzes."""

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = self.create_verb_with_person()
        ik_eet, jij_eet, zij_eet = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(NL_EN, concept)
            | {
                self.create_quiz(NL_EN, concept, ik_eet, [jij_eet], SECOND_PERSON),
                self.create_quiz(NL_EN, concept, ik_eet, [zij_eet], THIRD_PERSON),
                self.create_quiz(NL_EN, concept, jij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(NL_EN, concept, jij_eet, [zij_eet], THIRD_PERSON),
                self.create_quiz(NL_EN, concept, zij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(NL_EN, concept, zij_eet, [jij_eet], SECOND_PERSON),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        concept = self.create_concept(
            "to eat",
            labels=[
                {
                    "label": {
                        "first person": "I eat",
                        "second person": "you eat",
                        "third person": {"feminine": "she eats", "masculine": "he eats"},
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "first person": "ik eet",
                        "second person": "jij eet",
                        "third person": {"feminine": "zij eet", "masculine": "hij eet"},
                    },
                    "language": NL,
                },
            ],
        )
        ik_eet, jij_eet, zij_eet, hij_eet = concept.labels(NL)
        third_person_feminine = GrammaticalQuizType("feminine third person")
        third_person_masculine = GrammaticalQuizType("masculine third person")
        self.assertSetEqual(
            self.translation_quizzes(NL_EN, concept)
            | {
                self.create_quiz(NL_EN, concept, zij_eet, [hij_eet], MASCULINE),
                self.create_quiz(NL_EN, concept, hij_eet, [zij_eet], FEMININE),
                self.create_quiz(NL_EN, concept, ik_eet, [jij_eet], SECOND_PERSON),
                self.create_quiz(NL_EN, concept, ik_eet, [zij_eet], third_person_feminine),
                self.create_quiz(NL_EN, concept, ik_eet, [hij_eet], third_person_masculine),
                self.create_quiz(NL_EN, concept, jij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(NL_EN, concept, jij_eet, [zij_eet], third_person_feminine),
                self.create_quiz(NL_EN, concept, jij_eet, [hij_eet], third_person_masculine),
                self.create_quiz(NL_EN, concept, zij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(NL_EN, concept, zij_eet, [jij_eet], SECOND_PERSON),
                self.create_quiz(NL_EN, concept, hij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(NL_EN, concept, hij_eet, [jij_eet], SECOND_PERSON),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_grammatical_person_nested_with_grammatical_gender_in_one_language_but_not_the_other(self):
        """Test quizzes for grammatical person nested with grammatical gender in one language but not the other."""
        concept = self.create_concept(
            "to eat",
            labels=[
                {
                    "label": {
                        "first person": "I eat",
                        "second person": "you eat",
                        "third person": {"feminine": "she eats", "masculine": "he eats"},
                    },
                    "language": EN,
                },
                {
                    "label": {"first person": "minä syön", "second person": "sinä syöt", "third person": "hän syö"},
                    "language": FI,
                },
            ],
        )
        syön, syöt, syö = concept.labels(FI)
        i_eat, you_eat, she_eats, he_eats = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(FI_EN, concept, syön, [i_eat], READ),
                self.create_quiz(FI_EN, concept, syön, [syön], DICTATE),
                self.create_quiz(FI_EN, concept, syön, [i_eat], INTERPRET),
                self.create_quiz(FI_EN, concept, i_eat, [syön], WRITE),
                self.create_quiz(FI_EN, concept, syöt, [you_eat], READ),
                self.create_quiz(FI_EN, concept, syöt, [syöt], DICTATE),
                self.create_quiz(FI_EN, concept, syöt, [you_eat], INTERPRET),
                self.create_quiz(FI_EN, concept, you_eat, [syöt], WRITE),
                self.create_quiz(FI_EN, concept, syö, [she_eats, he_eats], READ),
                self.create_quiz(FI_EN, concept, syö, [syö], DICTATE),
                self.create_quiz(FI_EN, concept, syö, [she_eats, he_eats], INTERPRET),
                self.create_quiz(FI_EN, concept, she_eats, [syö], WRITE),
                self.create_quiz(FI_EN, concept, he_eats, [syö], WRITE),
                self.create_quiz(FI_EN, concept, syön, [syöt], SECOND_PERSON),
                self.create_quiz(FI_EN, concept, syön, [syö], THIRD_PERSON),
                self.create_quiz(FI_EN, concept, syöt, [syön], FIRST_PERSON),
                self.create_quiz(FI_EN, concept, syöt, [syö], THIRD_PERSON),
                self.create_quiz(FI_EN, concept, syö, [syön], FIRST_PERSON),
                self.create_quiz(FI_EN, concept, syö, [syöt], SECOND_PERSON),
            },
            create_quizzes(FI_EN, (), concept),
        )
