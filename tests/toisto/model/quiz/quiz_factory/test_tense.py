"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    DICTATE,
    FIRST_PERSON,
    INFINITIVE,
    INTERPRET,
    PAST_TENSE,
    PLURAL,
    PRESENT_TENSE,
    READ,
    SECOND_PERSON,
    SINGULAR,
    THIRD_PERSON,
    WRITE,
)

from .....base import NL_EN, NL_FI
from .quiz_factory_test_case import OLLA_PRESENT_TENSE, ZIJN_PRESENT_TENSE, QuizFactoryTestCase


class TenseQuizzesTest(QuizFactoryTestCase):
    """Unit tests for concepts with tenses."""

    def test_present_and_past_tense_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for present and past tense nested with grammatical person."""
        concept = self.create_verb_with_tense_and_person()
        en = concept.labels(EN)
        nl = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, nl.ik_eet, [en.i_eat], READ),
                self.create_quiz(concept, nl.ik_eet, [nl.ik_eet], DICTATE),
                self.create_quiz(concept, nl.ik_eet, [en.i_eat], INTERPRET),
                self.create_quiz(concept, en.i_eat, [nl.ik_eet], WRITE),
                self.create_quiz(concept, nl.wij_eten, [en.we_eat], READ),
                self.create_quiz(concept, nl.wij_eten, [nl.wij_eten], DICTATE),
                self.create_quiz(concept, nl.wij_eten, [en.we_eat], INTERPRET),
                self.create_quiz(concept, en.we_eat, [nl.wij_eten], WRITE),
                self.create_quiz(concept, nl.ik_eet, [nl.wij_eten], PLURAL),
                self.create_quiz(concept, nl.wij_eten, [nl.ik_eet], SINGULAR),
                self.create_quiz(concept, nl.ik_at, [en.i_ate], READ),
                self.create_quiz(concept, nl.ik_at, [nl.ik_at], DICTATE),
                self.create_quiz(concept, nl.ik_at, [en.i_ate], INTERPRET),
                self.create_quiz(concept, en.i_ate, [nl.ik_at], WRITE),
                self.create_quiz(concept, nl.wij_aten, [en.we_ate], READ),
                self.create_quiz(concept, nl.wij_aten, [nl.wij_aten], DICTATE),
                self.create_quiz(concept, nl.wij_aten, [en.we_ate], INTERPRET),
                self.create_quiz(concept, en.we_ate, [nl.wij_aten], WRITE),
                self.create_quiz(concept, nl.ik_at, [nl.wij_aten], PLURAL),
                self.create_quiz(concept, nl.wij_aten, [nl.ik_at], SINGULAR),
                self.create_quiz(concept, nl.ik_eet, [nl.ik_at], PAST_TENSE),
                self.create_quiz(concept, nl.wij_eten, [nl.wij_aten], PAST_TENSE),
                self.create_quiz(concept, nl.ik_at, [nl.ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, nl.wij_aten, [nl.wij_eten], PRESENT_TENSE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_tense_nested_with_grammatical_person_and_infinitive(self):
        """Test that quizzes can be generated for tense nested with grammatical person and infinitive."""
        concept = self.create_concept(
            "to eat",
            labels=[
                {
                    "label": {
                        "infinitive": "to eat",
                        "present tense": {"singular": "I eat", "plural": "we eat"},
                        "past tense": {"singular": "I ate", "plural": "we ate"},
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "infinitive": "eten",
                        "present tense": {"singular": "ik eet", "plural": "wij eten"},
                        "past tense": {"singular": "ik at", "plural": "wij aten"},
                    },
                    "language": NL,
                },
            ],
        )
        nl = concept.labels(NL)
        en = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, nl.ik_eet, [en.i_eat], READ),
                self.create_quiz(concept, nl.ik_eet, [nl.ik_eet], DICTATE),
                self.create_quiz(concept, nl.ik_eet, [en.i_eat], INTERPRET),
                self.create_quiz(concept, en.i_eat, [nl.ik_eet], WRITE),
                self.create_quiz(concept, nl.wij_eten, [en.we_eat], READ),
                self.create_quiz(concept, nl.wij_eten, [nl.wij_eten], DICTATE),
                self.create_quiz(concept, nl.wij_eten, [en.we_eat], INTERPRET),
                self.create_quiz(concept, en.we_eat, [nl.wij_eten], WRITE),
                self.create_quiz(concept, nl.ik_eet, [nl.wij_eten], PLURAL),
                self.create_quiz(concept, nl.wij_eten, [nl.ik_eet], SINGULAR),
                self.create_quiz(concept, nl.ik_at, [en.i_ate], READ),
                self.create_quiz(concept, nl.ik_at, [nl.ik_at], DICTATE),
                self.create_quiz(concept, nl.ik_at, [en.i_ate], INTERPRET),
                self.create_quiz(concept, en.i_ate, [nl.ik_at], WRITE),
                self.create_quiz(concept, nl.wij_aten, [en.we_ate], READ),
                self.create_quiz(concept, nl.wij_aten, [nl.wij_aten], DICTATE),
                self.create_quiz(concept, nl.wij_aten, [en.we_ate], INTERPRET),
                self.create_quiz(concept, en.we_ate, [nl.wij_aten], WRITE),
                self.create_quiz(concept, nl.ik_at, [nl.wij_aten], PLURAL),
                self.create_quiz(concept, nl.wij_aten, [nl.ik_at], SINGULAR),
                self.create_quiz(concept, nl.ik_eet, [nl.ik_at], PAST_TENSE),
                self.create_quiz(concept, nl.wij_eten, [nl.wij_aten], PAST_TENSE),
                self.create_quiz(concept, nl.ik_at, [nl.ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, nl.wij_aten, [nl.wij_eten], PRESENT_TENSE),
                self.create_quiz(concept, nl.eten, [en.to_eat], READ),
                self.create_quiz(concept, nl.eten, [nl.eten], DICTATE),
                self.create_quiz(concept, nl.eten, [en.to_eat], INTERPRET),
                self.create_quiz(concept, en.to_eat, [nl.eten], WRITE),
                self.create_quiz(concept, nl.ik_eet, [nl.eten], INFINITIVE),
                self.create_quiz(concept, nl.wij_eten, [nl.eten], INFINITIVE),
                self.create_quiz(concept, nl.ik_at, [nl.eten], INFINITIVE),
                self.create_quiz(concept, nl.wij_aten, [nl.eten], INFINITIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_tense_nested_with_grammatical_number_nested_and_grammatical_person(self):
        """Test generating quizzes for tense, grammatical number, and grammatical person."""
        concept = self.create_concept(
            "to be",
            labels=[
                {
                    "label": {
                        "present tense": OLLA_PRESENT_TENSE,
                        "past tense": {
                            "singular": {
                                "first person": "minä olin",
                                "second person": "sinä olit",
                                "third person": "hän oli",
                            },
                            "plural": {
                                "first person": "me olimme",
                                "second person": "te olitte",
                                "third person": "he olivat",
                            },
                        },
                    },
                    "language": FI,
                },
                {
                    "label": {
                        "present tense": ZIJN_PRESENT_TENSE,
                        "past tense": {
                            "singular": {
                                "first person": "ik was",
                                "second person": "jij was",
                                "third person": "zij was",
                            },
                            "plural": {
                                "first person": "wij waren",
                                "second person": "jullie waren",
                                "third person": "zij waren",
                            },
                        },
                    },
                    "language": NL,
                },
            ],
        )
        fi = concept.labels(FI)
        nl = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, nl.ik_ben, [fi.minä_olen], READ),
                self.create_quiz(concept, nl.ik_ben, [nl.ik_ben], DICTATE),
                self.create_quiz(concept, nl.ik_ben, [fi.minä_olen], INTERPRET),
                self.create_quiz(concept, fi.minä_olen, [nl.ik_ben], WRITE),
                self.create_quiz(concept, nl.jij_bent, [fi.sinä_olet], READ),
                self.create_quiz(concept, nl.jij_bent, [nl.jij_bent], DICTATE),
                self.create_quiz(concept, nl.jij_bent, [fi.sinä_olet], INTERPRET),
                self.create_quiz(concept, fi.sinä_olet, [nl.jij_bent], WRITE),
                self.create_quiz(concept, nl.zij_is, [fi.hän_on], READ),
                self.create_quiz(concept, nl.zij_is, [nl.zij_is], DICTATE),
                self.create_quiz(concept, nl.zij_is, [fi.hän_on], INTERPRET),
                self.create_quiz(concept, fi.hän_on, [nl.zij_is], WRITE),
                self.create_quiz(concept, nl.ik_ben, [nl.jij_bent], SECOND_PERSON),
                self.create_quiz(concept, nl.ik_ben, [nl.zij_is], THIRD_PERSON),
                self.create_quiz(concept, nl.jij_bent, [nl.ik_ben], FIRST_PERSON),
                self.create_quiz(concept, nl.jij_bent, [nl.zij_is], THIRD_PERSON),
                self.create_quiz(concept, nl.zij_is, [nl.ik_ben], FIRST_PERSON),
                self.create_quiz(concept, nl.zij_is, [nl.jij_bent], SECOND_PERSON),
                self.create_quiz(concept, nl.wij_zijn, [fi.me_olemme], READ),
                self.create_quiz(concept, nl.wij_zijn, [nl.wij_zijn], DICTATE),
                self.create_quiz(concept, nl.wij_zijn, [fi.me_olemme], INTERPRET),
                self.create_quiz(concept, fi.me_olemme, [nl.wij_zijn], WRITE),
                self.create_quiz(concept, nl.jullie_zijn, [fi.te_olette], READ),
                self.create_quiz(concept, nl.jullie_zijn, [nl.jullie_zijn], DICTATE),
                self.create_quiz(concept, nl.jullie_zijn, [fi.te_olette], INTERPRET),
                self.create_quiz(concept, fi.te_olette, [nl.jullie_zijn], WRITE),
                self.create_quiz(concept, nl.zij_zijn, [fi.he_ovat], READ),
                self.create_quiz(concept, nl.zij_zijn, [nl.zij_zijn], DICTATE),
                self.create_quiz(concept, nl.zij_zijn, [fi.he_ovat], INTERPRET),
                self.create_quiz(concept, fi.he_ovat, [nl.zij_zijn], WRITE),
                self.create_quiz(concept, nl.wij_zijn, [nl.jullie_zijn], SECOND_PERSON),
                self.create_quiz(concept, nl.wij_zijn, [nl.zij_zijn], THIRD_PERSON),
                self.create_quiz(concept, nl.jullie_zijn, [nl.wij_zijn], FIRST_PERSON),
                self.create_quiz(concept, nl.jullie_zijn, [nl.zij_zijn], THIRD_PERSON),
                self.create_quiz(concept, nl.zij_zijn, [nl.wij_zijn], FIRST_PERSON),
                self.create_quiz(concept, nl.zij_zijn, [nl.jullie_zijn], SECOND_PERSON),
                self.create_quiz(concept, nl.ik_ben, [nl.wij_zijn], PLURAL),
                self.create_quiz(concept, nl.jij_bent, [nl.jullie_zijn], PLURAL),
                self.create_quiz(concept, nl.zij_is, [nl.zij_zijn], PLURAL),
                self.create_quiz(concept, nl.wij_zijn, [nl.ik_ben], SINGULAR),
                self.create_quiz(concept, nl.jullie_zijn, [nl.jij_bent], SINGULAR),
                self.create_quiz(concept, nl.zij_zijn, [nl.zij_is], SINGULAR),
                self.create_quiz(concept, nl.ik_was, [fi.minä_olin], READ),
                self.create_quiz(concept, nl.ik_was, [nl.ik_was], DICTATE),
                self.create_quiz(concept, nl.ik_was, [fi.minä_olin], INTERPRET),
                self.create_quiz(concept, fi.minä_olin, [nl.ik_was], WRITE),
                self.create_quiz(concept, nl.jij_was, [fi.sinä_olit], READ),
                self.create_quiz(concept, nl.jij_was, [nl.jij_was], DICTATE),
                self.create_quiz(concept, nl.jij_was, [fi.sinä_olit], INTERPRET),
                self.create_quiz(concept, fi.sinä_olit, [nl.jij_was], WRITE),
                self.create_quiz(concept, nl.zij_was, [fi.hän_oli], READ),
                self.create_quiz(concept, nl.zij_was, [nl.zij_was], DICTATE),
                self.create_quiz(concept, nl.zij_was, [fi.hän_oli], INTERPRET),
                self.create_quiz(concept, fi.hän_oli, [nl.zij_was], WRITE),
                self.create_quiz(concept, nl.ik_was, [nl.jij_was], SECOND_PERSON),
                self.create_quiz(concept, nl.ik_was, [nl.zij_was], THIRD_PERSON),
                self.create_quiz(concept, nl.jij_was, [nl.ik_was], FIRST_PERSON),
                self.create_quiz(concept, nl.jij_was, [nl.zij_was], THIRD_PERSON),
                self.create_quiz(concept, nl.zij_was, [nl.ik_was], FIRST_PERSON),
                self.create_quiz(concept, nl.zij_was, [nl.jij_was], SECOND_PERSON),
                self.create_quiz(concept, nl.wij_waren, [fi.me_olimme], READ),
                self.create_quiz(concept, nl.wij_waren, [nl.wij_waren], DICTATE),
                self.create_quiz(concept, nl.wij_waren, [fi.me_olimme], INTERPRET),
                self.create_quiz(concept, fi.me_olimme, [nl.wij_waren], WRITE),
                self.create_quiz(concept, nl.jullie_waren, [fi.te_olitte], READ),
                self.create_quiz(concept, nl.jullie_waren, [nl.jullie_waren], DICTATE),
                self.create_quiz(concept, nl.jullie_waren, [fi.te_olitte], INTERPRET),
                self.create_quiz(concept, fi.te_olitte, [nl.jullie_waren], WRITE),
                self.create_quiz(concept, nl.zij_waren, [fi.he_olivat], READ),
                self.create_quiz(concept, nl.zij_waren, [nl.zij_waren], DICTATE),
                self.create_quiz(concept, nl.zij_waren, [fi.he_olivat], INTERPRET),
                self.create_quiz(concept, fi.he_olivat, [nl.zij_waren], WRITE),
                self.create_quiz(concept, nl.wij_waren, [nl.jullie_waren], SECOND_PERSON),
                self.create_quiz(concept, nl.wij_waren, [nl.zij_waren], THIRD_PERSON),
                self.create_quiz(concept, nl.jullie_waren, [nl.wij_waren], FIRST_PERSON),
                self.create_quiz(concept, nl.jullie_waren, [nl.zij_waren], THIRD_PERSON),
                self.create_quiz(concept, nl.zij_waren, [nl.wij_waren], FIRST_PERSON),
                self.create_quiz(concept, nl.zij_waren, [nl.jullie_waren], SECOND_PERSON),
                self.create_quiz(concept, nl.ik_was, [nl.wij_waren], PLURAL),
                self.create_quiz(concept, nl.jij_was, [nl.jullie_waren], PLURAL),
                self.create_quiz(concept, nl.zij_was, [nl.zij_waren], PLURAL),
                self.create_quiz(concept, nl.wij_waren, [nl.ik_was], SINGULAR),
                self.create_quiz(concept, nl.jullie_waren, [nl.jij_was], SINGULAR),
                self.create_quiz(concept, nl.zij_waren, [nl.zij_was], SINGULAR),
                self.create_quiz(concept, nl.ik_ben, [nl.ik_was], PAST_TENSE),
                self.create_quiz(concept, nl.jij_bent, [nl.jij_was], PAST_TENSE),
                self.create_quiz(concept, nl.zij_is, [nl.zij_was], PAST_TENSE),
                self.create_quiz(concept, nl.wij_zijn, [nl.wij_waren], PAST_TENSE),
                self.create_quiz(concept, nl.jullie_zijn, [nl.jullie_waren], PAST_TENSE),
                self.create_quiz(concept, nl.zij_zijn, [nl.zij_waren], PAST_TENSE),
                self.create_quiz(concept, nl.ik_was, [nl.ik_ben], PRESENT_TENSE),
                self.create_quiz(concept, nl.jij_was, [nl.jij_bent], PRESENT_TENSE),
                self.create_quiz(concept, nl.zij_was, [nl.zij_is], PRESENT_TENSE),
                self.create_quiz(concept, nl.wij_waren, [nl.wij_zijn], PRESENT_TENSE),
                self.create_quiz(concept, nl.jullie_waren, [nl.jullie_zijn], PRESENT_TENSE),
                self.create_quiz(concept, nl.zij_waren, [nl.zij_zijn], PRESENT_TENSE),
            },
            create_quizzes(NL_FI, (), concept),
        )
