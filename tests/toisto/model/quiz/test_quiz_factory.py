"""Concept unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept
from toisto.model.language.grammar import Tense
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes, grammatical_quiz_type
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

from ....base import EN_FI, EN_NL, FI_EN, FI_NL, NL_EN, NL_FI, ToistoTestCase


class QuizFactoryTestCase(ToistoTestCase):
    """Base class for quiz factory unit tests."""

    def create_verb_with_person(self) -> Concept:
        """Create a verb with grammatical person."""
        return self.create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", nl="ik eet"),
                "second person": dict(en="you eat", nl="jij eet"),
                "third person": dict(en="she eats", nl="zij eet"),
            },
        )

    def create_verb_with_tense_and_person(self, *tense: Tense) -> Concept:
        """Create a verb with grammatical person nested within tense."""
        concept_dict: dict[str, object] = {}
        if "present tense" in tense:
            concept_dict["present tense"] = {
                "singular": dict(en="I eat", nl="ik eet"),
                "plural": dict(en="we eat", nl="wij eten"),
            }
        if "past tense" in tense:
            concept_dict["past tense"] = {
                "singular": dict(en="I ate", nl="ik at"),
                "plural": dict(en="we ate", nl="wij aten"),
            }
        if "present perfect tense" in tense:
            concept_dict["present perfect tense"] = {
                "singular": dict(en="I have eaten", nl="ik heb gegeten"),
                "plural": dict(en="we have eaten", nl="wij hebben gegeten"),
            }
        if "past perfect tense" in tense:
            concept_dict["past perfect tense"] = {
                "singular": dict(en="I had eaten", nl="ik had gegeten"),
                "plural": dict(en="we had eaten", nl="wij hadden gegeten"),
            }
        return self.create_concept("to eat", concept_dict)

    def create_verb_with_infinitive_and_person(self) -> Concept:
        """Create a verb with infinitive and grammatical person."""
        return self.create_concept(
            "to sleep",
            dict(
                infinitive=dict(en="to sleep", nl="slapen"),
                singular=dict(en="I sleep", nl="ik slaap"),
                plural=dict(en="we sleep", nl="wij slapen"),
            ),
        )

    def create_verb_with_infinitive_and_number_and_person(self) -> Concept:
        """Create a verb with infinitive and grammatical number nested with person."""
        return self.create_concept(
            "to be",
            dict(
                infinitive=dict(fi="olla", nl="zijn"),
                singular={
                    "first person": dict(fi="minä olen", nl="ik ben"),
                    "second person": dict(fi="sinä olet", nl="jij bent"),
                    "third person": dict(fi="hän on", nl="zij is"),
                },
                plural={
                    "first person": dict(fi="me olemme", nl="wij zijn"),
                    "second person": dict(fi="te olette", nl="jullie zijn"),
                    "third person": dict(fi="he ovat", nl="zij zijn"),
                },
            ),
        )

    def create_adjective_with_degrees_of_comparison(self) -> Concept:
        """Create an adjective with degrees of comparison."""
        return self.create_concept(
            "big",
            {
                "positive degree": dict(en="big", nl="groot"),
                "comparative degree": dict(en="bigger", nl="groter"),
                "superlative degree": dict(en="biggest", nl="grootst"),
            },
        )

    def create_noun(self) -> Concept:
        """Create a simple noun."""
        return self.create_concept("mall", dict(fi="kauppakeskus", nl="het winkelcentrum"))

    def create_noun_with_grammatical_number(self) -> Concept:
        """Create a noun with grammatical number."""
        return self.create_concept(
            "morning",
            dict(singular=dict(fi="aamu", nl="de ochtend"), plural=dict(fi="aamut", nl="de ochtenden")),
        )

    def create_noun_with_grammatical_gender(self) -> Concept:
        """Create a noun with grammatical gender."""
        return self.create_concept(
            "cat",
            dict(feminine=dict(en="her cat", nl="haar kat"), masculine=dict(en="his cat", nl="zijn kat")),
        )

    def create_noun_with_grammatical_gender_including_neuter(self) -> Concept:
        """Create a noun with grammatical gender, including neuter."""
        return self.create_concept(
            "bone",
            dict(
                feminine=dict(en="her bone", nl="haar bot"),
                masculine=dict(en="his bone", nl="zijn bot;masculine"),
                neuter=dict(en="its bone", nl="zijn bot;neuter"),
            ),
        )

    def create_noun_with_grammatical_number_and_gender(self) -> Concept:
        """Create a noun with grammatical number and grammatical gender."""
        return self.create_concept(
            "cat",
            dict(
                singular=dict(feminine=dict(en="her cat", nl="haar kat"), masculine=dict(en="his cat", nl="zijn kat")),
                plural=dict(
                    feminine=dict(en="her cats", nl="haar katten"), masculine=dict(en="his cats", nl="zijn katten")
                ),
            ),
        )


class ConceptQuizzesTest(QuizFactoryTestCase):
    """Unit tests for the concept class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from a concept."""
        self.language_pair = NL_EN
        concept = self.create_concept("english", dict(en="English", nl="Engels"))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "Engels", ["English"], READ),
                self.create_quiz(concept, "Engels", ["Engels"], DICTATE),
                self.create_quiz(concept, "Engels", ["English"], INTERPRET),
                self.create_quiz(concept, "English", ["Engels"], WRITE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_only_listening_quizzes_for_one_language(self):
        """Test that only listening quizzes are generated for a concept with one language."""
        concept = self.create_concept("english", dict(nl="Engels"))
        self.assertSetEqual(
            {self.create_quiz(concept, "Engels", ["Engels"], DICTATE, language_pair=NL_EN)},
            create_quizzes(NL_EN, concept),
        )

    def test_answer_only_concept(self):
        """Test that no quizzes are generated for an answer-only concept."""
        concept = self.create_concept("yes, i do like something", {"answer-only": True, EN: "Yes, I do.", FI: "Pidän"})
        self.assertSetEqual(Quizzes(), create_quizzes(EN_FI, concept))

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        self.language_pair = NL_EN
        concept = self.create_concept("couch", dict(nl=["bank"], en=["couch", "bank"]))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "bank", ["couch", "bank"], READ),
                self.create_quiz(concept, "bank", ["bank"], DICTATE),
                self.create_quiz(concept, "bank", ["couch", "bank"], INTERPRET),
                self.create_quiz(concept, "couch", ["bank"], WRITE),
                self.create_quiz(concept, "bank", ["bank"], WRITE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_missing_language(self):
        """Test that no quizzes are generated from a concept if it's missing one of the languages."""
        concept = self.create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertSetEqual(Quizzes(), create_quizzes(FI_EN, concept))

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        self.language_pair = FI_NL
        concept = self.create_noun_with_grammatical_number()
        singular, plural = concept.leaf_concepts(FI)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "aamu", ["de ochtend"], READ),
                self.create_quiz(singular, "aamu", ["aamu"], DICTATE),
                self.create_quiz(singular, "aamu", ["de ochtend"], INTERPRET),
                self.create_quiz(singular, "de ochtend", ["aamu"], WRITE),
                self.create_quiz(plural, "aamut", ["de ochtenden"], READ),
                self.create_quiz(plural, "aamut", ["aamut"], DICTATE),
                self.create_quiz(plural, "aamut", ["de ochtenden"], INTERPRET),
                self.create_quiz(plural, "de ochtenden", ["aamut"], WRITE),
                self.create_quiz(concept, "aamu", ["aamut"], PLURAL),
                self.create_quiz(concept, "aamut", ["aamu"], SINGULAR),
            },
            create_quizzes(FI_NL, concept),
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        self.language_pair = FI_NL
        concept = self.create_concept(
            "ketchup",
            dict(singular=dict(fi="ketsuppi", nl="de ketchup"), plural=dict(fi="ketsupit")),
        )
        singular, plural = concept.leaf_concepts(FI)
        quizzes = create_quizzes(FI_NL, concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "ketsuppi", ["de ketchup"], READ),
                self.create_quiz(singular, "ketsuppi", ["ketsuppi"], DICTATE),
                self.create_quiz(singular, "ketsuppi", ["de ketchup"], INTERPRET),
                self.create_quiz(singular, "de ketchup", ["ketsuppi"], WRITE),
                self.create_quiz(plural, "ketsupit", ["ketsupit"], DICTATE),
                self.create_quiz(concept, "ketsuppi", ["ketsupit"], PLURAL),
                self.create_quiz(concept, "ketsupit", ["ketsuppi"], SINGULAR),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_in_target_language_not_in_source_language(self):
        """Test that quizzes can be generated even if one language has no grammatical number for the concept."""
        self.language_pair = NL_EN
        concept = self.create_noun_invariant_in_english()
        singular, plural = concept.leaf_concepts(NL)
        quizzes = create_quizzes(NL_EN, concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "het vervoersmiddel", ["means of transportation"], INTERPRET),
                self.create_quiz(singular, "het vervoersmiddel", ["het vervoersmiddel"], DICTATE),
                self.create_quiz(singular, "het vervoersmiddel", ["means of transportation"], READ),
                self.create_quiz(singular, "het vervoersmiddel", ["de vervoersmiddelen"], PLURAL),
                self.create_quiz(plural, "de vervoersmiddelen", ["means of transportation"], INTERPRET),
                self.create_quiz(plural, "de vervoersmiddelen", ["de vervoersmiddelen"], DICTATE),
                self.create_quiz(plural, "de vervoersmiddelen", ["means of transportation"], READ),
                self.create_quiz(plural, "de vervoersmiddelen", ["het vervoersmiddel"], SINGULAR),
                self.create_quiz(concept, "means of transportation", ["means of transportation"], WRITE),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_in_source_language_not_in_target_language(self):
        """Test that quizzes can be generated even if one language has no grammatical number for the concept."""
        self.language_pair = EN_NL
        concept = self.create_noun_invariant_in_english()
        quizzes = create_quizzes(EN_NL, concept)
        self.assertSetEqual(
            {
                self.create_quiz(
                    concept,
                    "means of transportation",
                    ["het vervoersmiddel", "de vervoersmiddelen"],
                    INTERPRET,
                ),
                self.create_quiz(
                    concept,
                    "means of transportation",
                    ["het vervoersmiddel", "de vervoersmiddelen"],
                    READ,
                ),
                self.create_quiz(concept, "het vervoersmiddel", ["means of transportation"], WRITE),
                self.create_quiz(concept, "de vervoersmiddelen", ["means of transportation"], WRITE),
                self.create_quiz(concept, "means of transportation", ["means of transportation"], DICTATE),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the target language only."""
        self.language_pair = FI_NL
        concept = self.create_concept("mämmi", dict(singular=dict(fi="mämmi"), plural=dict(fi="mämmit")))
        singular, plural = concept.leaf_concepts(FI)
        quizzes = create_quizzes(FI_NL, concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "mämmi", ["mämmi"], DICTATE),
                self.create_quiz(plural, "mämmit", ["mämmit"], DICTATE),
                self.create_quiz(concept, "mämmi", ["mämmit"], PLURAL),
                self.create_quiz(concept, "mämmit", ["mämmi"], SINGULAR),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", quiz.question_meanings.as_strings)
            self.assertNotIn("", quiz.answer_meanings.as_strings)

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes are generated from a noun concept with labels in the native language."""
        concept = self.create_concept("mämmi", dict(singular=dict(fi="mämmi"), plural=dict(fi="mämmit")))
        self.assertSetEqual(Quizzes(), create_quizzes(EN_FI, concept))

    def test_grammatical_number_with_synonyms(self):
        """Test that in case of synonyms the plural of one synonym isn't the correct answer for the other synonym."""
        self.language_pair = FI_NL
        concept = self.create_concept(
            "mall",
            dict(
                singular=dict(fi=["kauppakeskus", "ostoskeskus"], nl="het winkelcentrum"),
                plural=dict(fi=["kauppakeskukset", "ostoskeskukset"], nl="de winkelcentra"),
            ),
        )
        singular, plural = concept.leaf_concepts(FI)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "kauppakeskus", ["het winkelcentrum"], READ),
                self.create_quiz(singular, "ostoskeskus", ["het winkelcentrum"], READ),
                self.create_quiz(singular, "kauppakeskus", ["kauppakeskus"], DICTATE),
                self.create_quiz(singular, "kauppakeskus", ["het winkelcentrum"], INTERPRET),
                self.create_quiz(singular, "ostoskeskus", ["ostoskeskus"], DICTATE),
                self.create_quiz(singular, "ostoskeskus", ["het winkelcentrum"], INTERPRET),
                self.create_quiz(singular, "het winkelcentrum", ["kauppakeskus", "ostoskeskus"], WRITE),
                self.create_quiz(plural, "kauppakeskukset", ["de winkelcentra"], READ),
                self.create_quiz(plural, "ostoskeskukset", ["de winkelcentra"], READ),
                self.create_quiz(plural, "kauppakeskukset", ["kauppakeskukset"], DICTATE),
                self.create_quiz(plural, "kauppakeskukset", ["de winkelcentra"], INTERPRET),
                self.create_quiz(plural, "ostoskeskukset", ["ostoskeskukset"], DICTATE),
                self.create_quiz(plural, "ostoskeskukset", ["de winkelcentra"], INTERPRET),
                self.create_quiz(plural, "de winkelcentra", ["kauppakeskukset", "ostoskeskukset"], WRITE),
                self.create_quiz(concept, "kauppakeskus", ["kauppakeskukset"], PLURAL),
                self.create_quiz(concept, "ostoskeskus", ["ostoskeskukset"], PLURAL),
                self.create_quiz(concept, "kauppakeskukset", ["kauppakeskus"], SINGULAR),
                self.create_quiz(concept, "ostoskeskukset", ["ostoskeskus"], SINGULAR),
            },
            create_quizzes(FI_NL, concept),
        )

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for feminine and masculine grammatical genders."""
        self.language_pair = NL_EN
        concept = self.create_noun_with_grammatical_gender()
        feminine, masculine = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(feminine, "haar kat", ["her cat"], READ),
                self.create_quiz(feminine, "haar kat", ["haar kat"], DICTATE),
                self.create_quiz(feminine, "haar kat", ["her cat"], INTERPRET),
                self.create_quiz(feminine, "her cat", ["haar kat"], WRITE),
                self.create_quiz(masculine, "zijn kat", ["his cat"], READ),
                self.create_quiz(masculine, "zijn kat", ["zijn kat"], DICTATE),
                self.create_quiz(masculine, "zijn kat", ["his cat"], INTERPRET),
                self.create_quiz(masculine, "his cat", ["zijn kat"], WRITE),
                self.create_quiz(concept, "haar kat", ["zijn kat"], MASCULINE),
                self.create_quiz(concept, "zijn kat", ["haar kat"], FEMININE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different feminine, masculine, and neuter grammatical genders."""
        self.language_pair = NL_EN
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        feminine, masculine, neuter = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(feminine, "haar bot", ["her bone"], READ),
                self.create_quiz(feminine, "haar bot", ["haar bot"], DICTATE),
                self.create_quiz(feminine, "haar bot", ["her bone"], INTERPRET),
                self.create_quiz(feminine, "her bone", ["haar bot"], WRITE),
                self.create_quiz(masculine, "zijn bot", ["his bone"], READ),
                self.create_quiz(masculine, "zijn bot", ["zijn bot"], DICTATE),
                self.create_quiz(masculine, "zijn bot", ["his bone"], INTERPRET),
                self.create_quiz(masculine, "his bone", ["zijn bot"], WRITE),
                self.create_quiz(neuter, "zijn bot", ["its bone"], READ),
                self.create_quiz(neuter, "zijn bot", ["zijn bot"], DICTATE),
                self.create_quiz(neuter, "zijn bot", ["its bone"], INTERPRET),
                self.create_quiz(neuter, "its bone", ["zijn bot"], WRITE),
                self.create_quiz(concept, "haar bot", ["zijn bot"], MASCULINE),
                self.create_quiz(concept, "haar bot", ["zijn bot"], NEUTER),
                self.create_quiz(concept, "zijn bot", ["haar bot"], FEMININE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        self.language_pair = NL_EN
        concept = self.create_noun_with_grammatical_number_and_gender()
        singular, plural = concept.constituents
        singular_feminine, singular_masculine, plural_feminine, plural_masculine = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(singular_feminine, "haar kat", ["her cat"], READ),
                self.create_quiz(singular_feminine, "haar kat", ["haar kat"], DICTATE),
                self.create_quiz(singular_feminine, "haar kat", ["her cat"], INTERPRET),
                self.create_quiz(singular_feminine, "her cat", ["haar kat"], WRITE),
                self.create_quiz(singular_masculine, "zijn kat", ["his cat"], READ),
                self.create_quiz(singular_masculine, "zijn kat", ["zijn kat"], DICTATE),
                self.create_quiz(singular_masculine, "zijn kat", ["his cat"], INTERPRET),
                self.create_quiz(singular_masculine, "his cat", ["zijn kat"], WRITE),
                self.create_quiz(singular, "haar kat", ["zijn kat"], MASCULINE),
                self.create_quiz(singular, "zijn kat", ["haar kat"], FEMININE),
                self.create_quiz(plural_feminine, "haar katten", ["her cats"], READ),
                self.create_quiz(plural_feminine, "haar katten", ["haar katten"], DICTATE),
                self.create_quiz(plural_feminine, "haar katten", ["her cats"], INTERPRET),
                self.create_quiz(plural_feminine, "her cats", ["haar katten"], WRITE),
                self.create_quiz(plural_masculine, "zijn katten", ["his cats"], READ),
                self.create_quiz(plural_masculine, "zijn katten", ["zijn katten"], DICTATE),
                self.create_quiz(plural_masculine, "zijn katten", ["his cats"], INTERPRET),
                self.create_quiz(plural_masculine, "his cats", ["zijn katten"], WRITE),
                self.create_quiz(plural, "haar katten", ["zijn katten"], MASCULINE),
                self.create_quiz(plural, "zijn katten", ["haar katten"], FEMININE),
                self.create_quiz(concept, "haar kat", ["haar katten"], PLURAL),
                self.create_quiz(concept, "haar katten", ["haar kat"], SINGULAR),
                self.create_quiz(concept, "zijn kat", ["zijn katten"], PLURAL),
                self.create_quiz(concept, "zijn katten", ["zijn kat"], SINGULAR),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        self.language_pair = NL_EN
        concept = self.create_adjective_with_degrees_of_comparison()
        positive_degree, comparative_degree, superlative_degree = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(positive_degree, "groot", ["big"], READ),
                self.create_quiz(positive_degree, "groot", ["groot"], DICTATE),
                self.create_quiz(positive_degree, "groot", ["big"], INTERPRET),
                self.create_quiz(positive_degree, "big", ["groot"], WRITE),
                self.create_quiz(comparative_degree, "groter", ["bigger"], READ),
                self.create_quiz(comparative_degree, "groter", ["groter"], DICTATE),
                self.create_quiz(comparative_degree, "groter", ["bigger"], INTERPRET),
                self.create_quiz(comparative_degree, "bigger", ["groter"], WRITE),
                self.create_quiz(superlative_degree, "grootst", ["biggest"], READ),
                self.create_quiz(superlative_degree, "grootst", ["grootst"], DICTATE),
                self.create_quiz(superlative_degree, "grootst", ["biggest"], INTERPRET),
                self.create_quiz(superlative_degree, "biggest", ["grootst"], WRITE),
                self.create_quiz(concept, "groot", ["groter"], COMPARATIVE_DEGREE),
                self.create_quiz(concept, "groot", ["grootst"], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, "groter", ["groot"], POSITIVE_DEGREE),
                self.create_quiz(concept, "groter", ["grootst"], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, "grootst", ["groot"], POSITIVE_DEGREE),
                self.create_quiz(concept, "grootst", ["groter"], COMPARATIVE_DEGREE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        self.language_pair = FI_EN
        concept = self.create_concept(
            "big",
            {
                "positive degree": dict(en="big", fi=["iso", "suuri"]),
                "comparative degree": dict(en="bigger", fi=["isompi", "suurempi"]),
                "superlative degree": dict(en="biggest", fi=["isoin", "suurin"]),
            },
        )
        positive_degree, comparative_degree, superlative_degree = concept.leaf_concepts(FI)
        self.assertSetEqual(
            {
                self.create_quiz(positive_degree, "iso", ["big"], READ),
                self.create_quiz(positive_degree, "suuri", ["big"], READ),
                self.create_quiz(positive_degree, "iso", ["iso"], DICTATE),
                self.create_quiz(positive_degree, "iso", ["big"], INTERPRET),
                self.create_quiz(positive_degree, "suuri", ["suuri"], DICTATE),
                self.create_quiz(positive_degree, "suuri", ["big"], INTERPRET),
                self.create_quiz(positive_degree, "big", ["iso", "suuri"], WRITE),
                self.create_quiz(comparative_degree, "isompi", ["bigger"], READ),
                self.create_quiz(comparative_degree, "suurempi", ["bigger"], READ),
                self.create_quiz(comparative_degree, "isompi", ["isompi"], DICTATE),
                self.create_quiz(comparative_degree, "isompi", ["bigger"], INTERPRET),
                self.create_quiz(comparative_degree, "suurempi", ["suurempi"], DICTATE),
                self.create_quiz(comparative_degree, "suurempi", ["bigger"], INTERPRET),
                self.create_quiz(comparative_degree, "bigger", ["isompi", "suurempi"], WRITE),
                self.create_quiz(superlative_degree, "isoin", ["biggest"], READ),
                self.create_quiz(superlative_degree, "suurin", ["biggest"], READ),
                self.create_quiz(superlative_degree, "isoin", ["isoin"], DICTATE),
                self.create_quiz(superlative_degree, "isoin", ["biggest"], INTERPRET),
                self.create_quiz(superlative_degree, "suurin", ["suurin"], DICTATE),
                self.create_quiz(superlative_degree, "suurin", ["biggest"], INTERPRET),
                self.create_quiz(superlative_degree, "biggest", ["isoin", "suurin"], WRITE),
                self.create_quiz(concept, "iso", ["isompi"], COMPARATIVE_DEGREE),
                self.create_quiz(concept, "suuri", ["suurempi"], COMPARATIVE_DEGREE),
                self.create_quiz(concept, "iso", ["isoin"], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, "suuri", ["suurin"], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, "isompi", ["iso"], POSITIVE_DEGREE),
                self.create_quiz(concept, "suurempi", ["suuri"], POSITIVE_DEGREE),
                self.create_quiz(concept, "isompi", ["isoin"], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, "suurempi", ["suurin"], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, "isoin", ["iso"], POSITIVE_DEGREE),
                self.create_quiz(concept, "suurin", ["suuri"], POSITIVE_DEGREE),
                self.create_quiz(concept, "isoin", ["isompi"], COMPARATIVE_DEGREE),
                self.create_quiz(concept, "suurin", ["suurempi"], COMPARATIVE_DEGREE),
            },
            create_quizzes(FI_EN, concept),
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        self.language_pair = NL_EN
        concept = self.create_verb_with_person()
        first_person, second_person, third_person = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "ik eet", ["I eat"], READ),
                self.create_quiz(first_person, "ik eet", ["ik eet"], DICTATE),
                self.create_quiz(first_person, "ik eet", ["I eat"], INTERPRET),
                self.create_quiz(first_person, "I eat", ["ik eet"], WRITE),
                self.create_quiz(second_person, "jij eet", ["you eat"], READ),
                self.create_quiz(second_person, "jij eet", ["jij eet"], DICTATE),
                self.create_quiz(second_person, "jij eet", ["you eat"], INTERPRET),
                self.create_quiz(second_person, "you eat", ["jij eet"], WRITE),
                self.create_quiz(third_person, "zij eet", ["she eats"], READ),
                self.create_quiz(third_person, "zij eet", ["zij eet"], DICTATE),
                self.create_quiz(third_person, "zij eet", ["she eats"], INTERPRET),
                self.create_quiz(third_person, "she eats", ["zij eet"], WRITE),
                self.create_quiz(concept, "ik eet", ["jij eet"], SECOND_PERSON),
                self.create_quiz(concept, "ik eet", ["zij eet"], THIRD_PERSON),
                self.create_quiz(concept, "jij eet", ["ik eet"], FIRST_PERSON),
                self.create_quiz(concept, "jij eet", ["zij eet"], THIRD_PERSON),
                self.create_quiz(concept, "zij eet", ["ik eet"], FIRST_PERSON),
                self.create_quiz(concept, "zij eet", ["jij eet"], SECOND_PERSON),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", nl="ik eet"),
                "second person": dict(en="you eat", nl="jij eet"),
                "third person": dict(
                    feminine=dict(en="she eats", nl="zij eet"), masculine=dict(en="he eats", nl="hij eet")
                ),
            },
        )
        first_person, second_person, third_person = concept.constituents
        third_person_feminine, third_person_masculine = third_person.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "ik eet", ["I eat"], READ),
                self.create_quiz(first_person, "ik eet", ["ik eet"], DICTATE),
                self.create_quiz(first_person, "ik eet", ["I eat"], INTERPRET),
                self.create_quiz(first_person, "I eat", ["ik eet"], WRITE),
                self.create_quiz(second_person, "jij eet", ["you eat"], READ),
                self.create_quiz(second_person, "jij eet", ["jij eet"], DICTATE),
                self.create_quiz(second_person, "jij eet", ["you eat"], INTERPRET),
                self.create_quiz(second_person, "you eat", ["jij eet"], WRITE),
                self.create_quiz(third_person_feminine, "zij eet", ["she eats"], READ),
                self.create_quiz(third_person_feminine, "zij eet", ["zij eet"], DICTATE),
                self.create_quiz(third_person_feminine, "zij eet", ["she eats"], INTERPRET),
                self.create_quiz(third_person_feminine, "she eats", ["zij eet"], WRITE),
                self.create_quiz(third_person_masculine, "hij eet", ["he eats"], READ),
                self.create_quiz(third_person_masculine, "hij eet", ["hij eet"], DICTATE),
                self.create_quiz(third_person_masculine, "hij eet", ["he eats"], INTERPRET),
                self.create_quiz(third_person_masculine, "he eats", ["hij eet"], WRITE),
                self.create_quiz(third_person, "zij eet", ["hij eet"], MASCULINE),
                self.create_quiz(third_person, "hij eet", ["zij eet"], FEMININE),
                self.create_quiz(concept, "ik eet", ["jij eet"], SECOND_PERSON),
                self.create_quiz(
                    concept, "ik eet", ["zij eet"], GrammaticalQuizType(quiz_types=(THIRD_PERSON, FEMININE))
                ),
                self.create_quiz(
                    concept, "ik eet", ["hij eet"], GrammaticalQuizType(quiz_types=(THIRD_PERSON, MASCULINE))
                ),
                self.create_quiz(concept, "jij eet", ["ik eet"], FIRST_PERSON),
                self.create_quiz(
                    concept, "jij eet", ["zij eet"], GrammaticalQuizType(quiz_types=(THIRD_PERSON, FEMININE))
                ),
                self.create_quiz(
                    concept, "jij eet", ["hij eet"], GrammaticalQuizType(quiz_types=(THIRD_PERSON, MASCULINE))
                ),
                self.create_quiz(concept, "zij eet", ["ik eet"], FIRST_PERSON),
                self.create_quiz(concept, "zij eet", ["jij eet"], SECOND_PERSON),
                self.create_quiz(concept, "hij eet", ["ik eet"], FIRST_PERSON),
                self.create_quiz(concept, "hij eet", ["jij eet"], SECOND_PERSON),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_person_nested_with_grammatical_gender_in_one_language_but_not_the_other(self):
        """Test quizzes for grammatical person nested with grammatical gender in one language but not the other."""
        self.language_pair = FI_EN
        concept = self.create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", fi="minä syön"),
                "second person": dict(en="you eat", fi="sinä syöt"),
                "third person": dict(feminine=dict(en="she eats"), masculine=dict(en="he eats"), fi="hän syö"),
            },
        )
        first_person, second_person, third_person = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "minä syön", ["I eat"], READ),
                self.create_quiz(first_person, "minä syön", ["minä syön"], DICTATE),
                self.create_quiz(first_person, "minä syön", ["I eat"], INTERPRET),
                self.create_quiz(first_person, "I eat", ["minä syön"], WRITE),
                self.create_quiz(second_person, "sinä syöt", ["you eat"], READ),
                self.create_quiz(second_person, "sinä syöt", ["sinä syöt"], DICTATE),
                self.create_quiz(second_person, "sinä syöt", ["you eat"], INTERPRET),
                self.create_quiz(second_person, "you eat", ["sinä syöt"], WRITE),
                self.create_quiz(third_person, "hän syö", ["she eats", "he eats"], READ),
                self.create_quiz(third_person, "hän syö", ["hän syö"], DICTATE),
                self.create_quiz(third_person, "hän syö", ["she eats", "he eats"], INTERPRET),
                self.create_quiz(third_person, "she eats", ["hän syö"], WRITE),
                self.create_quiz(third_person, "he eats", ["hän syö"], WRITE),
                self.create_quiz(concept, "minä syön", ["sinä syöt"], SECOND_PERSON),
                self.create_quiz(concept, "minä syön", ["hän syö"], THIRD_PERSON),
                self.create_quiz(concept, "sinä syöt", ["minä syön"], FIRST_PERSON),
                self.create_quiz(concept, "sinä syöt", ["hän syö"], THIRD_PERSON),
                self.create_quiz(concept, "hän syö", ["minä syön"], FIRST_PERSON),
                self.create_quiz(concept, "hän syö", ["sinä syöt"], SECOND_PERSON),
            },
            create_quizzes(FI_EN, concept),
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        self.language_pair = NL_FI
        concept = self.create_verb_with_grammatical_number_and_person()
        singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "ik heb", ["minulla on"], READ),
                self.create_quiz(first_person_singular, "minulla on", ["ik heb"], WRITE),
                self.create_quiz(first_person_singular, "ik heb", ["ik heb"], DICTATE),
                self.create_quiz(first_person_singular, "ik heb", ["minulla on"], INTERPRET),
                self.create_quiz(second_person_singular, "jij hebt", ["sinulla on"], READ),
                self.create_quiz(second_person_singular, "sinulla on", ["jij hebt"], WRITE),
                self.create_quiz(second_person_singular, "jij hebt", ["jij hebt"], DICTATE),
                self.create_quiz(second_person_singular, "jij hebt", ["sinulla on"], INTERPRET),
                self.create_quiz(third_person_singular, "zij heeft", ["hänellä on"], READ),
                self.create_quiz(third_person_singular, "hänellä on", ["zij heeft"], WRITE),
                self.create_quiz(third_person_singular, "zij heeft", ["zij heeft"], DICTATE),
                self.create_quiz(third_person_singular, "zij heeft", ["hänellä on"], INTERPRET),
                self.create_quiz(singular, "ik heb", ["jij hebt"], SECOND_PERSON),
                self.create_quiz(singular, "ik heb", ["zij heeft"], THIRD_PERSON),
                self.create_quiz(singular, "jij hebt", ["ik heb"], FIRST_PERSON),
                self.create_quiz(singular, "jij hebt", ["zij heeft"], THIRD_PERSON),
                self.create_quiz(singular, "zij heeft", ["ik heb"], FIRST_PERSON),
                self.create_quiz(singular, "zij heeft", ["jij hebt"], SECOND_PERSON),
                self.create_quiz(first_person_plural, "wij hebben", ["meillä on"], READ),
                self.create_quiz(first_person_plural, "meillä on", ["wij hebben"], WRITE),
                self.create_quiz(first_person_plural, "wij hebben", ["wij hebben"], DICTATE),
                self.create_quiz(first_person_plural, "wij hebben", ["meillä on"], INTERPRET),
                self.create_quiz(second_person_plural, "jullie hebben", ["teillä on"], READ),
                self.create_quiz(second_person_plural, "teillä on", ["jullie hebben"], WRITE),
                self.create_quiz(second_person_plural, "jullie hebben", ["jullie hebben"], DICTATE),
                self.create_quiz(second_person_plural, "jullie hebben", ["teillä on"], INTERPRET),
                self.create_quiz(third_person_plural, "zij hebben", ["heillä on"], READ),
                self.create_quiz(third_person_plural, "heillä on", ["zij hebben"], WRITE),
                self.create_quiz(third_person_plural, "zij hebben", ["zij hebben"], DICTATE),
                self.create_quiz(third_person_plural, "zij hebben", ["heillä on"], INTERPRET),
                self.create_quiz(plural, "wij hebben", ["jullie hebben"], SECOND_PERSON),
                self.create_quiz(plural, "wij hebben", ["zij hebben"], THIRD_PERSON),
                self.create_quiz(plural, "jullie hebben", ["wij hebben"], FIRST_PERSON),
                self.create_quiz(plural, "jullie hebben", ["zij hebben"], THIRD_PERSON),
                self.create_quiz(plural, "zij hebben", ["wij hebben"], FIRST_PERSON),
                self.create_quiz(plural, "zij hebben", ["jullie hebben"], SECOND_PERSON),
                self.create_quiz(concept, "ik heb", ["wij hebben"], PLURAL),
                self.create_quiz(concept, "wij hebben", ["ik heb"], SINGULAR),
                self.create_quiz(concept, "jij hebt", ["jullie hebben"], PLURAL),
                self.create_quiz(concept, "jullie hebben", ["jij hebt"], SINGULAR),
                self.create_quiz(concept, "zij heeft", ["zij hebben"], PLURAL),
                self.create_quiz(concept, "zij hebben", ["zij heeft"], SINGULAR),
            },
            create_quizzes(NL_FI, concept),
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "cat",
            dict(
                feminine=dict(singular=dict(en="her cat", nl="haar kat"), plural=dict(en="her cats", nl="haar katten")),
                masculine=dict(
                    singular=dict(en="his cat", nl="zijn kat"), plural=dict(en="his cats", nl="zijn katten")
                ),
            ),
        )
        feminine, masculine = concept.constituents
        feminine_singular, feminine_plural, masculine_singular, masculine_plural = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(feminine_singular, "haar kat", ["her cat"], READ),
                self.create_quiz(feminine_singular, "haar kat", ["haar kat"], DICTATE),
                self.create_quiz(feminine_singular, "haar kat", ["her cat"], INTERPRET),
                self.create_quiz(feminine_singular, "her cat", ["haar kat"], WRITE),
                self.create_quiz(feminine_plural, "haar katten", ["her cats"], READ),
                self.create_quiz(feminine_plural, "haar katten", ["haar katten"], DICTATE),
                self.create_quiz(feminine_plural, "haar katten", ["her cats"], INTERPRET),
                self.create_quiz(feminine_plural, "her cats", ["haar katten"], WRITE),
                self.create_quiz(feminine, "haar kat", ["haar katten"], PLURAL),
                self.create_quiz(feminine, "haar katten", ["haar kat"], SINGULAR),
                self.create_quiz(masculine_singular, "zijn kat", ["his cat"], READ),
                self.create_quiz(masculine_singular, "zijn kat", ["zijn kat"], DICTATE),
                self.create_quiz(masculine_singular, "zijn kat", ["his cat"], INTERPRET),
                self.create_quiz(masculine_singular, "his cat", ["zijn kat"], WRITE),
                self.create_quiz(masculine_plural, "zijn katten", ["his cats"], READ),
                self.create_quiz(masculine_plural, "zijn katten", ["zijn katten"], DICTATE),
                self.create_quiz(masculine_plural, "zijn katten", ["his cats"], INTERPRET),
                self.create_quiz(masculine_plural, "his cats", ["zijn katten"], WRITE),
                self.create_quiz(masculine, "zijn kat", ["zijn katten"], PLURAL),
                self.create_quiz(masculine, "zijn katten", ["zijn kat"], SINGULAR),
                self.create_quiz(concept, "haar kat", ["zijn kat"], MASCULINE),
                self.create_quiz(concept, "zijn kat", ["haar kat"], FEMININE),
                self.create_quiz(concept, "haar katten", ["zijn katten"], MASCULINE),
                self.create_quiz(concept, "zijn katten", ["haar katten"], FEMININE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        self.language_pair = FI_EN
        concept = self.create_concept(
            "to be",
            dict(
                feminine=dict(en="she is|she's", fi="hän on"),
                masculine=dict(en="he is|he's", fi="hän on"),
            ),
        )
        feminine, masculine = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(feminine, "hän on", ["she is|she's"], READ),
                self.create_quiz(feminine, "hän on", ["hän on"], DICTATE),
                self.create_quiz(feminine, "hän on", ["she is|she's"], INTERPRET),
                self.create_quiz(feminine, "she is|she's", ["hän on"], WRITE),
                self.create_quiz(masculine, "hän on", ["he is|he's"], READ),
                self.create_quiz(masculine, "he is|he's", ["hän on"], WRITE),
            },
            create_quizzes(FI_EN, concept),
        )

    def test_infinitive_verb_form(self):
        """Test the infinitive verb form."""
        self.language_pair = NL_EN
        concept = self.create_verb_with_infinitive_and_person()
        infinitive, singular, plural = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(infinitive, "slapen", ["to sleep"], READ),
                self.create_quiz(infinitive, "slapen", ["slapen"], DICTATE),
                self.create_quiz(infinitive, "slapen", ["to sleep"], INTERPRET),
                self.create_quiz(infinitive, "to sleep", ["slapen"], WRITE),
                self.create_quiz(singular, "ik slaap", ["I sleep"], READ),
                self.create_quiz(singular, "ik slaap", ["ik slaap"], DICTATE),
                self.create_quiz(singular, "ik slaap", ["I sleep"], INTERPRET),
                self.create_quiz(singular, "I sleep", ["ik slaap"], WRITE),
                self.create_quiz(plural, "wij slapen", ["we sleep"], READ),
                self.create_quiz(plural, "wij slapen", ["wij slapen"], DICTATE),
                self.create_quiz(plural, "wij slapen", ["we sleep"], INTERPRET),
                self.create_quiz(plural, "we sleep", ["wij slapen"], WRITE),
                self.create_quiz(concept, "wij slapen", ["slapen"], INFINITIVE),
                self.create_quiz(concept, "ik slaap", ["slapen"], INFINITIVE),
                self.create_quiz(concept, "slapen", ["wij slapen"], PLURAL),
                self.create_quiz(concept, "ik slaap", ["wij slapen"], PLURAL),
                self.create_quiz(concept, "slapen", ["ik slaap"], SINGULAR),
                self.create_quiz(concept, "wij slapen", ["ik slaap"], SINGULAR),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_number_nested_with_grammatical_person_and_infinitive(self):
        """Test generating quizzes for grammatical number, including infinitive, nested with grammatical person."""
        self.language_pair = NL_FI
        concept = self.create_verb_with_infinitive_and_number_and_person()
        infinitive, singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "ik ben", ["minä olen"], READ),
                self.create_quiz(first_person_singular, "ik ben", ["ik ben"], DICTATE),
                self.create_quiz(first_person_singular, "ik ben", ["minä olen"], INTERPRET),
                self.create_quiz(first_person_singular, "minä olen", ["ik ben"], WRITE),
                self.create_quiz(concept, "ik ben", ["zijn"], INFINITIVE),
                self.create_quiz(second_person_singular, "jij bent", ["sinä olet"], READ),
                self.create_quiz(second_person_singular, "jij bent", ["jij bent"], DICTATE),
                self.create_quiz(second_person_singular, "jij bent", ["sinä olet"], INTERPRET),
                self.create_quiz(second_person_singular, "sinä olet", ["jij bent"], WRITE),
                self.create_quiz(concept, "jij bent", ["zijn"], INFINITIVE),
                self.create_quiz(third_person_singular, "zij is", ["hän on"], READ),
                self.create_quiz(third_person_singular, "zij is", ["zij is"], DICTATE),
                self.create_quiz(third_person_singular, "zij is", ["hän on"], INTERPRET),
                self.create_quiz(third_person_singular, "hän on", ["zij is"], WRITE),
                self.create_quiz(concept, "zij is", ["zijn"], INFINITIVE),
                self.create_quiz(singular, "ik ben", ["jij bent"], SECOND_PERSON),
                self.create_quiz(singular, "ik ben", ["zij is"], THIRD_PERSON),
                self.create_quiz(singular, "jij bent", ["ik ben"], FIRST_PERSON),
                self.create_quiz(singular, "jij bent", ["zij is"], THIRD_PERSON),
                self.create_quiz(singular, "zij is", ["ik ben"], FIRST_PERSON),
                self.create_quiz(singular, "zij is", ["jij bent"], SECOND_PERSON),
                self.create_quiz(first_person_plural, "wij zijn", ["me olemme"], READ),
                self.create_quiz(first_person_plural, "wij zijn", ["wij zijn"], DICTATE),
                self.create_quiz(first_person_plural, "wij zijn", ["me olemme"], INTERPRET),
                self.create_quiz(first_person_plural, "me olemme", ["wij zijn"], WRITE),
                self.create_quiz(concept, "wij zijn", ["zijn"], INFINITIVE),
                self.create_quiz(second_person_plural, "jullie zijn", ["te olette"], READ),
                self.create_quiz(second_person_plural, "jullie zijn", ["jullie zijn"], DICTATE),
                self.create_quiz(second_person_plural, "jullie zijn", ["te olette"], INTERPRET),
                self.create_quiz(second_person_plural, "te olette", ["jullie zijn"], WRITE),
                self.create_quiz(concept, "jullie zijn", ["zijn"], INFINITIVE),
                self.create_quiz(third_person_plural, "zij zijn", ["he ovat"], READ),
                self.create_quiz(third_person_plural, "zij zijn", ["zij zijn"], DICTATE),
                self.create_quiz(third_person_plural, "zij zijn", ["he ovat"], INTERPRET),
                self.create_quiz(third_person_plural, "he ovat", ["zij zijn"], WRITE),
                self.create_quiz(concept, "zij zijn", ["zijn"], INFINITIVE),
                self.create_quiz(plural, "wij zijn", ["jullie zijn"], SECOND_PERSON),
                self.create_quiz(plural, "wij zijn", ["zij zijn"], THIRD_PERSON),
                self.create_quiz(plural, "jullie zijn", ["wij zijn"], FIRST_PERSON),
                self.create_quiz(plural, "jullie zijn", ["zij zijn"], THIRD_PERSON),
                self.create_quiz(plural, "zij zijn", ["wij zijn"], FIRST_PERSON),
                self.create_quiz(plural, "zij zijn", ["jullie zijn"], SECOND_PERSON),
                self.create_quiz(concept, "ik ben", ["wij zijn"], PLURAL),
                self.create_quiz(concept, "wij zijn", ["ik ben"], SINGULAR),
                self.create_quiz(concept, "jij bent", ["jullie zijn"], PLURAL),
                self.create_quiz(concept, "jullie zijn", ["jij bent"], SINGULAR),
                self.create_quiz(concept, "zij is", ["zij zijn"], PLURAL),
                self.create_quiz(concept, "zij zijn", ["zij is"], SINGULAR),
                self.create_quiz(infinitive, "zijn", ["olla"], READ),
                self.create_quiz(infinitive, "zijn", ["zijn"], DICTATE),
                self.create_quiz(infinitive, "zijn", ["olla"], INTERPRET),
                self.create_quiz(infinitive, "olla", ["zijn"], WRITE),
            },
            create_quizzes(NL_FI, concept),
        )

    def test_tense_nested_with_grammatical_number_nested_and_grammatical_person(self):
        """Test generating quizzes for tense, grammatical number, and grammatical person."""
        self.language_pair = NL_FI
        concept = self.create_concept(
            "to be",
            {
                "past tense": dict(
                    singular={
                        "first person": dict(fi="minä olin", nl="ik was"),
                        "second person": dict(fi="sinä olit", nl="jij was"),
                        "third person": dict(fi="hän oli", nl="zij was"),
                    },
                    plural={
                        "first person": dict(fi="me olimme", nl="wij waren"),
                        "second person": dict(fi="te olitte", nl="jullie waren"),
                        "third person": dict(fi="he olivat", nl="zij waren"),
                    },
                ),
                "present tense": dict(
                    singular={
                        "first person": dict(fi="minä olen", nl="ik ben"),
                        "second person": dict(fi="sinä olet", nl="jij bent"),
                        "third person": dict(fi="hän on", nl="zij is"),
                    },
                    plural={
                        "first person": dict(fi="me olemme", nl="wij zijn"),
                        "second person": dict(fi="te olette", nl="jullie zijn"),
                        "third person": dict(fi="he ovat", nl="zij zijn"),
                    },
                ),
            },
        )
        past, present = concept.constituents
        singular_past, plural_past = past.constituents
        first_singular_past, second_singular_past, third_singular_past = singular_past.constituents
        first_plural_past, second_plural_past, third_plural_past = plural_past.constituents
        singular_present, plural_present = present.constituents
        first_singular_present, second_singular_present, third_singular_present = singular_present.constituents
        first_plural_present, second_plural_present, third_plural_present = plural_present.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_singular_present, "ik ben", ["minä olen"], READ),
                self.create_quiz(first_singular_present, "ik ben", ["ik ben"], DICTATE),
                self.create_quiz(first_singular_present, "ik ben", ["minä olen"], INTERPRET),
                self.create_quiz(first_singular_present, "minä olen", ["ik ben"], WRITE),
                self.create_quiz(second_singular_present, "jij bent", ["sinä olet"], READ),
                self.create_quiz(second_singular_present, "jij bent", ["jij bent"], DICTATE),
                self.create_quiz(second_singular_present, "jij bent", ["sinä olet"], INTERPRET),
                self.create_quiz(second_singular_present, "sinä olet", ["jij bent"], WRITE),
                self.create_quiz(third_singular_present, "zij is", ["hän on"], READ),
                self.create_quiz(third_singular_present, "zij is", ["zij is"], DICTATE),
                self.create_quiz(third_singular_present, "zij is", ["hän on"], INTERPRET),
                self.create_quiz(third_singular_present, "hän on", ["zij is"], WRITE),
                self.create_quiz(singular_present, "ik ben", ["jij bent"], SECOND_PERSON),
                self.create_quiz(singular_present, "ik ben", ["zij is"], THIRD_PERSON),
                self.create_quiz(singular_present, "jij bent", ["ik ben"], FIRST_PERSON),
                self.create_quiz(singular_present, "jij bent", ["zij is"], THIRD_PERSON),
                self.create_quiz(singular_present, "zij is", ["ik ben"], FIRST_PERSON),
                self.create_quiz(singular_present, "zij is", ["jij bent"], SECOND_PERSON),
                self.create_quiz(first_plural_present, "wij zijn", ["me olemme"], READ),
                self.create_quiz(first_plural_present, "wij zijn", ["wij zijn"], DICTATE),
                self.create_quiz(first_plural_present, "wij zijn", ["me olemme"], INTERPRET),
                self.create_quiz(first_plural_present, "me olemme", ["wij zijn"], WRITE),
                self.create_quiz(second_plural_present, "jullie zijn", ["te olette"], READ),
                self.create_quiz(second_plural_present, "jullie zijn", ["jullie zijn"], DICTATE),
                self.create_quiz(second_plural_present, "jullie zijn", ["te olette"], INTERPRET),
                self.create_quiz(second_plural_present, "te olette", ["jullie zijn"], WRITE),
                self.create_quiz(third_plural_present, "zij zijn", ["he ovat"], READ),
                self.create_quiz(third_plural_present, "zij zijn", ["zij zijn"], DICTATE),
                self.create_quiz(third_plural_present, "zij zijn", ["he ovat"], INTERPRET),
                self.create_quiz(third_plural_present, "he ovat", ["zij zijn"], WRITE),
                self.create_quiz(plural_present, "wij zijn", ["jullie zijn"], SECOND_PERSON),
                self.create_quiz(plural_present, "wij zijn", ["zij zijn"], THIRD_PERSON),
                self.create_quiz(plural_present, "jullie zijn", ["wij zijn"], FIRST_PERSON),
                self.create_quiz(plural_present, "jullie zijn", ["zij zijn"], THIRD_PERSON),
                self.create_quiz(plural_present, "zij zijn", ["wij zijn"], FIRST_PERSON),
                self.create_quiz(plural_present, "zij zijn", ["jullie zijn"], SECOND_PERSON),
                self.create_quiz(present, "ik ben", ["wij zijn"], PLURAL),
                self.create_quiz(present, "jij bent", ["jullie zijn"], PLURAL),
                self.create_quiz(present, "zij is", ["zij zijn"], PLURAL),
                self.create_quiz(present, "wij zijn", ["ik ben"], SINGULAR),
                self.create_quiz(present, "jullie zijn", ["jij bent"], SINGULAR),
                self.create_quiz(present, "zij zijn", ["zij is"], SINGULAR),
                self.create_quiz(first_singular_past, "ik was", ["minä olin"], READ),
                self.create_quiz(first_singular_past, "ik was", ["ik was"], DICTATE),
                self.create_quiz(first_singular_past, "ik was", ["minä olin"], INTERPRET),
                self.create_quiz(first_singular_past, "minä olin", ["ik was"], WRITE),
                self.create_quiz(second_singular_past, "jij was", ["sinä olit"], READ),
                self.create_quiz(second_singular_past, "jij was", ["jij was"], DICTATE),
                self.create_quiz(second_singular_past, "jij was", ["sinä olit"], INTERPRET),
                self.create_quiz(second_singular_past, "sinä olit", ["jij was"], WRITE),
                self.create_quiz(third_singular_past, "zij was", ["hän oli"], READ),
                self.create_quiz(third_singular_past, "zij was", ["zij was"], DICTATE),
                self.create_quiz(third_singular_past, "zij was", ["hän oli"], INTERPRET),
                self.create_quiz(third_singular_past, "hän oli", ["zij was"], WRITE),
                self.create_quiz(singular_past, "ik was", ["jij was"], SECOND_PERSON),
                self.create_quiz(singular_past, "ik was", ["zij was"], THIRD_PERSON),
                self.create_quiz(singular_past, "jij was", ["ik was"], FIRST_PERSON),
                self.create_quiz(singular_past, "jij was", ["zij was"], THIRD_PERSON),
                self.create_quiz(singular_past, "zij was", ["ik was"], FIRST_PERSON),
                self.create_quiz(singular_past, "zij was", ["jij was"], SECOND_PERSON),
                self.create_quiz(first_plural_past, "wij waren", ["me olimme"], READ),
                self.create_quiz(first_plural_past, "wij waren", ["wij waren"], DICTATE),
                self.create_quiz(first_plural_past, "wij waren", ["me olimme"], INTERPRET),
                self.create_quiz(first_plural_past, "me olimme", ["wij waren"], WRITE),
                self.create_quiz(second_plural_past, "jullie waren", ["te olitte"], READ),
                self.create_quiz(second_plural_past, "jullie waren", ["jullie waren"], DICTATE),
                self.create_quiz(second_plural_past, "jullie waren", ["te olitte"], INTERPRET),
                self.create_quiz(second_plural_past, "te olitte", ["jullie waren"], WRITE),
                self.create_quiz(third_plural_past, "zij waren", ["he olivat"], READ),
                self.create_quiz(third_plural_past, "zij waren", ["zij waren"], DICTATE),
                self.create_quiz(third_plural_past, "zij waren", ["he olivat"], INTERPRET),
                self.create_quiz(third_plural_past, "he olivat", ["zij waren"], WRITE),
                self.create_quiz(plural_past, "wij waren", ["jullie waren"], SECOND_PERSON),
                self.create_quiz(plural_past, "wij waren", ["zij waren"], THIRD_PERSON),
                self.create_quiz(plural_past, "jullie waren", ["wij waren"], FIRST_PERSON),
                self.create_quiz(plural_past, "jullie waren", ["zij waren"], THIRD_PERSON),
                self.create_quiz(plural_past, "zij waren", ["wij waren"], FIRST_PERSON),
                self.create_quiz(plural_past, "zij waren", ["jullie waren"], SECOND_PERSON),
                self.create_quiz(past, "ik was", ["wij waren"], PLURAL),
                self.create_quiz(past, "jij was", ["jullie waren"], PLURAL),
                self.create_quiz(past, "zij was", ["zij waren"], PLURAL),
                self.create_quiz(past, "wij waren", ["ik was"], SINGULAR),
                self.create_quiz(past, "jullie waren", ["jij was"], SINGULAR),
                self.create_quiz(past, "zij waren", ["zij was"], SINGULAR),
                self.create_quiz(concept, "ik ben", ["ik was"], PAST_TENSE),
                self.create_quiz(concept, "jij bent", ["jij was"], PAST_TENSE),
                self.create_quiz(concept, "zij is", ["zij was"], PAST_TENSE),
                self.create_quiz(concept, "wij zijn", ["wij waren"], PAST_TENSE),
                self.create_quiz(concept, "jullie zijn", ["jullie waren"], PAST_TENSE),
                self.create_quiz(concept, "zij zijn", ["zij waren"], PAST_TENSE),
                self.create_quiz(concept, "ik was", ["ik ben"], PRESENT_TENSE),
                self.create_quiz(concept, "jij was", ["jij bent"], PRESENT_TENSE),
                self.create_quiz(concept, "zij was", ["zij is"], PRESENT_TENSE),
                self.create_quiz(concept, "wij waren", ["wij zijn"], PRESENT_TENSE),
                self.create_quiz(concept, "jullie waren", ["jullie zijn"], PRESENT_TENSE),
                self.create_quiz(concept, "zij waren", ["zij zijn"], PRESENT_TENSE),
            },
            create_quizzes(NL_FI, concept),
        )


