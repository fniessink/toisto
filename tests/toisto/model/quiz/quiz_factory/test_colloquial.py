"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import ConceptId
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import ANTONYM, DICTATE, INTERPRET, PLURAL, READ, SINGULAR, WRITE

from .....base import EN_FI, FI_EN, FI_NL, NL_FI, ToistoTestCase


class ColloquialTest(ToistoTestCase):
    """Unit tests for quizzes with colloquial (spoken language) labels."""

    def test_colloquial_and_regular_label(self):
        """Test the generated quizzes when one language has both a colloquial and a regular label."""
        concept = self.create_concept(
            "seven",
            labels=[
                {"label": "seittemän", "language": FI, "colloquial": True},
                {"label": "seitsemän", "language": FI},
                {"label": "zeven", "language": NL},
            ],
        )
        seittemän, seitsemän = concept.labels(FI)
        (zeven,) = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, seitsemän, [zeven], READ),
                self.create_quiz(concept, seitsemän, [seitsemän], DICTATE),
                self.create_quiz(concept, zeven, [seitsemän], WRITE),
                self.create_quiz(concept, seitsemän, [zeven], INTERPRET),
                self.create_quiz(concept, seittemän, [seitsemän], DICTATE),
                self.create_quiz(concept, seittemän, [zeven], INTERPRET),
            },
            create_quizzes(FI_NL, (), concept),
        )
        self.assertSetEqual(
            {
                self.create_quiz(concept, zeven, [seitsemän], READ),
                self.create_quiz(concept, zeven, [zeven], DICTATE),
                self.create_quiz(concept, seitsemän, [zeven], WRITE),
                self.create_quiz(concept, zeven, [seitsemän], INTERPRET),
            },
            create_quizzes(NL_FI, (), concept),
        )

    def test_grammar_and_colloquial(self):
        """Test the generated quizzes when colloquial labels and grammar are combined."""
        concept = self.create_concept(
            "kiosk",
            labels=[
                {"label": {"singular": "kioski", "plural": "kioskit"}, "language": FI},
                {"label": {"singular": "kiska", "plural": "kiskat"}, "language": FI, "colloquial": True},
                {"label": {"singular": "kiosk", "plural": "kiosks"}, "language": EN},
            ],
        )
        kioski, kioskit, kiska, kiskat = concept.labels(FI)
        kiosk, kiosks = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, kioski, [kiosk], READ),
                self.create_quiz(concept, kioski, [kioski], DICTATE),
                self.create_quiz(concept, kiosk, [kioski], WRITE),
                self.create_quiz(concept, kioski, [kiosk], INTERPRET),
                self.create_quiz(concept, kiska, [kiosk], INTERPRET),
                self.create_quiz(concept, kiska, [kioski], DICTATE),
                self.create_quiz(concept, kioskit, [kiosks], READ),
                self.create_quiz(concept, kioskit, [kioskit], DICTATE),
                self.create_quiz(concept, kiosks, [kioskit], WRITE),
                self.create_quiz(concept, kioskit, [kiosks], INTERPRET),
                self.create_quiz(concept, kiskat, [kiosks], INTERPRET),
                self.create_quiz(concept, kiskat, [kioskit], DICTATE),
                self.create_quiz(concept, kioski, [kioskit], PLURAL),
                self.create_quiz(concept, kioskit, [kioski], SINGULAR),
            },
            create_quizzes(FI_EN, (), concept),
        )
        self.assertSetEqual(
            {
                self.create_quiz(concept, kiosk, [kioski], READ),
                self.create_quiz(concept, kiosk, [kiosk], DICTATE),
                self.create_quiz(concept, kioski, [kiosk], WRITE),
                self.create_quiz(concept, kiosk, [kioski], INTERPRET),
                self.create_quiz(concept, kiosks, [kioskit], READ),
                self.create_quiz(concept, kiosks, [kiosks], DICTATE),
                self.create_quiz(concept, kioskit, [kiosks], WRITE),
                self.create_quiz(concept, kiosks, [kioskit], INTERPRET),
                self.create_quiz(concept, kiosk, [kiosks], PLURAL),
                self.create_quiz(concept, kiosks, [kiosk], SINGULAR),
            },
            create_quizzes(EN_FI, (), concept),
        )

    def test_related_concepts_and_colloquial(self):
        """Test the generated quizzes when colloquial labels and related concepts are combined."""
        yes = self.create_concept(
            "yes",
            {"antonym": ConceptId("no")},
            labels=[{"label": "kylla", "language": FI}, {"label": "kyl", "language": FI, "colloquial": True}],
        )
        no = self.create_concept("no", {"antonym": ConceptId("yes")}, labels=[{"label": "ei", "language": FI}])
        kylla, kyl = yes.labels(FI)
        (ei,) = no.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(yes, kylla, [kylla], DICTATE),
                self.create_quiz(yes, kyl, [kylla], DICTATE),
                self.create_quiz(yes, kylla, [ei], ANTONYM),
            },
            create_quizzes(FI_EN, (), yes),
        )
        self.assertSetEqual(
            {
                self.create_quiz(no, ei, [ei], DICTATE),
                self.create_quiz(no, ei, [kylla], ANTONYM),
            },
            create_quizzes(FI_EN, (), no),
        )
