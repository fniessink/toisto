"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept
from toisto.model.language.grammar import Tense
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import GrammaticalQuizFactory, create_quizzes
from toisto.model.quiz.quiz_type import (
    ABBREVIATION,
    AFFIRMATIVE,
    ANTONYM,
    CARDINAL,
    COMPARATIVE_DEGREE,
    DECLARATIVE,
    DICTATE,
    DIMINUTIVE,
    FEMININE,
    FIRST_PERSON,
    FULL_FORM,
    IMPERATIVE,
    INFINITIVE,
    INTERPRET,
    INTERROGATIVE,
    MASCULINE,
    NEGATIVE,
    NEUTER,
    ORDER,
    ORDINAL,
    PAST_PERFECT_TENSE,
    PAST_TENSE,
    PLURAL,
    POSITIVE_DEGREE,
    PRESENT_PERFECT_TENSE,
    PRESENT_TENSE,
    READ,
    SECOND_PERSON,
    SINGULAR,
    SUPERLATIVE_DEGREE,
    THIRD_PERSON,
    WRITE,
    GrammaticalQuizType,
)
from toisto.tools import first

from ....base import EN_FI, EN_NL, FI_EN, FI_NL, NL_EN, NL_FI, ConceptDict, LabelDict, ToistoTestCase


class QuizFactoryTestCase(ToistoTestCase):
    """Base class for quiz factory unit tests."""

    def create_verb_with_person(self) -> Concept:
        """Create a verb with grammatical person."""
        return self.create_concept(
            "to eat",
            labels=[
                {
                    "label": {
                        "first person": "I eat",
                        "second person": "you eat",
                        "third person": "she eats",
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "first person": "ik eet",
                        "second person": "jij eet",
                        "third person": "zij eet",
                    },
                    "language": NL,
                },
            ],
        )

    def create_verb_with_tense_and_person(self, *tense: Tense) -> Concept:
        """Create a verb with grammatical person nested within tense."""
        label_en = {}
        label_nl = {}
        if "present tense" in tense:
            label_en["present tense"] = {"singular": "I eat", "plural": "we eat"}
            label_nl["present tense"] = {"singular": "ik eet", "plural": "wij eten"}
        if "past tense" in tense:
            label_en["past tense"] = {"singular": "I ate", "plural": "we ate"}
            label_nl["past tense"] = {"singular": "ik at", "plural": "wij aten"}
        if "present perfect tense" in tense:
            label_en["present perfect tense"] = {"singular": "I have eaten", "plural": "we have eaten"}
            label_nl["present perfect tense"] = {"singular": "ik heb gegeten", "plural": "wij hebben gegeten"}
        if "past perfect tense" in tense:
            label_en["past perfect tense"] = {"singular": "I had eaten", "plural": "we had eaten"}
            label_nl["past perfect tense"] = {"singular": "ik had gegeten", "plural": "wij hadden gegeten"}
        return self.create_concept(
            "to eat", labels=[{"label": label_en, "language": EN}, {"label": label_nl, "language": NL}]
        )

    def create_verb_with_infinitive_and_person(self) -> Concept:
        """Create a verb with infinitive and grammatical person."""
        return self.create_concept(
            "to sleep",
            labels=[
                {"label": {"infinitive": "to sleep", "singular": "I sleep", "plural": "we sleep"}, "language": EN},
                {"label": {"infinitive": "slapen", "singular": "ik slaap", "plural": "wij slapen"}, "language": NL},
            ],
        )

    def create_verb_with_infinitive_and_number_and_person(self) -> Concept:
        """Create a verb with infinitive and grammatical number nested with person."""
        return self.create_concept(
            "to be",
            labels=[
                {
                    "label": {
                        "infinitive": "olla",
                        "singular": {
                            "first person": "minä olen",
                            "second person": "sinä olet",
                            "third person": "hän on",
                        },
                        "plural": {
                            "first person": "me olemme",
                            "second person": "te olette",
                            "third person": "he ovat",
                        },
                    },
                    "language": FI,
                },
                {
                    "label": {
                        "infinitive": "zijn",
                        "singular": {"first person": "ik ben", "second person": "jij bent", "third person": "zij is"},
                        "plural": {
                            "first person": "wij zijn",
                            "second person": "jullie zijn",
                            "third person": "zij zijn",
                        },
                    },
                    "language": NL,
                },
            ],
        )

    def create_adjective_with_degrees_of_comparison(self, antonym: str = "") -> Concept:
        """Create an adjective with degrees of comparison."""
        labels: list[LabelDict] = [
            {
                "label": {"positive degree": "big", "comparative degree": "bigger", "superlative degree": "biggest"},
                "language": EN,
            },
            {
                "label": {"positive degree": "groot", "comparative degree": "groter", "superlative degree": "grootst"},
                "language": NL,
            },
        ]
        big: ConceptDict = {"antonym": antonym} if antonym else {}
        return self.create_concept("big", big, labels=labels)

    def create_noun(self) -> Concept:
        """Create a simple noun."""
        return self.create_concept(
            "mall", labels=[{"label": "kauppakeskus", "language": FI}, {"label": "het winkelcentrum", "language": NL}]
        )

    def create_noun_with_grammatical_number(self) -> Concept:
        """Create a noun with grammatical number."""
        return self.create_concept(
            "morning",
            labels=[
                {"label": {"singular": "aamu", "plural": "aamut"}, "language": FI},
                {"label": {"singular": "de ochtend", "plural": "de ochtenden"}, "language": NL},
            ],
        )

    def create_noun_with_grammatical_gender(self) -> Concept:
        """Create a noun with grammatical gender."""
        return self.create_concept(
            "cat",
            labels=[
                {"label": {"feminine": "her cat", "masculine": "his cat"}, "language": EN},
                {"label": {"feminine": "haar kat", "masculine": "zijn kat"}, "language": NL},
            ],
        )

    def create_noun_with_grammatical_gender_including_neuter(self) -> Concept:
        """Create a noun with grammatical gender, including neuter."""
        return self.create_concept(
            "bone",
            labels=[
                {"label": {"feminine": "her bone", "masculine": "his bone", "neuter": "its bone"}, "language": EN},
                {"label": {"feminine": "haar bot", "masculine": "zijn bot", "neuter": "zijn bot"}, "language": NL},
            ],
        )

    def create_noun_with_grammatical_number_and_gender(self) -> Concept:
        """Create a noun with grammatical number and grammatical gender."""
        return self.create_concept(
            "cat",
            labels=[
                {
                    "label": {
                        "singular": {"feminine": "her cat", "masculine": "his cat"},
                        "plural": {"feminine": "her cats", "masculine": "his cats"},
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "singular": {"feminine": "haar kat", "masculine": "zijn kat"},
                        "plural": {"feminine": "haar katten", "masculine": "zijn katten"},
                    },
                    "language": NL,
                },
            ],
        )