class TenseQuizzesTest(QuizFactoryTestCase):
    """Unit tests for concepts with tenses."""

    def test_present_and_past_tense_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for present and past tense nested with grammatical person."""
        self.language_pair = NL_EN
        concept = self.create_verb_with_tense_and_person("present tense", "past tense")
        present, past = concept.constituents
        present_singular, present_plural, past_singular, past_plural = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(present_singular, "ik eet", ["I eat"], READ),
                self.create_quiz(present_singular, "ik eet", ["ik eet"], DICTATE),
                self.create_quiz(present_singular, "ik eet", ["I eat"], INTERPRET),
                self.create_quiz(present_singular, "I eat", ["ik eet"], WRITE),
                self.create_quiz(present_plural, "wij eten", ["we eat"], READ),
                self.create_quiz(present_plural, "wij eten", ["wij eten"], DICTATE),
                self.create_quiz(present_plural, "wij eten", ["we eat"], INTERPRET),
                self.create_quiz(present_plural, "we eat", ["wij eten"], WRITE),
                self.create_quiz(present, "ik eet", ["wij eten"], PLURAL),
                self.create_quiz(present, "wij eten", ["ik eet"], SINGULAR),
                self.create_quiz(past_singular, "ik at", ["I ate"], READ),
                self.create_quiz(past_singular, "ik at", ["ik at"], DICTATE),
                self.create_quiz(past_singular, "ik at", ["I ate"], INTERPRET),
                self.create_quiz(past_singular, "I ate", ["ik at"], WRITE),
                self.create_quiz(past_plural, "wij aten", ["we ate"], READ),
                self.create_quiz(past_plural, "wij aten", ["wij aten"], DICTATE),
                self.create_quiz(past_plural, "wij aten", ["we ate"], INTERPRET),
                self.create_quiz(past_plural, "we ate", ["wij aten"], WRITE),
                self.create_quiz(past, "ik at", ["wij aten"], PLURAL),
                self.create_quiz(past, "wij aten", ["ik at"], SINGULAR),
                self.create_quiz(concept, "ik eet", ["ik at"], PAST_TENSE),
                self.create_quiz(concept, "wij eten", ["wij aten"], PAST_TENSE),
                self.create_quiz(concept, "ik at", ["ik eet"], PRESENT_TENSE),
                self.create_quiz(concept, "wij aten", ["wij eten"], PRESENT_TENSE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_all_tenses_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for all tenses nested with grammatical person."""
        self.language_pair = NL_EN
        concept = self.create_verb_with_tense_and_person(
            "present tense", "past tense", "present perfect tense", "past perfect tense"
        )
        present, past, perfect, past_perfect = concept.constituents
        (
            present_singular,
            present_plural,
            past_singular,
            past_plural,
            perfect_singular,
            perfect_plural,
            past_perfect_singular,
            past_perfect_plural,
        ) = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(present_singular, "ik eet", ["I eat"], READ),
                self.create_quiz(present_singular, "ik eet", ["ik eet"], DICTATE),
                self.create_quiz(present_singular, "ik eet", ["I eat"], INTERPRET),
                self.create_quiz(present_singular, "I eat", ["ik eet"], WRITE),
                self.create_quiz(present_plural, "wij eten", ["we eat"], READ),
                self.create_quiz(present_plural, "wij eten", ["wij eten"], DICTATE),
                self.create_quiz(present_plural, "wij eten", ["we eat"], INTERPRET),
                self.create_quiz(present_plural, "we eat", ["wij eten"], WRITE),
                self.create_quiz(present, "ik eet", ["wij eten"], PLURAL),
                self.create_quiz(present, "wij eten", ["ik eet"], SINGULAR),
                self.create_quiz(past_singular, "ik at", ["I ate"], READ),
                self.create_quiz(past_singular, "ik at", ["ik at"], DICTATE),
                self.create_quiz(past_singular, "ik at", ["I ate"], INTERPRET),
                self.create_quiz(past_singular, "I ate", ["ik at"], WRITE),
                self.create_quiz(past_plural, "wij aten", ["we ate"], READ),
                self.create_quiz(past_plural, "wij aten", ["wij aten"], DICTATE),
                self.create_quiz(past_plural, "wij aten", ["we ate"], INTERPRET),
                self.create_quiz(past_plural, "we ate", ["wij aten"], WRITE),
                self.create_quiz(past, "ik at", ["wij aten"], PLURAL),
                self.create_quiz(past, "wij aten", ["ik at"], SINGULAR),
                self.create_quiz(perfect_singular, "ik heb gegeten", ["I have eaten"], READ),
                self.create_quiz(perfect_singular, "ik heb gegeten", ["ik heb gegeten"], DICTATE),
                self.create_quiz(perfect_singular, "ik heb gegeten", ["I have eaten"], INTERPRET),
                self.create_quiz(perfect_singular, "I have eaten", ["ik heb gegeten"], WRITE),
                self.create_quiz(perfect_plural, "wij hebben gegeten", ["we have eaten"], READ),
                self.create_quiz(perfect_plural, "wij hebben gegeten", ["wij hebben gegeten"], DICTATE),
                self.create_quiz(perfect_plural, "wij hebben gegeten", ["we have eaten"], INTERPRET),
                self.create_quiz(perfect_plural, "we have eaten", ["wij hebben gegeten"], WRITE),
                self.create_quiz(perfect, "ik heb gegeten", ["wij hebben gegeten"], PLURAL),
                self.create_quiz(perfect, "wij hebben gegeten", ["ik heb gegeten"], SINGULAR),
                self.create_quiz(past_perfect_singular, "ik had gegeten", ["I had eaten"], READ),
                self.create_quiz(past_perfect_singular, "ik had gegeten", ["ik had gegeten"], DICTATE),
                self.create_quiz(past_perfect_singular, "ik had gegeten", ["I had eaten"], INTERPRET),
                self.create_quiz(past_perfect_singular, "I had eaten", ["ik had gegeten"], WRITE),
                self.create_quiz(past_perfect_plural, "wij hadden gegeten", ["we had eaten"], READ),
                self.create_quiz(past_perfect_plural, "wij hadden gegeten", ["wij hadden gegeten"], DICTATE),
                self.create_quiz(past_perfect_plural, "wij hadden gegeten", ["we had eaten"], INTERPRET),
                self.create_quiz(past_perfect_plural, "we had eaten", ["wij hadden gegeten"], WRITE),
                self.create_quiz(past_perfect, "ik had gegeten", ["wij hadden gegeten"], PLURAL),
                self.create_quiz(past_perfect, "wij hadden gegeten", ["ik had gegeten"], SINGULAR),
                self.create_quiz(concept, "ik eet", ["ik at"], PAST_TENSE),
                self.create_quiz(concept, "ik eet", ["ik heb gegeten"], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, "ik eet", ["ik had gegeten"], PAST_PERFECT_TENSE),
                self.create_quiz(concept, "wij eten", ["wij aten"], PAST_TENSE),
                self.create_quiz(concept, "wij eten", ["wij hebben gegeten"], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, "wij eten", ["wij hadden gegeten"], PAST_PERFECT_TENSE),
                self.create_quiz(concept, "ik at", ["ik eet"], PRESENT_TENSE),
                self.create_quiz(concept, "ik at", ["ik heb gegeten"], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, "ik at", ["ik had gegeten"], PAST_PERFECT_TENSE),
                self.create_quiz(concept, "wij aten", ["wij eten"], PRESENT_TENSE),
                self.create_quiz(concept, "wij aten", ["wij hebben gegeten"], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, "wij aten", ["wij hadden gegeten"], PAST_PERFECT_TENSE),
                self.create_quiz(concept, "ik heb gegeten", ["ik eet"], PRESENT_TENSE),
                self.create_quiz(concept, "ik heb gegeten", ["ik had gegeten"], PAST_PERFECT_TENSE),
                self.create_quiz(concept, "ik heb gegeten", ["ik at"], PAST_TENSE),
                self.create_quiz(concept, "wij hebben gegeten", ["wij eten"], PRESENT_TENSE),
                self.create_quiz(concept, "wij hebben gegeten", ["wij aten"], PAST_TENSE),
                self.create_quiz(concept, "wij hebben gegeten", ["wij hadden gegeten"], PAST_PERFECT_TENSE),
                self.create_quiz(concept, "ik had gegeten", ["ik eet"], PRESENT_TENSE),
                self.create_quiz(concept, "ik had gegeten", ["ik at"], PAST_TENSE),
                self.create_quiz(concept, "ik had gegeten", ["ik heb gegeten"], PRESENT_PERFECT_TENSE),
                self.create_quiz(concept, "wij hadden gegeten", ["wij eten"], PRESENT_TENSE),
                self.create_quiz(concept, "wij hadden gegeten", ["wij aten"], PAST_TENSE),
                self.create_quiz(concept, "wij hadden gegeten", ["wij hebben gegeten"], PRESENT_PERFECT_TENSE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_tense_nested_with_grammatical_person_and_infinitive(self):
        """Test that quizzes can be generated for tense nested with grammatical person and infinitive."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "to eat",
            {
                "infinitive": dict(en="to eat", nl="eten"),
                "present tense": dict(singular=dict(en="I eat", nl="ik eet"), plural=dict(en="we eat", nl="wij eten")),
                "past tense": dict(singular=dict(en="I ate", nl="ik at"), plural=dict(en="we ate", nl="wij aten")),
            },
        )
        infinitive, present, past = concept.constituents
        present_singular, present_plural = present.constituents
        past_singular, past_plural = past.constituents
        self.assertSetEqual(
            {
                self.create_quiz(present_singular, "ik eet", ["I eat"], READ),
                self.create_quiz(present_singular, "ik eet", ["ik eet"], DICTATE),
                self.create_quiz(present_singular, "ik eet", ["I eat"], INTERPRET),
                self.create_quiz(present_singular, "I eat", ["ik eet"], WRITE),
                self.create_quiz(present_plural, "wij eten", ["we eat"], READ),
                self.create_quiz(present_plural, "wij eten", ["wij eten"], DICTATE),
                self.create_quiz(present_plural, "wij eten", ["we eat"], INTERPRET),
                self.create_quiz(present_plural, "we eat", ["wij eten"], WRITE),
                self.create_quiz(present, "ik eet", ["wij eten"], PLURAL),
                self.create_quiz(present, "wij eten", ["ik eet"], SINGULAR),
                self.create_quiz(past_singular, "ik at", ["I ate"], READ),
                self.create_quiz(past_singular, "ik at", ["ik at"], DICTATE),
                self.create_quiz(past_singular, "ik at", ["I ate"], INTERPRET),
                self.create_quiz(past_singular, "I ate", ["ik at"], WRITE),
                self.create_quiz(past_plural, "wij aten", ["we ate"], READ),
                self.create_quiz(past_plural, "wij aten", ["wij aten"], DICTATE),
                self.create_quiz(past_plural, "wij aten", ["we ate"], INTERPRET),
                self.create_quiz(past_plural, "we ate", ["wij aten"], WRITE),
                self.create_quiz(past, "ik at", ["wij aten"], PLURAL),
                self.create_quiz(past, "wij aten", ["ik at"], SINGULAR),
                self.create_quiz(concept, "ik eet", ["ik at"], PAST_TENSE),
                self.create_quiz(concept, "wij eten", ["wij aten"], PAST_TENSE),
                self.create_quiz(concept, "ik at", ["ik eet"], PRESENT_TENSE),
                self.create_quiz(concept, "wij aten", ["wij eten"], PRESENT_TENSE),
                self.create_quiz(infinitive, "eten", ["to eat"], READ),
                self.create_quiz(infinitive, "eten", ["eten"], DICTATE),
                self.create_quiz(infinitive, "eten", ["to eat"], INTERPRET),
                self.create_quiz(infinitive, "to eat", ["eten"], WRITE),
                self.create_quiz(concept, "ik eet", ["eten"], INFINITIVE),
                self.create_quiz(concept, "wij eten", ["eten"], INFINITIVE),
                self.create_quiz(concept, "ik at", ["eten"], INFINITIVE),
                self.create_quiz(concept, "wij aten", ["eten"], INFINITIVE),
            },
            create_quizzes(NL_EN, concept),
        )


class GrammaticalMoodTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical moods."""

    def test_declarative_and_interrogative_moods(self):
        """Test that quizzes can be generated for the declarative and interrogative moods."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "car",
            {
                "declarative": dict(en="The car is black.", nl="De auto is zwart."),
                "interrogative": dict(en="Is the car black?", nl="Is de auto zwart?"),
            },
        )
        declarative, interrogative = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(declarative, "De auto is zwart.", ["The car is black."], READ),
                self.create_quiz(declarative, "De auto is zwart.", ["De auto is zwart."], DICTATE),
                self.create_quiz(declarative, "De auto is zwart.", ["The car is black."], INTERPRET),
                self.create_quiz(declarative, "The car is black.", ["De auto is zwart."], WRITE),
                self.create_quiz(interrogative, "Is de auto zwart?", ["Is the car black?"], READ),
                self.create_quiz(interrogative, "Is de auto zwart?", ["Is de auto zwart?"], DICTATE),
                self.create_quiz(interrogative, "Is de auto zwart?", ["Is the car black?"], INTERPRET),
                self.create_quiz(interrogative, "Is the car black?", ["Is de auto zwart?"], WRITE),
                self.create_quiz(concept, "De auto is zwart.", ["Is de auto zwart"], INTERROGATIVE),
                self.create_quiz(concept, "Is de auto zwart?", ["De auto is zwart."], DECLARATIVE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_declarative_and_imperative_moods(self):
        """Test that quizzes can be generated for the declarative and imperative moods."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "you run",
            {
                "declarative": dict(en="You run.", nl="Jij rent."),
                "imperative": dict(en="Run!", nl="Ren!"),
            },
        )
        declarative, imperative = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(declarative, "Jij rent.", ["You run."], READ),
                self.create_quiz(declarative, "Jij rent.", ["Jij rent."], DICTATE),
                self.create_quiz(declarative, "Jij rent.", ["You run."], INTERPRET),
                self.create_quiz(declarative, "You run.", ["Jij rent."], WRITE),
                self.create_quiz(imperative, "Ren!", ["Run!"], READ),
                self.create_quiz(imperative, "Ren!", ["Ren!"], DICTATE),
                self.create_quiz(imperative, "Ren!", ["Run!"], INTERPRET),
                self.create_quiz(imperative, "Run!", ["Ren!"], WRITE),
                self.create_quiz(concept, "Jij rent.", ["Ren!"], IMPERATIVE),
                self.create_quiz(concept, "Ren!", ["Jij rent."], DECLARATIVE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_declarative_interrogative_and_imperative_moods(self):
        """Test that quizzes can be generated for the declarative, interrogative, and imperative moods."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "you run",
            {
                "declarative": dict(en="You run.", nl="Jij rent."),
                "interrogative": dict(en="Do you run?", nl="Ren jij?"),
                "imperative": dict(en="Run!", nl="Ren!"),
            },
        )
        declarative, interrogative, imperative = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(declarative, "Jij rent.", ["You run."], READ),
                self.create_quiz(declarative, "Jij rent.", ["Jij rent."], DICTATE),
                self.create_quiz(declarative, "Jij rent.", ["You run."], INTERPRET),
                self.create_quiz(declarative, "You run.", ["Jij rent."], WRITE),
                self.create_quiz(interrogative, "Ren jij?", ["Ren jij?"], READ),
                self.create_quiz(interrogative, "Ren jij?", ["Ren jij?"], DICTATE),
                self.create_quiz(interrogative, "Ren jij?", ["Do you run?"], INTERPRET),
                self.create_quiz(interrogative, "Do you run?", ["Ren jij?"], WRITE),
                self.create_quiz(imperative, "Ren!", ["Run!"], READ),
                self.create_quiz(imperative, "Ren!", ["Ren!"], DICTATE),
                self.create_quiz(imperative, "Ren!", ["Run!"], INTERPRET),
                self.create_quiz(imperative, "Run!", ["Ren!"], WRITE),
                self.create_quiz(concept, "Jij rent.", ["Ren!"], IMPERATIVE),
                self.create_quiz(concept, "Jij rent.", ["Ren jij?"], INTERROGATIVE),
                self.create_quiz(concept, "Ren!", ["Jij rent."], DECLARATIVE),
                self.create_quiz(concept, "Ren!", ["Ren jij?"], INTERROGATIVE),
                self.create_quiz(concept, "Ren jij?", ["Ren!"], IMPERATIVE),
                self.create_quiz(concept, "Ren jij?", ["Jij rent."], DECLARATIVE),
            },
            create_quizzes(NL_EN, concept),
        )


class GrammaticalPolarityTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical polarities."""

    def test_affirmative_and_negative_polarities(self):
        """Test that quizzes can be generated for the affirmative and negative polarities."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "car",
            {
                "affirmative": dict(en="The car is black.", nl="De auto is zwart."),
                "negative": dict(en="The car is not black.", nl="De auto is niet zwart."),
            },
        )
        affirmative, negative = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(affirmative, "De auto is zwart.", ["The car is black."], READ),
                self.create_quiz(affirmative, "De auto is zwart.", ["De auto is zwart."], DICTATE),
                self.create_quiz(affirmative, "De auto is zwart.", ["The cat is black."], INTERPRET),
                self.create_quiz(affirmative, "The car is black.", ["De auto is zwart."], WRITE),
                self.create_quiz(negative, "De auto is niet zwart.", ["The car is not black."], READ),
                self.create_quiz(negative, "De auto is niet zwart.", ["De auto is niet zwart."], DICTATE),
                self.create_quiz(negative, "De auto is niet zwart.", ["The car is not black."], INTERPRET),
                self.create_quiz(negative, "The car is not black.", ["De auto is niet zwart."], WRITE),
                self.create_quiz(concept, "De auto is zwart.", ["De auto is niet zwart."], NEGATIVE),
                self.create_quiz(concept, "De auto is niet zwart.", ["De auto is zwart."], AFFIRMATIVE),
                self.create_quiz(concept, "De auto is niet zwart.", ["De auto is niet zwart."], ORDER),
            },
            create_quizzes(NL_EN, concept),
        )


class DiminutiveTest(ToistoTestCase):
    """Unit tests for diminutive forms."""

    def test_diminutive(self):
        """Test that quizzes can be generated for diminutive forms."""
        self.language_pair = NL_EN
        concept = self.create_concept("car", dict(root=dict(nl="de auto"), diminutive=dict(nl="het autootje")))
        root, diminutive = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(root, "de auto", ["de auto"], DICTATE),
                self.create_quiz(diminutive, "het autootje", ["het autootje"], DICTATE),
                self.create_quiz(concept, "de auto", ["het autootje"], DIMINUTIVE),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_diminutive_and_translation(self):
        """Test that quizzes can be generated for diminutive forms."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "car",
            {
                "root": dict(en="car", nl="de auto"),
                "diminutive": dict(nl="het autootje"),
            },
        )
        root, diminutive = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(root, "de auto", ["car"], READ),
                self.create_quiz(root, "de auto", ["de auto"], DICTATE),
                self.create_quiz(root, "de auto", ["car"], INTERPRET),
                self.create_quiz(root, "car", ["de auto"], WRITE),
                self.create_quiz(diminutive, "het autootje", ["het autootje"], DICTATE),
                self.create_quiz(concept, "de auto", ["het autootje"], DIMINUTIVE),
            },
            create_quizzes(NL_EN, concept),
        )


