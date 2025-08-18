"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, INFINITIVE, INTERPRET, PLURAL, READ, SINGULAR, WRITE

from .....base import EN_FI, FI_EN, NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class QuizFactoryTest(QuizFactoryTestCase):
    """Unit tests for creating quizzes."""

    def test_quizzes(self):
        """Test that quizzes can be generated from a concept."""
        concept = self.create_concept(
            "english", labels=[{"label": "English", "language": EN}, {"label": "Engels", "language": NL}]
        )
        (engels,) = concept.labels(NL)
        (english,) = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, engels, [english], READ),
                self.create_quiz(concept, engels, [engels], DICTATE),
                self.create_quiz(concept, engels, [english], INTERPRET),
                self.create_quiz(concept, english, [engels], WRITE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_only_listening_quizzes_for_one_language(self):
        """Test that only listening quizzes are generated for a concept with one language."""
        concept = self.create_concept("english", labels=[{"label": "Engels", "language": NL}])
        (engels,) = concept.labels(NL)
        self.assertSetEqual(
            {self.create_quiz(concept, engels, [engels], DICTATE)},
            create_quizzes(NL_EN, (), concept),
        )

    def test_answer_only_concept(self):
        """Test that no quizzes are generated for an answer-only concept."""
        concept = self.create_concept(
            "yes, i do like something",
            {"answer-only": True},
            labels=[{"label": "Yes, I do.", "language": EN}, {"label": "Pidän", "language": FI}],
        )
        self.assertSetEqual(Quizzes(), create_quizzes(EN_FI, (), concept))

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        concept = self.create_concept(
            "couch",
            labels=[
                {"label": "bank", "language": NL},
                {"label": "couch", "language": EN},
                {"label": "bank", "language": EN},
            ],
        )
        (bank_nl,) = concept.labels(NL)
        couch, bank_en = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, bank_nl, [couch, bank_en], READ),
                self.create_quiz(concept, bank_nl, [bank_nl], DICTATE),
                self.create_quiz(concept, bank_nl, [couch, bank_en], INTERPRET),
                self.create_quiz(concept, couch, [bank_nl], WRITE),
                self.create_quiz(concept, bank_en, [bank_nl], WRITE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_missing_language(self):
        """Test that no quizzes are generated from a concept if it's missing one of the languages."""
        concept = self.create_concept(
            "english", labels=[{"label": "English", "language": EN}, {"label": "Engels", "language": NL}]
        )
        self.assertSetEqual(Quizzes(), create_quizzes(FI_EN, (), concept))

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        concept = self.create_concept(
            "to be",
            labels=[
                {"label": {"feminine": ["she is", "she's"], "masculine": ["he is", "he's"]}, "language": EN},
                {"label": {"feminine": "hän on", "masculine": "hän on"}, "language": FI},
            ],
        )
        hän_on, _ = concept.labels(FI)
        she_is, he_is = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, hän_on, [she_is], READ),
                self.create_quiz(concept, hän_on, [hän_on], DICTATE),
                self.create_quiz(concept, hän_on, [she_is], INTERPRET),
                self.create_quiz(concept, she_is, [hän_on], WRITE),
                self.create_quiz(concept, hän_on, [he_is], READ),
                self.create_quiz(concept, hän_on, [hän_on], DICTATE),
                self.create_quiz(concept, hän_on, [he_is], INTERPRET),
                self.create_quiz(concept, he_is, [hän_on], WRITE),
                self.create_quiz(concept, hän_on, [he_is], INTERPRET),
            },
            create_quizzes(FI_EN, (), concept),
        )

    def test_infinitive_verb_form(self):
        """Test the infinitive verb form."""
        concept = self.create_verb_with_infinitive_and_person()
        slapen, ik_slaap, wij_slapen = concept.labels(NL)
        to_sleep, i_sleep, we_sleep = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, slapen, [to_sleep], READ),
                self.create_quiz(concept, slapen, [slapen], DICTATE),
                self.create_quiz(concept, slapen, [to_sleep], INTERPRET),
                self.create_quiz(concept, to_sleep, [slapen], WRITE),
                self.create_quiz(concept, ik_slaap, [i_sleep], READ),
                self.create_quiz(concept, ik_slaap, [ik_slaap], DICTATE),
                self.create_quiz(concept, ik_slaap, [i_sleep], INTERPRET),
                self.create_quiz(concept, i_sleep, [ik_slaap], WRITE),
                self.create_quiz(concept, wij_slapen, [we_sleep], READ),
                self.create_quiz(concept, wij_slapen, [wij_slapen], DICTATE),
                self.create_quiz(concept, wij_slapen, [we_sleep], INTERPRET),
                self.create_quiz(concept, we_sleep, [wij_slapen], WRITE),
                self.create_quiz(concept, wij_slapen, [slapen], INFINITIVE),
                self.create_quiz(concept, ik_slaap, [slapen], INFINITIVE),
                self.create_quiz(concept, slapen, [wij_slapen], PLURAL),
                self.create_quiz(concept, ik_slaap, [wij_slapen], PLURAL),
                self.create_quiz(concept, slapen, [ik_slaap], SINGULAR),
                self.create_quiz(concept, wij_slapen, [ik_slaap], SINGULAR),
            },
            create_quizzes(NL_EN, (), concept),
        )