class ConceptQuizzesTest(QuizFactoryTestCase):
    """Unit tests for the concept class."""

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
                self.create_quiz(concept, ketchup, [ketsupit], WRITE),
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
                self.create_quiz(concept, means_of_transportation, [vervoersmiddelen], WRITE),
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
        kauppakeskus, ostoskeskus, kauppakeskukset, ostoskeskukset = concept.labels(FI)
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

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = self.create_adjective_with_degrees_of_comparison()
        groot, groter, grootst = concept.labels(NL)
        big, bigger, biggest = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, groot, [big], READ),
                self.create_quiz(concept, groot, [groot], DICTATE),
                self.create_quiz(concept, groot, [big], INTERPRET),
                self.create_quiz(concept, big, [groot], WRITE),
                self.create_quiz(concept, groter, [bigger], READ),
                self.create_quiz(concept, groter, [groter], DICTATE),
                self.create_quiz(concept, groter, [bigger], INTERPRET),
                self.create_quiz(concept, bigger, [groter], WRITE),
                self.create_quiz(concept, grootst, [biggest], READ),
                self.create_quiz(concept, grootst, [grootst], DICTATE),
                self.create_quiz(concept, grootst, [biggest], INTERPRET),
                self.create_quiz(concept, biggest, [grootst], WRITE),
                self.create_quiz(concept, groot, [groter], COMPARATIVE_DEGREE),
                self.create_quiz(concept, groot, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, groter, [groot], POSITIVE_DEGREE),
                self.create_quiz(concept, groter, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, grootst, [groot], POSITIVE_DEGREE),
                self.create_quiz(concept, grootst, [groter], COMPARATIVE_DEGREE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        concept = self.create_concept(
            "big",
            labels=[
                {
                    "concept": "big",
                    "label": {
                        "positive degree": "big",
                        "comparative degree": "bigger",
                        "superlative degree": "biggest",
                    },
                    "language": EN,
                },
                {
                    "concept": "big",
                    "label": {"positive degree": "iso", "comparative degree": "isompi", "superlative degree": "isoin"},
                    "language": FI,
                },
                {
                    "concept": "big",
                    "label": {
                        "positive degree": "suuri",
                        "comparative degree": "suurempi",
                        "superlative degree": "suurin",
                    },
                    "language": FI,
                },
            ],
        )
        big, bigger, biggest = concept.labels(EN)
        iso, suuri, isompi, suurempi, isoin, suurin = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(concept, iso, [big], READ),
                self.create_quiz(concept, suuri, [big], READ),
                self.create_quiz(concept, iso, [iso], DICTATE),
                self.create_quiz(concept, iso, [big], INTERPRET),
                self.create_quiz(concept, suuri, [suuri], DICTATE),
                self.create_quiz(concept, suuri, [big], INTERPRET),
                self.create_quiz(concept, big, [iso, suuri], WRITE),
                self.create_quiz(concept, isompi, [bigger], READ),
                self.create_quiz(concept, suurempi, [bigger], READ),
                self.create_quiz(concept, isompi, [isompi], DICTATE),
                self.create_quiz(concept, isompi, [bigger], INTERPRET),
                self.create_quiz(concept, suurempi, [suurempi], DICTATE),
                self.create_quiz(concept, suurempi, [bigger], INTERPRET),
                self.create_quiz(concept, bigger, [isompi, suurempi], WRITE),
                self.create_quiz(concept, isoin, [biggest], READ),
                self.create_quiz(concept, suurin, [biggest], READ),
                self.create_quiz(concept, isoin, [isoin], DICTATE),
                self.create_quiz(concept, isoin, [biggest], INTERPRET),
                self.create_quiz(concept, suurin, [suurin], DICTATE),
                self.create_quiz(concept, suurin, [biggest], INTERPRET),
                self.create_quiz(concept, biggest, [isoin, suurin], WRITE),
                self.create_quiz(concept, iso, [isompi], COMPARATIVE_DEGREE),
                self.create_quiz(concept, suuri, [suurempi], COMPARATIVE_DEGREE),
                self.create_quiz(concept, iso, [isoin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, suuri, [suurin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, isompi, [iso], POSITIVE_DEGREE),
                self.create_quiz(concept, suurempi, [suuri], POSITIVE_DEGREE),
                self.create_quiz(concept, isompi, [isoin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, suurempi, [suurin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, isoin, [iso], POSITIVE_DEGREE),
                self.create_quiz(concept, suurin, [suuri], POSITIVE_DEGREE),
                self.create_quiz(concept, isoin, [isompi], COMPARATIVE_DEGREE),
                self.create_quiz(concept, suurin, [suurempi], COMPARATIVE_DEGREE),
            },
            create_quizzes(FI_EN, (), concept),
        )

    def test_degrees_of_comparison_with_antonym(self):
        """Test that quizzes can be generated for degrees of comparison with antonym."""
        big_concept = self.create_adjective_with_degrees_of_comparison(antonym="small")
        small_concept = self.create_concept(
            "small",
            {"antonym": "big"},
            labels=[
                {
                    "label": {
                        "positive degree": "small",
                        "comparative degree": "smaller",
                        "superlative degree": "smallest",
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "positive degree": "klein",
                        "comparative degree": "kleiner",
                        "superlative degree": "kleinst",
                    },
                    "language": NL,
                },
            ],
        )
        groot, groter, grootst = big_concept.labels(NL)
        big, bigger, biggest = big_concept.labels(EN)
        klein, kleiner, kleinst = small_concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(big_concept, groot, [big], READ),
                self.create_quiz(big_concept, groot, [groot], DICTATE),
                self.create_quiz(big_concept, groot, [big], INTERPRET),
                self.create_quiz(big_concept, big, [groot], WRITE),
                self.create_quiz(big_concept, groter, [bigger], READ),
                self.create_quiz(big_concept, groter, [groter], DICTATE),
                self.create_quiz(big_concept, groter, [bigger], INTERPRET),
                self.create_quiz(big_concept, bigger, [groter], WRITE),
                self.create_quiz(big_concept, grootst, [biggest], READ),
                self.create_quiz(big_concept, grootst, [grootst], DICTATE),
                self.create_quiz(big_concept, grootst, [biggest], INTERPRET),
                self.create_quiz(big_concept, biggest, [grootst], WRITE),
                self.create_quiz(big_concept, groot, [groter], COMPARATIVE_DEGREE),
                self.create_quiz(big_concept, groot, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(big_concept, groot, [klein], ANTONYM),
                self.create_quiz(big_concept, groter, [groot], POSITIVE_DEGREE),
                self.create_quiz(big_concept, groter, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(big_concept, groter, [kleiner], ANTONYM),
                self.create_quiz(big_concept, grootst, [groot], POSITIVE_DEGREE),
                self.create_quiz(big_concept, grootst, [groter], COMPARATIVE_DEGREE),
                self.create_quiz(big_concept, grootst, [kleinst], ANTONYM),
            },
            create_quizzes(NL_EN, (), big_concept),
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = self.create_verb_with_person()
        ik_eet, jij_eet, zij_eet = concept.labels(NL)
        i_eat, you_eat, she_eats = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_eet, [i_eat], READ),
                self.create_quiz(concept, ik_eet, [ik_eet], DICTATE),
                self.create_quiz(concept, ik_eet, [i_eat], INTERPRET),
                self.create_quiz(concept, i_eat, [ik_eet], WRITE),
                self.create_quiz(concept, jij_eet, [you_eat], READ),
                self.create_quiz(concept, jij_eet, [jij_eet], DICTATE),
                self.create_quiz(concept, jij_eet, [you_eat], INTERPRET),
                self.create_quiz(concept, you_eat, [jij_eet], WRITE),
                self.create_quiz(concept, zij_eet, [she_eats], READ),
                self.create_quiz(concept, zij_eet, [zij_eet], DICTATE),
                self.create_quiz(concept, zij_eet, [she_eats], INTERPRET),
                self.create_quiz(concept, she_eats, [zij_eet], WRITE),
                self.create_quiz(concept, ik_eet, [jij_eet], SECOND_PERSON),
                self.create_quiz(concept, ik_eet, [zij_eet], THIRD_PERSON),
                self.create_quiz(concept, jij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(concept, jij_eet, [zij_eet], THIRD_PERSON),
                self.create_quiz(concept, zij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(concept, zij_eet, [jij_eet], SECOND_PERSON),
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
        i_eat, you_eat, she_eats, he_eats = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_eet, [i_eat], READ),
                self.create_quiz(concept, ik_eet, [ik_eet], DICTATE),
                self.create_quiz(concept, ik_eet, [i_eat], INTERPRET),
                self.create_quiz(concept, i_eat, [ik_eet], WRITE),
                self.create_quiz(concept, jij_eet, [you_eat], READ),
                self.create_quiz(concept, jij_eet, [jij_eet], DICTATE),
                self.create_quiz(concept, jij_eet, [you_eat], INTERPRET),
                self.create_quiz(concept, you_eat, [jij_eet], WRITE),
                self.create_quiz(concept, zij_eet, [she_eats], READ),
                self.create_quiz(concept, zij_eet, [zij_eet], DICTATE),
                self.create_quiz(concept, zij_eet, [she_eats], INTERPRET),
                self.create_quiz(concept, she_eats, [zij_eet], WRITE),
                self.create_quiz(concept, hij_eet, [he_eats], READ),
                self.create_quiz(concept, hij_eet, [hij_eet], DICTATE),
                self.create_quiz(concept, hij_eet, [he_eats], INTERPRET),
                self.create_quiz(concept, he_eats, [hij_eet], WRITE),
                self.create_quiz(concept, zij_eet, [hij_eet], MASCULINE),
                self.create_quiz(concept, hij_eet, [zij_eet], FEMININE),
                self.create_quiz(concept, ik_eet, [jij_eet], SECOND_PERSON),
                self.create_quiz(concept, ik_eet, [zij_eet], GrammaticalQuizType(quiz_types=(THIRD_PERSON, FEMININE))),
                self.create_quiz(concept, ik_eet, [hij_eet], GrammaticalQuizType(quiz_types=(THIRD_PERSON, MASCULINE))),
                self.create_quiz(concept, jij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(concept, jij_eet, [zij_eet], GrammaticalQuizType(quiz_types=(THIRD_PERSON, FEMININE))),
                self.create_quiz(
                    concept, jij_eet, [hij_eet], GrammaticalQuizType(quiz_types=(THIRD_PERSON, MASCULINE))
                ),
                self.create_quiz(concept, zij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(concept, zij_eet, [jij_eet], SECOND_PERSON),
                self.create_quiz(concept, hij_eet, [ik_eet], FIRST_PERSON),
                self.create_quiz(concept, hij_eet, [jij_eet], SECOND_PERSON),
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
                self.create_quiz(concept, syön, [i_eat], READ),
                self.create_quiz(concept, syön, [syön], DICTATE),
                self.create_quiz(concept, syön, [i_eat], INTERPRET),
                self.create_quiz(concept, i_eat, [syön], WRITE),
                self.create_quiz(concept, syöt, [you_eat], READ),
                self.create_quiz(concept, syöt, [syöt], DICTATE),
                self.create_quiz(concept, syöt, [you_eat], INTERPRET),
                self.create_quiz(concept, you_eat, [syöt], WRITE),
                self.create_quiz(concept, syö, [she_eats, he_eats], READ),
                self.create_quiz(concept, syö, [syö], DICTATE),
                self.create_quiz(concept, syö, [she_eats, he_eats], INTERPRET),
                self.create_quiz(concept, she_eats, [syö], WRITE),
                self.create_quiz(concept, he_eats, [syö], WRITE),
                self.create_quiz(concept, syön, [syöt], SECOND_PERSON),
                self.create_quiz(concept, syön, [syö], THIRD_PERSON),
                self.create_quiz(concept, syöt, [syön], FIRST_PERSON),
                self.create_quiz(concept, syöt, [syö], THIRD_PERSON),
                self.create_quiz(concept, syö, [syön], FIRST_PERSON),
                self.create_quiz(concept, syö, [syöt], SECOND_PERSON),
            },
            create_quizzes(FI_EN, (), concept),
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

    def test_tense_nested_with_grammatical_number_nested_and_grammatical_person(self):
        """Test generating quizzes for tense, grammatical number, and grammatical person."""
        concept = self.create_concept(
            "to be",
            labels=[
                {
                    "label": {
                        "present tense": {
                            "singular": {
                                "first person": "minä olen",
                                "second person": "sinä olet",
                                "third person": "hän on",
                            },
                            "plural": {
                                "first person": "me olemme",
                                "second person": "te olette",
                                "third person": "he ovat",
                            },
                        },
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
                        "present tense": {
                            "singular": {
                                "first person": "ik ben",
                                "second person": "jij bent",
                                "third person": "zij is",
                            },
                            "plural": {
                                "first person": "wij zijn",
                                "second person": "jullie zijn",
                                "third person": "zij zijn",
                            },
                        },
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
        (
            ik_ben,
            jij_bent,
            zij_is,
            wij_zijn,
            jullie_zijn,
            zij_zijn,
            ik_was,
            jij_was,
            zij_was,
            wij_waren,
            jullie_waren,
            zij_waren,
        ) = concept.labels(NL)
        (
            minä_olen,
            sinä_olet,
            hän_on,
            me_olemme,
            te_olette,
            he_ovat,
            minä_olin,
            sinä_olit,
            hän_oli,
            me_olimme,
            te_olitte,
            he_olivat,
        ) = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_ben, [minä_olen], READ),
                self.create_quiz(concept, ik_ben, [ik_ben], DICTATE),
                self.create_quiz(concept, ik_ben, [minä_olen], INTERPRET),
                self.create_quiz(concept, minä_olen, [ik_ben], WRITE),
                self.create_quiz(concept, jij_bent, [sinä_olet], READ),
                self.create_quiz(concept, jij_bent, [jij_bent], DICTATE),
                self.create_quiz(concept, jij_bent, [sinä_olet], INTERPRET),
                self.create_quiz(concept, sinä_olet, [jij_bent], WRITE),
                self.create_quiz(concept, zij_is, [hän_on], READ),
                self.create_quiz(concept, zij_is, [zij_is], DICTATE),
                self.create_quiz(concept, zij_is, [hän_on], INTERPRET),
                self.create_quiz(concept, hän_on, [zij_is], WRITE),
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
                self.create_quiz(concept, jullie_zijn, [te_olette], READ),
                self.create_quiz(concept, jullie_zijn, [jullie_zijn], DICTATE),
                self.create_quiz(concept, jullie_zijn, [te_olette], INTERPRET),
                self.create_quiz(concept, te_olette, [jullie_zijn], WRITE),
                self.create_quiz(concept, zij_zijn, [he_ovat], READ),
                self.create_quiz(concept, zij_zijn, [zij_zijn], DICTATE),
                self.create_quiz(concept, zij_zijn, [he_ovat], INTERPRET),
                self.create_quiz(concept, he_ovat, [zij_zijn], WRITE),
                self.create_quiz(concept, wij_zijn, [jullie_zijn], SECOND_PERSON),
                self.create_quiz(concept, wij_zijn, [zij_zijn], THIRD_PERSON),
                self.create_quiz(concept, jullie_zijn, [wij_zijn], FIRST_PERSON),
                self.create_quiz(concept, jullie_zijn, [zij_zijn], THIRD_PERSON),
                self.create_quiz(concept, zij_zijn, [wij_zijn], FIRST_PERSON),
                self.create_quiz(concept, zij_zijn, [jullie_zijn], SECOND_PERSON),
                self.create_quiz(concept, ik_ben, [wij_zijn], PLURAL),
                self.create_quiz(concept, jij_bent, [jullie_zijn], PLURAL),
                self.create_quiz(concept, zij_is, [zij_zijn], PLURAL),
                self.create_quiz(concept, wij_zijn, [ik_ben], SINGULAR),
                self.create_quiz(concept, jullie_zijn, [jij_bent], SINGULAR),
                self.create_quiz(concept, zij_zijn, [zij_is], SINGULAR),
                self.create_quiz(concept, ik_was, [minä_olin], READ),
                self.create_quiz(concept, ik_was, [ik_was], DICTATE),
                self.create_quiz(concept, ik_was, [minä_olin], INTERPRET),
                self.create_quiz(concept, minä_olin, [ik_was], WRITE),
                self.create_quiz(concept, jij_was, [sinä_olit], READ),
                self.create_quiz(concept, jij_was, [jij_was], DICTATE),
                self.create_quiz(concept, jij_was, [sinä_olit], INTERPRET),
                self.create_quiz(concept, sinä_olit, [jij_was], WRITE),
                self.create_quiz(concept, zij_was, [hän_oli], READ),
                self.create_quiz(concept, zij_was, [zij_was], DICTATE),
                self.create_quiz(concept, zij_was, [hän_oli], INTERPRET),
                self.create_quiz(concept, hän_oli, [zij_was], WRITE),
                self.create_quiz(concept, ik_was, [jij_was], SECOND_PERSON),
                self.create_quiz(concept, ik_was, [zij_was], THIRD_PERSON),
                self.create_quiz(concept, jij_was, [ik_was], FIRST_PERSON),
                self.create_quiz(concept, jij_was, [zij_was], THIRD_PERSON),
                self.create_quiz(concept, zij_was, [ik_was], FIRST_PERSON),
                self.create_quiz(concept, zij_was, [jij_was], SECOND_PERSON),
                self.create_quiz(concept, wij_waren, [me_olimme], READ),
                self.create_quiz(concept, wij_waren, [wij_waren], DICTATE),
                self.create_quiz(concept, wij_waren, [me_olimme], INTERPRET),
                self.create_quiz(concept, me_olimme, [wij_waren], WRITE),
                self.create_quiz(concept, jullie_waren, [te_olitte], READ),
                self.create_quiz(concept, jullie_waren, [jullie_waren], DICTATE),
                self.create_quiz(concept, jullie_waren, [te_olitte], INTERPRET),
                self.create_quiz(concept, te_olitte, [jullie_waren], WRITE),
                self.create_quiz(concept, zij_waren, [he_olivat], READ),
                self.create_quiz(concept, zij_waren, [zij_waren], DICTATE),
                self.create_quiz(concept, zij_waren, [he_olivat], INTERPRET),
                self.create_quiz(concept, he_olivat, [zij_waren], WRITE),
                self.create_quiz(concept, wij_waren, [jullie_waren], SECOND_PERSON),
                self.create_quiz(concept, wij_waren, [zij_waren], THIRD_PERSON),
                self.create_quiz(concept, jullie_waren, [wij_waren], FIRST_PERSON),
                self.create_quiz(concept, jullie_waren, [zij_waren], THIRD_PERSON),
                self.create_quiz(concept, zij_waren, [wij_waren], FIRST_PERSON),
                self.create_quiz(concept, zij_waren, [jullie_waren], SECOND_PERSON),
                self.create_quiz(concept, ik_was, [wij_waren], PLURAL),
                self.create_quiz(concept, jij_was, [jullie_waren], PLURAL),
                self.create_quiz(concept, zij_was, [zij_waren], PLURAL),
                self.create_quiz(concept, wij_waren, [ik_was], SINGULAR),
                self.create_quiz(concept, jullie_waren, [jij_was], SINGULAR),
                self.create_quiz(concept, zij_waren, [zij_was], SINGULAR),
                self.create_quiz(concept, ik_ben, [ik_was], PAST_TENSE),
                self.create_quiz(concept, jij_bent, [jij_was], PAST_TENSE),
                self.create_quiz(concept, zij_is, [zij_was], PAST_TENSE),
                self.create_quiz(concept, wij_zijn, [wij_waren], PAST_TENSE),
                self.create_quiz(concept, jullie_zijn, [jullie_waren], PAST_TENSE),
                self.create_quiz(concept, zij_zijn, [zij_waren], PAST_TENSE),
                self.create_quiz(concept, ik_was, [ik_ben], PRESENT_TENSE),
                self.create_quiz(concept, jij_was, [jij_bent], PRESENT_TENSE),
                self.create_quiz(concept, zij_was, [zij_is], PRESENT_TENSE),
                self.create_quiz(concept, wij_waren, [wij_zijn], PRESENT_TENSE),
                self.create_quiz(concept, jullie_waren, [jullie_zijn], PRESENT_TENSE),
                self.create_quiz(concept, zij_waren, [zij_zijn], PRESENT_TENSE),
            },
            create_quizzes(NL_FI, (), concept),
        )


class TenseQuizzesTest(QuizFactoryTestCase):
    """Unit tests for concepts with tenses."""

    def test_present_and_past_tense_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for present and past tense nested with grammatical person."""
        concept = self.create_verb_with_tense_and_person("present tense", "past tense")
        i_eat, we_eat, i_ate, we_ate = concept.labels(EN)
        ik_eet, wij_eten, ik_at, wij_aten = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_eet, [i_eat], READ),
                self.create_quiz(concept, ik_eet, [ik_eet], DICTATE),
                self.create_quiz(concept, ik_eet, [i_eat], INTERPRET),
                self.create_quiz(concept, i_eat, [ik_eet], WRITE),
                self.create_quiz(concept, wij_eten, [we_eat], READ),
                self.create_quiz(concept, wij_eten, [wij_eten], DICTATE),
                self.create_quiz(concept, wij_eten, [we_eat], INTERPRET),
                self.create_quiz(concept, we_eat, [wij_eten], WRITE),
                self.create_quiz(concept, ik_eet, [wij_eten], PLURAL),
                self.create_quiz(concept, wij_eten, [ik_eet], SINGULAR),
                self.create_quiz(concept, ik_at, [i_ate], READ),
                self.create_quiz(concept, ik_at, [ik_at], DICTATE),
                self.create_quiz(concept, ik_at, [i_ate], INTERPRET),
                self.create_quiz(concept, i_ate, [ik_at], WRITE),
                self.create_quiz(concept, wij_aten, [we_ate], READ),
                self.create_quiz(concept, wij_aten, [wij_aten], DICTATE),
                self.create_quiz(concept, wij_aten, [we_ate], INTERPRET),
                self.create_quiz(concept, we_ate, [wij_aten], WRITE),
                self.create_quiz(concept, ik_at, [wij_aten], PLURAL),
                self.create_quiz(concept, wij_aten, [ik_at], SINGULAR),
                self.create_quiz(concept, ik_eet, [ik_at], PAST_TENSE),
                self.create_quiz(concept, wij_eten, [wij_aten], PAST_TENSE),
                self.create_quiz(concept, ik_at, [ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, wij_aten, [wij_eten], PRESENT_TENSE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_all_tenses_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for all tenses nested with grammatical person."""
        concept = self.create_verb_with_tense_and_person(
            "present tense", "past tense", "present perfect tense", "past perfect tense"
        )
        ik_eet, wij_eten, ik_at, wij_aten, ik_heb_gegeten, wij_hebben_gegeten, ik_had_gegeten, wij_hadden_gegeten = (
            concept.labels(NL)
        )
        i_eat, we_eat, i_ate, we_ate, i_have_eaten, we_have_eaten, i_had_eaten, we_had_eaten = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_eet, [i_eat], READ),
                self.create_quiz(concept, ik_eet, [ik_eet], DICTATE),
                self.create_quiz(concept, ik_eet, [i_eat], INTERPRET),
                self.create_quiz(concept, i_eat, [ik_eet], WRITE),
                self.create_quiz(concept, wij_eten, [we_eat], READ),
                self.create_quiz(concept, wij_eten, [wij_eten], DICTATE),
                self.create_quiz(concept, wij_eten, [we_eat], INTERPRET),
                self.create_quiz(concept, we_eat, [wij_eten], WRITE),
                self.create_quiz(concept, ik_eet, [wij_eten], PLURAL),
                self.create_quiz(concept, wij_eten, [ik_eet], SINGULAR),
                self.create_quiz(concept, ik_at, [i_ate], READ),
                self.create_quiz(concept, ik_at, [ik_at], DICTATE),
                self.create_quiz(concept, ik_at, [i_ate], INTERPRET),
                self.create_quiz(concept, i_ate, [ik_at], WRITE),
                self.create_quiz(concept, wij_aten, [we_ate], READ),
                self.create_quiz(concept, wij_aten, [wij_aten], DICTATE),
                self.create_quiz(concept, wij_aten, [we_ate], INTERPRET),
                self.create_quiz(concept, we_ate, [wij_aten], WRITE),
                self.create_quiz(concept, ik_at, [wij_aten], PLURAL),
                self.create_quiz(concept, wij_aten, [ik_at], SINGULAR),
                self.create_quiz(concept, ik_heb_gegeten, [i_have_eaten], READ),
                self.create_quiz(concept, ik_heb_gegeten, [ik_heb_gegeten], DICTATE),
                self.create_quiz(concept, ik_heb_gegeten, [i_have_eaten], INTERPRET),
                self.create_quiz(concept, i_have_eaten, [ik_heb_gegeten], WRITE),
                self.create_quiz(concept, wij_hebben_gegeten, [we_have_eaten], READ),
                self.create_quiz(concept, wij_hebben_gegeten, [wij_hebben_gegeten], DICTATE),
                self.create_quiz(concept, wij_hebben_gegeten, [we_have_eaten], INTERPRET),
                self.create_quiz(concept, we_have_eaten, [wij_hebben_gegeten], WRITE),
                self.create_quiz(concept, ik_heb_gegeten, [wij_hebben_gegeten], PLURAL),
                self.create_quiz(concept, wij_hebben_gegeten, [ik_heb_gegeten], SINGULAR),
                self.create_quiz(concept, ik_had_gegeten, [i_had_eaten], READ),
                self.create_quiz(concept, ik_had_gegeten, [ik_had_gegeten], DICTATE),
                self.create_quiz(concept, ik_had_gegeten, [i_had_eaten], INTERPRET),
                self.create_quiz(concept, i_had_eaten, [ik_had_gegeten], WRITE),
                self.create_quiz(concept, wij_hadden_gegeten, [we_had_eaten], READ),
                self.create_quiz(concept, wij_hadden_gegeten, [wij_hadden_gegeten], DICTATE),
                self.create_quiz(concept, wij_hadden_gegeten, [we_had_eaten], INTERPRET),
                self.create_quiz(concept, we_had_eaten, [wij_hadden_gegeten], WRITE),
                self.create_quiz(concept, ik_had_gegeten, [wij_hadden_gegeten], PLURAL),
                self.create_quiz(concept, wij_hadden_gegeten, [ik_had_gegeten], SINGULAR),
                self.create_quiz(concept, ik_eet, [ik_at], PAST_TENSE),
                self.create_quiz(concept, ik_eet, [ik_heb_gegeten], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, ik_eet, [ik_had_gegeten], PAST_PERFECT_TENSE),
                self.create_quiz(concept, wij_eten, [wij_aten], PAST_TENSE),
                self.create_quiz(concept, wij_eten, [wij_hebben_gegeten], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, wij_eten, [wij_hadden_gegeten], PAST_PERFECT_TENSE),
                self.create_quiz(concept, ik_at, [ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, ik_at, [ik_heb_gegeten], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, ik_at, [ik_had_gegeten], PAST_PERFECT_TENSE),
                self.create_quiz(concept, wij_aten, [wij_eten], PRESENT_TENSE),
                self.create_quiz(concept, wij_aten, [wij_hebben_gegeten], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, wij_aten, [wij_hadden_gegeten], PAST_PERFECT_TENSE),
                self.create_quiz(concept, ik_heb_gegeten, [ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, ik_heb_gegeten, [ik_had_gegeten], PAST_PERFECT_TENSE),
                self.create_quiz(concept, ik_heb_gegeten, [ik_at], PAST_TENSE),
                self.create_quiz(concept, wij_hebben_gegeten, [wij_eten], PRESENT_TENSE),
                self.create_quiz(concept, wij_hebben_gegeten, [wij_aten], PAST_TENSE),
                self.create_quiz(concept, wij_hebben_gegeten, [wij_hadden_gegeten], PAST_PERFECT_TENSE),
                self.create_quiz(concept, ik_had_gegeten, [ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, ik_had_gegeten, [ik_at], PAST_TENSE),
                self.create_quiz(concept, ik_had_gegeten, [ik_heb_gegeten], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, wij_hadden_gegeten, [wij_eten], PRESENT_TENSE),
                self.create_quiz(concept, wij_hadden_gegeten, [wij_aten], PAST_TENSE),
                self.create_quiz(concept, wij_hadden_gegeten, [wij_hebben_gegeten], PRESENT_PERFECT_TENSE),
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
        eten, ik_eet, wij_eten, ik_at, wij_aten = concept.labels(NL)
        to_eat, i_eat, we_eat, i_ate, we_ate = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, ik_eet, [i_eat], READ),
                self.create_quiz(concept, ik_eet, [ik_eet], DICTATE),
                self.create_quiz(concept, ik_eet, [i_eat], INTERPRET),
                self.create_quiz(concept, i_eat, [ik_eet], WRITE),
                self.create_quiz(concept, wij_eten, [we_eat], READ),
                self.create_quiz(concept, wij_eten, [wij_eten], DICTATE),
                self.create_quiz(concept, wij_eten, [we_eat], INTERPRET),
                self.create_quiz(concept, we_eat, [wij_eten], WRITE),
                self.create_quiz(concept, ik_eet, [wij_eten], PLURAL),
                self.create_quiz(concept, wij_eten, [ik_eet], SINGULAR),
                self.create_quiz(concept, ik_at, [i_ate], READ),
                self.create_quiz(concept, ik_at, [ik_at], DICTATE),
                self.create_quiz(concept, ik_at, [i_ate], INTERPRET),
                self.create_quiz(concept, i_ate, [ik_at], WRITE),
                self.create_quiz(concept, wij_aten, [we_ate], READ),
                self.create_quiz(concept, wij_aten, [wij_aten], DICTATE),
                self.create_quiz(concept, wij_aten, [we_ate], INTERPRET),
                self.create_quiz(concept, we_ate, [wij_aten], WRITE),
                self.create_quiz(concept, ik_at, [wij_aten], PLURAL),
                self.create_quiz(concept, wij_aten, [ik_at], SINGULAR),
                self.create_quiz(concept, ik_eet, [ik_at], PAST_TENSE),
                self.create_quiz(concept, wij_eten, [wij_aten], PAST_TENSE),
                self.create_quiz(concept, ik_at, [ik_eet], PRESENT_TENSE),
                self.create_quiz(concept, wij_aten, [wij_eten], PRESENT_TENSE),
                self.create_quiz(concept, eten, [to_eat], READ),
                self.create_quiz(concept, eten, [eten], DICTATE),
                self.create_quiz(concept, eten, [to_eat], INTERPRET),
                self.create_quiz(concept, to_eat, [eten], WRITE),
                self.create_quiz(concept, ik_eet, [eten], INFINITIVE),
                self.create_quiz(concept, wij_eten, [eten], INFINITIVE),
                self.create_quiz(concept, ik_at, [eten], INFINITIVE),
                self.create_quiz(concept, wij_aten, [eten], INFINITIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )


class GrammaticalMoodTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical moods."""

    def test_declarative_and_interrogative_moods(self):
        """Test that quizzes can be generated for the declarative and interrogative moods."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": {"declarative": "The car is black.", "interrogative": "Is the car black?"}, "language": EN},
                {"label": {"declarative": "De auto is zwart.", "interrogative": "Is de auto zwart?"}, "language": NL},
            ],
        )
        de_auto_is_zwart, is_de_auto_zwart = concept.labels(NL)
        the_car_is_black, is_the_car_black = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, de_auto_is_zwart, [the_car_is_black], READ),
                self.create_quiz(concept, de_auto_is_zwart, [de_auto_is_zwart], DICTATE),
                self.create_quiz(concept, de_auto_is_zwart, [the_car_is_black], INTERPRET),
                self.create_quiz(concept, the_car_is_black, [de_auto_is_zwart], WRITE),
                self.create_quiz(concept, is_de_auto_zwart, [is_the_car_black], READ),
                self.create_quiz(concept, is_de_auto_zwart, [is_de_auto_zwart], DICTATE),
                self.create_quiz(concept, is_de_auto_zwart, [is_the_car_black], INTERPRET),
                self.create_quiz(concept, is_the_car_black, [is_de_auto_zwart], WRITE),
                self.create_quiz(concept, de_auto_is_zwart, [is_de_auto_zwart], INTERROGATIVE),
                self.create_quiz(concept, is_de_auto_zwart, [de_auto_is_zwart], DECLARATIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_declarative_and_imperative_moods(self):
        """Test that quizzes can be generated for the declarative and imperative moods."""
        concept = self.create_concept(
            "you run",
            labels=[
                {"label": {"declarative": "You run.", "imperative": "Run!"}, "language": EN},
                {"label": {"declarative": "Jij rent.", "imperative": "Ren!"}, "language": NL},
            ],
        )
        jij_rent, ren = concept.labels(NL)
        you_run, run = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, jij_rent, [you_run], READ),
                self.create_quiz(concept, jij_rent, [jij_rent], DICTATE),
                self.create_quiz(concept, jij_rent, [you_run], INTERPRET),
                self.create_quiz(concept, you_run, [jij_rent], WRITE),
                self.create_quiz(concept, ren, [run], READ),
                self.create_quiz(concept, ren, [ren], DICTATE),
                self.create_quiz(concept, ren, [run], INTERPRET),
                self.create_quiz(concept, run, [ren], WRITE),
                self.create_quiz(concept, jij_rent, [ren], IMPERATIVE),
                self.create_quiz(concept, ren, [jij_rent], DECLARATIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_declarative_interrogative_and_imperative_moods(self):
        """Test that quizzes can be generated for the declarative, interrogative, and imperative moods."""
        concept = self.create_concept(
            "you run",
            labels=[
                {
                    "label": {"declarative": "You run.", "interrogative": "Do you run?", "imperative": "Run!"},
                    "language": EN,
                },
                {
                    "label": {"declarative": "Jij rent.", "interrogative": "Ren jij?", "imperative": "Ren!"},
                    "language": NL,
                },
            ],
        )
        jij_rent, ren_jij, ren = concept.labels(NL)
        you_run, do_you_run, run = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, jij_rent, [you_run], READ),
                self.create_quiz(concept, jij_rent, [jij_rent], DICTATE),
                self.create_quiz(concept, jij_rent, [you_run], INTERPRET),
                self.create_quiz(concept, you_run, [jij_rent], WRITE),
                self.create_quiz(concept, ren_jij, [do_you_run], READ),
                self.create_quiz(concept, ren_jij, [ren_jij], DICTATE),
                self.create_quiz(concept, ren_jij, [do_you_run], INTERPRET),
                self.create_quiz(concept, do_you_run, [ren_jij], WRITE),
                self.create_quiz(concept, ren, [run], READ),
                self.create_quiz(concept, ren, [ren], DICTATE),
                self.create_quiz(concept, ren, [run], INTERPRET),
                self.create_quiz(concept, run, [ren], WRITE),
                self.create_quiz(concept, jij_rent, [ren], IMPERATIVE),
                self.create_quiz(concept, jij_rent, [ren_jij], INTERROGATIVE),
                self.create_quiz(concept, ren, [jij_rent], DECLARATIVE),
                self.create_quiz(concept, ren, [ren_jij], INTERROGATIVE),
                self.create_quiz(concept, ren_jij, [ren], IMPERATIVE),
                self.create_quiz(concept, ren_jij, [jij_rent], DECLARATIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )


class GrammaticalPolarityTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical polarities."""

    def test_affirmative_and_negative_polarities(self):
        """Test that quizzes can be generated for the affirmative and negative polarities."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": {"affirmative": "The car is black.", "negative": "The car is not black."}, "language": EN},
                {"label": {"affirmative": "De auto is zwart.", "negative": "De auto is niet zwart."}, "language": NL},
            ],
        )
        de_auto_is_zwart, de_auto_is_niet_zwart = concept.labels(NL)
        the_car_is_black, the_car_is_not_black = concept.labels(EN)
        self.assertSetEqual(
            {
                self.create_quiz(concept, de_auto_is_zwart, [the_car_is_black], READ),
                self.create_quiz(concept, de_auto_is_zwart, [de_auto_is_zwart], DICTATE),
                self.create_quiz(concept, de_auto_is_zwart, [the_car_is_black], INTERPRET),
                self.create_quiz(concept, the_car_is_black, [de_auto_is_zwart], WRITE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [the_car_is_not_black], READ),
                self.create_quiz(concept, de_auto_is_niet_zwart, [de_auto_is_niet_zwart], DICTATE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [the_car_is_not_black], INTERPRET),
                self.create_quiz(concept, the_car_is_not_black, [de_auto_is_niet_zwart], WRITE),
                self.create_quiz(concept, de_auto_is_zwart, [de_auto_is_niet_zwart], NEGATIVE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [de_auto_is_zwart], AFFIRMATIVE),
                self.create_quiz(concept, de_auto_is_niet_zwart, [de_auto_is_niet_zwart], ORDER),
            },
            create_quizzes(NL_EN, (), concept),
        )