class NumberTest(ToistoTestCase):
    """Unit tests for numbers."""

    def test_numbers(self):
        """Test that quizzes can be generated for numbers."""
        self.language_pair = NL_EN
        concept = self.create_concept("one", dict(cardinal=dict(nl="een"), ordinal=dict(nl="eerste")))
        cardinal, ordinal = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(cardinal, "een", ["een"], DICTATE),
                self.create_quiz(ordinal, "eerste", ["eerste"], DICTATE),
                self.create_quiz(concept, "een", ["eerste"], ORDINAL),
                self.create_quiz(concept, "eerste", ["een"], CARDINAL),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_numbers_and_translations(self):
        """Test that quizzes can be generated for numbers."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "one", dict(cardinal=dict(nl="een", en="one"), ordinal=dict(nl="eerste", en="first"))
        )
        cardinal, ordinal = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(cardinal, "een", ["one"], READ),
                self.create_quiz(cardinal, "een", ["een"], DICTATE),
                self.create_quiz(cardinal, "een", ["one"], INTERPRET),
                self.create_quiz(cardinal, "one", ["een"], WRITE),
                self.create_quiz(ordinal, "eerste", ["first"], READ),
                self.create_quiz(ordinal, "eerste", ["eerste"], DICTATE),
                self.create_quiz(ordinal, "eerste", ["first"], INTERPRET),
                self.create_quiz(ordinal, "first", ["eerste"], WRITE),
                self.create_quiz(concept, "eerste", ["een"], CARDINAL),
                self.create_quiz(concept, "een", ["eerste"], ORDINAL),
            },
            create_quizzes(NL_EN, concept),
        )


class AbbreviationTest(ToistoTestCase):
    """Unit tests for abbreviations."""

    def test_abbreviations(self):
        """Test that quizzes can be generated for abbreviations."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "llc", {"full form": dict(nl="naamloze vennootschap"), "abbreviation": dict(nl="NV")}
        )
        full_form, abbreviation = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(full_form, "naamloze vennootschap", ["naamloze vennootschap"], DICTATE),
                self.create_quiz(abbreviation, "NV", ["NV"], DICTATE),
                self.create_quiz(concept, "naamloze vennootschap", ["NV"], ABBREVIATION),
                self.create_quiz(concept, "NV", ["naamloze vennootschap"], FULL_FORM),
            },
            create_quizzes(NL_EN, concept),
        )


