"""Quiz factory unit tests for grammatical case."""

from toisto.model.language import EN, FI
from toisto.model.language.concept import Concept
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    DICTATE,
    INTERPRET,
    NOMINATIVE,
    PARTITIVE,
    PLURAL,
    READ,
    SINGULAR,
    WRITE,
)

from .....base import FI_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalCaseQuizzesTest(QuizFactoryTestCase):
    """Unit tests for grammatical case quizzes."""

    def create_finnish_noun_with_case(self) -> Concept:
        """Create a Finnish noun with partitive nested under grammatical number, no case in English."""
        return self.create_concept(
            "animal",
            labels=[
                {"label": {"singular": "animal", "plural": "animals"}, "language": EN},
                {
                    "label": {
                        "singular": {"nominative": "eläin", "partitive": "eläintä"},
                        "plural": {"nominative": "eläimet", "partitive": "eläimiä"},
                    },
                    "language": FI,
                },
            ],
        )

    def test_partitive_and_nominative_quizzes_within_finnish(self):
        """Quizzes are generated between nominative and partitive forms in Finnish."""
        concept = self.create_finnish_noun_with_case()
        elain, elainta, elaimet, elaimia = concept.labels(FI)
        quizzes = create_quizzes(FI_EN, (), concept)
        case_quizzes = {quiz for quiz in quizzes if quiz.action in ("partitive", "nominative")}
        self.assertSetEqual(
            {
                self.create_quiz(FI_EN, concept, elain, [elainta], PARTITIVE),
                self.create_quiz(FI_EN, concept, elainta, [elain], NOMINATIVE),
                self.create_quiz(FI_EN, concept, elaimet, [elaimia], PARTITIVE),
                self.create_quiz(FI_EN, concept, elaimia, [elaimet], NOMINATIVE),
            },
            case_quizzes,
        )

    def test_plural_and_singular_quizzes_pair_by_case(self):
        """Grammatical number quizzes pair labels of the same case (nominative-with-nominative)."""
        concept = self.create_finnish_noun_with_case()
        elain, elainta, elaimet, elaimia = concept.labels(FI)
        quizzes = create_quizzes(FI_EN, (), concept)
        number_quizzes = {quiz for quiz in quizzes if quiz.action in ("plural", "singular")}
        self.assertSetEqual(
            {
                self.create_quiz(FI_EN, concept, elain, [elaimet], PLURAL),
                self.create_quiz(FI_EN, concept, elaimet, [elain], SINGULAR),
                self.create_quiz(FI_EN, concept, elainta, [elaimia], PLURAL),
                self.create_quiz(FI_EN, concept, elaimia, [elainta], SINGULAR),
            },
            number_quizzes,
        )

    def test_partitive_not_accepted_as_translation_from_other_language(self):
        """Translating English `animal` to Finnish must NOT accept the partitive form."""
        concept = self.create_finnish_noun_with_case()
        elain, elainta, elaimet, _ = concept.labels(FI)
        animal, animals = concept.labels(EN)
        quizzes = create_quizzes(FI_EN, (), concept)
        write_quizzes = {quiz for quiz in quizzes if quiz.action == "write"}
        self.assertSetEqual(
            {
                self.create_quiz(FI_EN, concept, animal, [elain], WRITE),
                self.create_quiz(FI_EN, concept, animals, [elaimet], WRITE),
            },
            write_quizzes,
        )
        for quiz in write_quizzes:
            self.assertNotIn(elainta, quiz.answers)

    def test_partitive_does_not_translate_to_unmarked_form_in_other_language(self):
        """Reading Finnish `eläintä` must NOT yield English `animal` as the translation answer."""
        concept = self.create_finnish_noun_with_case()
        elain, _, elaimet, _ = concept.labels(FI)
        animal, animals = concept.labels(EN)
        quizzes = create_quizzes(FI_EN, (), concept)
        translation_quizzes = {quiz for quiz in quizzes if quiz.action in ("read", "interpret")}
        self.assertSetEqual(
            {
                self.create_quiz(FI_EN, concept, elain, [animal], READ),
                self.create_quiz(FI_EN, concept, elaimet, [animals], READ),
                self.create_quiz(FI_EN, concept, elain, [animal], INTERPRET),
                self.create_quiz(FI_EN, concept, elaimet, [animals], INTERPRET),
            },
            translation_quizzes,
        )

    def test_dictate_quizzes_for_all_finnish_forms(self):
        """Every Finnish form (including partitive) gets a dictate quiz."""
        concept = self.create_finnish_noun_with_case()
        elain, elainta, elaimet, elaimia = concept.labels(FI)
        quizzes = create_quizzes(FI_EN, (), concept)
        dictate_quizzes = {quiz for quiz in quizzes if quiz.action == "dictate"}
        self.assertSetEqual(
            {
                self.create_quiz(FI_EN, concept, elain, [elain], DICTATE),
                self.create_quiz(FI_EN, concept, elainta, [elainta], DICTATE),
                self.create_quiz(FI_EN, concept, elaimet, [elaimet], DICTATE),
                self.create_quiz(FI_EN, concept, elaimia, [elaimia], DICTATE),
            },
            dictate_quizzes,
        )