class DiminutiveTest(ToistoTestCase):
    """Unit tests for diminutive forms."""

    def test_diminutive_one_language(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = self.create_concept(
            "car", labels=[{"label": {"root": "de auto", "diminutive": "het autootje"}, "language": NL}]
        )
        auto, autootje = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, auto, [auto], DICTATE),
                self.create_quiz(concept, autootje, [autootje], DICTATE),
                self.create_quiz(concept, auto, [autootje], DIMINUTIVE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_diminutive_two_languages(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": {"root": "de auto", "diminutive": "het autootje"}, "language": NL},
                {"label": {"root": "auto", "diminutive": "pikkuauto"}, "language": FI},
            ],
        )
        de_auto, autootje = concept.labels(NL)
        auto, pikkuauto = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(concept, de_auto, [auto], READ),
                self.create_quiz(concept, de_auto, [de_auto], DICTATE),
                self.create_quiz(concept, de_auto, [auto], INTERPRET),
                self.create_quiz(concept, auto, [de_auto], WRITE),
                self.create_quiz(concept, de_auto, [autootje], DIMINUTIVE),
                self.create_quiz(concept, autootje, [autootje], DICTATE),
                self.create_quiz(concept, autootje, [pikkuauto], READ),
                self.create_quiz(concept, autootje, [pikkuauto], INTERPRET),
                self.create_quiz(concept, pikkuauto, [autootje], WRITE),
            },
            create_quizzes(NL_FI, (), concept),
        )

    def test_diminutive_in_one_language_but_not_the_other(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = self.create_concept(
            "car",
            labels=[
                {"label": "car", "language": EN},
                {"label": {"root": "de auto", "diminutive": "het autootje"}, "language": NL},
            ],
        )
        (car,) = concept.labels(EN)
        auto, autootje = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, auto, [car], READ),
                self.create_quiz(concept, auto, [auto], DICTATE),
                self.create_quiz(concept, auto, [car], INTERPRET),
                self.create_quiz(concept, car, [auto], WRITE),
                self.create_quiz(concept, autootje, [autootje], DICTATE),
                self.create_quiz(concept, autootje, [car], READ),
                self.create_quiz(concept, auto, [autootje], DIMINUTIVE),
                self.create_quiz(concept, autootje, [car], INTERPRET),
                self.create_quiz(concept, car, [autootje], WRITE),
            },
            create_quizzes(NL_EN, (), concept),
        )


