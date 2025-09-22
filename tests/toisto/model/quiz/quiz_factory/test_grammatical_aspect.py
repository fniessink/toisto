"""Quiz factory unit tests."""

from toisto.model.language import EN, NL
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    IMPERFECTIVE,
    PAST_TENSE,
    PERFECTIVE,
    PLURAL,
    PRESENT_TENSE,
    SINGULAR,
)

from .....base import NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalAspectQuizzesTest(QuizFactoryTestCase):
    """Unit tests for concepts with grammatical aspects."""

    def test_all_tenses_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for aspects and tenses nested with grammatical person."""
        concept = self.create_verb_with_tense_and_person(include_aspect=True)
        nl = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, nl.ik_eet, [nl.wij_eten], PLURAL),
                self.create_quiz(concept, nl.wij_eten, [nl.ik_eet], SINGULAR),
                self.create_quiz(concept, nl.ik_at, [nl.wij_aten], PLURAL),
                self.create_quiz(concept, nl.wij_aten, [nl.ik_at], SINGULAR),
                self.create_quiz(concept, nl.ik_heb_gegeten, [nl.wij_hebben_gegeten], PLURAL),
                self.create_quiz(concept, nl.wij_hebben_gegeten, [nl.ik_heb_gegeten], SINGULAR),
                self.create_quiz(concept, nl.ik_had_gegeten, [nl.wij_hadden_gegeten], PLURAL),
                self.create_quiz(concept, nl.wij_hadden_gegeten, [nl.ik_had_gegeten], SINGULAR),
                self.create_quiz(concept, nl.ik_eet, [nl.ik_at], PAST_TENSE),
                self.create_quiz(concept, nl.ik_eet, [nl.ik_heb_gegeten], PERFECTIVE),
                self.create_quiz(concept, nl.wij_eten, [nl.wij_aten], PAST_TENSE),
                self.create_quiz(concept, nl.wij_eten, [nl.wij_hebben_gegeten], PERFECTIVE),
                self.create_quiz(concept, nl.ik_at, [nl.ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, nl.ik_at, [nl.ik_had_gegeten], PERFECTIVE),
                self.create_quiz(concept, nl.wij_aten, [nl.wij_eten], PRESENT_TENSE),
                self.create_quiz(concept, nl.wij_aten, [nl.wij_hadden_gegeten], PERFECTIVE),
                self.create_quiz(concept, nl.ik_heb_gegeten, [nl.ik_eet], IMPERFECTIVE),
                self.create_quiz(concept, nl.ik_heb_gegeten, [nl.ik_had_gegeten], PAST_TENSE),
                self.create_quiz(concept, nl.wij_hebben_gegeten, [nl.wij_eten], IMPERFECTIVE),
                self.create_quiz(concept, nl.wij_hebben_gegeten, [nl.wij_hadden_gegeten], PAST_TENSE),
                self.create_quiz(concept, nl.ik_had_gegeten, [nl.ik_at], IMPERFECTIVE),
                self.create_quiz(concept, nl.ik_had_gegeten, [nl.ik_heb_gegeten], PRESENT_TENSE),
                self.create_quiz(concept, nl.wij_hadden_gegeten, [nl.wij_aten], IMPERFECTIVE),
                self.create_quiz(concept, nl.wij_hadden_gegeten, [nl.wij_hebben_gegeten], PRESENT_TENSE),
            },
            create_quizzes(NL_EN, (), concept),
        )
