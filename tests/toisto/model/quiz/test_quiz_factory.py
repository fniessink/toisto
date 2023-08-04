"""Concept unit tests."""

from toisto.model.language.concept_factory import create_concept
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes

from ....base import ToistoTestCase


class QuizFactoryTestCase(ToistoTestCase):
    """Base class for quiz factory unit tests."""

    def create_verb_with_tense_and_person(self):
        """Create a verb with grammatical person nested within tense."""
        return create_concept(
            "to eat",
            {
                "present tense": {
                    "singular": dict(en="I eat", nl="ik eet"),
                    "plural": dict(en="we eat", nl="wij eten"),
                },
                "past tense": {"singular": dict(en="I ate", nl="ik at"), "plural": dict(en="we ate", nl="wij aten")},
            },
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
                male=dict(en="his bone", nl="zijn bot"),
                neuter=dict(en="its bone", nl="zijn bot"),
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
                self.create_quiz(concept, "nl", "nl", "Engels", ["Engels"], "listen"),
                self.create_quiz(concept, "en", "nl", "English", ["Engels"], "write"),
            },
            create_quizzes("nl", "en", concept),
        )

    def test_only_listening_quizzes_for_one_language(self):
        """Test that only listening quizzes are generated for a concept with one language."""
        concept = create_concept("english", dict(nl="Engels"))
        self.assertSetEqual(
            {
                self.create_quiz(concept, "nl", "nl", "Engels", ["Engels"], "listen"),
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
                self.create_quiz(concept, "nl", "nl", "bank", ["bank"], "listen"),
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
                self.create_quiz(singular, "fi", "fi", "aamu", ["aamu"], "listen"),
                self.create_quiz(singular, "nl", "fi", "de ochtend", ["aamu"], "write"),
                self.create_quiz(plural, "fi", "nl", "aamut", ["de ochtenden"], "read"),
                self.create_quiz(plural, "fi", "fi", "aamut", ["aamut"], "listen"),
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
                self.create_quiz(singular, "fi", "fi", "ketsuppi", ["ketsuppi"], "listen"),
                self.create_quiz(singular, "nl", "fi", "de ketchup", ["ketsuppi"], "write"),
                self.create_quiz(plural, "fi", "fi", "ketsupit", ["ketsupit"], "listen"),
                self.create_quiz(concept, "fi", "fi", "ketsuppi", ["ketsupit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "ketsupit", ["ketsuppi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.meanings))

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the target language only."""
        concept = create_concept("mämmi", dict(singular=dict(fi="mämmi"), plural=dict(fi="mämmit")))
        singular, plural = concept.leaf_concepts("fi")
        quizzes = create_quizzes("fi", "nl", concept)
        self.assertSetEqual(
            {
                self.create_quiz(singular, "fi", "fi", "mämmi", ["mämmi"], "listen"),
                self.create_quiz(plural, "fi", "fi", "mämmit", ["mämmit"], "listen"),
                self.create_quiz(concept, "fi", "fi", "mämmi", ["mämmit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "mämmit", ["mämmi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.meanings))

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
                self.create_quiz(singular, "fi", "fi", "kauppakeskus", ["kauppakeskus"], "listen"),
                self.create_quiz(singular, "fi", "fi", "ostoskeskus", ["ostoskeskus"], "listen"),
                self.create_quiz(singular, "nl", "fi", "het winkelcentrum", ["kauppakeskus", "ostoskeskus"], "write"),
                self.create_quiz(plural, "fi", "nl", "kauppakeskukset", ["de winkelcentra"], "read"),
                self.create_quiz(plural, "fi", "nl", "ostoskeskukset", ["de winkelcentra"], "read"),
                self.create_quiz(plural, "fi", "fi", "kauppakeskukset", ["kauppakeskukset"], "listen"),
                self.create_quiz(plural, "fi", "fi", "ostoskeskukset", ["ostoskeskukset"], "listen"),
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
                self.create_quiz(female, "nl", "nl", "haar kat", ["haar kat"], "listen"),
                self.create_quiz(female, "en", "nl", "her cat", ["haar kat"], "write"),
                self.create_quiz(male, "nl", "en", "zijn kat", ["his cat"], "read"),
                self.create_quiz(male, "nl", "nl", "zijn kat", ["zijn kat"], "listen"),
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
                self.create_quiz(female, "nl", "nl", "haar bot", ["haar bot"], "listen"),
                self.create_quiz(female, "en", "nl", "her bone", ["haar bot"], "write"),
                self.create_quiz(male, "nl", "en", "zijn bot", ["his bone"], "read"),
                self.create_quiz(male, "nl", "nl", "zijn bot", ["zijn bot"], "listen"),
                self.create_quiz(male, "en", "nl", "his bone", ["zijn bot"], "write"),
                self.create_quiz(neuter, "nl", "en", "zijn bot", ["its bone"], "read"),
                self.create_quiz(neuter, "nl", "nl", "zijn bot", ["zijn bot"], "listen"),
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
                self.create_quiz(singular_female, "nl", "nl", "haar kat", ["haar kat"], "listen"),
                self.create_quiz(singular_female, "en", "nl", "her cat", ["haar kat"], "write"),
                self.create_quiz(singular_male, "nl", "en", "zijn kat", ["his cat"], "read"),
                self.create_quiz(singular_male, "nl", "nl", "zijn kat", ["zijn kat"], "listen"),
                self.create_quiz(singular_male, "en", "nl", "his cat", ["zijn kat"], "write"),
                self.create_quiz(singular, "nl", "nl", "haar kat", ["zijn kat"], "masculinize"),
                self.create_quiz(singular, "nl", "nl", "zijn kat", ["haar kat"], "feminize"),
                self.create_quiz(plural_female, "nl", "en", "haar katten", ["her cats"], "read"),
                self.create_quiz(plural_female, "nl", "nl", "haar katten", ["haar katten"], "listen"),
                self.create_quiz(plural_female, "en", "nl", "her cats", ["haar katten"], "write"),
                self.create_quiz(plural_male, "nl", "en", "zijn katten", ["his cats"], "read"),
                self.create_quiz(plural_male, "nl", "nl", "zijn katten", ["zijn katten"], "listen"),
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
                self.create_quiz(positive_degree, "nl", "nl", "groot", ["groot"], "listen"),
                self.create_quiz(positive_degree, "en", "nl", "big", ["groot"], "write"),
                self.create_quiz(comparative_degree, "nl", "en", "groter", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "nl", "nl", "groter", ["groter"], "listen"),
                self.create_quiz(comparative_degree, "en", "nl", "bigger", ["groter"], "write"),
                self.create_quiz(superlative_degree, "nl", "en", "grootst", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "nl", "nl", "grootst", ["grootst"], "listen"),
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
                self.create_quiz(positive_degree, "fi", "fi", "iso", ["iso"], "listen"),
                self.create_quiz(positive_degree, "fi", "fi", "suuri", ["suuri"], "listen"),
                self.create_quiz(positive_degree, "en", "fi", "big", ["iso", "suuri"], "write"),
                self.create_quiz(comparative_degree, "fi", "en", "isompi", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "fi", "en", "suurempi", ["bigger"], "read"),
                self.create_quiz(comparative_degree, "fi", "fi", "isompi", ["isompi"], "listen"),
                self.create_quiz(comparative_degree, "fi", "fi", "suurempi", ["suurempi"], "listen"),
                self.create_quiz(comparative_degree, "en", "fi", "bigger", ["isompi", "suurempi"], "write"),
                self.create_quiz(superlative_degree, "fi", "en", "isoin", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "fi", "en", "suurin", ["biggest"], "read"),
                self.create_quiz(superlative_degree, "fi", "fi", "isoin", ["isoin"], "listen"),
                self.create_quiz(superlative_degree, "fi", "fi", "suurin", ["suurin"], "listen"),
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
        concept = create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", nl="ik eet"),
                "second person": dict(en="you eat", nl="jij eet"),
                "third person": dict(en="she eats", nl="zij eet"),
            },
        )
        first_person, second_person, third_person = concept.leaf_concepts("nl")
        self.assertSetEqual(
            {
                self.create_quiz(first_person, "nl", "en", "ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "nl", "nl", "ik eet", ["ik eet"], "listen"),
                self.create_quiz(first_person, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(second_person, "nl", "en", "jij eet", ["you eat"], "read"),
                self.create_quiz(second_person, "nl", "nl", "jij eet", ["jij eet"], "listen"),
                self.create_quiz(second_person, "en", "nl", "you eat", ["jij eet"], "write"),
                self.create_quiz(third_person, "nl", "en", "zij eet", ["she eats"], "read"),
                self.create_quiz(third_person, "nl", "nl", "zij eet", ["zij eet"], "listen"),
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
                self.create_quiz(first_person, "nl", "nl", "ik eet", ["ik eet"], "listen"),
                self.create_quiz(first_person, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(second_person, "nl", "en", "jij eet", ["you eat"], "read"),
                self.create_quiz(second_person, "nl", "nl", "jij eet", ["jij eet"], "listen"),
                self.create_quiz(second_person, "en", "nl", "you eat", ["jij eet"], "write"),
                self.create_quiz(third_person_female, "nl", "en", "zij eet", ["she eats"], "read"),
                self.create_quiz(third_person_female, "nl", "nl", "zij eet", ["zij eet"], "listen"),
                self.create_quiz(third_person_female, "en", "nl", "she eats", ["zij eet"], "write"),
                self.create_quiz(third_person_male, "nl", "en", "hij eet", ["he eats"], "read"),
                self.create_quiz(third_person_male, "nl", "nl", "hij eet", ["hij eet"], "listen"),
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
                self.create_quiz(first_person, "fi", "fi", "minä syön", ["minä syön"], "listen"),
                self.create_quiz(first_person, "en", "fi", "I eat", ["minä syön"], "write"),
                self.create_quiz(second_person, "fi", "en", "sinä syöt", ["you eat"], "read"),
                self.create_quiz(second_person, "fi", "fi", "sinä syöt", ["sinä syöt"], "listen"),
                self.create_quiz(second_person, "en", "fi", "you eat", ["sinä syöt"], "write"),
                self.create_quiz(third_person, "fi", "en", "hän syö", ["she eats", "he eats"], "read"),
                self.create_quiz(third_person, "fi", "fi", "hän syö", ["hän syö"], "listen"),
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
        concept = create_concept(
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
        singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "nl", "fi", "ik heb", ["minulla on"], "read"),
                self.create_quiz(first_person_singular, "fi", "nl", "minulla on", ["ik heb"], "write"),
                self.create_quiz(first_person_singular, "nl", "nl", "ik heb", ["ik heb"], "listen"),
                self.create_quiz(second_person_singular, "nl", "fi", "jij hebt", ["sinulla on"], "read"),
                self.create_quiz(second_person_singular, "fi", "nl", "sinulla on", ["jij hebt"], "write"),
                self.create_quiz(second_person_singular, "nl", "nl", "jij hebt", ["jij hebt"], "listen"),
                self.create_quiz(third_person_singular, "nl", "fi", "zij heeft", ["hänellä on"], "read"),
                self.create_quiz(third_person_singular, "fi", "nl", "hänellä on", ["zij heeft"], "write"),
                self.create_quiz(third_person_singular, "nl", "nl", "zij heeft", ["zij heeft"], "listen"),
                self.create_quiz(singular, "nl", "nl", "ik heb", ["jij hebt"], "give second person"),
                self.create_quiz(singular, "nl", "nl", "ik heb", ["zij heeft"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "jij hebt", ["ik heb"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "jij hebt", ["zij heeft"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "zij heeft", ["ik heb"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "zij heeft", ["jij hebt"], "give second person"),
                self.create_quiz(first_person_plural, "nl", "fi", "wij hebben", ["meillä on"], "read"),
                self.create_quiz(first_person_plural, "fi", "nl", "meillä on", ["wij hebben"], "write"),
                self.create_quiz(first_person_plural, "nl", "nl", "wij hebben", ["wij hebben"], "listen"),
                self.create_quiz(second_person_plural, "nl", "fi", "jullie hebben", ["teillä on"], "read"),
                self.create_quiz(second_person_plural, "fi", "nl", "teillä on", ["jullie hebben"], "write"),
                self.create_quiz(second_person_plural, "nl", "nl", "jullie hebben", ["jullie hebben"], "listen"),
                self.create_quiz(third_person_plural, "nl", "fi", "zij hebben", ["heillä on"], "read"),
                self.create_quiz(third_person_plural, "fi", "nl", "heillä on", ["zij hebben"], "write"),
                self.create_quiz(third_person_plural, "nl", "nl", "zij hebben", ["zij hebben"], "listen"),
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
                self.create_quiz(female_singular, "nl", "nl", "haar kat", ["haar kat"], "listen"),
                self.create_quiz(female_singular, "en", "nl", "her cat", ["haar kat"], "write"),
                self.create_quiz(female_plural, "nl", "en", "haar katten", ["her cats"], "read"),
                self.create_quiz(female_plural, "nl", "nl", "haar katten", ["haar katten"], "listen"),
                self.create_quiz(female_plural, "en", "nl", "her cats", ["haar katten"], "write"),
                self.create_quiz(female, "nl", "nl", "haar kat", ["haar katten"], "pluralize"),
                self.create_quiz(female, "nl", "nl", "haar katten", ["haar kat"], "singularize"),
                self.create_quiz(male_singular, "nl", "en", "zijn kat", ["his cat"], "read"),
                self.create_quiz(male_singular, "nl", "nl", "zijn kat", ["zijn kat"], "listen"),
                self.create_quiz(male_singular, "en", "nl", "his cat", ["zijn kat"], "write"),
                self.create_quiz(male_plural, "nl", "en", "zijn katten", ["his cats"], "read"),
                self.create_quiz(male_plural, "nl", "nl", "zijn katten", ["zijn katten"], "listen"),
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
                self.create_quiz(female, "fi", "fi", "hän on;female", ("hän on;female",), "listen"),
                self.create_quiz(female, "en", "fi", "she is|she's", ("hän on;female",), "write"),
                self.create_quiz(male, "fi", "en", "hän on;male", ("he is|he's",), "read"),
                self.create_quiz(male, "en", "fi", "he is|he's", ("hän on;male",), "write"),
            },
            create_quizzes("fi", "en", concept),
        )

    def test_infinitive_verb_form(self):
        """Test the infinitive verb form."""
        concept = create_concept(
            "to sleep",
            dict(
                infinitive=dict(en="to sleep", nl="slapen"),
                singular=dict(en="I sleep", nl="ik slaap"),
                plural=dict(en="we sleep", nl="wij slapen"),
            ),
        )
        infinitive, singular, plural = concept.constituents
        self.assertSetEqual(
            {
                self.create_quiz(infinitive, "nl", "en", "slapen", ["to sleep"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "slapen", ["slapen"], "listen"),
                self.create_quiz(infinitive, "en", "nl", "to sleep", ["slapen"], "write"),
                self.create_quiz(singular, "nl", "en", "ik slaap", ["I sleep"], "read"),
                self.create_quiz(singular, "nl", "nl", "ik slaap", ["ik slaap"], "listen"),
                self.create_quiz(singular, "en", "nl", "I sleep", ["ik slaap"], "write"),
                self.create_quiz(plural, "nl", "en", "wij slapen", ["we sleep"], "read"),
                self.create_quiz(plural, "nl", "nl", "wij slapen", ["wij slapen"], "listen"),
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
        concept = create_concept(
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
        infinitive, singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertSetEqual(
            {
                self.create_quiz(first_person_singular, "nl", "fi", "ik ben", ["minä olen"], "read"),
                self.create_quiz(first_person_singular, "nl", "nl", "ik ben", ["ik ben"], "listen"),
                self.create_quiz(first_person_singular, "fi", "nl", "minä olen", ["ik ben"], "write"),
                self.create_quiz(concept, "nl", "nl", "ik ben", ["zijn"], "give infinitive"),
                self.create_quiz(second_person_singular, "nl", "fi", "jij bent", ["sinä olet"], "read"),
                self.create_quiz(second_person_singular, "nl", "nl", "jij bent", ["jij bent"], "listen"),
                self.create_quiz(second_person_singular, "fi", "nl", "sinä olet", ["jij bent"], "write"),
                self.create_quiz(concept, "nl", "nl", "jij bent", ["zijn"], "give infinitive"),
                self.create_quiz(third_person_singular, "nl", "fi", "zij is", ["hän on"], "read"),
                self.create_quiz(third_person_singular, "nl", "nl", "zij is", ["zij is"], "listen"),
                self.create_quiz(third_person_singular, "fi", "nl", "hän on", ["zij is"], "write"),
                self.create_quiz(concept, "nl", "nl", "zij is", ["zijn"], "give infinitive"),
                self.create_quiz(singular, "nl", "nl", "ik ben", ["jij bent"], "give second person"),
                self.create_quiz(singular, "nl", "nl", "ik ben", ["zij is"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "jij bent", ["ik ben"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "jij bent", ["zij is"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "zij is", ["ik ben"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "zij is", ["jij bent"], "give second person"),
                self.create_quiz(first_person_plural, "nl", "fi", "wij zijn", ["me olemme"], "read"),
                self.create_quiz(first_person_plural, "nl", "nl", "wij zijn", ["wij zijn"], "listen"),
                self.create_quiz(first_person_plural, "fi", "nl", "me olemme", ["wij zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "wij zijn", ["zijn"], "give infinitive"),
                self.create_quiz(second_person_plural, "nl", "fi", "jullie zijn", ["te olette"], "read"),
                self.create_quiz(second_person_plural, "nl", "nl", "jullie zijn", ["jullie zijn"], "listen"),
                self.create_quiz(second_person_plural, "fi", "nl", "te olette", ["jullie zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "jullie zijn", ["zijn"], "give infinitive"),
                self.create_quiz(third_person_plural, "nl", "fi", "zij zijn", ["he ovat"], "read"),
                self.create_quiz(third_person_plural, "nl", "nl", "zij zijn", ["zij zijn"], "listen"),
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
                self.create_quiz(infinitive, "nl", "nl", "zijn", ["zijn"], "listen"),
                self.create_quiz(infinitive, "fi", "nl", "olla", ["zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "zijn", ["ik ben"], ("singularize", "give first person")),
                self.create_quiz(concept, "nl", "nl", "zijn", ["jij bent"], ("singularize", "give second person")),
                self.create_quiz(concept, "nl", "nl", "zijn", ["zij is"], ("singularize", "give third person")),
                self.create_quiz(concept, "nl", "nl", "zijn", ["wij zijn"], ("pluralize", "give first person")),
                self.create_quiz(concept, "nl", "nl", "zijn", ["jullie zijn"], ("pluralize", "give second person")),
                self.create_quiz(concept, "nl", "nl", "zijn", ["zij zijn"], ("pluralize", "give third person")),
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
                self.create_quiz(first_singular_present, "nl", "nl", "ik ben", ["ik ben"], "listen"),
                self.create_quiz(first_singular_present, "fi", "nl", "minä olen", ["ik ben"], "write"),
                self.create_quiz(second_singular_present, "nl", "fi", "jij bent", ["sinä olet"], "read"),
                self.create_quiz(second_singular_present, "nl", "nl", "jij bent", ["jij bent"], "listen"),
                self.create_quiz(second_singular_present, "fi", "nl", "sinä olet", ["jij bent"], "write"),
                self.create_quiz(third_singular_present, "nl", "fi", "zij is", ["hän on"], "read"),
                self.create_quiz(third_singular_present, "nl", "nl", "zij is", ["zij is"], "listen"),
                self.create_quiz(third_singular_present, "fi", "nl", "hän on", ["zij is"], "write"),
                self.create_quiz(singular_present, "nl", "nl", "ik ben", ["jij bent"], "give second person"),
                self.create_quiz(singular_present, "nl", "nl", "ik ben", ["zij is"], "give third person"),
                self.create_quiz(singular_present, "nl", "nl", "jij bent", ["ik ben"], "give first person"),
                self.create_quiz(singular_present, "nl", "nl", "jij bent", ["zij is"], "give third person"),
                self.create_quiz(singular_present, "nl", "nl", "zij is", ["ik ben"], "give first person"),
                self.create_quiz(singular_present, "nl", "nl", "zij is", ["jij bent"], "give second person"),
                self.create_quiz(first_plural_present, "nl", "fi", "wij zijn", ["me olemme"], "read"),
                self.create_quiz(first_plural_present, "nl", "nl", "wij zijn", ["wij zijn"], "listen"),
                self.create_quiz(first_plural_present, "fi", "nl", "me olemme", ["wij zijn"], "write"),
                self.create_quiz(second_plural_present, "nl", "fi", "jullie zijn", ["te olette"], "read"),
                self.create_quiz(second_plural_present, "nl", "nl", "jullie zijn", ["jullie zijn"], "listen"),
                self.create_quiz(second_plural_present, "fi", "nl", "te olette", ["jullie zijn"], "write"),
                self.create_quiz(third_plural_present, "nl", "fi", "zij zijn", ["he ovat"], "read"),
                self.create_quiz(third_plural_present, "nl", "nl", "zij zijn", ["zij zijn"], "listen"),
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
                self.create_quiz(first_singular_past, "nl", "nl", "ik was", ["ik was"], "listen"),
                self.create_quiz(first_singular_past, "fi", "nl", "minä olin", ["ik was"], "write"),
                self.create_quiz(second_singular_past, "nl", "fi", "jij was", ["sinä olot"], "read"),
                self.create_quiz(second_singular_past, "nl", "nl", "jij was", ["jij was"], "listen"),
                self.create_quiz(second_singular_past, "fi", "nl", "sinä olit", ["jij was"], "write"),
                self.create_quiz(third_singular_past, "nl", "fi", "zij was", ["hän oli"], "read"),
                self.create_quiz(third_singular_past, "nl", "nl", "zij was", ["zij was"], "listen"),
                self.create_quiz(third_singular_past, "fi", "nl", "hän oli", ["zij was"], "write"),
                self.create_quiz(singular_past, "nl", "nl", "ik was", ["jij was"], "give second person"),
                self.create_quiz(singular_past, "nl", "nl", "ik was", ["zij was"], "give third person"),
                self.create_quiz(singular_past, "nl", "nl", "jij was", ["ik was"], "give first person"),
                self.create_quiz(singular_past, "nl", "nl", "jij was", ["zij was"], "give third person"),
                self.create_quiz(singular_past, "nl", "nl", "zij was", ["ik was"], "give first person"),
                self.create_quiz(singular_past, "nl", "nl", "zij was", ["jij was"], "give second person"),
                self.create_quiz(first_plural_past, "nl", "fi", "wij waren", ["me olimme"], "read"),
                self.create_quiz(first_plural_past, "nl", "nl", "wij waren", ["wij waren"], "listen"),
                self.create_quiz(first_plural_past, "fi", "nl", "me olimme", ["wij waren"], "write"),
                self.create_quiz(second_plural_past, "nl", "fi", "jullie waren", ["te olitte"], "read"),
                self.create_quiz(second_plural_past, "nl", "nl", "jullie waren", ["jullie waren"], "listen"),
                self.create_quiz(second_plural_past, "fi", "nl", "te olitte", ["jullie waren"], "write"),
                self.create_quiz(third_plural_past, "nl", "fi", "zij waren", ["he olivat"], "read"),
                self.create_quiz(third_plural_past, "nl", "nl", "zij waren", ["zij waren"], "listen"),
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
                self.create_quiz(present_singular, "nl", "nl", "ik eet", ["ik eet"], "listen"),
                self.create_quiz(present_singular, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "nl", "en", "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "nl", "nl", "wij eten", ["wij eten"], "listen"),
                self.create_quiz(present_plural, "en", "nl", "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "nl", "nl", "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "nl", "en", "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "nl", "nl", "ik at", ["ik at"], "listen"),
                self.create_quiz(past_singular, "en", "nl", "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "nl", "en", "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "nl", "nl", "wij aten", ["wij aten"], "listen"),
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
                self.create_quiz(present_singular, "nl", "nl", "ik eet", ["ik eet"], "listen"),
                self.create_quiz(present_singular, "en", "nl", "I eat", ["ik eet"], "write"),
                self.create_quiz(present_plural, "nl", "en", "wij eten", ["we eat"], "read"),
                self.create_quiz(present_plural, "nl", "nl", "wij eten", ["wij eten"], "listen"),
                self.create_quiz(present_plural, "en", "nl", "we eat", ["wij eten"], "write"),
                self.create_quiz(present, "nl", "nl", "ik eet", ["wij eten"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "wij eten", ["ik eet"], "singularize"),
                self.create_quiz(past_singular, "nl", "en", "ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "nl", "nl", "ik at", ["ik at"], "listen"),
                self.create_quiz(past_singular, "en", "nl", "I ate", ["ik at"], "write"),
                self.create_quiz(past_plural, "nl", "en", "wij aten", ["we ate"], "read"),
                self.create_quiz(past_plural, "nl", "nl", "wij aten", ["wij aten"], "listen"),
                self.create_quiz(past_plural, "en", "nl", "we ate", ["wij aten"], "write"),
                self.create_quiz(past, "nl", "nl", "ik at", ["wij aten"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "wij aten", ["ik at"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "ik eet", ["ik at"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "wij eten", ["wij aten"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "ik at", ["ik eet"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "wij aten", ["wij eten"], "give present tense"),
                self.create_quiz(infinitive, "nl", "en", "eten", ["to eat"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "eten", ["eten"], "listen"),
                self.create_quiz(infinitive, "en", "nl", "to eat", ["eten"], "write"),
                self.create_quiz(concept, "nl", "nl", "eten", ["ik eet"], ("give present tense", "singularize")),
                self.create_quiz(concept, "nl", "nl", "eten", ["ik at"], ("give past tense", "singularize")),
                self.create_quiz(concept, "nl", "nl", "eten", ["wij eten"], ("give present tense", "pluralize")),
                self.create_quiz(concept, "nl", "nl", "eten", ["wij aten"], ("give past tense", "pluralize")),
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
                self.create_quiz(declarative, "nl", "nl", "De auto is zwart.", ["De auto is zwart."], "listen"),
                self.create_quiz(declarative, "en", "nl", "The car is black.", ["De auto is zwart."], "write"),
                self.create_quiz(interrogative, "nl", "en", "Is de auto zwart?", ["Is the car black?"], "read"),
                self.create_quiz(interrogative, "nl", "nl", "Is de auto zwart?", ["Is de auto zwart?"], "listen"),
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
                self.create_quiz(affirmative, "nl", "nl", "De auto is zwart.", ["De auto is zwart."], "listen"),
                self.create_quiz(affirmative, "en", "nl", "The car is black.", ["De auto is zwart."], "write"),
                self.create_quiz(negative, "nl", "en", "De auto is niet zwart.", ["The car is not black."], "read"),
                self.create_quiz(negative, "nl", "nl", "De auto is niet zwart.", ["De auto is niet zwart."], "listen"),
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
                self.create_quiz(root, "nl", "nl", "de auto", ["de auto"], "listen"),
                self.create_quiz(diminutive, "nl", "nl", "het autootje", ["het autootje"], "listen"),
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
                self.create_quiz(root, "nl", "nl", "de auto", ["de auto"], "listen"),
                self.create_quiz(root, "en", "nl", "car", ["de auto"], "write"),
                self.create_quiz(diminutive, "nl", "nl", "het autootje", ["het autootje"], "listen"),
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
            self.assertEqual("In Finnish, the names of languages are not capitalized", quiz.notes[-1])