class NumberTest(ToistoTestCase):
    """Unit tests for numbers."""

    def test_numbers(self):
        """Test that quizzes can be generated for numbers."""
        concept = self.create_concept(
            "one", labels=[{"label": {"cardinal": "een", "ordinal": "eerste"}, "language": NL}]
        )
        een, eerste = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, een, [een], DICTATE),
                self.create_quiz(concept, eerste, [eerste], DICTATE),
                self.create_quiz(concept, een, [eerste], ORDINAL),
                self.create_quiz(concept, eerste, [een], CARDINAL),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_numbers_and_translations(self):
        """Test that quizzes can be generated for numbers."""
        concept = self.create_concept(
            "one",
            labels=[
                {"label": {"cardinal": "one", "ordinal": "first"}, "language": EN},
                {"label": {"cardinal": "een", "ordinal": "eerste"}, "language": NL},
            ],
        )
        one, first = concept.labels(EN)
        een, eerste = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, een, [one], READ),
                self.create_quiz(concept, een, [een], DICTATE),
                self.create_quiz(concept, een, [one], INTERPRET),
                self.create_quiz(concept, one, [een], WRITE),
                self.create_quiz(concept, eerste, [first], READ),
                self.create_quiz(concept, eerste, [eerste], DICTATE),
                self.create_quiz(concept, eerste, [first], INTERPRET),
                self.create_quiz(concept, first, [eerste], WRITE),
                self.create_quiz(concept, eerste, [een], CARDINAL),
                self.create_quiz(concept, een, [eerste], ORDINAL),
            },
            create_quizzes(NL_EN, (), concept),
        )


