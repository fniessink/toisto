"""Concept unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept
from toisto.model.language.grammar import Tense
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes, grammatical_quiz_types

from ....base import EN_FI, FI_EN, FI_NL, NL_EN, NL_FI, ToistoTestCase


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
        return self.create_concept("to eat", concept_dict)

    def create_verb_with_number_and_person(self) -> Concept:
        """Create a verb with grammatical number nested with grammatical person."""
        return self.create_concept(
            "to have",
            dict(
                singular={
                    "first person": dict(fi="minulla on", nl="ik heb"),
                    "second person": dict(fi="sinulla on", nl="jij hebt"),
                    "third person": dict(fi="hänellä on", nl="zij heeft"),
                },
                plural={
                    "first person": dict(fi="meillä on", nl="wij hebben"),
                    "second person": dict(fi="teillä on", nl="jullie hebben"),
                    "third person": dict(fi="heillä on", nl="zij hebben"),
                },
            ),
        )

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
            dict(female=dict(en="her cat", nl="haar kat"), male=dict(en="his cat", nl="zijn kat")),
        )

    def create_noun_with_grammatical_gender_including_neuter(self) -> Concept:
        """Create a noun with grammatical gender, including neuter."""
        return self.create_concept(
            "bone",
            dict(
                female=dict(en="her bone", nl="haar bot"),
                male=dict(en="his bone", nl="zijn bot;male"),
                neuter=dict(en="its bone", nl="zijn bot;neuter"),
            ),
        )

    def create_noun_with_grammatical_number_and_gender(self) -> Concept:
        """Create a noun with grammatical number and grammatical gender."""
        return self.create_concept(
            "cat",
            dict(
                singular=dict(female=dict(en="her cat", nl="haar kat"), male=dict(en="his cat", nl="zijn kat")),
                plural=dict(female=dict(en="her cats", nl="haar katten"), male=dict(en="his cats", nl="zijn katten")),
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
                self.create_quiz(concept, "Engels", ["English"], "read"),
                self.create_quiz(concept, "Engels", ["Engels"], "dictate"),
                self.create_quiz(concept, "Engels", ["English"], "interpret"),
                self.create_quiz(concept, "English", ["Engels"], "write"),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_only_listening_quizzes_for_one_language(self):
        """Test that only listening quizzes are generated for a concept with one language."""
        concept = self.create_concept("english", dict(nl="Engels"))
        self.assertSetEqual(
            {self.create_quiz(concept, "Engels", ["Engels"], "dictate", language_pair=NL_EN)},
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
                self.create_quiz(concept, "bank", ["couch", "bank"], "read"),
                self.create_quiz(concept, "bank", ["bank"], "dictate"),
                self.create_quiz(concept, "bank", ["couch", "bank"], "interpret"),
                self.create_quiz(concept, "couch", ["bank"], "write"),
                self.create_quiz(concept, "bank", ["bank"], "write"),
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
                self.create_quiz(singular, "aamu", ["de ochtend"], "read"),
                self.create_quiz(singular, "aamu", ["aamu"], "dictate"),
                self.create_quiz(singular, "aamu", ["de ochtend"], "interpret"),
                self.create_quiz(singular, "de ochtend", ["aamu"], "write"),
                self.create_quiz(plural, "aamut", ["de ochtenden"], "read"),
                self.create_quiz(plural, "aamut", ["aamut"], "dictate"),
                self.create_quiz(plural, "aamut", ["de ochtenden"], "interpret"),
                self.create_quiz(plural, "de ochtenden", ["aamut"], "write"),
                self.create_quiz(concept, "aamu", ["aamut"], "pluralize"),
                self.create_quiz(concept, "aamut", ["aamu"], "singularize"),
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
                self.create_quiz(singular, "ketsuppi", ["de ketchup"], "read"),
                self.create_quiz(singular, "ketsuppi", ["ketsuppi"], "dictate"),
                self.create_quiz(singular, "ketsuppi", ["de ketchup"], "interpret"),
                self.create_quiz(singular, "de ketchup", ["ketsuppi"], "write"),
                self.create_quiz(plural, "ketsupit", ["ketsupit"], "dictate"),
                self.create_quiz(concept, "ketsuppi", ["ketsupit"], "pluralize"),
                self.create_quiz(concept, "ketsupit", ["ketsuppi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.question_meanings))
            self.assertNotIn("", (str(meaning) for meaning in quiz.answer_meanings))

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the target language only."""
        self.language_pair = FI_NL
        concept = self.create_concept("mämmi", dict(singular=dict(fi="mämmi"), plural=dict(fi="mämmit")))
        singular, plural = concept.leaf_concepts(FI)
        quizzes = create_quizzes(FI_NL, concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "mämmi", ["mämmi"], "dictate"),
                self.create_quiz(plural, "mämmit", ["mämmit"], "dictate"),
                self.create_quiz(concept, "mämmi", ["mämmit"], "pluralize"),
                self.create_quiz(concept, "mämmit", ["mämmi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.question_meanings))
            self.assertNotIn("", (str(meaning) for meaning in quiz.answer_meanings))

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
                self.create_quiz(singular, "kauppakeskus", ["het winkelcentrum"], "read"),
                self.create_quiz(singular, "ostoskeskus", ["het winkelcentrum"], "read"),
                self.create_quiz(singular, "kauppakeskus", ["kauppakeskus"], "dictate"),
                self.create_quiz(singular, "kauppakeskus", ["het winkelcentrum"], "interpret"),
                self.create_quiz(singular, "ostoskeskus", ["ostoskeskus"], "dictate"),
                self.create_quiz(singular, "ostoskeskus", ["het winkelcentrum"], "interpret"),
                self.create_quiz(singular, "het winkelcentrum", ["kauppakeskus", "ostoskeskus"], "write"),
                self.create_quiz(plural, "kauppakeskukset", ["de winkelcentra"], "read"),
                self.create_quiz(plural, "ostoskeskukset", ["de winkelcentra"], "read"),
                self.create_quiz(plural, "kauppakeskukset", ["kauppakeskukset"], "dictate"),
                self.create_quiz(plural, "kauppakeskukset", ["de winkelcentra"], "interpret"),
                self.create_quiz(plural, "ostoskeskukset", ["ostoskeskukset"], "dictate"),
                self.create_quiz(plural, "ostoskeskukset", ["de winkelcentra"], "interpret"),
                self.create_quiz(plural, "de winkelcentra", ["kauppakeskukset", "ostoskeskukset"], "write"),
                self.create_quiz(concept, "kauppakeskus", ["kauppakeskukset"], "pluralize"),
                self.create_quiz(concept, "ostoskeskus", ["ostoskeskukset"], "pluralize"),
                self.create_quiz(concept, "kauppakeskukset", ["kauppakeskus"], "singularize"),
                self.create_quiz(concept, "ostoskeskukset", ["ostoskeskus"], "singularize"),
            },
            create_quizzes(FI_NL, concept),
        )

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        self.language_pair = NL_EN
        concept = self.create_noun_with_grammatical_gender()
        female, male = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(female, "haar kat", ["her cat"], "read"),
                self.create_quiz(female, "haar kat", ["haar kat"], "dictate"),
                self.create_quiz(female, "haar kat", ["her cat"], "interpret"),
                self.create_quiz(female, "her cat", ["haar kat"], "write"),
                self.create_quiz(male, "zijn kat", ["his cat"], "read"),
                self.create_quiz(male, "zijn kat", ["zijn kat"], "dictate"),
                self.create_quiz(male, "zijn kat", ["his cat"], "interpret"),
                self.create_quiz(male, "his cat", ["zijn kat"], "write"),
                self.create_quiz(concept, "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(concept, "zijn kat", ["haar kat"], "feminize"),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        self.language_pair = NL_EN
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        female, male, neuter = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(female, "haar bot", ["her bone"], "read"),
                self.create_quiz(female, "haar bot", ["haar bot"], "dictate"),
                self.create_quiz(female, "haar bot", ["her bone"], "interpret"),
                self.create_quiz(female, "her bone", ["haar bot"], "write"),
                self.create_quiz(male, "zijn bot", ["his bone"], "read"),
                self.create_quiz(male, "zijn bot", ["zijn bot"], "dictate"),
                self.create_quiz(male, "zijn bot", ["his bone"], "interpret"),
                self.create_quiz(male, "his bone", ["zijn bot"], "write"),
                self.create_quiz(neuter, "zijn bot", ["its bone"], "read"),
                self.create_quiz(neuter, "zijn bot", ["zijn bot"], "dictate"),
                self.create_quiz(neuter, "zijn bot", ["its bone"], "interpret"),
                self.create_quiz(neuter, "its bone", ["zijn bot"], "write"),
                self.create_quiz(concept, "haar bot", ["zijn bot"], "masculinize"),
                self.create_quiz(concept, "haar bot", ["zijn bot"], "neuterize"),
                self.create_quiz(concept, "zijn bot", ["haar bot"], "feminize"),
                self.create_quiz(concept, "zijn bot", ["haar bot"], "feminize"),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        self.language_pair = NL_EN
        concept = self.create_noun_with_grammatical_number_and_gender()
        singular, plural = concept.constituents
        singular_female, singular_male, plural_female, plural_male = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(singular_female, "haar kat", ["her cat"], "read"),
                self.create_quiz(singular_female, "haar kat", ["haar kat"], "dictate"),
                self.create_quiz(singular_female, "haar kat", ["her cat"], "interpret"),
                self.create_quiz(singular_female, "her cat", ["haar kat"], "write"),
                self.create_quiz(singular_male, "zijn kat", ["his cat"], "read"),
                self.create_quiz(singular_male, "zijn kat", ["zijn kat"], "dictate"),
                self.create_quiz(singular_male, "zijn kat", ["his cat"], "interpret"),
                self.create_quiz(singular_male, "his cat", ["zijn kat"], "write"),
                self.create_quiz(singular, "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(singular, "zijn kat", ["haar kat"], "feminize"),
                self.create_quiz(plural_female, "haar katten", ["her cats"], "read"),
                self.create_quiz(plural_female, "haar katten", ["haar katten"], "dictate"),
                self.create_quiz(plural_female, "haar katten", ["her cats"], "interpret"),
                self.create_quiz(plural_female, "her cats", ["haar katten"], "write"),
                self.create_quiz(plural_male, "zijn katten", ["his cats"], "read"),
                self.create_quiz(plural_male, "zijn katten", ["zijn katten"], "dictate"),
                self.create_quiz(plural_male, "zijn katten", ["his cats"], "interpret"),
                self.create_quiz(plural_male, "his cats", ["zijn katten"], "write"),
                self.create_quiz(plural, "haar katten", ["zijn katten"], "masculinize"),
                self.create_quiz(plural, "zijn katten", ["haar katten"], "feminize"),
                self.create_quiz(concept, "haar kat", ["haar katten"], "pluralize"),
                self.create_quiz(concept, "haar katten", ["haar kat"], "singularize"),
                self.create_quiz(concept, "zijn kat", ["zijn katten"], "pluralize"),
                self.create_quiz(concept, "zijn katten", ["zijn kat"], "singularize"),
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
                self.create_quiz(positive_degree, "groot", ["big"], "read"),
                self.create_quiz(positive_degree, "groot", ["groot"], "dictate"),
                self.create_quiz(positive_degree, "groot", ["big"], "interpret"),
                self.create_quiz(positive_degree, "big", ["groot"], "write"),
                self.create_quiz(comparative_degree, "groter", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "groter", ["groter"], "dictate"),
                self.create_quiz(comparative_degree, "groter", ["bigger"], "interpret"),
                self.create_quiz(comparative_degree, "bigger", ["groter"], "write"),
                self.create_quiz(superlative_degree, "grootst", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "grootst", ["grootst"], "dictate"),
                self.create_quiz(superlative_degree, "grootst", ["biggest"], "interpret"),
                self.create_quiz(superlative_degree, "biggest", ["grootst"], "write"),
                self.create_quiz(concept, "groot", ["groter"], "give comparative degree"),
                self.create_quiz(concept, "groot", ["grootst"], "give superlative degree"),
                self.create_quiz(concept, "groter", ["groot"], "give positive degree"),
                self.create_quiz(concept, "groter", ["grootst"], "give superlative degree"),
                self.create_quiz(concept, "grootst", ["groot"], "give positive degree"),
                self.create_quiz(concept, "grootst", ["groter"], "give comparative degree"),
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
                self.create_quiz(positive_degree, "iso", ["big"], "read"),
                self.create_quiz(positive_degree, "suuri", ["big"], "read"),
                self.create_quiz(positive_degree, "iso", ["iso"], "dictate"),
                self.create_quiz(positive_degree, "iso", ["big"], "interpret"),
                self.create_quiz(positive_degree, "suuri", ["suuri"], "dictate"),
                self.create_quiz(positive_degree, "suuri", ["big"], "interpret"),
                self.create_quiz(positive_degree, "big", ["iso", "suuri"], "write"),
                self.create_quiz(comparative_degree, "isompi", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "suurempi", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "isompi", ["isompi"], "dictate"),
                self.create_quiz(comparative_degree, "isompi", ["bigger"], "interpret"),
                self.create_quiz(comparative_degree, "suurempi", ["suurempi"], "dictate"),
                self.create_quiz(comparative_degree, "suurempi", ["bigger"], "interpret"),
                self.create_quiz(comparative_degree, "bigger", ["isompi", "suurempi"], "write"),
                self.create_quiz(superlative_degree, "isoin", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "suurin", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "isoin", ["isoin"], "dictate"),
                self.create_quiz(superlative_degree, "isoin", ["biggest"], "interpret"),
                self.create_quiz(superlative_degree, "suurin", ["suurin"], "dictate"),
                self.create_quiz(superlative_degree, "suurin", ["biggest"], "interpret"),
                self.create_quiz(superlative_degree, "biggest", ["isoin", "suurin"], "write"),
                self.create_quiz(concept, "iso", ["isompi"], "give comparative degree"),
                self.create_quiz(concept, "suuri", ["suurempi"], "give comparative degree"),
                self.create_quiz(concept, "iso", ["isoin"], "give superlative degree"),
                self.create_quiz(concept, "suuri", ["suurin"], "give superlative degree"),
                self.create_quiz(concept, "isompi", ["iso"], "give positive degree"),
                self.create_quiz(concept, "suurempi", ["suuri"], "give positive degree"),
                self.create_quiz(concept, "isompi", ["isoin"], "give superlative degree"),
                self.create_quiz(concept, "suurempi", ["suurin"], "give superlative degree"),
                self.create_quiz(concept, "isoin", ["iso"], "give positive degree"),
                self.create_quiz(concept, "suurin", ["suuri"], "give positive degree"),
                self.create_quiz(concept, "isoin", ["isompi"], "give comparative degree"),
                self.create_quiz(concept, "suurin", ["suurempi"], "give comparative degree"),
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
                self.create_quiz(first_person, "ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(first_person, "ik eet", ["I eat"], "interpret"),
                self.create_quiz(first_person, "I eat", ["ik eet"], "write"),
                self.create_quiz(second_person, "jij eet", ["you eat"], "read"),
                self.create_quiz(second_person, "jij eet", ["jij eet"], "dictate"),
                self.create_quiz(second_person, "jij eet", ["you eat"], "interpret"),
                self.create_quiz(second_person, "you eat", ["jij eet"], "write"),
                self.create_quiz(third_person, "zij eet", ["she eats"], "read"),
                self.create_quiz(third_person, "zij eet", ["zij eet"], "dictate"),
                self.create_quiz(third_person, "zij eet", ["she eats"], "interpret"),
                self.create_quiz(third_person, "she eats", ["zij eet"], "write"),
                self.create_quiz(concept, "ik eet", ["jij eet"], "give second person"),
                self.create_quiz(concept, "ik eet", ["zij eet"], "give third person"),
                self.create_quiz(concept, "jij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "jij eet", ["zij eet"], "give third person"),
                self.create_quiz(concept, "zij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "zij eet", ["jij eet"], "give second person"),
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
                "third person": dict(female=dict(en="she eats", nl="zij eet"), male=dict(en="he eats", nl="hij eet")),
            },
        )
        first_person, second_person, third_person = concept.constituents
        third_person_female, third_person_male = third_person.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(first_person, "ik eet", ["I eat"], "interpret"),
                self.create_quiz(first_person, "I eat", ["ik eet"], "write"),
                self.create_quiz(second_person, "jij eet", ["you eat"], "read"),
                self.create_quiz(second_person, "jij eet", ["jij eet"], "dictate"),
                self.create_quiz(second_person, "jij eet", ["you eat"], "interpret"),
                self.create_quiz(second_person, "you eat", ["jij eet"], "write"),
                self.create_quiz(third_person_female, "zij eet", ["she eats"], "read"),
                self.create_quiz(third_person_female, "zij eet", ["zij eet"], "dictate"),
                self.create_quiz(third_person_female, "zij eet", ["she eats"], "interpret"),
                self.create_quiz(third_person_female, "she eats", ["zij eet"], "write"),
                self.create_quiz(third_person_male, "hij eet", ["he eats"], "read"),
                self.create_quiz(third_person_male, "hij eet", ["hij eet"], "dictate"),
                self.create_quiz(third_person_male, "hij eet", ["he eats"], "interpret"),
                self.create_quiz(third_person_male, "he eats", ["hij eet"], "write"),
                self.create_quiz(third_person, "zij eet", ["hij eet"], "masculinize"),
                self.create_quiz(third_person, "hij eet", ["zij eet"], "feminize"),
                self.create_quiz(concept, "ik eet", ["jij eet"], "give second person"),
                self.create_quiz(concept, "ik eet", ["zij eet"], ("give third person", "feminize")),
                self.create_quiz(concept, "ik eet", ["hij eet"], ("give third person", "masculinize")),
                self.create_quiz(concept, "jij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "jij eet", ["zij eet"], ("give third person", "feminize")),
                self.create_quiz(concept, "jij eet", ["hij eet"], ("give third person", "masculinize")),
                self.create_quiz(concept, "zij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "zij eet", ["jij eet"], "give second person"),
                self.create_quiz(concept, "hij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "hij eet", ["jij eet"], "give second person"),
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
                "third person": dict(female=dict(en="she eats"), male=dict(en="he eats"), fi="hän syö"),
            },
        )
        first_person, second_person, third_person = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "minä syön", ["I eat"], "read"),
                self.create_quiz(first_person, "minä syön", ["minä syön"], "dictate"),
                self.create_quiz(first_person, "minä syön", ["I eat"], "interpret"),
                self.create_quiz(first_person, "I eat", ["minä syön"], "write"),
                self.create_quiz(second_person, "sinä syöt", ["you eat"], "read"),
                self.create_quiz(second_person, "sinä syöt", ["sinä syöt"], "dictate"),
                self.create_quiz(second_person, "sinä syöt", ["you eat"], "interpret"),
                self.create_quiz(second_person, "you eat", ["sinä syöt"], "write"),
                self.create_quiz(third_person, "hän syö", ["she eats", "he eats"], "read"),
                self.create_quiz(third_person, "hän syö", ["hän syö"], "dictate"),
                self.create_quiz(third_person, "hän syö", ["she eats", "he eats"], "interpret"),
                self.create_quiz(third_person, "she eats", ["hän syö"], "write"),
                self.create_quiz(third_person, "he eats", ["hän syö"], "write"),
                self.create_quiz(concept, "minä syön", ["sinä syöt"], "give second person"),
                self.create_quiz(concept, "minä syön", ["hän syö"], "give third person"),
                self.create_quiz(concept, "sinä syöt", ["minä syön"], "give first person"),
                self.create_quiz(concept, "sinä syöt", ["hän syö"], "give third person"),
                self.create_quiz(concept, "hän syö", ["minä syön"], "give first person"),
                self.create_quiz(concept, "hän syö", ["sinä syöt"], "give second person"),
            },
            create_quizzes(FI_EN, concept),
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        self.language_pair = NL_FI
        concept = self.create_verb_with_number_and_person()
        singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "ik heb", ["minulla on"], "read"),
                self.create_quiz(first_person_singular, "minulla on", ["ik heb"], "write"),
                self.create_quiz(first_person_singular, "ik heb", ["ik heb"], "dictate"),
                self.create_quiz(first_person_singular, "ik heb", ["minulla on"], "interpret"),
                self.create_quiz(second_person_singular, "jij hebt", ["sinulla on"], "read"),
                self.create_quiz(second_person_singular, "sinulla on", ["jij hebt"], "write"),
                self.create_quiz(second_person_singular, "jij hebt", ["jij hebt"], "dictate"),
                self.create_quiz(second_person_singular, "jij hebt", ["sinulla on"], "interpret"),
                self.create_quiz(third_person_singular, "zij heeft", ["hänellä on"], "read"),
                self.create_quiz(third_person_singular, "hänellä on", ["zij heeft"], "write"),
                self.create_quiz(third_person_singular, "zij heeft", ["zij heeft"], "dictate"),
                self.create_quiz(third_person_singular, "zij heeft", ["hänellä on"], "interpret"),
                self.create_quiz(singular, "ik heb", ["jij hebt"], "give second person"),
                self.create_quiz(singular, "ik heb", ["zij heeft"], "give third person"),
                self.create_quiz(singular, "jij hebt", ["ik heb"], "give first person"),
                self.create_quiz(singular, "jij hebt", ["zij heeft"], "give third person"),
                self.create_quiz(singular, "zij heeft", ["ik heb"], "give first person"),
                self.create_quiz(singular, "zij heeft", ["jij hebt"], "give second person"),
                self.create_quiz(first_person_plural, "wij hebben", ["meillä on"], "read"),
                self.create_quiz(first_person_plural, "meillä on", ["wij hebben"], "write"),
                self.create_quiz(first_person_plural, "wij hebben", ["wij hebben"], "dictate"),
                self.create_quiz(first_person_plural, "wij hebben", ["meillä on"], "interpret"),
                self.create_quiz(second_person_plural, "jullie hebben", ["teillä on"], "read"),
                self.create_quiz(second_person_plural, "teillä on", ["jullie hebben"], "write"),
                self.create_quiz(second_person_plural, "jullie hebben", ["jullie hebben"], "dictate"),
                self.create_quiz(second_person_plural, "jullie hebben", ["teillä on"], "interpret"),
                self.create_quiz(third_person_plural, "zij hebben", ["heillä on"], "read"),
                self.create_quiz(third_person_plural, "heillä on", ["zij hebben"], "write"),
                self.create_quiz(third_person_plural, "zij hebben", ["zij hebben"], "dictate"),
                self.create_quiz(third_person_plural, "zij hebben", ["heillä on"], "interpret"),
                self.create_quiz(plural, "wij hebben", ["jullie hebben"], "give second person"),
                self.create_quiz(plural, "wij hebben", ["zij hebben"], "give third person"),
                self.create_quiz(plural, "jullie hebben", ["wij hebben"], "give first person"),
                self.create_quiz(plural, "jullie hebben", ["zij hebben"], "give third person"),
                self.create_quiz(plural, "zij hebben", ["wij hebben"], "give first person"),
                self.create_quiz(plural, "zij hebben", ["jullie hebben"], "give second person"),
                self.create_quiz(concept, "ik heb", ["wij hebben"], "pluralize"),
                self.create_quiz(concept, "wij hebben", ["ik heb"], "singularize"),
                self.create_quiz(concept, "jij hebt", ["jullie hebben"], "pluralize"),
                self.create_quiz(concept, "jullie hebben", ["jij hebt"], "singularize"),
                self.create_quiz(concept, "zij heeft", ["zij hebben"], "pluralize"),
                self.create_quiz(concept, "zij hebben", ["zij heeft"], "singularize"),
            },
            create_quizzes(NL_FI, concept),
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        self.language_pair = NL_EN
        concept = self.create_concept(
            "cat",
            dict(
                female=dict(singular=dict(en="her cat", nl="haar kat"), plural=dict(en="her cats", nl="haar katten")),
                male=dict(singular=dict(en="his cat", nl="zijn kat"), plural=dict(en="his cats", nl="zijn katten")),
            ),
        )
        female, male = concept.constituents
        female_singular, female_plural, male_singular, male_plural = concept.leaf_concepts(NL)
        self.assertSetEqual(
            {
                self.create_quiz(female_singular, "haar kat", ["her cat"], "read"),
                self.create_quiz(female_singular, "haar kat", ["haar kat"], "dictate"),
                self.create_quiz(female_singular, "haar kat", ["her cat"], "interpret"),
                self.create_quiz(female_singular, "her cat", ["haar kat"], "write"),
                self.create_quiz(female_plural, "haar katten", ["her cats"], "read"),
                self.create_quiz(female_plural, "haar katten", ["haar katten"], "dictate"),
                self.create_quiz(female_plural, "haar katten", ["her cats"], "interpret"),
                self.create_quiz(female_plural, "her cats", ["haar katten"], "write"),
                self.create_quiz(female, "haar kat", ["haar katten"], "pluralize"),
                self.create_quiz(female, "haar katten", ["haar kat"], "singularize"),
                self.create_quiz(male_singular, "zijn kat", ["his cat"], "read"),
                self.create_quiz(male_singular, "zijn kat", ["zijn kat"], "dictate"),
                self.create_quiz(male_singular, "zijn kat", ["his cat"], "interpret"),
                self.create_quiz(male_singular, "his cat", ["zijn kat"], "write"),
                self.create_quiz(male_plural, "zijn katten", ["his cats"], "read"),
                self.create_quiz(male_plural, "zijn katten", ["zijn katten"], "dictate"),
                self.create_quiz(male_plural, "zijn katten", ["his cats"], "interpret"),
                self.create_quiz(male_plural, "his cats", ["zijn katten"], "write"),
                self.create_quiz(male, "zijn kat", ["zijn katten"], "pluralize"),
                self.create_quiz(male, "zijn katten", ["zijn kat"], "singularize"),
                self.create_quiz(concept, "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(concept, "zijn kat", ["haar kat"], "feminize"),
                self.create_quiz(concept, "haar katten", ["zijn katten"], "masculinize"),
                self.create_quiz(concept, "zijn katten", ["haar katten"], "feminize"),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        self.language_pair = FI_EN
        concept = self.create_concept(
            "to be",
            dict(female=dict(en="she is|she's", fi="hän on;female"), male=dict(en="he is|he's", fi="hän on;male")),
        )
        female, male = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(female, "hän on;female", ["she is|she's"], "read"),
                self.create_quiz(female, "hän on;female", ["hän on;female"], "dictate"),
                self.create_quiz(female, "hän on;female", ["she is|she's"], "interpret"),
                self.create_quiz(female, "she is|she's", ["hän on;female"], "write"),
                self.create_quiz(male, "hän on;male", ["he is|he's"], "read"),
                self.create_quiz(male, "he is|he's", ["hän on;male"], "write"),
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
                self.create_quiz(infinitive, "slapen", ["to sleep"], "read"),
                self.create_quiz(infinitive, "slapen", ["slapen"], "dictate"),
                self.create_quiz(infinitive, "slapen", ["to sleep"], "interpret"),
                self.create_quiz(infinitive, "to sleep", ["slapen"], "write"),
                self.create_quiz(singular, "ik slaap", ["I sleep"], "read"),
                self.create_quiz(singular, "ik slaap", ["ik slaap"], "dictate"),
                self.create_quiz(singular, "ik slaap", ["I sleep"], "interpret"),
                self.create_quiz(singular, "I sleep", ["ik slaap"], "write"),
                self.create_quiz(plural, "wij slapen", ["we sleep"], "read"),
                self.create_quiz(plural, "wij slapen", ["wij slapen"], "dictate"),
                self.create_quiz(plural, "wij slapen", ["we sleep"], "interpret"),
                self.create_quiz(plural, "we sleep", ["wij slapen"], "write"),
                self.create_quiz(concept, "wij slapen", ["slapen"], "give infinitive"),
                self.create_quiz(concept, "ik slaap", ["slapen"], "give infinitive"),
                self.create_quiz(concept, "slapen", ["wij slapen"], "pluralize"),
                self.create_quiz(concept, "ik slaap", ["wij slapen"], "pluralize"),
                self.create_quiz(concept, "slapen", ["ik slaap"], "singularize"),
                self.create_quiz(concept, "wij slapen", ["ik slaap"], "singularize"),
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
                self.create_quiz(first_person_singular, "ik ben", ["minä olen"], "read"),
                self.create_quiz(first_person_singular, "ik ben", ["ik ben"], "dictate"),
                self.create_quiz(first_person_singular, "ik ben", ["minä olen"], "interpret"),
                self.create_quiz(first_person_singular, "minä olen", ["ik ben"], "write"),
                self.create_quiz(concept, "ik ben", ["zijn"], "give infinitive"),
                self.create_quiz(second_person_singular, "jij bent", ["sinä olet"], "read"),
                self.create_quiz(second_person_singular, "jij bent", ["jij bent"], "dictate"),
                self.create_quiz(second_person_singular, "jij bent", ["sinä olet"], "interpret"),
                self.create_quiz(second_person_singular, "sinä olet", ["jij bent"], "write"),
                self.create_quiz(concept, "jij bent", ["zijn"], "give infinitive"),
                self.create_quiz(third_person_singular, "zij is", ["hän on"], "read"),
                self.create_quiz(third_person_singular, "zij is", ["zij is"], "dictate"),
                self.create_quiz(third_person_singular, "zij is", ["hän on"], "interpret"),
                self.create_quiz(third_person_singular, "hän on", ["zij is"], "write"),
                self.create_quiz(concept, "zij is", ["zijn"], "give infinitive"),
                self.create_quiz(singular, "ik ben", ["jij bent"], "give second person"),
                self.create_quiz(singular, "ik ben", ["zij is"], "give third person"),
                self.create_quiz(singular, "jij bent", ["ik ben"], "give first person"),
                self.create_quiz(singular, "jij bent", ["zij is"], "give third person"),
                self.create_quiz(singular, "zij is", ["ik ben"], "give first person"),
                self.create_quiz(singular, "zij is", ["jij bent"], "give second person"),
                self.create_quiz(first_person_plural, "wij zijn", ["me olemme"], "read"),
                self.create_quiz(first_person_plural, "wij zijn", ["wij zijn"], "dictate"),
                self.create_quiz(first_person_plural, "wij zijn", ["me olemme"], "interpret"),
                self.create_quiz(first_person_plural, "me olemme", ["wij zijn"], "write"),
                self.create_quiz(concept, "wij zijn", ["zijn"], "give infinitive"),
                self.create_quiz(second_person_plural, "jullie zijn", ["te olette"], "read"),
                self.create_quiz(second_person_plural, "jullie zijn", ["jullie zijn"], "dictate"),
                self.create_quiz(second_person_plural, "jullie zijn", ["te olette"], "interpret"),
                self.create_quiz(second_person_plural, "te olette", ["jullie zijn"], "write"),
                self.create_quiz(concept, "jullie zijn", ["zijn"], "give infinitive"),
                self.create_quiz(third_person_plural, "zij zijn", ["he ovat"], "read"),
                self.create_quiz(third_person_plural, "zij zijn", ["zij zijn"], "dictate"),
                self.create_quiz(third_person_plural, "zij zijn", ["he ovat"], "interpret"),
                self.create_quiz(third_person_plural, "he ovat", ["zij zijn"], "write"),
                self.create_quiz(concept, "zij zijn", ["zijn"], "give infinitive"),
                self.create_quiz(plural, "wij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(plural, "wij zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural, "jullie zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural, "jullie zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural, "zij zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural, "zij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(concept, "ik ben", ["wij zijn"], "pluralize"),
                self.create_quiz(concept, "wij zijn", ["ik ben"], "singularize"),
                self.create_quiz(concept, "jij bent", ["jullie zijn"], "pluralize"),
                self.create_quiz(concept, "jullie zijn", ["jij bent"], "singularize"),
                self.create_quiz(concept, "zij is", ["zij zijn"], "pluralize"),
                self.create_quiz(concept, "zij zijn", ["zij is"], "singularize"),
                self.create_quiz(infinitive, "zijn", ["olla"], "read"),
                self.create_quiz(infinitive, "zijn", ["zijn"], "dictate"),
                self.create_quiz(infinitive, "zijn", ["olla"], "interpret"),
                self.create_quiz(infinitive, "olla", ["zijn"], "write"),
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
                self.create_quiz(first_singular_present, "ik ben", ["minä olen"], "read"),
                self.create_quiz(first_singular_present, "ik ben", ["ik ben"], "dictate"),
                self.create_quiz(first_singular_present, "ik ben", ["minä olen"], "interpret"),
                self.create_quiz(first_singular_present, "minä olen", ["ik ben"], "write"),
                self.create_quiz(second_singular_present, "jij bent", ["sinä olet"], "read"),
                self.create_quiz(second_singular_present, "jij bent", ["jij bent"], "dictate"),
                self.create_quiz(second_singular_present, "jij bent", ["sinä olet"], "interpret"),
                self.create_quiz(second_singular_present, "sinä olet", ["jij bent"], "write"),
                self.create_quiz(third_singular_present, "zij is", ["hän on"], "read"),
                self.create_quiz(third_singular_present, "zij is", ["zij is"], "dictate"),
                self.create_quiz(third_singular_present, "zij is", ["hän on"], "interpret"),
                self.create_quiz(third_singular_present, "hän on", ["zij is"], "write"),
                self.create_quiz(singular_present, "ik ben", ["jij bent"], "give second person"),
                self.create_quiz(singular_present, "ik ben", ["zij is"], "give third person"),
                self.create_quiz(singular_present, "jij bent", ["ik ben"], "give first person"),
                self.create_quiz(singular_present, "jij bent", ["zij is"], "give third person"),
                self.create_quiz(singular_present, "zij is", ["ik ben"], "give first person"),
                self.create_quiz(singular_present, "zij is", ["jij bent"], "give second person"),
                self.create_quiz(first_plural_present, "wij zijn", ["me olemme"], "read"),
                self.create_quiz(first_plural_present, "wij zijn", ["wij zijn"], "dictate"),
                self.create_quiz(first_plural_present, "wij zijn", ["me olemme"], "interpret"),
                self.create_quiz(first_plural_present, "me olemme", ["wij zijn"], "write"),
                self.create_quiz(second_plural_present, "jullie zijn", ["te olette"], "read"),
                self.create_quiz(second_plural_present, "jullie zijn", ["jullie zijn"], "dictate"),
                self.create_quiz(second_plural_present, "jullie zijn", ["te olette"], "interpret"),
                self.create_quiz(second_plural_present, "te olette", ["jullie zijn"], "write"),
                self.create_quiz(third_plural_present, "zij zijn", ["he ovat"], "read"),
                self.create_quiz(third_plural_present, "zij zijn", ["zij zijn"], "dictate"),
                self.create_quiz(third_plural_present, "zij zijn", ["he ovat"], "interpret"),
                self.create_quiz(third_plural_present, "he ovat", ["zij zijn"], "write"),
                self.create_quiz(plural_present, "wij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(plural_present, "wij zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural_present, "jullie zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural_present, "jullie zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural_present, "zij zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural_present, "zij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(present, "ik ben", ["wij zijn"], "pluralize"),
                self.create_quiz(present, "jij bent", ["jullie zijn"], "pluralize"),
                self.create_quiz(present, "zij is", ["zij zijn"], "pluralize"),
                self.create_quiz(present, "wij zijn", ["ik ben"], "singularize"),
                self.create_quiz(present, "jullie zijn", ["jij bent"], "singularize"),
                self.create_quiz(present, "zij zijn", ["zij is"], "singularize"),
                self.create_quiz(first_singular_past, "ik was", ["minä olin"], "read"),
                self.create_quiz(first_singular_past, "ik was", ["ik was"], "dictate"),
                self.create_quiz(first_singular_past, "ik was", ["minä olin"], "interpret"),
                self.create_quiz(first_singular_past, "minä olin", ["ik was"], "write"),
                self.create_quiz(second_singular_past, "jij was", ["sinä olot"], "read"),
                self.create_quiz(second_singular_past, "jij was", ["jij was"], "dictate"),
                self.create_quiz(second_singular_past, "jij was", ["sinä olit"], "interpret"),
                self.create_quiz(second_singular_past, "sinä olit", ["jij was"], "write"),
                self.create_quiz(third_singular_past, "zij was", ["hän oli"], "read"),
                self.create_quiz(third_singular_past, "zij was", ["zij was"], "dictate"),
                self.create_quiz(third_singular_past, "zij was", ["hän oli"], "interpret"),
                self.create_quiz(third_singular_past, "hän oli", ["zij was"], "write"),
                self.create_quiz(singular_past, "ik was", ["jij was"], "give second person"),
                self.create_quiz(singular_past, "ik was", ["zij was"], "give third person"),
                self.create_quiz(singular_past, "jij was", ["ik was"], "give first person"),
                self.create_quiz(singular_past, "jij was", ["zij was"], "give third person"),
                self.create_quiz(singular_past, "zij was", ["ik was"], "give first person"),
                self.create_quiz(singular_past, "zij was", ["jij was"], "give second person"),
                self.create_quiz(first_plural_past, "wij waren", ["me olimme"], "read"),
                self.create_quiz(first_plural_past, "wij waren", ["wij waren"], "dictate"),
                self.create_quiz(first_plural_past, "wij waren", ["me olimme"], "interpret"),
                self.create_quiz(first_plural_past, "me olimme", ["wij waren"], "write"),
                self.create_quiz(second_plural_past, "jullie waren", ["te olitte"], "read"),
                self.create_quiz(second_plural_past, "jullie waren", ["jullie waren"], "dictate"),
                self.create_quiz(second_plural_past, "jullie waren", ["te olitte"], "interpret"),
                self.create_quiz(second_plural_past, "te olitte", ["jullie waren"], "write"),
                self.create_quiz(third_plural_past, "zij waren", ["he olivat"], "read"),
                self.create_quiz(third_plural_past, "zij waren", ["zij waren"], "dictate"),
                self.create_quiz(third_plural_past, "zij waren", ["he olivät"], "interpret"),
                self.create_quiz(third_plural_past, "he olivat", ["zij waren"], "write"),
                self.create_quiz(plural_past, "wij waren", ["jullie waren"], "give second person"),
                self.create_quiz(plural_past, "wij waren", ["zij waren"], "give third person"),
                self.create_quiz(plural_past, "jullie waren", ["wij waren"], "give first person"),
                self.create_quiz(plural_past, "jullie waren", ["zij waren"], "give third person"),
                self.create_quiz(plural_past, "zij waren", ["wij waren"], "give first person"),
                self.create_quiz(plural_past, "zij waren", ["jullie waren"], "give second person"),
                self.create_quiz(past, "ik was", ["wij waren"], "pluralize"),
                self.create_quiz(past, "jij was", ["jullie waren"], "pluralize"),
                self.create_quiz(past, "zij was", ["zij waren"], "pluralize"),
                self.create_quiz(past, "wij waren", ["ik was"], "singularize"),
                self.create_quiz(past, "jullie waren", ["jij was"], "singularize"),
                self.create_quiz(past, "zij waren", ["zij was"], "singularize"),
                self.create_quiz(concept, "ik ben", ["ik was"], "give past tense"),
                self.create_quiz(concept, "jij bent", ["jij was"], "give past tense"),
                self.create_quiz(concept, "zij is", ["zij was"], "give past tense"),
                self.create_quiz(concept, "wij zijn", ["wij waren"], "give past tense"),
                self.create_quiz(concept, "jullie zijn", ["jullie waren"], "give past tense"),
                self.create_quiz(concept, "zij zijn", ["zij waren"], "give past tense"),
                self.create_quiz(concept, "ik was", ["ik ben"], "give present tense"),
                self.create_quiz(concept, "jij was", ["jij bent"], "give present tense"),
                self.create_quiz(concept, "zij was", ["zij is"], "give present tense"),
                self.create_quiz(concept, "wij waren", ["wij zijn"], "give present tense"),
                self.create_quiz(concept, "jullie waren", ["jullie zijn"], "give present tense"),
                self.create_quiz(concept, "zij waren", ["zij zijn"], "give present tense"),
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
                self.create_quiz(present_singular, "ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(present_singular, "ik eet", ["I eat"], "interpret"),
                self.create_quiz(present_singular, "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "wij eten", ["wij eten"], "dictate"),
                self.create_quiz(present_plural, "wij eten", ["we eat"], "interpret"),
                self.create_quiz(present_plural, "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "ik at", ["ik at"], "dictate"),
                self.create_quiz(past_singular, "ik at", ["I ate"], "interpret"),
                self.create_quiz(past_singular, "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "wij aten", ["wij aten"], "dictate"),
                self.create_quiz(past_plural, "wij aten", ["we ate"], "interpret"),
                self.create_quiz(past_plural, "we ate", ["wij aten"], "write"),
                self.create_quiz(past, "ik at", ["wij aten"], "pluralize"),
                self.create_quiz(past, "wij aten", ["ik at"], "singularize"),
                self.create_quiz(concept, "ik eet", ["ik at"], "give past tense"),
                self.create_quiz(concept, "wij eten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "ik at", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "wij aten", ["wij eten"], "give present tense"),
            },
            create_quizzes(NL_EN, concept),
        )

    def test_present_past_and_perfect_tense_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for present, past, and perfect tense nested with grammatical person."""
        self.language_pair = NL_EN
        concept = self.create_verb_with_tense_and_person("present tense", "past tense", "present perfect tense")
        present, past, perfect = concept.constituents
        present_singular, present_plural, past_singular, past_plural, perfect_singular, perfect_plural = (
            concept.leaf_concepts(NL)
        )
        self.assertSetEqual(
            {
                self.create_quiz(present_singular, "ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(present_singular, "ik eet", ["I eat"], "interpret"),
                self.create_quiz(present_singular, "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "wij eten", ["wij eten"], "dictate"),
                self.create_quiz(present_plural, "wij eten", ["we eat"], "interpret"),
                self.create_quiz(present_plural, "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "ik at", ["ik at"], "dictate"),
                self.create_quiz(past_singular, "ik at", ["I ate"], "interpret"),
                self.create_quiz(past_singular, "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "wij aten", ["wij aten"], "dictate"),
                self.create_quiz(past_plural, "wij aten", ["we ate"], "interpret"),
                self.create_quiz(past_plural, "we ate", ["wij aten"], "write"),
                self.create_quiz(past, "ik at", ["wij aten"], "pluralize"),
                self.create_quiz(past, "wij aten", ["ik at"], "singularize"),
                self.create_quiz(perfect_singular, "ik heb gegeten", ["I have eaten"], "read"),
                self.create_quiz(perfect_singular, "ik heb gegeten", ["ik heb gegeten"], "dictate"),
                self.create_quiz(perfect_singular, "ik heb gegeten", ["I have eaten"], "interpret"),
                self.create_quiz(perfect_singular, "I have eaten", ["ik heb gegeten"], "write"),
                self.create_quiz(perfect_plural, "wij hebben gegeten", ["we have eaten"], "read"),
                self.create_quiz(perfect_plural, "wij hebben gegeten", ["wij hebben gegeten"], "dictate"),
                self.create_quiz(perfect_plural, "wij hebben gegeten", ["we have eaten"], "interpret"),
                self.create_quiz(perfect_plural, "we have eaten", ["wij hebben gegeten"], "write"),
                self.create_quiz(perfect, "ik heb gegeten", ["wij hebben gegeten"], "pluralize"),
                self.create_quiz(perfect, "wij hebben gegeten", ["ik heb gegeten"], "singularize"),
                self.create_quiz(concept, "ik eet", ["ik at"], "give past tense"),
                self.create_quiz(concept, "wij eten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "ik at", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "wij aten", ["wij eten"], "give present tense"),
                self.create_quiz(concept, "ik heb gegeten", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "wij hebben gegeten", ["wij eten"], "give present tense"),
                self.create_quiz(concept, "ik heb gegeten", ["ik at"], "give past tense"),
                self.create_quiz(concept, "wij hebben gegeten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "ik eet", ["ik heb gegeten"], "give present perfect tense"),
                self.create_quiz(concept, "wij eten", ["wij hebben gegeten"], "give present perfect tense"),
                self.create_quiz(concept, "ik at", ["ik heb gegeten"], "give present perfect tense"),
                self.create_quiz(concept, "wij aten", ["wij hebben gegeten"], "give present perfect tense"),
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
                self.create_quiz(present_singular, "ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(present_singular, "ik eet", ["I eat"], "interpret"),
                self.create_quiz(present_singular, "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "wij eten", ["wij eten"], "dictate"),
                self.create_quiz(present_plural, "wij eten", ["we eat"], "interpret"),
                self.create_quiz(present_plural, "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "ik at", ["ik at"], "dictate"),
                self.create_quiz(past_singular, "ik at", ["I ate"], "interpret"),
                self.create_quiz(past_singular, "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "wij aten", ["wij aten"], "dictate"),
                self.create_quiz(past_plural, "wij aten", ["we ate"], "interpret"),
                self.create_quiz(past_plural, "we ate", ["wij aten"], "write"),
                self.create_quiz(past, "ik at", ["wij aten"], "pluralize"),
                self.create_quiz(past, "wij aten", ["ik at"], "singularize"),
                self.create_quiz(concept, "ik eet", ["ik at"], "give past tense"),
                self.create_quiz(concept, "wij eten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "ik at", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "wij aten", ["wij eten"], "give present tense"),
                self.create_quiz(infinitive, "eten", ["to eat"], "read"),
                self.create_quiz(infinitive, "eten", ["eten"], "dictate"),
                self.create_quiz(infinitive, "eten", ["to eat"], "interpret"),
                self.create_quiz(infinitive, "to eat", ["eten"], "write"),
                self.create_quiz(concept, "ik eet", ["eten"], "give infinitive"),
                self.create_quiz(concept, "wij eten", ["eten"], "give infinitive"),
                self.create_quiz(concept, "ik at", ["eten"], "give infinitive"),
                self.create_quiz(concept, "wij aten", ["eten"], "give infinitive"),
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
                self.create_quiz(declarative, "De auto is zwart.", ["The car is black."], "read"),
                self.create_quiz(declarative, "De auto is zwart.", ["De auto is zwart."], "dictate"),
                self.create_quiz(declarative, "De auto is zwart.", ["The car is black."], "interpret"),
                self.create_quiz(declarative, "The car is black.", ["De auto is zwart."], "write"),
                self.create_quiz(interrogative, "Is de auto zwart?", ["Is the car black?"], "read"),
                self.create_quiz(interrogative, "Is de auto zwart?", ["Is de auto zwart?"], "dictate"),
                self.create_quiz(interrogative, "Is de auto zwart?", ["Is the car black?"], "interpret"),
                self.create_quiz(interrogative, "Is the car black?", ["Is de auto zwart?"], "write"),
                self.create_quiz(concept, "De auto is zwart.", ["Is de auto zwart"], "make interrogative"),
                self.create_quiz(concept, "Is de auto zwart?", ["De auto is zwart."], "make declarative"),
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
                self.create_quiz(declarative, "Jij rent.", ["You run."], "read"),
                self.create_quiz(declarative, "Jij rent.", ["Jij rent."], "dictate"),
                self.create_quiz(declarative, "Jij rent.", ["You run."], "interpret"),
                self.create_quiz(declarative, "You run.", ["Jij rent."], "write"),
                self.create_quiz(imperative, "Ren!", ["Run!"], "read"),
                self.create_quiz(imperative, "Ren!", ["Ren!"], "dictate"),
                self.create_quiz(imperative, "Ren!", ["Run!"], "interpret"),
                self.create_quiz(imperative, "Run!", ["Ren!"], "write"),
                self.create_quiz(concept, "Jij rent.", ["Ren!"], "make imperative"),
                self.create_quiz(concept, "Ren!", ["Jij rent."], "make declarative"),
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
                self.create_quiz(declarative, "Jij rent.", ["You run."], "read"),
                self.create_quiz(declarative, "Jij rent.", ["Jij rent."], "dictate"),
                self.create_quiz(declarative, "Jij rent.", ["You run."], "interpret"),
                self.create_quiz(declarative, "You run.", ["Jij rent."], "write"),
                self.create_quiz(interrogative, "Ren jij?", ["Ren jij?"], "read"),
                self.create_quiz(interrogative, "Ren jij?", ["Ren jij?"], "dictate"),
                self.create_quiz(interrogative, "Ren jij?", ["Do you run?"], "interpret"),
                self.create_quiz(interrogative, "Do you run?", ["Ren jij?"], "write"),
                self.create_quiz(imperative, "Ren!", ["Run!"], "read"),
                self.create_quiz(imperative, "Ren!", ["Ren!"], "dictate"),
                self.create_quiz(imperative, "Ren!", ["Run!"], "interpret"),
                self.create_quiz(imperative, "Run!", ["Ren!"], "write"),
                self.create_quiz(concept, "Jij rent.", ["Ren!"], "make imperative"),
                self.create_quiz(concept, "Jij rent.", ["Ren jij?"], "make interrogative"),
                self.create_quiz(concept, "Ren!", ["Jij rent."], "make declarative"),
                self.create_quiz(concept, "Ren!", ["Ren jij?"], "make interrogative"),
                self.create_quiz(concept, "Ren jij?", ["Ren!"], "make imperative"),
                self.create_quiz(concept, "Ren jij?", ["Jij rent."], "make declarative"),
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
                self.create_quiz(affirmative, "De auto is zwart.", ["The car is black."], "read"),
                self.create_quiz(affirmative, "De auto is zwart.", ["De auto is zwart."], "dictate"),
                self.create_quiz(affirmative, "De auto is zwart.", ["The cat is black."], "interpret"),
                self.create_quiz(affirmative, "The car is black.", ["De auto is zwart."], "write"),
                self.create_quiz(negative, "De auto is niet zwart.", ["The car is not black."], "read"),
                self.create_quiz(negative, "De auto is niet zwart.", ["De auto is niet zwart."], "dictate"),
                self.create_quiz(negative, "De auto is niet zwart.", ["The car is not black."], "interpret"),
                self.create_quiz(negative, "The car is not black.", ["De auto is niet zwart."], "write"),
                self.create_quiz(concept, "De auto is zwart.", ["De auto is niet zwart."], "negate"),
                self.create_quiz(concept, "De auto is niet zwart.", ["De auto is zwart."], "affirm"),
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
                self.create_quiz(root, "de auto", ["de auto"], "dictate"),
                self.create_quiz(diminutive, "het autootje", ["het autootje"], "dictate"),
                self.create_quiz(concept, "de auto", ["het autootje"], "diminutize"),
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
                self.create_quiz(root, "de auto", ["car"], "read"),
                self.create_quiz(root, "de auto", ["de auto"], "dictate"),
                self.create_quiz(root, "de auto", ["car"], "interpret"),
                self.create_quiz(root, "car", ["de auto"], "write"),
                self.create_quiz(diminutive, "het autootje", ["het autootje"], "dictate"),
                self.create_quiz(concept, "de auto", ["het autootje"], "diminutize"),
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
                self.create_quiz(cardinal, "een", ["een"], "dictate"),
                self.create_quiz(ordinal, "eerste", ["eerste"], "dictate"),
                self.create_quiz(concept, "een", ["eerste"], "make ordinal"),
                self.create_quiz(concept, "eerste", ["een"], "make cardinal"),
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
                self.create_quiz(cardinal, "een", ["one"], "read"),
                self.create_quiz(cardinal, "een", ["een"], "dictate"),
                self.create_quiz(cardinal, "een", ["one"], "interpret"),
                self.create_quiz(cardinal, "one", ["een"], "write"),
                self.create_quiz(ordinal, "eerste", ["first"], "read"),
                self.create_quiz(ordinal, "eerste", ["eerste"], "dictate"),
                self.create_quiz(ordinal, "eerste", ["eerste"], "interpret"),
                self.create_quiz(ordinal, "first", ["eerste"], "write"),
                self.create_quiz(concept, "eerste", ["een"], "make cardinal"),
                self.create_quiz(concept, "een", ["eerste"], "make ordinal"),
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
                self.create_quiz(full_form, "naamloze vennootschap", ["naamloze vennootschap"], "dictate"),
                self.create_quiz(abbreviation, "NV", ["NV"], "dictate"),
                self.create_quiz(concept, "naamloze vennootschap", ["NV"], "abbreviate"),
                self.create_quiz(concept, "NV", ["naamloze vennootschap"], "give full form"),
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
                self.create_quiz(concept, "seitsemän", ["zeven"], "read"),
                self.create_quiz(concept, "seitsemän", ["seitsemän"], "dictate"),
                self.create_quiz(concept, "zeven", ["seitsemän"], "write"),
                self.create_quiz(concept, "seitsemän", ["zeven"], "interpret"),
                self.create_quiz(concept, "seittemän*", ["seitsemän"], "dictate"),
                self.create_quiz(concept, "seittemän*", ["zeven"], "interpret"),
            },
            create_quizzes(FI_NL, concept),
        )
        self.language_pair = NL_FI
        self.assertSetEqual(
            {
                self.create_quiz(concept, "zeven", ["seitsemän"], "read"),
                self.create_quiz(concept, "zeven", ["zeven"], "dictate"),
                self.create_quiz(concept, "seitsemän", ["zeven"], "write"),
                self.create_quiz(concept, "zeven", ["seitsemän"], "interpret"),
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
                self.create_quiz(singular, "kioski", ["kiosk"], "read"),
                self.create_quiz(singular, "kioski", ["kioski"], "dictate"),
                self.create_quiz(singular, "kiosk", ["kioski"], "write"),
                self.create_quiz(singular, "kioski", ["kiosk"], "interpret"),
                self.create_quiz(singular, "kiska*", ["kiosk"], "interpret"),
                self.create_quiz(singular, "kiska*", ["kioski"], "dictate"),
                self.create_quiz(plural, "kioskit", ["kiosks"], "read"),
                self.create_quiz(plural, "kioskit", ["kioskit"], "dictate"),
                self.create_quiz(plural, "kiosks", ["kioskit"], "write"),
                self.create_quiz(plural, "kioskit", ["kiosks"], "interpret"),
                self.create_quiz(plural, "kiskat*", ["kiosks"], "interpret"),
                self.create_quiz(plural, "kiskat*", ["kioskit"], "dictate"),
                self.create_quiz(concept, "kioski", ["kioskit"], "pluralize"),
                self.create_quiz(concept, "kioskit", ["kioski"], "singularize"),
            },
            create_quizzes(FI_EN, concept),
        )
        self.language_pair = EN_FI
        self.assertSetEqual(
            {
                self.create_quiz(singular, "kiosk", ["kioski"], "read"),
                self.create_quiz(singular, "kiosk", ["kiosk"], "dictate"),
                self.create_quiz(singular, "kioski", ["kiosk"], "write"),
                self.create_quiz(singular, "kiosk", ["kioski"], "interpret"),
                self.create_quiz(plural, "kiosks", ["kioskit"], "read"),
                self.create_quiz(plural, "kiosks", ["kiosks"], "dictate"),
                self.create_quiz(plural, "kioskit", ["kiosks"], "write"),
                self.create_quiz(plural, "kiosks", ["kioskit"], "interpret"),
                self.create_quiz(concept, "kiosk", ["kiosks"], "pluralize"),
                self.create_quiz(concept, "kiosks", ["kiosk"], "singularize"),
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
                self.create_quiz(yes, "kylla", ["kylla"], "dictate"),
                self.create_quiz(yes, "kyl*", ["kylla"], "dictate"),
                self.create_quiz(yes, "kylla", ["ei"], "antonym"),
            },
            create_quizzes(FI_EN, yes),
        )
        self.assertSetEqual(
            {
                self.create_quiz(no, "ei", ["ei"], "dictate"),
                self.create_quiz(no, "ei", ["kylla"], "antonym"),
            },
            create_quizzes(FI_EN, no),
        )


class MeaningsTest(ToistoTestCase):
    """Test that quizzes have the correct meaning."""

    def test_interpret_with_synonym(self):
        """Test that interpret quizzes show all synonyms as meaning."""
        concept = self.create_concept("yes", dict(fi=["kylla", "joo"], en="yes"))
        quizzes = create_quizzes(FI_EN, concept)
        interpret_quizzes = [quiz for quiz in quizzes if "interpret" in quiz.quiz_types]
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kylla"), Label(FI, "joo")), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)

    def test_interpret_with_colloquial(self):
        """Test that interpret quizzes don't show colloquial labels as meaning."""
        concept = self.create_concept("20", dict(fi=["kaksikymmentä", "kakskyt*"], nl="twintig"))
        quizzes = create_quizzes(FI_NL, concept)
        interpret_quizzes = [quiz for quiz in quizzes if "interpret" in quiz.quiz_types]
        for quiz in interpret_quizzes:
            self.assertEqual((Label(FI, "kaksikymmentä"),), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)


class GrammaticalQuizTypesTest(QuizFactoryTestCase):
    """Test the grammatical quiz types generator."""

    def test_adjective_with_degrees_of_comparison(self):
        """Test the grammatical quiz types for an adjective with degrees of comparison."""
        positive, comparative, superlative = self.create_adjective_with_degrees_of_comparison().leaf_concepts(EN)
        for concept in (positive, comparative):
            self.assertEqual(("give superlative degree",), grammatical_quiz_types(concept, superlative))
        for concept in (positive, superlative):
            self.assertEqual(("give comparative degree",), grammatical_quiz_types(concept, comparative))
        for concept in (comparative, superlative):
            self.assertEqual(("give positive degree",), grammatical_quiz_types(concept, positive))

    def test_noun_with_grammatical_number(self):
        """Test the grammatical quiz types for a noun with singular and plural form."""
        singular, plural = self.create_noun_with_grammatical_number().leaf_concepts(FI)
        self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
        self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))

    def test_noun_with_grammatical_gender(self):
        """Test the grammatical quiz types for a noun with grammatical gender."""
        female, male = self.create_noun_with_grammatical_gender().leaf_concepts(EN)
        self.assertEqual(("masculinize",), grammatical_quiz_types(female, male))
        self.assertEqual(("feminize",), grammatical_quiz_types(male, female))

    def test_noun_with_grammatical_gender_including_neuter(self):
        """Test the grammatical quiz types for a noun with grammatical gender including neuter."""
        female, male, neuter = self.create_noun_with_grammatical_gender_including_neuter().leaf_concepts(NL)
        for concept in (female, neuter):
            self.assertEqual(("masculinize",), grammatical_quiz_types(concept, male))
        for concept in (female, male):
            self.assertEqual(("neuterize",), grammatical_quiz_types(concept, neuter))
        for concept in (male, neuter):
            self.assertEqual(("feminize",), grammatical_quiz_types(concept, female))

    def test_noun_with_grammatical_number_and_gender(self):
        """Test the grammatical quiz types for a noun with grammatical number and gender."""
        noun = self.create_noun_with_grammatical_number_and_gender()
        singular_female, singular_male, plural_female, plural_male = noun.leaf_concepts(EN)
        for female, male in ((singular_female, singular_male), (plural_female, plural_male)):
            self.assertEqual(("masculinize",), grammatical_quiz_types(female, male))
            self.assertEqual(("feminize",), grammatical_quiz_types(male, female))
        for singular, plural in ((singular_female, plural_female), (singular_male, plural_male)):
            self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
            self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))

    def test_verb_with_person(self):
        """Test the grammatical quiz types for a verb with grammatical person."""
        verb = self.create_verb_with_person()
        first, second, third = verb.leaf_concepts(EN)
        for concept in (first, second):
            self.assertEqual(("give third person",), grammatical_quiz_types(concept, third))
        for concept in (first, third):
            self.assertEqual(("give second person",), grammatical_quiz_types(concept, second))
        for concept in (second, third):
            self.assertEqual(("give first person",), grammatical_quiz_types(concept, first))

    def test_verb_with_tense_and_person(self):
        """Test the grammatical quiz types for a verb with tense and grammatical person."""
        verb = self.create_verb_with_tense_and_person("present tense", "past tense")
        present_singular, present_plural, past_singular, past_plural = verb.leaf_concepts(NL)
        for singular, plural in ((present_singular, present_plural), (past_singular, past_plural)):
            self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
            self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))
        for present, past in ((present_singular, past_singular), (present_plural, past_plural)):
            self.assertEqual(("give past tense",), grammatical_quiz_types(present, past))
            self.assertEqual(("give present tense",), grammatical_quiz_types(past, present))

    def test_verb_with_infinitive_and_person(self):
        """Test the grammatical quiz types for a verb with infinitive and grammatical person."""
        verb = self.create_verb_with_infinitive_and_person()
        infinitive, singular, plural = verb.leaf_concepts(EN)
        for concept in (infinitive, singular):
            self.assertEqual(("pluralize",), grammatical_quiz_types(concept, plural))
        for concept in (infinitive, plural):
            self.assertEqual(("singularize",), grammatical_quiz_types(concept, singular))
        for concept in (singular, plural):
            self.assertEqual(("give infinitive",), grammatical_quiz_types(concept, infinitive))

    def test_verb_with_person_and_number(self):
        """Test the grammatical quiz types for a verb with grammatical person and number."""
        verb = self.create_verb_with_number_and_person()
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
            self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
            self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))
        for first, second in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(("give second person",), grammatical_quiz_types(first, second))
            self.assertEqual(("give first person",), grammatical_quiz_types(second, first))
        for first, third in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(("give third person",), grammatical_quiz_types(first, third))
            self.assertEqual(("give first person",), grammatical_quiz_types(third, first))
        for second, third in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(("give third person",), grammatical_quiz_types(second, third))
            self.assertEqual(("give second person",), grammatical_quiz_types(third, second))

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
            self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
            self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))
            self.assertEqual((), grammatical_quiz_types(infinitive, singular))
            self.assertEqual((), grammatical_quiz_types(infinitive, plural))
        for first, second in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(("give second person",), grammatical_quiz_types(first, second))
            self.assertEqual(("give first person",), grammatical_quiz_types(second, first))
        for first, third in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(("give third person",), grammatical_quiz_types(first, third))
            self.assertEqual(("give first person",), grammatical_quiz_types(third, first))
        for second, third in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(("give third person",), grammatical_quiz_types(second, third))
            self.assertEqual(("give second person",), grammatical_quiz_types(third, second))
