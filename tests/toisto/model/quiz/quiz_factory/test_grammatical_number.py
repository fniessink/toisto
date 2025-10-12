"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    DICTATE,
    FEMININE,
    FIRST_PERSON,
    INFINITIVE,
    INTERPRET,
    MASCULINE,
    PLURAL,
    PLURAL_PRONOUN,
    READ,
    SECOND_PERSON,
    SINGULAR,
    SINGULAR_PRONOUN,
    THIRD_PERSON,
    WRITE,
)

from .....base import EN_FI, EN_NL, FI_NL, NL_EN, NL_FI
from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalNumberQuizzesTest(QuizFactoryTestCase):
    """Unit tests for creating grammatical number quizzes."""

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        concept = self.create_noun_with_grammatical_number()
        aamu, aamut = concept.labels(FI)
        self.assertSetEqual(
            self.translation_quizzes(FI_NL, concept)
            | {
                self.create_quiz(FI_NL, concept, aamu, [aamut], PLURAL),
                self.create_quiz(FI_NL, concept, aamut, [aamu], SINGULAR),
            },
            create_quizzes(FI_NL, (), concept),
        )

    def test_grammatical_number_pronoun(self):
        """Test that quizzes can be generated for different grammatical numbers of pronouns."""
        concept = self.create_concept(
            "cat",
            labels=[{"label": {"singular pronoun": "my cat", "plural pronoun": "our cat"}, "language": EN}],
        )
        my_cat, our_cat = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(EN_NL, concept, my_cat, [our_cat], PLURAL_PRONOUN),
                self.create_quiz(EN_NL, concept, our_cat, [my_cat], SINGULAR_PRONOUN),
                self.create_quiz(EN_NL, concept, my_cat, [my_cat], DICTATE),
                self.create_quiz(EN_NL, concept, our_cat, [our_cat], DICTATE),
            },
            create_quizzes(EN_NL, (), concept),
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        concept = self.create_concept(
            "ketchup",
            labels=[
                {"label": {"singular": "ketsuppi", "plural": "ketsupit"}, "language": FI},
                {"label": "de ketchup", "language": NL},
            ],
        )
        quizzes = create_quizzes(FI_NL, (), concept)
        ketsuppi, ketsupit = concept.labels(FI)
        (ketchup,) = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(FI_NL, concept, ketsuppi, [ketchup], READ),
                self.create_quiz(FI_NL, concept, ketsupit, [ketchup], READ),
                self.create_quiz(FI_NL, concept, ketsuppi, [ketsuppi], DICTATE),
                self.create_quiz(FI_NL, concept, ketsupit, [ketsupit], DICTATE),
                self.create_quiz(FI_NL, concept, ketsuppi, [ketchup], INTERPRET),
                self.create_quiz(FI_NL, concept, ketsupit, [ketchup], INTERPRET),
                self.create_quiz(FI_NL, concept, ketchup, [ketsuppi], WRITE),
                self.create_quiz(FI_NL, concept, ketsuppi, [ketsupit], PLURAL),
                self.create_quiz(FI_NL, concept, ketsupit, [ketsuppi], SINGULAR),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_in_target_language_not_in_source_language(self):
        """Test that quizzes can be generated even if one language has no grammatical number for the concept."""
        concept = self.create_noun_invariant_in_english()
        quizzes = create_quizzes(NL_EN, (), concept)
        vervoersmiddel, vervoersmiddelen = concept.labels(NL)
        (means_of_transportation,) = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(NL_EN, concept, vervoersmiddel, [means_of_transportation], INTERPRET),
                self.create_quiz(NL_EN, concept, vervoersmiddel, [vervoersmiddel], DICTATE),
                self.create_quiz(NL_EN, concept, vervoersmiddel, [means_of_transportation], READ),
                self.create_quiz(NL_EN, concept, vervoersmiddel, [vervoersmiddelen], PLURAL),
                self.create_quiz(NL_EN, concept, vervoersmiddelen, [means_of_transportation], INTERPRET),
                self.create_quiz(NL_EN, concept, vervoersmiddelen, [vervoersmiddelen], DICTATE),
                self.create_quiz(NL_EN, concept, vervoersmiddelen, [means_of_transportation], READ),
                self.create_quiz(NL_EN, concept, vervoersmiddelen, [vervoersmiddel], SINGULAR),
                self.create_quiz(NL_EN, concept, means_of_transportation, [vervoersmiddel], WRITE),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_in_source_language_not_in_target_language(self):
        """Test that quizzes can be generated even if one language has no grammatical number for the concept."""
        concept = self.create_noun_invariant_in_english()
        quizzes = create_quizzes(EN_NL, (), concept)
        vervoersmiddel, vervoersmiddelen = concept.labels(NL)
        (means_of_transportation,) = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(
                    EN_NL,
                    concept,
                    means_of_transportation,
                    [vervoersmiddel, vervoersmiddelen],
                    INTERPRET,
                ),
                self.create_quiz(
                    EN_NL,
                    concept,
                    means_of_transportation,
                    [vervoersmiddel, vervoersmiddelen],
                    READ,
                ),
                self.create_quiz(EN_NL, concept, vervoersmiddel, [means_of_transportation], WRITE),
                self.create_quiz(EN_NL, concept, vervoersmiddelen, [means_of_transportation], WRITE),
                self.create_quiz(EN_NL, concept, means_of_transportation, [means_of_transportation], DICTATE),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the target language only."""
        concept = self.create_concept(
            "mämmi", labels=[{"label": {"singular": "mämmi", "plural": "mämmit"}, "language": FI}]
        )
        quizzes = create_quizzes(FI_NL, (), concept)
        mämmi, mämmit = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(FI_NL, concept, mämmi, [mämmi], DICTATE),
                self.create_quiz(FI_NL, concept, mämmit, [mämmit], DICTATE),
                self.create_quiz(FI_NL, concept, mämmi, [mämmit], PLURAL),
                self.create_quiz(FI_NL, concept, mämmit, [mämmi], SINGULAR),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes are generated from a noun concept with labels in the native language."""
        concept = self.create_concept(
            "mämmi", labels=[{"label": {"singular": "mämmi", "plural": "mämmit"}, "language": FI}]
        )
        self.assertSetEqual(Quizzes(), create_quizzes(EN_FI, (), concept))

    def test_grammatical_number_with_synonyms(self):
        """Test that in case of synonyms the plural of one synonym isn't the correct answer for the other synonym."""
        concept = self.create_concept(
            "mall",
            labels=[
                {"label": {"singular": "kauppakeskus", "plural": "kauppakeskukset"}, "language": FI},
                {"label": {"singular": "ostoskeskus", "plural": "ostoskeskukset"}, "language": FI},
                {"label": {"singular": "winkelcentrum", "plural": "winkelcentra"}, "language": NL},
            ],
        )
        fi = concept.labels(FI)
        nl = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(FI_NL, concept, fi.kauppakeskus, [nl.winkelcentrum], READ),
                self.create_quiz(FI_NL, concept, fi.ostoskeskus, [nl.winkelcentrum], READ),
                self.create_quiz(FI_NL, concept, fi.kauppakeskus, [fi.kauppakeskus], DICTATE),
                self.create_quiz(FI_NL, concept, fi.kauppakeskus, [nl.winkelcentrum], INTERPRET),
                self.create_quiz(FI_NL, concept, fi.ostoskeskus, [fi.ostoskeskus], DICTATE),
                self.create_quiz(FI_NL, concept, fi.ostoskeskus, [nl.winkelcentrum], INTERPRET),
                self.create_quiz(FI_NL, concept, nl.winkelcentrum, [fi.kauppakeskus, fi.ostoskeskus], WRITE),
                self.create_quiz(FI_NL, concept, fi.kauppakeskukset, [nl.winkelcentra], READ),
                self.create_quiz(FI_NL, concept, fi.ostoskeskukset, [nl.winkelcentra], READ),
                self.create_quiz(FI_NL, concept, fi.kauppakeskukset, [fi.kauppakeskukset], DICTATE),
                self.create_quiz(FI_NL, concept, fi.kauppakeskukset, [nl.winkelcentra], INTERPRET),
                self.create_quiz(FI_NL, concept, fi.ostoskeskukset, [fi.ostoskeskukset], DICTATE),
                self.create_quiz(FI_NL, concept, fi.ostoskeskukset, [nl.winkelcentra], INTERPRET),
                self.create_quiz(FI_NL, concept, nl.winkelcentra, [fi.kauppakeskukset, fi.ostoskeskukset], WRITE),
                self.create_quiz(FI_NL, concept, fi.kauppakeskus, [fi.kauppakeskukset], PLURAL),
                self.create_quiz(FI_NL, concept, fi.ostoskeskus, [fi.ostoskeskukset], PLURAL),
                self.create_quiz(FI_NL, concept, fi.kauppakeskukset, [fi.kauppakeskus], SINGULAR),
                self.create_quiz(FI_NL, concept, fi.ostoskeskukset, [fi.ostoskeskus], SINGULAR),
            },
            create_quizzes(FI_NL, (), concept),
        )

    def test_grammatical_number_nested_with_grammatical_person_and_infinitive(self):
        """Test generating quizzes for grammatical number, including infinitive, nested with grammatical person."""
        concept = self.create_verb_with_infinitive_and_number_and_person()
        nl = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(NL_FI, concept)
            | {
                self.create_quiz(NL_FI, concept, nl.ik_ben, [nl.zijn], INFINITIVE),
                self.create_quiz(NL_FI, concept, nl.jij_bent, [nl.zijn], INFINITIVE),
                self.create_quiz(NL_FI, concept, nl.zij_is, [nl.zijn], INFINITIVE),
                self.create_quiz(NL_FI, concept, nl.ik_ben, [nl.jij_bent], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.ik_ben, [nl.zij_is], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.jij_bent, [nl.ik_ben], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.jij_bent, [nl.zij_is], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_is, [nl.ik_ben], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_is, [nl.jij_bent], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.wij_zijn, [nl.zijn], INFINITIVE),
                self.create_quiz(NL_FI, concept, nl.jullie_zijn, [nl.zijn], INFINITIVE),
                self.create_quiz(NL_FI, concept, nl.zij_zijn, [nl.zijn], INFINITIVE),
                self.create_quiz(NL_FI, concept, nl.wij_zijn, [nl.jullie_zijn], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.wij_zijn, [nl.zij_zijn], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.jullie_zijn, [nl.wij_zijn], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.jullie_zijn, [nl.zij_zijn], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_zijn, [nl.wij_zijn], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_zijn, [nl.jullie_zijn], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.ik_ben, [nl.wij_zijn], PLURAL),
                self.create_quiz(NL_FI, concept, nl.wij_zijn, [nl.ik_ben], SINGULAR),
                self.create_quiz(NL_FI, concept, nl.jij_bent, [nl.jullie_zijn], PLURAL),
                self.create_quiz(NL_FI, concept, nl.jullie_zijn, [nl.jij_bent], SINGULAR),
                self.create_quiz(NL_FI, concept, nl.zij_is, [nl.zij_zijn], PLURAL),
                self.create_quiz(NL_FI, concept, nl.zij_zijn, [nl.zij_is], SINGULAR),
            },
            create_quizzes(NL_FI, (), concept),
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = self.create_verb_with_grammatical_number_and_person()
        nl = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(NL_FI, concept)
            | {
                self.create_quiz(NL_FI, concept, nl.ik_heb, [nl.jij_hebt], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.ik_heb, [nl.zij_heeft], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.jij_hebt, [nl.ik_heb], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.jij_hebt, [nl.zij_heeft], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_heeft, [nl.ik_heb], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_heeft, [nl.jij_hebt], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.wij_hebben, [nl.jullie_hebben], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.wij_hebben, [nl.zij_hebben], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.jullie_hebben, [nl.wij_hebben], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.jullie_hebben, [nl.zij_hebben], THIRD_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_hebben, [nl.wij_hebben], FIRST_PERSON),
                self.create_quiz(NL_FI, concept, nl.zij_hebben, [nl.jullie_hebben], SECOND_PERSON),
                self.create_quiz(NL_FI, concept, nl.ik_heb, [nl.wij_hebben], PLURAL),
                self.create_quiz(NL_FI, concept, nl.wij_hebben, [nl.ik_heb], SINGULAR),
                self.create_quiz(NL_FI, concept, nl.jij_hebt, [nl.jullie_hebben], PLURAL),
                self.create_quiz(NL_FI, concept, nl.jullie_hebben, [nl.jij_hebt], SINGULAR),
                self.create_quiz(NL_FI, concept, nl.zij_heeft, [nl.zij_hebben], PLURAL),
                self.create_quiz(NL_FI, concept, nl.zij_hebben, [nl.zij_heeft], SINGULAR),
            },
            create_quizzes(NL_FI, (), concept),
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        concept = self.create_noun_with_grammatical_number_and_gender()
        nl = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(NL_EN, concept)
            | {
                self.create_quiz(NL_EN, concept, nl.haar_kat, [nl.zijn_kat], MASCULINE),
                self.create_quiz(NL_EN, concept, nl.zijn_kat, [nl.haar_kat], FEMININE),
                self.create_quiz(NL_EN, concept, nl.haar_katten, [nl.zijn_katten], MASCULINE),
                self.create_quiz(NL_EN, concept, nl.zijn_katten, [nl.haar_katten], FEMININE),
                self.create_quiz(NL_EN, concept, nl.haar_kat, [nl.haar_katten], PLURAL),
                self.create_quiz(NL_EN, concept, nl.haar_katten, [nl.haar_kat], SINGULAR),
                self.create_quiz(NL_EN, concept, nl.zijn_kat, [nl.zijn_katten], PLURAL),
                self.create_quiz(NL_EN, concept, nl.zijn_katten, [nl.zijn_kat], SINGULAR),
            },
            create_quizzes(NL_EN, (), concept),
        )