class AbbreviationTest(ToistoTestCase):
    """Unit tests for abbreviations."""

    def test_abbreviations(self):
        """Test that quizzes can be generated for abbreviations."""
        concept = self.create_concept(
            "llc", labels=[{"label": {"full form": "naamloze vennootschap", "abbreviation": "NV"}, "language": NL}]
        )
        nv, naamloze_vennootschap = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, naamloze_vennootschap, [naamloze_vennootschap], DICTATE),
                self.create_quiz(concept, nv, [nv], DICTATE),
                self.create_quiz(concept, naamloze_vennootschap, [nv], ABBREVIATION),
                self.create_quiz(concept, nv, [naamloze_vennootschap], FULL_FORM),
            },
            create_quizzes(NL_EN, (), concept),
        )


class QuizNoteTest(ToistoTestCase):
    """Unit tests for the quiz notes."""

    def test_note(self):
        """Test that the quizzes use the notes of the target language."""
        concept = self.create_concept(
            "finnish",
            labels=[
                {"label": "suomi", "language": FI, "note": "In Finnish, the names of languages are not capitalized"},
                {"label": "Fins", "language": NL, "note": "In Dutch, the names of languages are capitalized"},
            ],
        )
        for quiz in create_quizzes(FI_NL, (), concept):
            self.assertEqual("In Finnish, the names of languages are not capitalized", quiz.notes[0])


