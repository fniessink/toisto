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
    READ,
    SECOND_PERSON,
    SINGULAR,
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
        ochtend, ochtenden = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, aamu, [ochtend], READ),
                self.create_quiz(concept, aamu, [aamu], DICTATE),
                self.create_quiz(concept, aamu, [ochtend], INTERPRET),
                self.create_quiz(concept, ochtend, [aamu], WRITE),
                self.create_quiz(concept, aamut, [ochtenden], READ),
                self.create_quiz(concept, aamut, [aamut], DICTATE),
                self.create_quiz(concept, aamut, [ochtenden], INTERPRET),
                self.create_quiz(concept, ochtenden, [aamut], WRITE),
                self.create_quiz(concept, aamu, [aamut], PLURAL),
                self.create_quiz(concept, aamut, [aamu], SINGULAR),
            },
            create_quizzes(FI_NL, (), concept),
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
                self.create_quiz(concept, ketsuppi, [ketchup], READ),
                self.create_quiz(concept, ketsupit, [ketchup], READ),
                self.create_quiz(concept, ketsuppi, [ketsuppi], DICTATE),
                self.create_quiz(concept, ketsupit, [ketsupit], DICTATE),
                self.create_quiz(concept, ketsuppi, [ketchup], INTERPRET),
                self.create_quiz(concept, ketsupit, [ketchup], INTERPRET),
                self.create_quiz(concept, ketchup, [ketsuppi], WRITE),
                self.create_quiz(concept, ketsuppi, [ketsupit], PLURAL),
                self.create_quiz(concept, ketsupit, [ketsuppi], SINGULAR),
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
                self.create_quiz(concept, vervoersmiddel, [means_of_transportation], INTERPRET),
                self.create_quiz(concept, vervoersmiddel, [vervoersmiddel], DICTATE),
                self.create_quiz(concept, vervoersmiddel, [means_of_transportation], READ),
                self.create_quiz(concept, vervoersmiddel, [vervoersmiddelen], PLURAL),
                self.create_quiz(concept, vervoersmiddelen, [means_of_transportation], INTERPRET),
                self.create_quiz(concept, vervoersmiddelen, [vervoersmiddelen], DICTATE),
                self.create_quiz(concept, vervoersmiddelen, [means_of_transportation], READ),
                self.create_quiz(concept, vervoersmiddelen, [vervoersmiddel], SINGULAR),
                self.create_quiz(concept, means_of_transportation, [vervoersmiddel], WRITE),
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
                    concept,
                    means_of_transportation,
                    [vervoersmiddel, vervoersmiddelen],
                    INTERPRET,
                ),
                self.create_quiz(
                    concept,
                    means_of_transportation,
                    [vervoersmiddel, vervoersmiddelen],
                    READ,
                ),
                self.create_quiz(concept, vervoersmiddel, [means_of_transportation], WRITE),
                self.create_quiz(concept, vervoersmiddelen, [means_of_transportation], WRITE),
                self.create_quiz(concept, means_of_transportation, [means_of_transportation], DICTATE),
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
                self.create_quiz(concept, mämmi, [mämmi], DICTATE),
                self.create_quiz(concept, mämmit, [mämmit], DICTATE),
                self.create_quiz(concept, mämmi, [mämmit], PLURAL),
                self.create_quiz(concept, mämmit, [mämmi], SINGULAR),
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
                {"label": {"singular": "het winkelcentrum", "plural": "de winkelcentra"}, "language": NL},
            ],
        )
        kauppakeskus, kauppakeskukset, ostoskeskus, ostoskeskukset = concept.labels(FI)
        winkelcentrum, winkelcentra = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, kauppakeskus, [winkelcentrum], READ),
                self.create_quiz(concept, ostoskeskus, [winkelcentrum], READ),
                self.create_quiz(concept, kauppakeskus, [kauppakeskus], DICTATE),
                self.create_quiz(concept, kauppakeskus, [winkelcentrum], INTERPRET),
                self.create_quiz(concept, ostoskeskus, [ostoskeskus], DICTATE),
                self.create_quiz(concept, ostoskeskus, [winkelcentrum], INTERPRET),
                self.create_quiz(concept, winkelcentrum, [kauppakeskus, ostoskeskus], WRITE),
                self.create_quiz(concept, kauppakeskukset, [winkelcentra], READ),
                self.create_quiz(concept, ostoskeskukset, [winkelcentra], READ),
                self.create_quiz(concept, kauppakeskukset, [kauppakeskukset], DICTATE),
                self.create_quiz(concept, kauppakeskukset, [winkelcentra], INTERPRET),
                self.create_quiz(concept, ostoskeskukset, [ostoskeskukset], DICTATE),
                self.create_quiz(concept, ostoskeskukset, [winkelcentra], INTERPRET),
                self.create_quiz(concept, winkelcentra, [kauppakeskukset, ostoskeskukset], WRITE),
                self.create_quiz(concept, kauppakeskus, [kauppakeskukset], PLURAL),
                self.create_quiz(concept, ostoskeskus, [ostoskeskukset], PLURAL),
                self.create_quiz(concept, kauppakeskukset, [kauppakeskus], SINGULAR),
                self.create_quiz(concept, ostoskeskukset, [ostoskeskus], SINGULAR),
            },
            create_quizzes(FI_NL, (), concept),
        )

    def test_grammatical_number_nested_with_grammatical_person_and_infinitive(self):
        """Test generating quizzes for grammatical number, including infinitive, nested with grammatical person."""
        concept = self.create_verb_with_infinitive_and_number_and_person()
        zijn, ik_ben, jij_bent, zij_is, wij_zijn, jullie_zijn, zij_zijn = concept.labels(NL)
        olla, minä_olen, sinä_olet, hän_on, me_olemme, te_olette, he_ovat = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_ben, [minä_olen], READ),
                self.create_quiz(concept, ik_ben, [ik_ben], DICTATE),
                self.create_quiz(concept, ik_ben, [minä_olen], INTERPRET),
                self.create_quiz(concept, minä_olen, [ik_ben], WRITE),
                self.create_quiz(concept, ik_ben, [zijn], INFINITIVE),
                self.create_quiz(concept, jij_bent, [sinä_olet], READ),
                self.create_quiz(concept, jij_bent, [jij_bent], DICTATE),
                self.create_quiz(concept, jij_bent, [sinä_olet], INTERPRET),
                self.create_quiz(concept, sinä_olet, [jij_bent], WRITE),
                self.create_quiz(concept, jij_bent, [zijn], INFINITIVE),
                self.create_quiz(concept, zij_is, [hän_on], READ),
                self.create_quiz(concept, zij_is, [zij_is], DICTATE),
                self.create_quiz(concept, zij_is, [hän_on], INTERPRET),
                self.create_quiz(concept, hän_on, [zij_is], WRITE),
                self.create_quiz(concept, zij_is, [zijn], INFINITIVE),
                self.create_quiz(concept, ik_ben, [jij_bent], SECOND_PERSON),
                self.create_quiz(concept, ik_ben, [zij_is], THIRD_PERSON),
                self.create_quiz(concept, jij_bent, [ik_ben], FIRST_PERSON),
                self.create_quiz(concept, jij_bent, [zij_is], THIRD_PERSON),
                self.create_quiz(concept, zij_is, [ik_ben], FIRST_PERSON),
                self.create_quiz(concept, zij_is, [jij_bent], SECOND_PERSON),
                self.create_quiz(concept, wij_zijn, [me_olemme], READ),
                self.create_quiz(concept, wij_zijn, [wij_zijn], DICTATE),
                self.create_quiz(concept, wij_zijn, [me_olemme], INTERPRET),
                self.create_quiz(concept, me_olemme, [wij_zijn], WRITE),
                self.create_quiz(concept, wij_zijn, [zijn], INFINITIVE),
                self.create_quiz(concept, jullie_zijn, [te_olette], READ),
                self.create_quiz(concept, jullie_zijn, [jullie_zijn], DICTATE),
                self.create_quiz(concept, jullie_zijn, [te_olette], INTERPRET),
                self.create_quiz(concept, te_olette, [jullie_zijn], WRITE),
                self.create_quiz(concept, jullie_zijn, [zijn], INFINITIVE),
                self.create_quiz(concept, zij_zijn, [he_ovat], READ),
                self.create_quiz(concept, zij_zijn, [zij_zijn], DICTATE),
                self.create_quiz(concept, zij_zijn, [he_ovat], INTERPRET),
                self.create_quiz(concept, he_ovat, [zij_zijn], WRITE),
                self.create_quiz(concept, zij_zijn, [zijn], INFINITIVE),
                self.create_quiz(concept, wij_zijn, [jullie_zijn], SECOND_PERSON),
                self.create_quiz(concept, wij_zijn, [zij_zijn], THIRD_PERSON),
                self.create_quiz(concept, jullie_zijn, [wij_zijn], FIRST_PERSON),
                self.create_quiz(concept, jullie_zijn, [zij_zijn], THIRD_PERSON),
                self.create_quiz(concept, zij_zijn, [wij_zijn], FIRST_PERSON),
                self.create_quiz(concept, zij_zijn, [jullie_zijn], SECOND_PERSON),
                self.create_quiz(concept, ik_ben, [wij_zijn], PLURAL),
                self.create_quiz(concept, wij_zijn, [ik_ben], SINGULAR),
                self.create_quiz(concept, jij_bent, [jullie_zijn], PLURAL),
                self.create_quiz(concept, jullie_zijn, [jij_bent], SINGULAR),
                self.create_quiz(concept, zij_is, [zij_zijn], PLURAL),
                self.create_quiz(concept, zij_zijn, [zij_is], SINGULAR),
                self.create_quiz(concept, zijn, [olla], READ),
                self.create_quiz(concept, zijn, [zijn], DICTATE),
                self.create_quiz(concept, zijn, [olla], INTERPRET),
                self.create_quiz(concept, olla, [zijn], WRITE),
            },
            create_quizzes(NL_FI, (), concept),
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = self.create_verb_with_grammatical_number_and_person()
        ik_heb, jij_hebt, zij_heeft, wij_hebben, jullie_hebben, zij_hebben = concept.labels(NL)
        minulla_on, sinulla_on, hänellä_on, meillä_on, teillä_on, heillä_on = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_heb, [minulla_on], READ),
                self.create_quiz(concept, minulla_on, [ik_heb], WRITE),
                self.create_quiz(concept, ik_heb, [ik_heb], DICTATE),
                self.create_quiz(concept, ik_heb, [minulla_on], INTERPRET),
                self.create_quiz(concept, jij_hebt, [sinulla_on], READ),
                self.create_quiz(concept, sinulla_on, [jij_hebt], WRITE),
                self.create_quiz(concept, jij_hebt, [jij_hebt], DICTATE),
                self.create_quiz(concept, jij_hebt, [sinulla_on], INTERPRET),
                self.create_quiz(concept, zij_heeft, [hänellä_on], READ),
                self.create_quiz(concept, hänellä_on, [zij_heeft], WRITE),
                self.create_quiz(concept, zij_heeft, [zij_heeft], DICTATE),
                self.create_quiz(concept, zij_heeft, [hänellä_on], INTERPRET),
                self.create_quiz(concept, ik_heb, [jij_hebt], SECOND_PERSON),
                self.create_quiz(concept, ik_heb, [zij_heeft], THIRD_PERSON),
                self.create_quiz(concept, jij_hebt, [ik_heb], FIRST_PERSON),
                self.create_quiz(concept, jij_hebt, [zij_heeft], THIRD_PERSON),
                self.create_quiz(concept, zij_heeft, [ik_heb], FIRST_PERSON),
                self.create_quiz(concept, zij_heeft, [jij_hebt], SECOND_PERSON),
                self.create_quiz(concept, wij_hebben, [meillä_on], READ),
                self.create_quiz(concept, meillä_on, [wij_hebben], WRITE),
                self.create_quiz(concept, wij_hebben, [wij_hebben], DICTATE),
                self.create_quiz(concept, wij_hebben, [meillä_on], INTERPRET),
                self.create_quiz(concept, jullie_hebben, [teillä_on], READ),
                self.create_quiz(concept, teillä_on, [jullie_hebben], WRITE),
                self.create_quiz(concept, jullie_hebben, [jullie_hebben], DICTATE),
                self.create_quiz(concept, jullie_hebben, [teillä_on], INTERPRET),
                self.create_quiz(concept, zij_hebben, [heillä_on], READ),
                self.create_quiz(concept, heillä_on, [zij_hebben], WRITE),
                self.create_quiz(concept, zij_hebben, [zij_hebben], DICTATE),
                self.create_quiz(concept, zij_hebben, [heillä_on], INTERPRET),
                self.create_quiz(concept, wij_hebben, [jullie_hebben], SECOND_PERSON),
                self.create_quiz(concept, wij_hebben, [zij_hebben], THIRD_PERSON),
                self.create_quiz(concept, jullie_hebben, [wij_hebben], FIRST_PERSON),
                self.create_quiz(concept, jullie_hebben, [zij_hebben], THIRD_PERSON),
                self.create_quiz(concept, zij_hebben, [wij_hebben], FIRST_PERSON),
                self.create_quiz(concept, zij_hebben, [jullie_hebben], SECOND_PERSON),
                self.create_quiz(concept, ik_heb, [wij_hebben], PLURAL),
                self.create_quiz(concept, wij_hebben, [ik_heb], SINGULAR),
                self.create_quiz(concept, jij_hebt, [jullie_hebben], PLURAL),
                self.create_quiz(concept, jullie_hebben, [jij_hebt], SINGULAR),
                self.create_quiz(concept, zij_heeft, [zij_hebben], PLURAL),
                self.create_quiz(concept, zij_hebben, [zij_heeft], SINGULAR),
            },
            create_quizzes(NL_FI, (), concept),
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        concept = self.create_noun_with_grammatical_number_and_gender()
        haar_kat, zijn_kat, haar_katten, zijn_katten = concept.labels(NL)
        her_cat, his_cat, her_cats, his_cats = concept.labels(EN)
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
                self.create_quiz(concept, haar_katten, [her_cats], READ),
                self.create_quiz(concept, haar_katten, [haar_katten], DICTATE),
                self.create_quiz(concept, haar_katten, [her_cats], INTERPRET),
                self.create_quiz(concept, her_cats, [haar_katten], WRITE),
                self.create_quiz(concept, zijn_katten, [his_cats], READ),
                self.create_quiz(concept, zijn_katten, [zijn_katten], DICTATE),
                self.create_quiz(concept, zijn_katten, [his_cats], INTERPRET),
                self.create_quiz(concept, his_cats, [zijn_katten], WRITE),
                self.create_quiz(concept, haar_katten, [zijn_katten], MASCULINE),
                self.create_quiz(concept, zijn_katten, [haar_katten], FEMININE),
                self.create_quiz(concept, haar_kat, [haar_katten], PLURAL),
                self.create_quiz(concept, haar_katten, [haar_kat], SINGULAR),
                self.create_quiz(concept, zijn_kat, [zijn_katten], PLURAL),
                self.create_quiz(concept, zijn_katten, [zijn_kat], SINGULAR),
            },
            create_quizzes(NL_EN, (), concept),
        )