class QuizNoteTest(ToistoTestCase):
    """Unit tests for the quiz notes."""

    def test_note(self):
        """Test that the quizzes use the notes of the target language."""
        self.language_pair = FI_NL
        concept = self.create_concept(
            "finnish",
            dict(
                fi="suomi;;In Finnish, the names of languages are not capitalized",
                nl="Fins;;In Dutch, the names of languages are capitalized",
            ),
        )
        for quiz in create_quizzes(FI_NL, concept):
            self.assertEqual("In Finnish, the names of languages are not capitalized", quiz.answer_notes[0])


class ColloquialTest(ToistoTestCase):
    """Unit tests for concepts with colloquial (spoken language) labels."""

    def test_colloquial_and_regular_label(self):
        """Test the generated quizzes when one language has both a colloquial and a regular label."""
        concept = self.create_concept("seven", dict(fi=["seittemän*", "seitsemän"], nl="zeven"))
        self.language_pair = FI_NL
        self.assertSetEqual(
            {
                self.create_quiz(concept, "seitsemän", ["zeven"], READ),
                self.create_quiz(concept, "seitsemän", ["seitsemän"], DICTATE),
                self.create_quiz(concept, "zeven", ["seitsemän"], WRITE),
                self.create_quiz(concept, "seitsemän", ["zeven"], INTERPRET),
                self.create_quiz(concept, "seittemän*", ["seitsemän"], DICTATE),
                self.create_quiz(concept, "seittemän*", ["zeven"], INTERPRET),
            },
            create_quizzes(FI_NL, concept),
        )
        self.language_pair = NL_FI
        self.assertSetEqual(
            {
                self.create_quiz(concept, "zeven", ["seitsemän"], READ),
                self.create_quiz(concept, "zeven", ["zeven"], DICTATE),
                self.create_quiz(concept, "seitsemän", ["zeven"], WRITE),
                self.create_quiz(concept, "zeven", ["seitsemän"], INTERPRET),
            },
            create_quizzes(NL_FI, concept),
        )

    def test_grammar_and_colloquial(self):
        """Test the generated quizzes when colloquial labels and grammar are combined."""
        concept = self.create_concept(
            "kiosk",
            dict(
                singular=dict(fi=["kioski", "kiska*"], en="kiosk"),
                plural=dict(fi=["kioskit", "kiskat*"], en="kiosks"),
            ),
        )
        singular, plural = concept.leaf_concepts(FI)
        self.language_pair = FI_EN
        self.assertSetEqual(
            {
                self.create_quiz(singular, "kioski", ["kiosk"], READ),
                self.create_quiz(singular, "kioski", ["kioski"], DICTATE),
                self.create_quiz(singular, "kiosk", ["kioski"], WRITE),
                self.create_quiz(singular, "kioski", ["kiosk"], INTERPRET),
                self.create_quiz(singular, "kiska*", ["kiosk"], INTERPRET),
                self.create_quiz(singular, "kiska*", ["kioski"], DICTATE),
                self.create_quiz(plural, "kioskit", ["kiosks"], READ),
                self.create_quiz(plural, "kioskit", ["kioskit"], DICTATE),
                self.create_quiz(plural, "kiosks", ["kioskit"], WRITE),
                self.create_quiz(plural, "kioskit", ["kiosks"], INTERPRET),
                self.create_quiz(plural, "kiskat*", ["kiosks"], INTERPRET),
                self.create_quiz(plural, "kiskat*", ["kioskit"], DICTATE),
                self.create_quiz(concept, "kioski", ["kioskit"], PLURAL),
                self.create_quiz(concept, "kioskit", ["kioski"], SINGULAR),
            },
            create_quizzes(FI_EN, concept),
        )
        self.language_pair = EN_FI
        self.assertSetEqual(
            {
                self.create_quiz(singular, "kiosk", ["kioski"], READ),
                self.create_quiz(singular, "kiosk", ["kiosk"], DICTATE),
                self.create_quiz(singular, "kioski", ["kiosk"], WRITE),
                self.create_quiz(singular, "kiosk", ["kioski"], INTERPRET),
                self.create_quiz(plural, "kiosks", ["kioskit"], READ),
                self.create_quiz(plural, "kiosks", ["kiosks"], DICTATE),
                self.create_quiz(plural, "kioskit", ["kiosks"], WRITE),
                self.create_quiz(plural, "kiosks", ["kioskit"], INTERPRET),
                self.create_quiz(concept, "kiosk", ["kiosks"], PLURAL),
                self.create_quiz(concept, "kiosks", ["kiosk"], SINGULAR),
            },
            create_quizzes(EN_FI, concept),
        )

    def test_related_concepts_and_colloquial(self):
        """Test the generated quizzes when colloquial labels and related concepts are combined."""
        self.language_pair = FI_EN
        yes = self.create_concept("yes", dict(antonym="no", fi=["kylla", "kyl*"]))
        no = self.create_concept("no", dict(antonym="yes", fi="ei"))
        self.assertSetEqual(
            {
                self.create_quiz(yes, "kylla", ["kylla"], DICTATE),
                self.create_quiz(yes, "kyl*", ["kylla"], DICTATE),
                self.create_quiz(yes, "kylla", ["ei"], ANTONYM),
            },
            create_quizzes(FI_EN, yes),
        )
        self.assertSetEqual(
            {
                self.create_quiz(no, "ei", ["ei"], DICTATE),
                self.create_quiz(no, "ei", ["kylla"], ANTONYM),
            },
            create_quizzes(FI_EN, no),
        )