class ColloquialTest(ToistoTestCase):
    """Unit tests for concepts with colloquial (spoken language) labels."""

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
        kioski, kiska, kioskit, kiskat = concept.labels(FI)
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
            {"antonym": "no"},
            labels=[{"label": "kylla", "language": FI}, {"label": "kyl", "language": FI, "colloquial": True}],
        )
        no = self.create_concept("no", {"antonym": "yes"}, labels=[{"label": "ei", "language": FI}])
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


class MeaningsTest(ToistoTestCase):
    """Test that quizzes have the correct meaning."""

    def test_interpret_with_synonym(self):
        """Test that interpret quizzes show all synonyms as meaning."""
        concept = self.create_concept(
            "yes",
            labels=[
                {"label": "kylla", "language": FI},
                {"label": "joo", "language": FI},
                {"label": "yes", "language": EN},
            ],
        )
        interpret_quizzes = create_quizzes(FI_EN, (INTERPRET,), concept)
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kylla"), Label(FI, "joo")), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)

    def test_interpret_with_colloquial(self):
        """Test that interpret quizzes don't show colloquial labels as meaning."""
        concept = self.create_concept(
            "20",
            labels=[
                {"label": "kaksikymmentä", "language": FI},
                {"label": "kakskyt", "language": FI, "colloquial": True},
                {"label": "twintig", "language": NL},
            ],
        )
        interpret_quizzes = create_quizzes(FI_NL, (INTERPRET,), concept)
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kaksikymmentä"),), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)


