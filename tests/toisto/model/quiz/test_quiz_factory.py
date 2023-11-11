"""Concept unit tests."""

from toisto.model.language.concept_factory import create_concept
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes, grammatical_quiz_types

from ....base import ToistoTestCase


class QuizFactoryTestCase(ToistoTestCase):
    """Base class for quiz factory unit tests."""

    def create_verb_with_person(self):
        """Create a verb with grammatical person."""
        return create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", nl="ik eet"),
                "second person": dict(en="you eat", nl="jij eet"),
                "third person": dict(en="she eats", nl="zij eet"),
            },
        )

    def create_verb_with_tense_and_person(self):
        """Create a verb with grammatical person nested within tense."""
        return create_concept(
            "to eat",
            {
                "present tense": {
                    "singular": dict(en="I eat", nl="ik eet"),
                    "plural": dict(en="we eat", nl="wij eten"),
                },
                "past tense": {
                    "singular": dict(en="I ate", nl="ik at"),
                    "plural": dict(en="we ate", nl="wij aten"),
                },
            },
        )

    def create_verb_with_number_and_person(self):
        """Create a verb with grammatical number nested with grammatical person."""
        return create_concept(
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

    def create_verb_with_infinitive_and_person(self):
        """Create a verb with infinitive and grammatical person."""
        return create_concept(
            "to sleep",
            dict(
                infinitive=dict(en="to sleep", nl="slapen"),
                singular=dict(en="I sleep", nl="ik slaap"),
                plural=dict(en="we sleep", nl="wij slapen"),
            ),
        )

    def create_verb_with_infinitive_and_number_and_person(self):
        """Create a verb with infinitive and grammatical number nested with person."""
        return create_concept(
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

    def create_adjective_with_degrees_of_comparison(self):
        """Create an adjective with degrees of comparison."""
        return create_concept(
            "big",
            {
                "positive degree": dict(en="big", nl="groot"),
                "comparative degree": dict(en="bigger", nl="groter"),
                "superlative degree": dict(en="biggest", nl="grootst"),
            },
        )

    def create_noun(self):
        """Create a simple noun."""
        return create_concept("mall", dict(fi="kauppakeskus", nl="het winkelcentrum"))

    def create_noun_with_grammatical_number(self):
        """Create a noun with grammatical number."""
        return create_concept(
            "morning",
            dict(singular=dict(fi="aamu", nl="de ochtend"), plural=dict(fi="aamut", nl="de ochtenden")),
        )

    def create_noun_with_grammatical_gender(self):
        """Create a noun with grammatical gender."""
        return create_concept(
            "cat",
            dict(female=dict(en="her cat", nl="haar kat"), male=dict(en="his cat", nl="zijn kat")),
        )

    def create_noun_with_grammatical_gender_including_neuter(self):
        """Create a noun with grammatical gender, including neuter."""
        return create_concept(
            "bone",
            dict(
                female=dict(en="her bone", nl="haar bot"),
                male=dict(en="his bone", nl="zijn bot;male"),
                neuter=dict(en="its bone", nl="zijn bot;neuter"),
            ),
        )

    def create_noun_with_grammatical_number_and_gender(self):
        """Create a noun with grammatical number and grammatical gender."""
        return create_concept(
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
        concept = create_concept("english", dict(en="English", nl="Engels"))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "nl", "en", "Engels", ["English"], "read"),
                self.create_quiz(concept, "nl", "nl", "Engels", ["Engels"], "dictate"),
                self.create_quiz(concept, "nl", "en", "Engels", ["English"], "interpret"),
                self.create_quiz(concept, "en", "nl", "English", ["Engels"], "write"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_only_listening_quizzes_for_one_language(self):
        """Test that only listening quizzes are generated for a concept with one language."""
        concept = create_concept("english", dict(nl="Engels"))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "nl", "nl", "Engels", ["Engels"], "dictate"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_answer_only_concept(self):
        """Test that no quizzes are generated for an answer-only concept."""
        concept = create_concept("yes, i do like something", {"answer-only": True, "en": "Yes, I do.", "fi": "Pidän"})
        self.assertSetEqual(Quizzes(), create_quizzes("en", "fi", concept))

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        concept = create_concept("couch", dict(nl=["bank"], en=["couch", "bank"]))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "nl", "en", "bank", ["couch", "bank"], "read"),
                self.create_quiz(concept, "nl", "nl", "bank", ["bank"], "dictate"),
                self.create_quiz(concept, "nl", "en", "bank", ["couch", "bank"], "interpret"),
                self.create_quiz(concept, "en", "nl", "couch", ["bank"], "write"),
                self.create_quiz(concept, "en", "nl", "bank", ["bank"], "write"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_missing_language(self):
        """Test that no quizzes are generated from a concept if it's missing one of the languages."""
        concept = create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertSetEqual(Quizzes(), create_quizzes("fi", "en", concept))

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        concept = self.create_noun_with_grammatical_number()
        singular, plural = concept.leaf_concepts("fi")
        self.assertSetEqual(
            {
                self.create_quiz(singular, "fi", "nl", "aamu", ["de ochtend"], "read"),
                self.create_quiz(singular, "fi", "fi", "aamu", ["aamu"], "dictate"),
                self.create_quiz(singular, "fi", "nl", "aamu", ["de ochtend"], "interpret"),
                self.create_quiz(singular, "nl", "fi", "de ochtend", ["aamu"], "write"),
                self.create_quiz(plural, "fi", "nl", "aamut", ["de ochtenden"], "read"),
                self.create_quiz(plural, "fi", "fi", "aamut", ["aamut"], "dictate"),
                self.create_quiz(plural, "fi", "nl", "aamut", ["de ochtenden"], "interpret"),
                self.create_quiz(plural, "nl", "fi", "de ochtenden", ["aamut"], "write"),
                self.create_quiz(concept, "fi", "fi", "aamu", ["aamut"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "aamut", ["aamu"], "singularize"),
            },
            create_quizzes("fi", "nl", concept),
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        concept = create_concept(
            "ketchup",
            dict(singular=dict(fi="ketsuppi", nl="de ketchup"), plural=dict(fi="ketsupit")),
        )
        singular, plural = concept.leaf_concepts("fi")
        quizzes = create_quizzes("fi", "nl", concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "fi", "nl", "ketsuppi", ["de ketchup"], "read"),
                self.create_quiz(singular, "fi", "fi", "ketsuppi", ["ketsuppi"], "dictate"),
                self.create_quiz(singular, "fi", "nl", "ketsuppi", ["de ketchup"], "interpret"),
                self.create_quiz(singular, "nl", "fi", "de ketchup", ["ketsuppi"], "write"),
                self.create_quiz(plural, "fi", "fi", "ketsupit", ["ketsupit"], "dictate"),
                self.create_quiz(concept, "fi", "fi", "ketsuppi", ["ketsupit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "ketsupit", ["ketsuppi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.question_meanings))
            self.assertNotIn("", (str(meaning) for meaning in quiz.answer_meanings))

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the target language only."""
        concept = create_concept("mämmi", dict(singular=dict(fi="mämmi"), plural=dict(fi="mämmit")))
        singular, plural = concept.leaf_concepts("fi")
        quizzes = create_quizzes("fi", "nl", concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "fi", "fi", "mämmi", ["mämmi"], "dictate"),
                self.create_quiz(plural, "fi", "fi", "mämmit", ["mämmit"], "dictate"),
                self.create_quiz(concept, "fi", "fi", "mämmi", ["mämmit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "mämmit", ["mämmi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.question_meanings))
            self.assertNotIn("", (str(meaning) for meaning in quiz.answer_meanings))

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes are generated from a noun concept with labels in the native language."""
        concept = create_concept("mämmi", dict(singular=dict(fi="mämmi"), plural=dict(fi="mämmit")))
        self.assertSetEqual(Quizzes(), create_quizzes("en", "fi", concept))

    def test_grammatical_number_with_synonyms(self):
        """Test that in case of synonyms the plural of one synonym isn't the correct answer for the other synonym."""
        concept = create_concept(
            "mall",
            dict(
                singular=dict(fi=["kauppakeskus", "ostoskeskus"], nl="het winkelcentrum"),
                plural=dict(fi=["kauppakeskukset", "ostoskeskukset"], nl="de winkelcentra"),
            ),
        )
        singular, plural = concept.leaf_concepts("fi")
        self.assertSetEqual(
            {
                self.create_quiz(singular, "fi", "nl", "kauppakeskus", ["het winkelcentrum"], "read"),
                self.create_quiz(singular, "fi", "nl", "ostoskeskus", ["het winkelcentrum"], "read"),
                self.create_quiz(singular, "fi", "fi", "kauppakeskus", ["kauppakeskus"], "dictate"),
                self.create_quiz(singular, "fi", "nl", "kauppakeskus", ["het winkelcentrum"], "interpret"),
                self.create_quiz(singular, "fi", "fi", "ostoskeskus", ["ostoskeskus"], "dictate"),
                self.create_quiz(singular, "fi", "nl", "ostoskeskus", ["het winkelcentrum"], "interpret"),
                self.create_quiz(singular, "nl", "fi", "het winkelcentrum", ["kauppakeskus", "ostoskeskus"], "write"),
                self.create_quiz(plural, "fi", "nl", "kauppakeskukset", ["de winkelcentra"], "read"),
                self.create_quiz(plural, "fi", "nl", "ostoskeskukset", ["de winkelcentra"], "read"),
                self.create_quiz(plural, "fi", "fi", "kauppakeskukset", ["kauppakeskukset"], "dictate"),
                self.create_quiz(plural, "fi", "nl", "kauppakeskukset", ["de winkelcentra"], "interpret"),
                self.create_quiz(plural, "fi", "fi", "ostoskeskukset", ["ostoskeskukset"], "dictate"),
                self.create_quiz(plural, "fi", "nl", "ostoskeskukset", ["de winkelcentra"], "interpret"),
                self.create_quiz(plural, "nl", "fi", "de winkelcentra", ["kauppakeskukset", "ostoskeskukset"], "write"),
                self.create_quiz(concept, "fi", "fi", "kauppakeskus", ["kauppakeskukset"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "ostoskeskus", ["ostoskeskukset"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "kauppakeskukset", ["kauppakeskus"], "singularize"),
                self.create_quiz(concept, "fi", "fi", "ostoskeskukset", ["ostoskeskus"], "singularize"),
            },
            create_quizzes("fi", "nl", concept),
        )

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender()
        female, male = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(female, "nl", "en", "haar kat", ["her cat"], "read"),
                self.create_quiz(female, "nl", "nl", "haar kat", ["haar kat"], "dictate"),
                self.create_quiz(female, "nl", "en", "haar kat", ["her cat"], "interpret"),
                self.create_quiz(female, "en", "nl", "her cat", ["haar kat"], "write"),
                self.create_quiz(male, "nl", "en", "zijn kat", ["his cat"], "read"),
                self.create_quiz(male, "nl", "nl", "zijn kat", ["zijn kat"], "dictate"),
                self.create_quiz(male, "nl", "en", "zijn kat", ["his cat"], "interpret"),
                self.create_quiz(male, "en", "nl", "his cat", ["zijn kat"], "write"),
                self.create_quiz(concept, "nl", "nl", "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "zijn kat", ["haar kat"], "feminize"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        female, male, neuter = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(female, "nl", "en", "haar bot", ["her bone"], "read"),
                self.create_quiz(female, "nl", "nl", "haar bot", ["haar bot"], "dictate"),
                self.create_quiz(female, "nl", "en", "haar bot", ["her bone"], "interpret"),
                self.create_quiz(female, "en", "nl", "her bone", ["haar bot"], "write"),
                self.create_quiz(male, "nl", "en", "zijn bot", ["his bone"], "read"),
                self.create_quiz(male, "nl", "nl", "zijn bot", ["zijn bot"], "dictate"),
                self.create_quiz(male, "nl", "en", "zijn bot", ["his bone"], "interpret"),
                self.create_quiz(male, "en", "nl", "his bone", ["zijn bot"], "write"),
                self.create_quiz(neuter, "nl", "en", "zijn bot", ["its bone"], "read"),
                self.create_quiz(neuter, "nl", "nl", "zijn bot", ["zijn bot"], "dictate"),
                self.create_quiz(neuter, "nl", "en", "zijn bot", ["its bone"], "interpret"),
                self.create_quiz(neuter, "en", "nl", "its bone", ["zijn bot"], "write"),
                self.create_quiz(concept, "nl", "nl", "haar bot", ["zijn bot"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "haar bot", ["zijn bot"], "neuterize"),
                self.create_quiz(concept, "nl", "nl", "zijn bot", ["haar bot"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "zijn bot", ["haar bot"], "feminize"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        concept = self.create_noun_with_grammatical_number_and_gender()
        singular, plural = concept.constituents
        singular_female, singular_male, plural_female, plural_male = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(singular_female, "nl", "en", "haar kat", ["her cat"], "read"),
                self.create_quiz(singular_female, "nl", "nl", "haar kat", ["haar kat"], "dictate"),
                self.create_quiz(singular_female, "nl", "en", "haar kat", ["her cat"], "interpret"),
                self.create_quiz(singular_female, "en", "nl", "her cat", ["haar kat"], "write"),
                self.create_quiz(singular_male, "nl", "en", "zijn kat", ["his cat"], "read"),
                self.create_quiz(singular_male, "nl", "nl", "zijn kat", ["zijn kat"], "dictate"),
                self.create_quiz(singular_male, "nl", "en", "zijn kat", ["his cat"], "interpret"),
                self.create_quiz(singular_male, "en", "nl", "his cat", ["zijn kat"], "write"),
                self.create_quiz(singular, "nl", "nl", "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(singular, "nl", "nl", "zijn kat", ["haar kat"], "feminize"),
                self.create_quiz(plural_female, "nl", "en", "haar katten", ["her cats"], "read"),
                self.create_quiz(plural_female, "nl", "nl", "haar katten", ["haar katten"], "dictate"),
                self.create_quiz(plural_female, "nl", "en", "haar katten", ["her cats"], "interpret"),
                self.create_quiz(plural_female, "en", "nl", "her cats", ["haar katten"], "write"),
                self.create_quiz(plural_male, "nl", "en", "zijn katten", ["his cats"], "read"),
                self.create_quiz(plural_male, "nl", "nl", "zijn katten", ["zijn katten"], "dictate"),
                self.create_quiz(plural_male, "nl", "en", "zijn katten", ["his cats"], "interpret"),
                self.create_quiz(plural_male, "en", "nl", "his cats", ["zijn katten"], "write"),
                self.create_quiz(plural, "nl", "nl", "haar katten", ["zijn katten"], "masculinize"),
                self.create_quiz(plural, "nl", "nl", "zijn katten", ["haar katten"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "haar kat", ["haar katten"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "haar katten", ["haar kat"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "zijn kat", ["zijn katten"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "zijn katten", ["zijn kat"], "singularize"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = self.create_adjective_with_degrees_of_comparison()
        positive_degree, comparative_degree, superlative_degree = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(positive_degree, "nl", "en", "groot", ["big"], "read"),
                self.create_quiz(positive_degree, "nl", "nl", "groot", ["groot"], "dictate"),
                self.create_quiz(positive_degree, "nl", "en", "groot", ["big"], "interpret"),
                self.create_quiz(positive_degree, "en", "nl", "big", ["groot"], "write"),
                self.create_quiz(comparative_degree, "nl", "en", "groter", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "nl", "nl", "groter", ["groter"], "dictate"),
                self.create_quiz(comparative_degree, "nl", "en", "groter", ["bigger"], "interpret"),
                self.create_quiz(comparative_degree, "en", "nl", "bigger", ["groter"], "write"),
                self.create_quiz(superlative_degree, "nl", "en", "grootst", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "nl", "nl", "grootst", ["grootst"], "dictate"),
                self.create_quiz(superlative_degree, "nl", "en", "grootst", ["biggest"], "interpret"),
                self.create_quiz(superlative_degree, "en", "nl", "biggest", ["grootst"], "write"),
                self.create_quiz(concept, "nl", "nl", "groot", ["groter"], "give comparative degree"),
                self.create_quiz(concept, "nl", "nl", "groot", ["grootst"], "give superlative degree"),
                self.create_quiz(concept, "nl", "nl", "groter", ["groot"], "give positive degree"),
                self.create_quiz(concept, "nl", "nl", "groter", ["grootst"], "give superlative degree"),
                self.create_quiz(concept, "nl", "nl", "grootst", ["groot"], "give positive degree"),
                self.create_quiz(concept, "nl", "nl", "grootst", ["groter"], "give comparative degree"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        concept = create_concept(
            "big",
            {
                "positive degree": dict(en="big", fi=["iso", "suuri"]),
                "comparative degree": dict(en="bigger", fi=["isompi", "suurempi"]),
                "superlative degree": dict(en="biggest", fi=["isoin", "suurin"]),
            },
        )
        positive_degree, comparative_degree, superlative_degree = concept.leaf_concepts("fi")
        self.assertSetEqual(
            {
                self.create_quiz(positive_degree, "fi", "en", "iso", ["big"], "read"),
                self.create_quiz(positive_degree, "fi", "en", "suuri", ["big"], "read"),
                self.create_quiz(positive_degree, "fi", "fi", "iso", ["iso"], "dictate"),
                self.create_quiz(positive_degree, "fi", "en", "iso", ["big"], "interpret"),
                self.create_quiz(positive_degree, "fi", "fi", "suuri", ["suuri"], "dictate"),
                self.create_quiz(positive_degree, "fi", "en", "suuri", ["big"], "interpret"),
                self.create_quiz(positive_degree, "en", "fi", "big", ["iso", "suuri"], "write"),
                self.create_quiz(comparative_degree, "fi", "en", "isompi", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "fi", "en", "suurempi", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "fi", "fi", "isompi", ["isompi"], "dictate"),
                self.create_quiz(comparative_degree, "fi", "en", "isompi", ["bigger"], "interpret"),
                self.create_quiz(comparative_degree, "fi", "fi", "suurempi", ["suurempi"], "dictate"),
                self.create_quiz(comparative_degree, "fi", "en", "suurempi", ["bigger"], "interpret"),
                self.create_quiz(comparative_degree, "en", "fi", "bigger", ["isompi", "suurempi"], "write"),
                self.create_quiz(superlative_degree, "fi", "en", "isoin", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "fi", "en", "suurin", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "fi", "fi", "isoin", ["isoin"], "dictate"),
                self.create_quiz(superlative_degree, "fi", "en", "isoin", ["biggest"], "interpret"),
                self.create_quiz(superlative_degree, "fi", "fi", "suurin", ["suurin"], "dictate"),
                self.create_quiz(superlative_degree, "fi", "en", "suurin", ["biggest"], "interpret"),
                self.create_quiz(superlative_degree, "en", "fi", "biggest", ["isoin", "suurin"], "write"),
                self.create_quiz(concept, "fi", "fi", "iso", ["isompi"], "give comparative degree"),
                self.create_quiz(concept, "fi", "fi", "suuri", ["suurempi"], "give comparative degree"),
                self.create_quiz(concept, "fi", "fi", "iso", ["isoin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "suuri", ["suurin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "isompi", ["iso"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "suurempi", ["suuri"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "isompi", ["isoin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "suurempi", ["suurin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "isoin", ["iso"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "suurin", ["suuri"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "isoin", ["isompi"], "give comparative degree"),
                self.create_quiz(concept, "fi", "fi", "suurin", ["suurempi"], "give comparative degree"),
            },
            create_quizzes("fi", "en", concept),
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = self.create_verb_with_person()
        first_person, second_person, third_person = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "nl", "en", "ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "nl", "nl", "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(first_person, "nl", "en", "ik eet", ["I eat"], "interpret"),
                self.create_quiz(first_person, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(second_person, "nl", "en", "jij eet", ["you eat"], "read"),
                self.create_quiz(second_person, "nl", "nl", "jij eet", ["jij eet"], "dictate"),
                self.create_quiz(second_person, "nl", "en", "jij eet", ["you eat"], "interpret"),
                self.create_quiz(second_person, "en", "nl", "you eat", ["jij eet"], "write"),
                self.create_quiz(third_person, "nl", "en", "zij eet", ["she eats"], "read"),
                self.create_quiz(third_person, "nl", "nl", "zij eet", ["zij eet"], "dictate"),
                self.create_quiz(third_person, "nl", "en", "zij eet", ["she eats"], "interpret"),
                self.create_quiz(third_person, "en", "nl", "she eats", ["zij eet"], "write"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["jij eet"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["zij eet"], "give third person"),
                self.create_quiz(concept, "nl", "nl", "jij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "jij eet", ["zij eet"], "give third person"),
                self.create_quiz(concept, "nl", "nl", "zij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "zij eet", ["jij eet"], "give second person"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        concept = create_concept(
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
                self.create_quiz(first_person, "nl", "en", "ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "nl", "nl", "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(first_person, "nl", "en", "ik eet", ["I eat"], "interpret"),
                self.create_quiz(first_person, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(second_person, "nl", "en", "jij eet", ["you eat"], "read"),
                self.create_quiz(second_person, "nl", "nl", "jij eet", ["jij eet"], "dictate"),
                self.create_quiz(second_person, "nl", "en", "jij eet", ["you eat"], "interpret"),
                self.create_quiz(second_person, "en", "nl", "you eat", ["jij eet"], "write"),
                self.create_quiz(third_person_female, "nl", "en", "zij eet", ["she eats"], "read"),
                self.create_quiz(third_person_female, "nl", "nl", "zij eet", ["zij eet"], "dictate"),
                self.create_quiz(third_person_female, "nl", "en", "zij eet", ["she eats"], "interpret"),
                self.create_quiz(third_person_female, "en", "nl", "she eats", ["zij eet"], "write"),
                self.create_quiz(third_person_male, "nl", "en", "hij eet", ["he eats"], "read"),
                self.create_quiz(third_person_male, "nl", "nl", "hij eet", ["hij eet"], "dictate"),
                self.create_quiz(third_person_male, "nl", "en", "hij eet", ["he eats"], "interpret"),
                self.create_quiz(third_person_male, "en", "nl", "he eats", ["hij eet"], "write"),
                self.create_quiz(third_person, "nl", "nl", "zij eet", ["hij eet"], "masculinize"),
                self.create_quiz(third_person, "nl", "nl", "hij eet", ["zij eet"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["jij eet"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["zij eet"], ("give third person", "feminize")),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["hij eet"], ("give third person", "masculinize")),
                self.create_quiz(concept, "nl", "nl", "jij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "jij eet", ["zij eet"], ("give third person", "feminize")),
                self.create_quiz(concept, "nl", "nl", "jij eet", ["hij eet"], ("give third person", "masculinize")),
                self.create_quiz(concept, "nl", "nl", "zij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "zij eet", ["jij eet"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "hij eet", ["ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "hij eet", ["jij eet"], "give second person"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_grammatical_person_nested_with_grammatical_gender_in_one_language_but_not_the_other(self):
        """Test quizzes for grammatical person nested with grammatical gender in one language but not the other."""
        concept = create_concept(
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
                self.create_quiz(first_person, "fi", "en", "minä syön", ["I eat"], "read"),
                self.create_quiz(first_person, "fi", "fi", "minä syön", ["minä syön"], "dictate"),
                self.create_quiz(first_person, "fi", "en", "minä syön", ["I eat"], "interpret"),
                self.create_quiz(first_person, "en", "fi", "I eat", ["minä syön"], "write"),
                self.create_quiz(second_person, "fi", "en", "sinä syöt", ["you eat"], "read"),
                self.create_quiz(second_person, "fi", "fi", "sinä syöt", ["sinä syöt"], "dictate"),
                self.create_quiz(second_person, "fi", "en", "sinä syöt", ["you eat"], "interpret"),
                self.create_quiz(second_person, "en", "fi", "you eat", ["sinä syöt"], "write"),
                self.create_quiz(third_person, "fi", "en", "hän syö", ["she eats", "he eats"], "read"),
                self.create_quiz(third_person, "fi", "fi", "hän syö", ["hän syö"], "dictate"),
                self.create_quiz(third_person, "fi", "en", "hän syö", ["she eats", "he eats"], "interpret"),
                self.create_quiz(third_person, "en", "fi", "she eats", ["hän syö"], "write"),
                self.create_quiz(third_person, "en", "fi", "he eats", ["hän syö"], "write"),
                self.create_quiz(concept, "fi", "fi", "minä syön", ["sinä syöt"], "give second person"),
                self.create_quiz(concept, "fi", "fi", "minä syön", ["hän syö"], "give third person"),
                self.create_quiz(concept, "fi", "fi", "sinä syöt", ["minä syön"], "give first person"),
                self.create_quiz(concept, "fi", "fi", "sinä syöt", ["hän syö"], "give third person"),
                self.create_quiz(concept, "fi", "fi", "hän syö", ["minä syön"], "give first person"),
                self.create_quiz(concept, "fi", "fi", "hän syö", ["sinä syöt"], "give second person"),
            },
            create_quizzes("fi", "en", concept),
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = self.create_verb_with_number_and_person()
        singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "nl", "fi", "ik heb", ["minulla on"], "read"),
                self.create_quiz(first_person_singular, "fi", "nl", "minulla on", ["ik heb"], "write"),
                self.create_quiz(first_person_singular, "nl", "nl", "ik heb", ["ik heb"], "dictate"),
                self.create_quiz(first_person_singular, "nl", "fi", "ik heb", ["minulla on"], "interpret"),
                self.create_quiz(second_person_singular, "nl", "fi", "jij hebt", ["sinulla on"], "read"),
                self.create_quiz(second_person_singular, "fi", "nl", "sinulla on", ["jij hebt"], "write"),
                self.create_quiz(second_person_singular, "nl", "nl", "jij hebt", ["jij hebt"], "dictate"),
                self.create_quiz(second_person_singular, "nl", "fi", "jij hebt", ["sinulla on"], "interpret"),
                self.create_quiz(third_person_singular, "nl", "fi", "zij heeft", ["hänellä on"], "read"),
                self.create_quiz(third_person_singular, "fi", "nl", "hänellä on", ["zij heeft"], "write"),
                self.create_quiz(third_person_singular, "nl", "nl", "zij heeft", ["zij heeft"], "dictate"),
                self.create_quiz(third_person_singular, "nl", "fi", "zij heeft", ["hänellä on"], "interpret"),
                self.create_quiz(singular, "nl", "nl", "ik heb", ["jij hebt"], "give second person"),
                self.create_quiz(singular, "nl", "nl", "ik heb", ["zij heeft"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "jij hebt", ["ik heb"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "jij hebt", ["zij heeft"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "zij heeft", ["ik heb"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "zij heeft", ["jij hebt"], "give second person"),
                self.create_quiz(first_person_plural, "nl", "fi", "wij hebben", ["meillä on"], "read"),
                self.create_quiz(first_person_plural, "fi", "nl", "meillä on", ["wij hebben"], "write"),
                self.create_quiz(first_person_plural, "nl", "nl", "wij hebben", ["wij hebben"], "dictate"),
                self.create_quiz(first_person_plural, "nl", "fi", "wij hebben", ["meillä on"], "interpret"),
                self.create_quiz(second_person_plural, "nl", "fi", "jullie hebben", ["teillä on"], "read"),
                self.create_quiz(second_person_plural, "fi", "nl", "teillä on", ["jullie hebben"], "write"),
                self.create_quiz(second_person_plural, "nl", "nl", "jullie hebben", ["jullie hebben"], "dictate"),
                self.create_quiz(second_person_plural, "nl", "fi", "jullie hebben", ["teillä on"], "interpret"),
                self.create_quiz(third_person_plural, "nl", "fi", "zij hebben", ["heillä on"], "read"),
                self.create_quiz(third_person_plural, "fi", "nl", "heillä on", ["zij hebben"], "write"),
                self.create_quiz(third_person_plural, "nl", "nl", "zij hebben", ["zij hebben"], "dictate"),
                self.create_quiz(third_person_plural, "nl", "fi", "zij hebben", ["heillä on"], "interpret"),
                self.create_quiz(plural, "nl", "nl", "wij hebben", ["jullie hebben"], "give second person"),
                self.create_quiz(plural, "nl", "nl", "wij hebben", ["zij hebben"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "jullie hebben", ["wij hebben"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "jullie hebben", ["zij hebben"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "zij hebben", ["wij hebben"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "zij hebben", ["jullie hebben"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "ik heb", ["wij hebben"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "wij hebben", ["ik heb"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "jij hebt", ["jullie hebben"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "jullie hebben", ["jij hebt"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "zij heeft", ["zij hebben"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "zij hebben", ["zij heeft"], "singularize"),
            },
            create_quizzes("nl", "fi", concept),
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        concept = create_concept(
            "cat",
            dict(
                female=dict(singular=dict(en="her cat", nl="haar kat"), plural=dict(en="her cats", nl="haar katten")),
                male=dict(singular=dict(en="his cat", nl="zijn kat"), plural=dict(en="his cats", nl="zijn katten")),
            ),
        )
        female, male = concept.constituents
        female_singular, female_plural, male_singular, male_plural = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(female_singular, "nl", "en", "haar kat", ["her cat"], "read"),
                self.create_quiz(female_singular, "nl", "nl", "haar kat", ["haar kat"], "dictate"),
                self.create_quiz(female_singular, "nl", "en", "haar kat", ["her cat"], "interpret"),
                self.create_quiz(female_singular, "en", "nl", "her cat", ["haar kat"], "write"),
                self.create_quiz(female_plural, "nl", "en", "haar katten", ["her cats"], "read"),
                self.create_quiz(female_plural, "nl", "nl", "haar katten", ["haar katten"], "dictate"),
                self.create_quiz(female_plural, "nl", "en", "haar katten", ["her cats"], "interpret"),
                self.create_quiz(female_plural, "en", "nl", "her cats", ["haar katten"], "write"),
                self.create_quiz(female, "nl", "nl", "haar kat", ["haar katten"], "pluralize"),
                self.create_quiz(female, "nl", "nl", "haar katten", ["haar kat"], "singularize"),
                self.create_quiz(male_singular, "nl", "en", "zijn kat", ["his cat"], "read"),
                self.create_quiz(male_singular, "nl", "nl", "zijn kat", ["zijn kat"], "dictate"),
                self.create_quiz(male_singular, "nl", "en", "zijn kat", ["his cat"], "interpret"),
                self.create_quiz(male_singular, "en", "nl", "his cat", ["zijn kat"], "write"),
                self.create_quiz(male_plural, "nl", "en", "zijn katten", ["his cats"], "read"),
                self.create_quiz(male_plural, "nl", "nl", "zijn katten", ["zijn katten"], "dictate"),
                self.create_quiz(male_plural, "nl", "en", "zijn katten", ["his cats"], "interpret"),
                self.create_quiz(male_plural, "en", "nl", "his cats", ["zijn katten"], "write"),
                self.create_quiz(male, "nl", "nl", "zijn kat", ["zijn katten"], "pluralize"),
                self.create_quiz(male, "nl", "nl", "zijn katten", ["zijn kat"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "zijn kat", ["haar kat"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "haar katten", ["zijn katten"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "zijn katten", ["haar katten"], "feminize"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        concept = create_concept(
            "to be",
            dict(female=dict(en="she is|she's", fi="hän on;female"), male=dict(en="he is|he's", fi="hän on;male")),
        )
        female, male = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(female, "fi", "en", Label("hän on;female"), ("she is|she's",), "read"),
                self.create_quiz(female, "fi", "fi", "hän on;female", ("hän on;female",), "dictate"),
                self.create_quiz(female, "fi", "en", "hän on;female", ("she is|she's",), "interpret"),
                self.create_quiz(female, "en", "fi", "she is|she's", ("hän on;female",), "write"),
                self.create_quiz(male, "fi", "en", "hän on;male", ("he is|he's",), "read"),
                self.create_quiz(male, "en", "fi", "he is|he's", ("hän on;male",), "write"),
            },
            create_quizzes("fi", "en", concept),
        )

    def test_infinitive_verb_form(self):
        """Test the infinitive verb form."""
        concept = self.create_verb_with_infinitive_and_person()
        infinitive, singular, plural = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(infinitive, "nl", "en", "slapen", ["to sleep"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "slapen", ["slapen"], "dictate"),
                self.create_quiz(infinitive, "nl", "en", "slapen", ["to sleep"], "interpret"),
                self.create_quiz(infinitive, "en", "nl", "to sleep", ["slapen"], "write"),
                self.create_quiz(singular, "nl", "en", "ik slaap", ["I sleep"], "read"),
                self.create_quiz(singular, "nl", "nl", "ik slaap", ["ik slaap"], "dictate"),
                self.create_quiz(singular, "nl", "en", "ik slaap", ["I sleep"], "interpret"),
                self.create_quiz(singular, "en", "nl", "I sleep", ["ik slaap"], "write"),
                self.create_quiz(plural, "nl", "en", "wij slapen", ["we sleep"], "read"),
                self.create_quiz(plural, "nl", "nl", "wij slapen", ["wij slapen"], "dictate"),
                self.create_quiz(plural, "nl", "en", "wij slapen", ["we sleep"], "interpret"),
                self.create_quiz(plural, "en", "nl", "we sleep", ["wij slapen"], "write"),
                self.create_quiz(concept, "nl", "nl", "wij slapen", ["slapen"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "ik slaap", ["slapen"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "slapen", ["wij slapen"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "ik slaap", ["wij slapen"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "slapen", ["ik slaap"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "wij slapen", ["ik slaap"], "singularize"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_grammatical_number_nested_with_grammatical_person_and_infinitive(self):
        """Test generating quizzes for grammatical number, including infinitive, nested with grammatical person."""
        concept = self.create_verb_with_infinitive_and_number_and_person()
        infinitive, singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "nl", "fi", "ik ben", ["minä olen"], "read"),
                self.create_quiz(first_person_singular, "nl", "nl", "ik ben", ["ik ben"], "dictate"),
                self.create_quiz(first_person_singular, "nl", "fi", "ik ben", ["minä olen"], "interpret"),
                self.create_quiz(first_person_singular, "fi", "nl", "minä olen", ["ik ben"], "write"),
                self.create_quiz(concept, "nl", "nl", "ik ben", ["zijn"], "give infinitive"),
                self.create_quiz(second_person_singular, "nl", "fi", "jij bent", ["sinä olet"], "read"),
                self.create_quiz(second_person_singular, "nl", "nl", "jij bent", ["jij bent"], "dictate"),
                self.create_quiz(second_person_singular, "nl", "fi", "jij bent", ["sinä olet"], "interpret"),
                self.create_quiz(second_person_singular, "fi", "nl", "sinä olet", ["jij bent"], "write"),
                self.create_quiz(concept, "nl", "nl", "jij bent", ["zijn"], "give infinitive"),
                self.create_quiz(third_person_singular, "nl", "fi", "zij is", ["hän on"], "read"),
                self.create_quiz(third_person_singular, "nl", "nl", "zij is", ["zij is"], "dictate"),
                self.create_quiz(third_person_singular, "nl", "fi", "zij is", ["hän on"], "interpret"),
                self.create_quiz(third_person_singular, "fi", "nl", "hän on", ["zij is"], "write"),
                self.create_quiz(concept, "nl", "nl", "zij is", ["zijn"], "give infinitive"),
                self.create_quiz(singular, "nl", "nl", "ik ben", ["jij bent"], "give second person"),
                self.create_quiz(singular, "nl", "nl", "ik ben", ["zij is"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "jij bent", ["ik ben"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "jij bent", ["zij is"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "zij is", ["ik ben"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "zij is", ["jij bent"], "give second person"),
                self.create_quiz(first_person_plural, "nl", "fi", "wij zijn", ["me olemme"], "read"),
                self.create_quiz(first_person_plural, "nl", "nl", "wij zijn", ["wij zijn"], "dictate"),
                self.create_quiz(first_person_plural, "nl", "fi", "wij zijn", ["me olemme"], "interpret"),
                self.create_quiz(first_person_plural, "fi", "nl", "me olemme", ["wij zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "wij zijn", ["zijn"], "give infinitive"),
                self.create_quiz(second_person_plural, "nl", "fi", "jullie zijn", ["te olette"], "read"),
                self.create_quiz(second_person_plural, "nl", "nl", "jullie zijn", ["jullie zijn"], "dictate"),
                self.create_quiz(second_person_plural, "nl", "fi", "jullie zijn", ["te olette"], "interpret"),
                self.create_quiz(second_person_plural, "fi", "nl", "te olette", ["jullie zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "jullie zijn", ["zijn"], "give infinitive"),
                self.create_quiz(third_person_plural, "nl", "fi", "zij zijn", ["he ovat"], "read"),
                self.create_quiz(third_person_plural, "nl", "nl", "zij zijn", ["zij zijn"], "dictate"),
                self.create_quiz(third_person_plural, "nl", "fi", "zij zijn", ["he ovat"], "interpret"),
                self.create_quiz(third_person_plural, "fi", "nl", "he ovat", ["zij zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "zij zijn", ["zijn"], "give infinitive"),
                self.create_quiz(plural, "nl", "nl", "wij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(plural, "nl", "nl", "wij zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "jullie zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "jullie zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "zij zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "zij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "ik ben", ["wij zijn"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "wij zijn", ["ik ben"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "jij bent", ["jullie zijn"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "jullie zijn", ["jij bent"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "zij is", ["zij zijn"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "zij zijn", ["zij is"], "singularize"),
                self.create_quiz(infinitive, "nl", "fi", "zijn", ["olla"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "zijn", ["zijn"], "dictate"),
                self.create_quiz(infinitive, "nl", "fi", "zijn", ["olla"], "interpret"),
                self.create_quiz(infinitive, "fi", "nl", "olla", ["zijn"], "write"),
            },
            create_quizzes("nl", "fi", concept),
        )

    def test_tense_nested_with_grammatical_number_nested_and_grammatical_person(self):
        """Test generating quizzes for tense, grammatical number, and grammatical person."""
        concept = create_concept(
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
                self.create_quiz(first_singular_present, "nl", "fi", "ik ben", ["minä olen"], "read"),
                self.create_quiz(first_singular_present, "nl", "nl", "ik ben", ["ik ben"], "dictate"),
                self.create_quiz(first_singular_present, "nl", "fi", "ik ben", ["minä olen"], "interpret"),
                self.create_quiz(first_singular_present, "fi", "nl", "minä olen", ["ik ben"], "write"),
                self.create_quiz(second_singular_present, "nl", "fi", "jij bent", ["sinä olet"], "read"),
                self.create_quiz(second_singular_present, "nl", "nl", "jij bent", ["jij bent"], "dictate"),
                self.create_quiz(second_singular_present, "nl", "fi", "jij bent", ["sinä olet"], "interpret"),
                self.create_quiz(second_singular_present, "fi", "nl", "sinä olet", ["jij bent"], "write"),
                self.create_quiz(third_singular_present, "nl", "fi", "zij is", ["hän on"], "read"),
                self.create_quiz(third_singular_present, "nl", "nl", "zij is", ["zij is"], "dictate"),
                self.create_quiz(third_singular_present, "nl", "fi", "zij is", ["hän on"], "interpret"),
                self.create_quiz(third_singular_present, "fi", "nl", "hän on", ["zij is"], "write"),
                self.create_quiz(singular_present, "nl", "nl", "ik ben", ["jij bent"], "give second person"),
                self.create_quiz(singular_present, "nl", "nl", "ik ben", ["zij is"], "give third person"),
                self.create_quiz(singular_present, "nl", "nl", "jij bent", ["ik ben"], "give first person"),
                self.create_quiz(singular_present, "nl", "nl", "jij bent", ["zij is"], "give third person"),
                self.create_quiz(singular_present, "nl", "nl", "zij is", ["ik ben"], "give first person"),
                self.create_quiz(singular_present, "nl", "nl", "zij is", ["jij bent"], "give second person"),
                self.create_quiz(first_plural_present, "nl", "fi", "wij zijn", ["me olemme"], "read"),
                self.create_quiz(first_plural_present, "nl", "nl", "wij zijn", ["wij zijn"], "dictate"),
                self.create_quiz(first_plural_present, "nl", "fi", "wij zijn", ["me olemme"], "interpret"),
                self.create_quiz(first_plural_present, "fi", "nl", "me olemme", ["wij zijn"], "write"),
                self.create_quiz(second_plural_present, "nl", "fi", "jullie zijn", ["te olette"], "read"),
                self.create_quiz(second_plural_present, "nl", "nl", "jullie zijn", ["jullie zijn"], "dictate"),
                self.create_quiz(second_plural_present, "nl", "fi", "jullie zijn", ["te olette"], "interpret"),
                self.create_quiz(second_plural_present, "fi", "nl", "te olette", ["jullie zijn"], "write"),
                self.create_quiz(third_plural_present, "nl", "fi", "zij zijn", ["he ovat"], "read"),
                self.create_quiz(third_plural_present, "nl", "nl", "zij zijn", ["zij zijn"], "dictate"),
                self.create_quiz(third_plural_present, "nl", "fi", "zij zijn", ["he ovat"], "interpret"),
                self.create_quiz(third_plural_present, "fi", "nl", "he ovat", ["zij zijn"], "write"),
                self.create_quiz(plural_present, "nl", "nl", "wij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(plural_present, "nl", "nl", "wij zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural_present, "nl", "nl", "jullie zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural_present, "nl", "nl", "jullie zijn", ["zij zijn"], "give third person"),
                self.create_quiz(plural_present, "nl", "nl", "zij zijn", ["wij zijn"], "give first person"),
                self.create_quiz(plural_present, "nl", "nl", "zij zijn", ["jullie zijn"], "give second person"),
                self.create_quiz(present, "nl", "nl", "ik ben", ["wij zijn"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "jij bent", ["jullie zijn"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "zij is", ["zij zijn"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "wij zijn", ["ik ben"], "singularize"),
                self.create_quiz(present, "nl", "nl", "jullie zijn", ["jij bent"], "singularize"),
                self.create_quiz(present, "nl", "nl", "zij zijn", ["zij is"], "singularize"),
                self.create_quiz(first_singular_past, "nl", "fi", "ik was", ["minä olin"], "read"),
                self.create_quiz(first_singular_past, "nl", "nl", "ik was", ["ik was"], "dictate"),
                self.create_quiz(first_singular_past, "nl", "fi", "ik was", ["minä olin"], "interpret"),
                self.create_quiz(first_singular_past, "fi", "nl", "minä olin", ["ik was"], "write"),
                self.create_quiz(second_singular_past, "nl", "fi", "jij was", ["sinä olot"], "read"),
                self.create_quiz(second_singular_past, "nl", "nl", "jij was", ["jij was"], "dictate"),
                self.create_quiz(second_singular_past, "nl", "fi", "jij was", ["sinä olit"], "interpret"),
                self.create_quiz(second_singular_past, "fi", "nl", "sinä olit", ["jij was"], "write"),
                self.create_quiz(third_singular_past, "nl", "fi", "zij was", ["hän oli"], "read"),
                self.create_quiz(third_singular_past, "nl", "nl", "zij was", ["zij was"], "dictate"),
                self.create_quiz(third_singular_past, "nl", "fi", "zij was", ["hän oli"], "interpret"),
                self.create_quiz(third_singular_past, "fi", "nl", "hän oli", ["zij was"], "write"),
                self.create_quiz(singular_past, "nl", "nl", "ik was", ["jij was"], "give second person"),
                self.create_quiz(singular_past, "nl", "nl", "ik was", ["zij was"], "give third person"),
                self.create_quiz(singular_past, "nl", "nl", "jij was", ["ik was"], "give first person"),
                self.create_quiz(singular_past, "nl", "nl", "jij was", ["zij was"], "give third person"),
                self.create_quiz(singular_past, "nl", "nl", "zij was", ["ik was"], "give first person"),
                self.create_quiz(singular_past, "nl", "nl", "zij was", ["jij was"], "give second person"),
                self.create_quiz(first_plural_past, "nl", "fi", "wij waren", ["me olimme"], "read"),
                self.create_quiz(first_plural_past, "nl", "nl", "wij waren", ["wij waren"], "dictate"),
                self.create_quiz(first_plural_past, "nl", "fi", "wij waren", ["me olimme"], "interpret"),
                self.create_quiz(first_plural_past, "fi", "nl", "me olimme", ["wij waren"], "write"),
                self.create_quiz(second_plural_past, "nl", "fi", "jullie waren", ["te olitte"], "read"),
                self.create_quiz(second_plural_past, "nl", "nl", "jullie waren", ["jullie waren"], "dictate"),
                self.create_quiz(second_plural_past, "nl", "fi", "jullie waren", ["te olitte"], "interpret"),
                self.create_quiz(second_plural_past, "fi", "nl", "te olitte", ["jullie waren"], "write"),
                self.create_quiz(third_plural_past, "nl", "fi", "zij waren", ["he olivat"], "read"),
                self.create_quiz(third_plural_past, "nl", "nl", "zij waren", ["zij waren"], "dictate"),
                self.create_quiz(third_plural_past, "nl", "fi", "zij waren", ["he olivät"], "interpret"),
                self.create_quiz(third_plural_past, "fi", "nl", "he olivat", ["zij waren"], "write"),
                self.create_quiz(plural_past, "nl", "nl", "wij waren", ["jullie waren"], "give second person"),
                self.create_quiz(plural_past, "nl", "nl", "wij waren", ["zij waren"], "give third person"),
                self.create_quiz(plural_past, "nl", "nl", "jullie waren", ["wij waren"], "give first person"),
                self.create_quiz(plural_past, "nl", "nl", "jullie waren", ["zij waren"], "give third person"),
                self.create_quiz(plural_past, "nl", "nl", "zij waren", ["wij waren"], "give first person"),
                self.create_quiz(plural_past, "nl", "nl", "zij waren", ["jullie waren"], "give second person"),
                self.create_quiz(past, "nl", "nl", "ik was", ["wij waren"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "jij was", ["jullie waren"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "zij was", ["zij waren"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "wij waren", ["ik was"], "singularize"),
                self.create_quiz(past, "nl", "nl", "jullie waren", ["jij was"], "singularize"),
                self.create_quiz(past, "nl", "nl", "zij waren", ["zij was"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "ik ben", ["ik was"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "jij bent", ["jij was"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "zij is", ["zij was"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "wij zijn", ["wij waren"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "jullie zijn", ["jullie waren"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "zij zijn", ["zij waren"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "ik was", ["ik ben"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "jij was", ["jij bent"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "zij was", ["zij is"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "wij waren", ["wij zijn"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "jullie waren", ["jullie zijn"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "zij waren", ["zij zijn"], "give present tense"),
            },
            create_quizzes("nl", "fi", concept),
        )


class TenseQuizzesTest(QuizFactoryTestCase):
    """Unit tests for concepts with tenses."""

    def test_tense_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for tense nested with grammatical person."""
        concept = self.create_verb_with_tense_and_person()
        present, past = concept.constituents
        present_singular, present_plural, past_singular, past_plural = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(present_singular, "nl", "en", "ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "nl", "nl", "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(present_singular, "nl", "en", "ik eet", ["I eat"], "interpret"),
                self.create_quiz(present_singular, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "nl", "en", "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "nl", "nl", "wij eten", ["wij eten"], "dictate"),
                self.create_quiz(present_plural, "nl", "en", "wij eten", ["we eat"], "interpret"),
                self.create_quiz(present_plural, "en", "nl", "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "nl", "nl", "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "nl", "en", "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "nl", "nl", "ik at", ["ik at"], "dictate"),
                self.create_quiz(past_singular, "nl", "en", "ik at", ["I ate"], "interpret"),
                self.create_quiz(past_singular, "en", "nl", "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "nl", "en", "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "nl", "nl", "wij aten", ["wij aten"], "dictate"),
                self.create_quiz(past_plural, "nl", "en", "wij aten", ["we ate"], "interpret"),
                self.create_quiz(past_plural, "en", "nl", "we ate", ["wij aten"], "write"),
                self.create_quiz(past, "nl", "nl", "ik at", ["wij aten"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "wij aten", ["ik at"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["ik at"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "wij eten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "ik at", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "wij aten", ["wij eten"], "give present tense"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_tense_nested_with_grammatical_person_and_infinitive(self):
        """Test that quizzes can be generated for tense nested with grammatical person and infinitive."""
        concept = create_concept(
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
                self.create_quiz(present_singular, "nl", "en", "ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "nl", "nl", "ik eet", ["ik eet"], "dictate"),
                self.create_quiz(present_singular, "nl", "en", "ik eet", ["I eat"], "interpret"),
                self.create_quiz(present_singular, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "nl", "en", "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "nl", "nl", "wij eten", ["wij eten"], "dictate"),
                self.create_quiz(present_plural, "nl", "en", "wij eten", ["we eat"], "interpret"),
                self.create_quiz(present_plural, "en", "nl", "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "nl", "nl", "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "nl", "en", "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "nl", "nl", "ik at", ["ik at"], "dictate"),
                self.create_quiz(past_singular, "nl", "en", "ik at", ["I ate"], "interpret"),
                self.create_quiz(past_singular, "en", "nl", "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "nl", "en", "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "nl", "nl", "wij aten", ["wij aten"], "dictate"),
                self.create_quiz(past_plural, "nl", "en", "wij aten", ["we ate"], "interpret"),
                self.create_quiz(past_plural, "en", "nl", "we ate", ["wij aten"], "write"),
                self.create_quiz(past, "nl", "nl", "ik at", ["wij aten"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "wij aten", ["ik at"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["ik at"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "wij eten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "ik at", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "wij aten", ["wij eten"], "give present tense"),
                self.create_quiz(infinitive, "nl", "en", "eten", ["to eat"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "eten", ["eten"], "dictate"),
                self.create_quiz(infinitive, "nl", "en", "eten", ["to eat"], "interpret"),
                self.create_quiz(infinitive, "en", "nl", "to eat", ["eten"], "write"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["eten"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "wij eten", ["eten"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "ik at", ["eten"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "wij aten", ["eten"], "give infinitive"),
            },
            create_quizzes("nl", "en", concept),
        )


class SentenceFormTest(ToistoTestCase):
    """Unit tests for concepts with different sentence forms."""

    def test_declarative_and_interrogative_sentence_types(self):
        """Test that quizzes can be generated for the declarative and interrogative sentence forms."""
        concept = create_concept(
            "car",
            {
                "declarative": dict(en="The car is black.", nl="De auto is zwart."),
                "interrogative": dict(en="Is the car black?", nl="Is de auto zwart?"),
            },
        )
        declarative, interrogative = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(declarative, "nl", "en", "De auto is zwart.", ["The car is black."], "read"),
                self.create_quiz(declarative, "nl", "nl", "De auto is zwart.", ["De auto is zwart."], "dictate"),
                self.create_quiz(declarative, "nl", "en", "De auto is zwart.", ["The car is black."], "interpret"),
                self.create_quiz(declarative, "en", "nl", "The car is black.", ["De auto is zwart."], "write"),
                self.create_quiz(interrogative, "nl", "en", "Is de auto zwart?", ["Is the car black?"], "read"),
                self.create_quiz(interrogative, "nl", "nl", "Is de auto zwart?", ["Is de auto zwart?"], "dictate"),
                self.create_quiz(interrogative, "nl", "en", "Is de auto zwart?", ["Is the cat black?"], "interpret"),
                self.create_quiz(interrogative, "en", "nl", "Is the car black?", ["Is de auto zwart?"], "write"),
                self.create_quiz(concept, "nl", "nl", "De auto is zwart.", ["Is de auto zwart"], "make interrogative"),
                self.create_quiz(concept, "nl", "nl", "Is de auto zwart?", ["De auto is zwart."], "make declarative"),
            },
            create_quizzes("nl", "en", concept),
        )


class GrammaticalPolarityTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical polarities."""

    def test_affirmative_and_negative_polarities(self):
        """Test that quizzes can be generated for the affirmative and negative polarities."""
        concept = create_concept(
            "car",
            {
                "affirmative": dict(en="The car is black.", nl="De auto is zwart."),
                "negative": dict(en="The car is not black.", nl="De auto is niet zwart."),
            },
        )
        affirmative, negative = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(affirmative, "nl", "en", "De auto is zwart.", ["The car is black."], "read"),
                self.create_quiz(affirmative, "nl", "nl", "De auto is zwart.", ["De auto is zwart."], "dictate"),
                self.create_quiz(affirmative, "nl", "en", "De auto is zwart.", ["The cat is black."], "interpret"),
                self.create_quiz(affirmative, "en", "nl", "The car is black.", ["De auto is zwart."], "write"),
                self.create_quiz(negative, "nl", "en", "De auto is niet zwart.", ["The car is not black."], "read"),
                self.create_quiz(negative, "nl", "nl", "De auto is niet zwart.", ["De auto is niet zwart."], "dictate"),
                self.create_quiz(
                    negative,
                    "nl",
                    "en",
                    "De auto is niet zwart.",
                    ["The car is not black."],
                    "interpret",
                ),
                self.create_quiz(negative, "en", "nl", "The car is not black.", ["De auto is niet zwart."], "write"),
                self.create_quiz(concept, "nl", "nl", "De auto is zwart.", ["De auto is niet zwart."], "negate"),
                self.create_quiz(concept, "nl", "nl", "De auto is niet zwart.", ["De auto is zwart."], "affirm"),
            },
            create_quizzes("nl", "en", concept),
        )


class DiminutiveTest(ToistoTestCase):
    """Unit tests for diminutive forms."""

    def test_diminutive(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = create_concept("car", dict(root=dict(nl="de auto"), diminutive=dict(nl="het autootje")))
        root, diminutive = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(root, "nl", "nl", "de auto", ["de auto"], "dictate"),
                self.create_quiz(diminutive, "nl", "nl", "het autootje", ["het autootje"], "dictate"),
                self.create_quiz(concept, "nl", "nl", "de auto", ["het autootje"], "diminutize"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_diminutive_and_translation(self):
        """Test that quizzes can be generated for diminutive forms."""
        concept = create_concept(
            "car",
            {
                "root": dict(en="car", nl="de auto"),
                "diminutive": dict(nl="het autootje"),
            },
        )
        root, diminutive = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(root, "nl", "en", "de auto", ["car"], "read"),
                self.create_quiz(root, "nl", "nl", "de auto", ["de auto"], "dictate"),
                self.create_quiz(root, "nl", "en", "de auto", ["car"], "interpret"),
                self.create_quiz(root, "en", "nl", "car", ["de auto"], "write"),
                self.create_quiz(diminutive, "nl", "nl", "het autootje", ["het autootje"], "dictate"),
                self.create_quiz(concept, "nl", "nl", "de auto", ["het autootje"], "diminutize"),
            },
            create_quizzes("nl", "en", concept),
        )


class QuizNoteTest(ToistoTestCase):
    """Unit tests for the quiz notes."""

    def test_note(self):
        """Test that the quizzes use the notes of the target language."""
        concept = create_concept(
            "finnish",
            dict(
                fi="suomi;;In Finnish, the names of languages are not capitalized",
                nl="Fins;;In Dutch, the names of languages are capitalized",
            ),
        )
        for quiz in create_quizzes("fi", "nl", concept):
            self.assertEqual("In Finnish, the names of languages are not capitalized", quiz.answer_notes[0])


class ColloquialTest(ToistoTestCase):
    """Unit tests for concepts with colloquial (spoken language) labels."""

    def test_colloquial_label_only(self):
        """Test the generated quizzes if one language only has a colloquial label."""
        concept = create_concept("seven", dict(fi="seittemän*", nl="zeven"))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "fi", "nl", "seittemän*", ["zeven"], "interpret"),
                self.create_quiz(concept, "fi", "fi", "seittemän*", ["seitsemän"], "dictate"),
            },
            create_quizzes("fi", "nl", concept),
        )
        self.assertSetEqual(
            {self.create_quiz(concept, "nl", "nl", "zeven", ["zeven"], "dictate")},
            create_quizzes("nl", "fi", concept),
        )

    def test_colloquial_and_regular_label(self):
        """Test the generated quizzes when one language has both a colloquial and a regular label."""
        concept = create_concept("seven", dict(fi=["seittemän*", "seitsemän"], nl="zeven"))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "fi", "nl", "seitsemän", ["zeven"], "read"),
                self.create_quiz(concept, "fi", "fi", "seitsemän", ["seitsemän"], "dictate"),
                self.create_quiz(concept, "nl", "fi", "zeven", ["seitsemän"], "write"),
                self.create_quiz(concept, "fi", "nl", "seitsemän", ["zeven"], "interpret"),
                self.create_quiz(concept, "fi", "fi", "seittemän*", ["seitsemän"], "dictate"),
                self.create_quiz(concept, "fi", "nl", "seittemän*", ["zeven"], "interpret"),
            },
            create_quizzes("fi", "nl", concept),
        )
        self.assertSetEqual(
            {
                self.create_quiz(concept, "nl", "fi", "zeven", ["seitsemän"], "read"),
                self.create_quiz(concept, "nl", "nl", "zeven", ["zeven"], "dictate"),
                self.create_quiz(concept, "fi", "nl", "seitsemän", ["zeven"], "write"),
                self.create_quiz(concept, "nl", "fi", "zeven", ["seitsemän"], "interpret"),
            },
            create_quizzes("nl", "fi", concept),
        )

    def test_grammar_and_colloquial(self):
        """Test the generated quizzes when colloquial labels and grammar are combined."""
        concept = create_concept(
            "kiosk",
            dict(
                singular=dict(fi=["kioski", "kiska*"], en="kiosk"),
                plural=dict(fi=["kioskit", "kiskat*"], en="kiosks"),
            ),
        )
        singular, plural = concept.leaf_concepts("fi")
        self.assertSetEqual(
            {
                self.create_quiz(singular, "fi", "en", "kioski", ["kiosk"], "read"),
                self.create_quiz(singular, "fi", "fi", "kioski", ["kioski"], "dictate"),
                self.create_quiz(singular, "en", "fi", "kiosk", ["kioski"], "write"),
                self.create_quiz(singular, "fi", "en", "kioski", ["kiosk"], "interpret"),
                self.create_quiz(singular, "fi", "en", "kiska*", ["kiosk"], "interpret"),
                self.create_quiz(singular, "fi", "fi", "kiska*", ["kioski"], "dictate"),
                self.create_quiz(plural, "fi", "en", "kioskit", ["kiosks"], "read"),
                self.create_quiz(plural, "fi", "fi", "kioskit", ["kioskit"], "dictate"),
                self.create_quiz(plural, "en", "fi", "kiosks", ["kioskit"], "write"),
                self.create_quiz(plural, "fi", "en", "kioskit", ["kiosks"], "interpret"),
                self.create_quiz(plural, "fi", "en", "kiskat*", ["kiosks"], "interpret"),
                self.create_quiz(plural, "fi", "fi", "kiskat*", ["kioskit"], "dictate"),
                self.create_quiz(concept, "fi", "fi", "kioski", ["kioskit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "kioskit", ["kioski"], "singularize"),
            },
            create_quizzes("fi", "en", concept),
        )
        self.assertSetEqual(
            {
                self.create_quiz(singular, "en", "fi", "kiosk", ["kioski"], "read"),
                self.create_quiz(singular, "en", "en", "kiosk", ["kiosk"], "dictate"),
                self.create_quiz(singular, "fi", "en", "kioski", ["kiosk"], "write"),
                self.create_quiz(singular, "en", "fi", "kiosk", ["kioski"], "interpret"),
                self.create_quiz(plural, "en", "fi", "kiosks", ["kioskit"], "read"),
                self.create_quiz(plural, "en", "en", "kiosks", ["kiosks"], "dictate"),
                self.create_quiz(plural, "fi", "en", "kioskit", ["kiosks"], "write"),
                self.create_quiz(plural, "en", "fi", "kiosks", ["kioskit"], "interpret"),
                self.create_quiz(concept, "en", "en", "kiosk", ["kiosks"], "pluralize"),
                self.create_quiz(concept, "en", "en", "kiosks", ["kiosk"], "singularize"),
            },
            create_quizzes("en", "fi", concept),
        )

    def test_related_concepts_and_colloquial(self):
        """Test the generated quizzes when colloquial labels and related concepts are combined."""
        yes = create_concept("yes", dict(antonym="no", fi=["kylla", "kyl*"]))
        no = create_concept("no", dict(antonym="yes", fi="ei"))
        self.assertSetEqual(
            {
                self.create_quiz(yes, "fi", "fi", "kylla", ["kylla"], "dictate"),
                self.create_quiz(yes, "fi", "fi", "kyl*", ["kylla"], "dictate"),
                self.create_quiz(yes, "fi", "fi", "kylla", ["ei"], "antonym"),
            },
            create_quizzes("fi", "en", yes),
        )
        self.assertSetEqual(
            {
                self.create_quiz(no, "fi", "fi", "ei", ["ei"], "dictate"),
                self.create_quiz(no, "fi", "fi", "ei", ["kylla"], "antonym"),
            },
            create_quizzes("fi", "en", no),
        )


class MeaningsTest(ToistoTestCase):
    """Test that quizzes have the correct meaning."""

    def test_interpret_with_synonym(self):
        """Test that interpret quizzes show all synonyms as meaning."""
        concept = create_concept("yes", dict(fi=["kylla", "joo"], en="yes"))
        quizzes = create_quizzes("fi", "en", concept)
        interpret_quizzes = [quiz for quiz in quizzes if "interpret" in quiz.quiz_types]
        for quiz in interpret_quizzes:
            self.assertEqual(("kylla", "joo"), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)

    def test_interpret_with_colloquial(self):
        """Test that interpret quizzes don't show colloquial labels as meaning."""
        concept = create_concept("20", dict(fi=["kaksikymmentä", "kakskyt*"], nl="twintig"))
        quizzes = create_quizzes("fi", "nl", concept)
        interpret_quizzes = [quiz for quiz in quizzes if "interpret" in quiz.quiz_types]
        for quiz in interpret_quizzes:
            self.assertEqual(("kaksikymmentä",), quiz.question_meanings)
            self.assertEqual((), quiz.answer_meanings)


class GrammaticalQuizTypesTest(QuizFactoryTestCase):
    """Test the grammatical quiz types generator."""

    def test_adjective_with_degrees_of_comparison(self):
        """Test the grammatical quiz types for an adjective with degrees of comparison."""
        positive, comparative, superlative = self.create_adjective_with_degrees_of_comparison().leaf_concepts("en")
        for concept in (positive, comparative):
            self.assertEqual(("give superlative degree",), grammatical_quiz_types(concept, superlative))
        for concept in (positive, superlative):
            self.assertEqual(("give comparative degree",), grammatical_quiz_types(concept, comparative))
        for concept in (comparative, superlative):
            self.assertEqual(("give positive degree",), grammatical_quiz_types(concept, positive))

    def test_noun_with_grammatical_number(self):
        """Test the grammatical quiz types for a noun with singular and plural form."""
        singular, plural = self.create_noun_with_grammatical_number().leaf_concepts("fi")
        self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
        self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))

    def test_noun_with_grammatical_gender(self):
        """Test the grammatical quiz types for a noun with grammatical gender."""
        female, male = self.create_noun_with_grammatical_gender().leaf_concepts("en")
        self.assertEqual(("masculinize",), grammatical_quiz_types(female, male))
        self.assertEqual(("feminize",), grammatical_quiz_types(male, female))

    def test_noun_with_grammatical_gender_including_neuter(self):
        """Test the grammatical quiz types for a noun with grammatical gender including neuter."""
        female, male, neuter = self.create_noun_with_grammatical_gender_including_neuter().leaf_concepts("nl")
        for concept in (female, neuter):
            self.assertEqual(("masculinize",), grammatical_quiz_types(concept, male))
        for concept in (female, male):
            self.assertEqual(("neuterize",), grammatical_quiz_types(concept, neuter))
        for concept in (male, neuter):
            self.assertEqual(("feminize",), grammatical_quiz_types(concept, female))

    def test_noun_with_grammatical_number_and_gender(self):
        """Test the grammatical quiz types for a noun with grammatical number and gender."""
        noun = self.create_noun_with_grammatical_number_and_gender()
        singular_female, singular_male, plural_female, plural_male = noun.leaf_concepts("en")
        for female, male in ((singular_female, singular_male), (plural_female, plural_male)):
            self.assertEqual(("masculinize",), grammatical_quiz_types(female, male))
            self.assertEqual(("feminize",), grammatical_quiz_types(male, female))
        for singular, plural in ((singular_female, plural_female), (singular_male, plural_male)):
            self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
            self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))

    def test_verb_with_person(self):
        """Test the grammatical quiz types for a verb with grammatical person."""
        verb = self.create_verb_with_person()
        first, second, third = verb.leaf_concepts("en")
        for concept in (first, second):
            self.assertEqual(("give third person",), grammatical_quiz_types(concept, third))
        for concept in (first, third):
            self.assertEqual(("give second person",), grammatical_quiz_types(concept, second))
        for concept in (second, third):
            self.assertEqual(("give first person",), grammatical_quiz_types(concept, first))

    def test_verb_with_tense_and_person(self):
        """Test the grammatical quiz types for a verb with tense and grammatical person."""
        verb = self.create_verb_with_tense_and_person()
        present_singular, present_plural, past_singular, past_plural = verb.leaf_concepts("nl")
        for singular, plural in ((present_singular, present_plural), (past_singular, past_plural)):
            self.assertEqual(("pluralize",), grammatical_quiz_types(singular, plural))
            self.assertEqual(("singularize",), grammatical_quiz_types(plural, singular))
        for present, past in ((present_singular, past_singular), (present_plural, past_plural)):
            self.assertEqual(("give past tense",), grammatical_quiz_types(present, past))
            self.assertEqual(("give present tense",), grammatical_quiz_types(past, present))

    def test_verb_with_infinitive_and_person(self):
        """Test the grammatical quiz types for a verb with infinitive and grammatical person."""
        verb = self.create_verb_with_infinitive_and_person()
        infinitive, singular, plural = verb.leaf_concepts("en")
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
        ) = verb.leaf_concepts("nl")
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
        ) = verb.leaf_concepts("nl")
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