class MeaningsTest(ToistoTestCase):
    """Test that quizzes have the correct meaning."""

    def test_interpret_with_synonym(self):
        """Test that interpret quizzes show all synonyms as meaning."""
        concept = self.create_concept("yes", dict(fi=["kylla", "joo"], en="yes"))
        quizzes = create_quizzes(FI_EN, concept)
        interpret_quizzes = quizzes.by_quiz_type(INTERPRET)
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kylla"), Label(FI, "joo")), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)

    def test_interpret_with_colloquial(self):
        """Test that interpret quizzes don't show colloquial labels as meaning."""
        concept = self.create_concept("20", dict(fi=["kaksikymmentä", "kakskyt*"], nl="twintig"))
        quizzes = create_quizzes(FI_NL, concept)
        interpret_quizzes = quizzes.by_quiz_type(INTERPRET)
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kaksikymmentä"),), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)


class GrammaticalQuizTypesTest(QuizFactoryTestCase):
    """Test the grammatical quiz types generator."""

    def test_adjective_with_degrees_of_comparison(self):
        """Test the grammatical quiz types for an adjective with degrees of comparison."""
        positive, comparative, superlative = self.create_adjective_with_degrees_of_comparison().leaf_concepts(EN)
        for concept in (positive, comparative):
            self.assertEqual(SUPERLATIVE_DEGREE, grammatical_quiz_type(concept, superlative))
        for concept in (positive, superlative):
            self.assertEqual(COMPARATIVE_DEGREE, grammatical_quiz_type(concept, comparative))
        for concept in (comparative, superlative):
            self.assertEqual(POSITIVE_DEGREE, grammatical_quiz_type(concept, positive))

    def test_noun_with_grammatical_number(self):
        """Test the grammatical quiz types for a noun with singular and plural form."""
        singular, plural = self.create_noun_with_grammatical_number().leaf_concepts(FI)
        self.assertEqual(PLURAL, grammatical_quiz_type(singular, plural))
        self.assertEqual(SINGULAR, grammatical_quiz_type(plural, singular))

    def test_noun_with_grammatical_gender(self):
        """Test the grammatical quiz types for a noun with grammatical gender."""
        feminine, maasculine = self.create_noun_with_grammatical_gender().leaf_concepts(EN)
        self.assertEqual(MASCULINE, grammatical_quiz_type(feminine, maasculine))
        self.assertEqual(FEMININE, grammatical_quiz_type(maasculine, feminine))

    def test_noun_with_grammatical_gender_including_neuter(self):
        """Test the grammatical quiz types for a noun with grammatical gender including neuter."""
        feminine, masculine, neuter = self.create_noun_with_grammatical_gender_including_neuter().leaf_concepts(NL)
        for concept in (feminine, neuter):
            self.assertEqual(MASCULINE, grammatical_quiz_type(concept, masculine))
        for concept in (feminine, masculine):
            self.assertEqual(NEUTER, grammatical_quiz_type(concept, neuter))
        for concept in (masculine, neuter):
            self.assertEqual(FEMININE, grammatical_quiz_type(concept, feminine))

    def test_noun_with_grammatical_number_and_gender(self):
        """Test the grammatical quiz types for a noun with grammatical number and gender."""
        noun = self.create_noun_with_grammatical_number_and_gender()
        singular_feminine, singular_masculine, plural_feminine, plural_masculine = noun.leaf_concepts(EN)
        for feminine, masculine in ((singular_feminine, singular_masculine), (plural_feminine, plural_masculine)):
            self.assertEqual(MASCULINE, grammatical_quiz_type(feminine, masculine))
            self.assertEqual(FEMININE, grammatical_quiz_type(masculine, feminine))
        for singular, plural in ((singular_feminine, plural_feminine), (singular_masculine, plural_masculine)):
            self.assertEqual(PLURAL, grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, grammatical_quiz_type(plural, singular))

    def test_verb_with_person(self):
        """Test the grammatical quiz types for a verb with grammatical person."""
        verb = self.create_verb_with_person()
        first, second, third = verb.leaf_concepts(EN)
        for concept in (first, second):
            self.assertEqual(THIRD_PERSON, grammatical_quiz_type(concept, third))
        for concept in (first, third):
            self.assertEqual(SECOND_PERSON, grammatical_quiz_type(concept, second))
        for concept in (second, third):
            self.assertEqual(FIRST_PERSON, grammatical_quiz_type(concept, first))

    def test_verb_with_tense_and_person(self):
        """Test the grammatical quiz types for a verb with tense and grammatical person."""
        verb = self.create_verb_with_tense_and_person("present tense", "past tense")
        present_singular, present_plural, past_singular, past_plural = verb.leaf_concepts(NL)
        for singular, plural in ((present_singular, present_plural), (past_singular, past_plural)):
            self.assertEqual(PLURAL, grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, grammatical_quiz_type(plural, singular))
        for present, past in ((present_singular, past_singular), (present_plural, past_plural)):
            self.assertEqual(PAST_TENSE, grammatical_quiz_type(present, past))
            self.assertEqual(PRESENT_TENSE, grammatical_quiz_type(past, present))

    def test_verb_with_infinitive_and_person(self):
        """Test the grammatical quiz types for a verb with infinitive and grammatical person."""
        verb = self.create_verb_with_infinitive_and_person()
        infinitive, singular, plural = verb.leaf_concepts(EN)
        for concept in (infinitive, singular):
            self.assertEqual(PLURAL, grammatical_quiz_type(concept, plural))
        for concept in (infinitive, plural):
            self.assertEqual(SINGULAR, grammatical_quiz_type(concept, singular))
        for concept in (singular, plural):
            self.assertEqual(INFINITIVE, grammatical_quiz_type(concept, infinitive))

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
            self.assertEqual(PLURAL, grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, grammatical_quiz_type(plural, singular))
        for first_person, second_person in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(SECOND_PERSON, grammatical_quiz_type(first_person, second_person))
            self.assertEqual(FIRST_PERSON, grammatical_quiz_type(second_person, first_person))
        for first_person, third_person in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, grammatical_quiz_type(first_person, third_person))
            self.assertEqual(FIRST_PERSON, grammatical_quiz_type(third_person, first_person))
        for second_person, third_person in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, grammatical_quiz_type(second_person, third_person))
            self.assertEqual(SECOND_PERSON, grammatical_quiz_type(third_person, second_person))

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
            self.assertEqual(PLURAL, grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, grammatical_quiz_type(plural, singular))
            self.assertIsNone(grammatical_quiz_type(infinitive, singular))
            self.assertIsNone(grammatical_quiz_type(infinitive, plural))
        for first_person, second_person in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(SECOND_PERSON, grammatical_quiz_type(first_person, second_person))
            self.assertEqual(FIRST_PERSON, grammatical_quiz_type(second_person, first_person))
        for first_person, third_person in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, grammatical_quiz_type(first_person, third_person))
            self.assertEqual(FIRST_PERSON, grammatical_quiz_type(third_person, first_person))
        for second_person, third_person in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, grammatical_quiz_type(second_person, third_person))
            self.assertEqual(SECOND_PERSON, grammatical_quiz_type(third_person, second_person))


class OrderQuizTest(QuizFactoryTestCase):
    """Unit tests for generating order quizzes."""

    def test_generate_order_quiz_for_long_enough_sentences(self):
        """Test that order quizzes are generated for long enough sentences."""
        concept = self.create_concept("breakfast", dict(en="We eat breakfast in the kitchen."))
        quizzes = create_quizzes(EN_NL, concept)
        quiz = first(quizzes.by_quiz_type(ORDER))
        self.assertEqual(ORDER, quiz.quiz_type)