class GrammaticalQuizTypesTest(QuizFactoryTestCase):
    """Test the grammatical quiz types generator."""

    def test_adjective_with_degrees_of_comparison(self):
        """Test the grammatical quiz types for an adjective with degrees of comparison."""
        positive, comparative, superlative = self.create_adjective_with_degrees_of_comparison().leaf_concepts(EN)
        for concept in (positive, comparative):
            self.assertEqual(SUPERLATIVE_DEGREE, GrammaticalQuizFactory.grammatical_quiz_type(concept, superlative))
        for concept in (positive, superlative):
            self.assertEqual(COMPARATIVE_DEGREE, GrammaticalQuizFactory.grammatical_quiz_type(concept, comparative))
        for concept in (comparative, superlative):
            self.assertEqual(POSITIVE_DEGREE, GrammaticalQuizFactory.grammatical_quiz_type(concept, positive))

    def test_noun_with_grammatical_number(self):
        """Test the grammatical quiz types for a noun with singular and plural form."""
        singular, plural = self.create_noun_with_grammatical_number().leaf_concepts(FI)
        self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
        self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))

    def test_noun_with_grammatical_gender(self):
        """Test the grammatical quiz types for a noun with grammatical gender."""
        feminine, maasculine = self.create_noun_with_grammatical_gender().leaf_concepts(EN)
        self.assertEqual(MASCULINE, GrammaticalQuizFactory.grammatical_quiz_type(feminine, maasculine))
        self.assertEqual(FEMININE, GrammaticalQuizFactory.grammatical_quiz_type(maasculine, feminine))

    def test_noun_with_grammatical_gender_including_neuter(self):
        """Test the grammatical quiz types for a noun with grammatical gender including neuter."""
        feminine, masculine, neuter = self.create_noun_with_grammatical_gender_including_neuter().leaf_concepts(NL)
        for concept in (feminine, neuter):
            self.assertEqual(MASCULINE, GrammaticalQuizFactory.grammatical_quiz_type(concept, masculine))
        for concept in (feminine, masculine):
            self.assertEqual(NEUTER, GrammaticalQuizFactory.grammatical_quiz_type(concept, neuter))
        for concept in (masculine, neuter):
            self.assertEqual(FEMININE, GrammaticalQuizFactory.grammatical_quiz_type(concept, feminine))

    def test_noun_with_grammatical_number_and_gender(self):
        """Test the grammatical quiz types for a noun with grammatical number and gender."""
        noun = self.create_noun_with_grammatical_number_and_gender()
        singular_feminine, singular_masculine, plural_feminine, plural_masculine = noun.leaf_concepts(EN)
        for feminine, masculine in ((singular_feminine, singular_masculine), (plural_feminine, plural_masculine)):
            self.assertEqual(MASCULINE, GrammaticalQuizFactory.grammatical_quiz_type(feminine, masculine))
            self.assertEqual(FEMININE, GrammaticalQuizFactory.grammatical_quiz_type(masculine, feminine))
        for singular, plural in ((singular_feminine, plural_feminine), (singular_masculine, plural_masculine)):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))

    def test_verb_with_person(self):
        """Test the grammatical quiz types for a verb with grammatical person."""
        verb = self.create_verb_with_person()
        first, second, third = verb.leaf_concepts(EN)
        for concept in (first, second):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(concept, third))
        for concept in (first, third):
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(concept, second))
        for concept in (second, third):
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(concept, first))

    def test_verb_with_tense_and_person(self):
        """Test the grammatical quiz types for a verb with tense and grammatical person."""
        verb = self.create_verb_with_tense_and_person("present tense", "past tense")
        present_singular, present_plural, past_singular, past_plural = verb.leaf_concepts(NL)
        for singular, plural in ((present_singular, present_plural), (past_singular, past_plural)):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))
        for present, past in ((present_singular, past_singular), (present_plural, past_plural)):
            self.assertEqual(PAST_TENSE, GrammaticalQuizFactory.grammatical_quiz_type(present, past))
            self.assertEqual(PRESENT_TENSE, GrammaticalQuizFactory.grammatical_quiz_type(past, present))

    def test_verb_with_infinitive_and_person(self):
        """Test the grammatical quiz types for a verb with infinitive and grammatical person."""
        verb = self.create_verb_with_infinitive_and_person()
        infinitive, singular, plural = verb.leaf_concepts(EN)
        for concept in (infinitive, singular):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(concept, plural))
        for concept in (infinitive, plural):
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(concept, singular))
        for concept in (singular, plural):
            self.assertEqual(INFINITIVE, GrammaticalQuizFactory.grammatical_quiz_type(concept, infinitive))

    def test_verb_with_person_and_number(self):
        """Test the grammatical quiz types for a verb with grammatical person and number."""
        verb = self.create_verb_with_grammatical_number_and_person()
        (
            first_singular,
            second_singular,
            third_singular,
            first_plural,
            second_plural,
            third_plural,
        ) = verb.leaf_concepts(NL)
        for singular, plural in (
            (first_singular, first_plural),
            (second_singular, second_plural),
            (third_singular, third_plural),
        ):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))
        for first_person, second_person in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, second_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, first_person))
        for first_person, third_person in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, third_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, first_person))
        for second_person, third_person in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, third_person))
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, second_person))

    def test_verb_with_infinitive_and_person_and_number(self):
        """Test the grammatical quiz types for a verb with infinitive, grammatical person and number."""
        verb = self.create_verb_with_infinitive_and_number_and_person()
        (
            infinitive,
            first_singular,
            second_singular,
            third_singular,
            first_plural,
            second_plural,
            third_plural,
        ) = verb.leaf_concepts(NL)
        for singular, plural in (
            (first_singular, first_plural),
            (second_singular, second_plural),
            (third_singular, third_plural),
        ):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))
            self.assertIsNone(GrammaticalQuizFactory.grammatical_quiz_type(infinitive, singular))
            self.assertIsNone(GrammaticalQuizFactory.grammatical_quiz_type(infinitive, plural))
        for first_person, second_person in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, second_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, first_person))
        for first_person, third_person in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, third_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, first_person))
        for second_person, third_person in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, third_person))
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, second_person))


class OrderQuizTest(QuizFactoryTestCase):
    """Unit tests for generating order quizzes."""

    def test_generate_order_quiz_for_long_enough_sentences(self):
        """Test that order quizzes are generated for long enough sentences."""
        concept = self.create_concept(
            "breakfast", labels=[{"label": "We eat breakfast in the kitchen.", "language": EN}]
        )
        quizzes = create_quizzes(EN_NL, (ORDER,), concept)
        quiz = first(quizzes)
        self.assertEqual(ORDER, quiz.quiz_type)


class FilterByQuizTypeTest(QuizFactoryTestCase):
    """Unit tests for limiting the quiz types created."""

    def test_filter_quizzes(self):
        """Test that quizzes can be limited to certain quiz types."""
        concept = self.create_concept(
            "english", labels=[{"label": "English", "language": EN}, {"label": "Engels", "language": NL}]
        )
        (english,) = concept.labels(EN)
        (engels,) = concept.labels(NL)
        self.assertSetEqual(
            {
                self.create_quiz(concept, engels, [english], READ),
                self.create_quiz(concept, english, [engels], WRITE),
            },
            create_quizzes(NL_EN, (READ, WRITE), concept),
        )
        self.assertSetEqual(
            {
                self.create_quiz(concept, engels, [engels], DICTATE),
                self.create_quiz(concept, engels, [english], INTERPRET),
            },
            create_quizzes(NL_EN, (DICTATE, INTERPRET), concept),
        )

    def test_filter_grammatical_number(self):
        """Test that quizzes can be filtered for plural and singular quiz types."""
        concept = self.create_noun_with_grammatical_number()
        aamu, aamut = concept.labels(FI)
        self.assertSetEqual(
            {self.create_quiz(concept, aamut, [aamu], SINGULAR)},
            create_quizzes(FI_NL, (SINGULAR,), concept),
        )
        self.assertSetEqual(
            {self.create_quiz(concept, aamu, [aamut], PLURAL)},
            create_quizzes(FI_NL, (PLURAL,), concept),
        )

    def test_filter_grammatical_gender(self):
        """Test that quizzes can be generated for feminine and masculine grammatical genders."""
        concept = self.create_noun_with_grammatical_gender()
        haar_kat, zijn_kat = concept.labels(NL)
        self.assertSetEqual(
            {self.create_quiz(concept, haar_kat, [zijn_kat], MASCULINE)},
            create_quizzes(NL_EN, (MASCULINE,), concept),
        )
        self.assertSetEqual(
            {self.create_quiz(concept, zijn_kat, [haar_kat], FEMININE)},
            create_quizzes(NL_EN, (FEMININE,), concept),
        )
