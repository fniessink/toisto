"""Concept unit tests."""

from toisto.model.language.label import Label

from ....base import ToistoTestCase


class QuizFactoryTestCase(ToistoTestCase):
    """Base class for quiz factory unit tests."""

    def create_verb_with_tense_and_person(self):
        """Create a verb with grammatical person nested within tense."""
        return self.create_concept(
            "to eat",
            {
                "present tense": {
                    "singular": dict(en="I eat", nl="Ik eet"),
                    "plural": dict(en="We eat", nl="Wij eten"),
                },
                "past tense": {"singular": dict(en="I ate", nl="Ik at"), "plural": dict(en="We ate", nl="Wij aten")},
            },
        )

    def create_adjective_with_degrees_of_comparison(self):
        """Create an adjective with degrees of comparison."""
        return self.create_concept(
            "big",
            {
                "positive degree": dict(en="Big", nl="Groot"),
                "comparative degree": dict(en="Bigger", nl="Groter"),
                "superlative degree": dict(en="Biggest", nl="Grootst"),
            },
        )

    def create_noun(self):
        """Create a simple noun."""
        return self.create_concept("mall", dict(fi="Kauppakeskus", nl="Het winkelcentrum"))

    def create_noun_with_grammatical_number(self):
        """Create a noun with grammatical number."""
        return self.create_concept(
            "morning",
            dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden")),
        )

    def create_noun_with_grammatical_gender(self):
        """Create a noun with grammatical gender."""
        return self.create_concept(
            "cat",
            dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat")),
        )

    def create_noun_with_grammatical_gender_including_neuter(self):
        """Create a noun with grammatical gender, including neuter."""
        return self.create_concept(
            "bone",
            dict(
                female=dict(en="Her bone", nl="Haar bot"),
                male=dict(en="His bone", nl="Zijn bot"),
                neuter=dict(en="Its bone", nl="Zijn bot"),
            ),
        )

    def create_noun_with_grammatical_number_and_gender(self):
        """Create a noun with grammatical number and grammatical gender."""
        return self.create_concept(
            "cat",
            dict(
                singular=dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat")),
                plural=dict(female=dict(en="Her cats", nl="Haar katten"), male=dict(en="His cats", nl="Zijn katten")),
            ),
        )


class ConceptQuizzesTest(QuizFactoryTestCase):
    """Unit tests for the concept class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from a concept."""
        concept = self.create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual(
            {
                self.create_quiz(concept, "nl", "en", "Engels", ["English"], "read"),
                self.create_quiz(concept, "nl", "nl", "Engels", ["Engels"], "listen"),
                self.create_quiz(concept, "en", "nl", "English", ["Engels"], "write"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        concept = self.create_concept("couch", dict(nl=["Bank"], en=["Couch", "Bank"]))
        self.assertEqual(
            {
                self.create_quiz(concept, "nl", "en", "Bank", ["Couch", "Bank"], "read"),
                self.create_quiz(concept, "nl", "nl", "Bank", ["Bank"], "listen"),
                self.create_quiz(concept, "en", "nl", "Couch", ["Bank"], "write"),
                self.create_quiz(concept, "en", "nl", "Bank", ["Bank"], "write"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_missing_language(self):
        """Test that quizzes can be generated from a concept even if it's missing one of the languages."""
        concept = self.create_concept("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual(set(), self.create_quizzes(concept, "fi", "en"))

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        concept = self.create_noun_with_grammatical_number()
        singular, plural = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(singular, "fi", "nl", "Aamu", ["De ochtend"], "read"),
                self.create_quiz(singular, "fi", "fi", "Aamu", ["Aamu"], "listen"),
                self.create_quiz(singular, "nl", "fi", "De ochtend", ["Aamu"], "write"),
                self.create_quiz(plural, "fi", "nl", "Aamut", ["De ochtenden"], "read"),
                self.create_quiz(plural, "fi", "fi", "Aamut", ["Aamut"], "listen"),
                self.create_quiz(plural, "nl", "fi", "De ochtenden", ["Aamut"], "write"),
                self.create_quiz(concept, "fi", "fi", "Aamu", ["Aamut"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "Aamut", ["Aamu"], "singularize"),
            },
            self.create_quizzes(concept, "fi", "nl"),
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        concept = self.create_concept(
            "ketchup",
            dict(singular=dict(fi="Ketsuppi", nl="De ketchup"), plural=dict(fi="Ketsupit")),
        )
        singular, plural = concept.leaf_concepts()
        quizzes = self.create_quizzes(concept, "fi", "nl")
        self.assertEqual(
            {
                self.create_quiz(singular, "fi", "nl", "Ketsuppi", ["De ketchup"], "read"),
                self.create_quiz(singular, "fi", "fi", "Ketsuppi", ["Ketsuppi"], "listen"),
                self.create_quiz(singular, "nl", "fi", "De ketchup", ["Ketsuppi"], "write"),
                self.create_quiz(plural, "fi", "fi", "Ketsupit", ["Ketsupit"], "listen"),
                self.create_quiz(concept, "fi", "fi", "Ketsuppi", ["Ketsupit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "Ketsupit", ["Ketsuppi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.meanings))

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the target language only."""
        concept = self.create_concept("mämmi", dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        singular, plural = concept.leaf_concepts()
        quizzes = self.create_quizzes(concept, "fi", "en")
        self.assertEqual(
            {
                self.create_quiz(singular, "fi", "fi", "Mämmi", ["Mämmi"], "listen"),
                self.create_quiz(plural, "fi", "fi", "Mämmit", ["Mämmit"], "listen"),
                self.create_quiz(concept, "fi", "fi", "Mämmi", ["Mämmit"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "Mämmit", ["Mämmi"], "singularize"),
            },
            quizzes,
        )
        for quiz in quizzes:
            self.assertNotIn("", (str(meaning) for meaning in quiz.meanings))

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes can be generated from a noun concept with labels in the native language."""
        concept = self.create_concept("mämmi", dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(set(), self.create_quizzes(concept, "en", "fi"))

    def test_grammatical_number_with_synonyms(self):
        """Test that in case of synonyms the plural of one synonym isn't the correct answer for the other synonym."""
        concept = self.create_concept(
            "mall",
            dict(
                singular=dict(fi=["Kauppakeskus", "Ostoskeskus"], nl="Het winkelcentrum"),
                plural=dict(fi=["Kauppakeskukset", "Ostoskeskukset"], nl="De winkelcentra"),
            ),
        )
        singular, plural = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(singular, "fi", "nl", "Kauppakeskus", ["Het winkelcentrum"], "read"),
                self.create_quiz(singular, "fi", "nl", "Ostoskeskus", ["Het winkelcentrum"], "read"),
                self.create_quiz(singular, "fi", "fi", "Kauppakeskus", ["Kauppakeskus"], "listen"),
                self.create_quiz(singular, "fi", "fi", "Ostoskeskus", ["Ostoskeskus"], "listen"),
                self.create_quiz(singular, "nl", "fi", "Het winkelcentrum", ["Kauppakeskus", "Ostoskeskus"], "write"),
                self.create_quiz(plural, "fi", "nl", "Kauppakeskukset", ["De winkelcentra"], "read"),
                self.create_quiz(plural, "fi", "nl", "Ostoskeskukset", ["De winkelcentra"], "read"),
                self.create_quiz(plural, "fi", "fi", "Kauppakeskukset", ["Kauppakeskukset"], "listen"),
                self.create_quiz(plural, "fi", "fi", "Ostoskeskukset", ["Ostoskeskukset"], "listen"),
                self.create_quiz(plural, "nl", "fi", "De winkelcentra", ["Kauppakeskukset", "Ostoskeskukset"], "write"),
                self.create_quiz(concept, "fi", "fi", "Kauppakeskus", ["Kauppakeskukset"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "Ostoskeskus", ["Ostoskeskukset"], "pluralize"),
                self.create_quiz(concept, "fi", "fi", "Kauppakeskukset", ["Kauppakeskus"], "singularize"),
                self.create_quiz(concept, "fi", "fi", "Ostoskeskukset", ["Ostoskeskus"], "singularize"),
            },
            self.create_quizzes(concept, "fi", "nl"),
        )

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender()
        female, male = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(female, "nl", "en", "Haar kat", ["Her cat"], "read"),
                self.create_quiz(female, "nl", "nl", "Haar kat", ["Haar kat"], "listen"),
                self.create_quiz(female, "en", "nl", "Her cat", ["Haar kat"], "write"),
                self.create_quiz(male, "nl", "en", "Zijn kat", ["His cat"], "read"),
                self.create_quiz(male, "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"),
                self.create_quiz(male, "en", "nl", "His cat", ["Zijn kat"], "write"),
                self.create_quiz(concept, "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = self.create_noun_with_grammatical_gender_including_neuter()
        female, male, neuter = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(female, "nl", "en", "Haar bot", ["Her bone"], "read"),
                self.create_quiz(female, "nl", "nl", "Haar bot", ["Haar bot"], "listen"),
                self.create_quiz(female, "en", "nl", "Her bone", ["Haar bot"], "write"),
                self.create_quiz(male, "nl", "en", "Zijn bot", ["His bone"], "read"),
                self.create_quiz(male, "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"),
                self.create_quiz(male, "en", "nl", "His bone", ["Zijn bot"], "write"),
                self.create_quiz(neuter, "nl", "en", "Zijn bot", ["Its bone"], "read"),
                self.create_quiz(neuter, "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"),
                self.create_quiz(neuter, "en", "nl", "Its bone", ["Zijn bot"], "write"),
                self.create_quiz(concept, "nl", "nl", "Haar bot", ["Zijn bot"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "Haar bot", ["Zijn bot"], "neuterize"),
                self.create_quiz(concept, "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        concept = self.create_noun_with_grammatical_number_and_gender()
        singular, plural = concept.constituents
        singular_female, singular_male, plural_female, plural_male = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(singular_female, "nl", "en", "Haar kat", ["Her cat"], "read"),
                self.create_quiz(singular_female, "nl", "nl", "Haar kat", ["Haar kat"], "listen"),
                self.create_quiz(singular_female, "en", "nl", "Her cat", ["Haar kat"], "write"),
                self.create_quiz(singular_male, "nl", "en", "Zijn kat", ["His cat"], "read"),
                self.create_quiz(singular_male, "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"),
                self.create_quiz(singular_male, "en", "nl", "His cat", ["Zijn kat"], "write"),
                self.create_quiz(singular, "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz(singular, "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                self.create_quiz(plural_female, "nl", "en", "Haar katten", ["Her cats"], "read"),
                self.create_quiz(plural_female, "nl", "nl", "Haar katten", ["Haar katten"], "listen"),
                self.create_quiz(plural_female, "en", "nl", "Her cats", ["Haar katten"], "write"),
                self.create_quiz(plural_male, "nl", "en", "Zijn katten", ["His cats"], "read"),
                self.create_quiz(plural_male, "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"),
                self.create_quiz(plural_male, "en", "nl", "His cats", ["Zijn katten"], "write"),
                self.create_quiz(plural, "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                self.create_quiz(plural, "nl", "nl", "Zijn katten", ["Haar katten"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = self.create_adjective_with_degrees_of_comparison()
        positive_degree, comparative_degree, superlative_degree = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(positive_degree, "nl", "en", "Groot", ["Big"], "read"),
                self.create_quiz(positive_degree, "nl", "nl", "Groot", ["Groot"], "listen"),
                self.create_quiz(positive_degree, "en", "nl", "Big", ["Groot"], "write"),
                self.create_quiz(comparative_degree, "nl", "en", "Groter", ["Bigger"], "read"),
                self.create_quiz(comparative_degree, "nl", "nl", "Groter", ["Groter"], "listen"),
                self.create_quiz(comparative_degree, "en", "nl", "Bigger", ["Groter"], "write"),
                self.create_quiz(superlative_degree, "nl", "en", "Grootst", ["Biggest"], "read"),
                self.create_quiz(superlative_degree, "nl", "nl", "Grootst", ["Grootst"], "listen"),
                self.create_quiz(superlative_degree, "en", "nl", "Biggest", ["Grootst"], "write"),
                self.create_quiz(concept, "nl", "nl", "Groot", ["Groter"], "give comparative degree"),
                self.create_quiz(concept, "nl", "nl", "Groot", ["Grootst"], "give superlative degree"),
                self.create_quiz(concept, "nl", "nl", "Groter", ["Groot"], "give positive degree"),
                self.create_quiz(concept, "nl", "nl", "Groter", ["Grootst"], "give superlative degree"),
                self.create_quiz(concept, "nl", "nl", "Grootst", ["Groot"], "give positive degree"),
                self.create_quiz(concept, "nl", "nl", "Grootst", ["Groter"], "give comparative degree"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        concept = self.create_concept(
            "big",
            {
                "positive degree": dict(en="Big", fi=["Iso", "Suuri"]),
                "comparative degree": dict(en="Bigger", fi=["Isompi", "Suurempi"]),
                "superlative degree": dict(en="Biggest", fi=["Isoin", "Suurin"]),
            },
        )
        positive_degree, comparative_degree, superlative_degree = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(positive_degree, "fi", "en", "Iso", ["Big"], "read"),
                self.create_quiz(positive_degree, "fi", "en", "Suuri", ["Big"], "read"),
                self.create_quiz(positive_degree, "fi", "fi", "Iso", ["Iso"], "listen"),
                self.create_quiz(positive_degree, "fi", "fi", "Suuri", ["Suuri"], "listen"),
                self.create_quiz(positive_degree, "en", "fi", "Big", ["Iso", "Suuri"], "write"),
                self.create_quiz(comparative_degree, "fi", "en", "Isompi", ["Bigger"], "read"),
                self.create_quiz(comparative_degree, "fi", "en", "Suurempi", ["Bigger"], "read"),
                self.create_quiz(comparative_degree, "fi", "fi", "Isompi", ["Isompi"], "listen"),
                self.create_quiz(comparative_degree, "fi", "fi", "Suurempi", ["Suurempi"], "listen"),
                self.create_quiz(comparative_degree, "en", "fi", "Bigger", ["Isompi", "Suurempi"], "write"),
                self.create_quiz(superlative_degree, "fi", "en", "Isoin", ["Biggest"], "read"),
                self.create_quiz(superlative_degree, "fi", "en", "Suurin", ["Biggest"], "read"),
                self.create_quiz(superlative_degree, "fi", "fi", "Isoin", ["Isoin"], "listen"),
                self.create_quiz(superlative_degree, "fi", "fi", "Suurin", ["Suurin"], "listen"),
                self.create_quiz(superlative_degree, "en", "fi", "Biggest", ["Isoin", "Suurin"], "write"),
                self.create_quiz(concept, "fi", "fi", "Iso", ["Isompi"], "give comparative degree"),
                self.create_quiz(concept, "fi", "fi", "Suuri", ["Suurempi"], "give comparative degree"),
                self.create_quiz(concept, "fi", "fi", "Iso", ["Isoin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "Suuri", ["Suurin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "Isompi", ["Iso"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "Suurempi", ["Suuri"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "Isompi", ["Isoin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "Suurempi", ["Suurin"], "give superlative degree"),
                self.create_quiz(concept, "fi", "fi", "Isoin", ["Iso"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "Suurin", ["Suuri"], "give positive degree"),
                self.create_quiz(concept, "fi", "fi", "Isoin", ["Isompi"], "give comparative degree"),
                self.create_quiz(concept, "fi", "fi", "Suurin", ["Suurempi"], "give comparative degree"),
            },
            self.create_quizzes(concept, "fi", "en"),
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = self.create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", nl="Ik eet"),
                "second person": dict(en="You eat", nl="Jij eet"),
                "third person": dict(en="She eats", nl="Zij eet"),
            },
        )
        first_person, second_person, third_person = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(first_person, "nl", "en", "Ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "nl", "nl", "Ik eet", ["Ik eet"], "listen"),
                self.create_quiz(first_person, "en", "nl", "I eat", ["Ik eet"], "write"),
                self.create_quiz(second_person, "nl", "en", "Jij eet", ["You eat"], "read"),
                self.create_quiz(second_person, "nl", "nl", "Jij eet", ["Jij eet"], "listen"),
                self.create_quiz(second_person, "en", "nl", "You eat", ["Jij eet"], "write"),
                self.create_quiz(third_person, "nl", "en", "Zij eet", ["She eats"], "read"),
                self.create_quiz(third_person, "nl", "nl", "Zij eet", ["Zij eet"], "listen"),
                self.create_quiz(third_person, "en", "nl", "She eats", ["Zij eet"], "write"),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                self.create_quiz(concept, "nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                self.create_quiz(concept, "nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        concept = self.create_concept(
            "to eat",
            {
                "first person": dict(en="I eat", nl="Ik eet"),
                "second person": dict(en="You eat", nl="Jij eet"),
                "third person": dict(female=dict(en="She eats", nl="Zij eet"), male=dict(en="He eats", nl="Hij eet")),
            },
        )
        first_person, second_person, third_person = concept.constituents
        third_person_female, third_person_male = third_person.constituents
        self.assertEqual(
            {
                self.create_quiz(first_person, "nl", "en", "Ik eet", ["I eat"], "read"),
                self.create_quiz(first_person, "nl", "nl", "Ik eet", ["Ik eet"], "listen"),
                self.create_quiz(first_person, "en", "nl", "I eat", ["Ik eet"], "write"),
                self.create_quiz(second_person, "nl", "en", "Jij eet", ["You eat"], "read"),
                self.create_quiz(second_person, "nl", "nl", "Jij eet", ["Jij eet"], "listen"),
                self.create_quiz(second_person, "en", "nl", "You eat", ["Jij eet"], "write"),
                self.create_quiz(third_person_female, "nl", "en", "Zij eet", ["She eats"], "read"),
                self.create_quiz(third_person_female, "nl", "nl", "Zij eet", ["Zij eet"], "listen"),
                self.create_quiz(third_person_female, "en", "nl", "She eats", ["Zij eet"], "write"),
                self.create_quiz(third_person_male, "nl", "en", "Hij eet", ["He eats"], "read"),
                self.create_quiz(third_person_male, "nl", "nl", "Hij eet", ["Hij eet"], "listen"),
                self.create_quiz(third_person_male, "en", "nl", "He eats", ["Hij eet"], "write"),
                self.create_quiz(third_person, "nl", "nl", "Zij eet", ["Hij eet"], "masculinize"),
                self.create_quiz(third_person, "nl", "nl", "Hij eet", ["Zij eet"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Zij eet"], ("give third person", "feminize")),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Hij eet"], ("give third person", "masculinize")),
                self.create_quiz(concept, "nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "Jij eet", ["Zij eet"], ("give third person", "feminize")),
                self.create_quiz(concept, "nl", "nl", "Jij eet", ["Hij eet"], ("give third person", "masculinize")),
                self.create_quiz(concept, "nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "Hij eet", ["Ik eet"], "give first person"),
                self.create_quiz(concept, "nl", "nl", "Hij eet", ["Jij eet"], "give second person"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = self.create_concept(
            "to have",
            dict(
                singular={
                    "first person": dict(fi="Minulla on", nl="Ik heb"),
                    "second person": dict(fi="Sinulla on", nl="Jij hebt"),
                    "third person": dict(fi="Hänellä on", nl="Zij heeft"),
                },
                plural={
                    "first person": dict(fi="Meillä on", nl="Wij hebben"),
                    "second person": dict(fi="Teillä on", nl="Jullie hebben"),
                    "third person": dict(fi="Heillä on", nl="Zij hebben"),
                },
            ),
        )
        singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertEqual(
            {
                self.create_quiz(first_person_singular, "nl", "fi", "Ik heb", ["Minulla on"], "read"),
                self.create_quiz(first_person_singular, "fi", "nl", "Minulla on", ["Ik heb"], "write"),
                self.create_quiz(first_person_singular, "nl", "nl", "Ik heb", ["Ik heb"], "listen"),
                self.create_quiz(second_person_singular, "nl", "fi", "Jij hebt", ["Sinulla on"], "read"),
                self.create_quiz(second_person_singular, "fi", "nl", "Sinulla on", ["Jij hebt"], "write"),
                self.create_quiz(second_person_singular, "nl", "nl", "Jij hebt", ["Jij hebt"], "listen"),
                self.create_quiz(third_person_singular, "nl", "fi", "Zij heeft", ["Hänellä on"], "read"),
                self.create_quiz(third_person_singular, "fi", "nl", "Hänellä on", ["Zij heeft"], "write"),
                self.create_quiz(third_person_singular, "nl", "nl", "Zij heeft", ["Zij heeft"], "listen"),
                self.create_quiz(singular, "nl", "nl", "Ik heb", ["Jij hebt"], "give second person"),
                self.create_quiz(singular, "nl", "nl", "Ik heb", ["Zij heeft"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "Jij hebt", ["Ik heb"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "Jij hebt", ["Zij heeft"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "Zij heeft", ["Ik heb"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "Zij heeft", ["Jij hebt"], "give second person"),
                self.create_quiz(first_person_plural, "nl", "fi", "Wij hebben", ["Meillä on"], "read"),
                self.create_quiz(first_person_plural, "fi", "nl", "Meillä on", ["Wij hebben"], "write"),
                self.create_quiz(first_person_plural, "nl", "nl", "Wij hebben", ["Wij hebben"], "listen"),
                self.create_quiz(second_person_plural, "nl", "fi", "Jullie hebben", ["Teillä on"], "read"),
                self.create_quiz(second_person_plural, "fi", "nl", "Teillä on", ["Jullie hebben"], "write"),
                self.create_quiz(second_person_plural, "nl", "nl", "Jullie hebben", ["Jullie hebben"], "listen"),
                self.create_quiz(third_person_plural, "nl", "fi", "Zij hebben", ["Heillä on"], "read"),
                self.create_quiz(third_person_plural, "fi", "nl", "Heillä on", ["Zij hebben"], "write"),
                self.create_quiz(third_person_plural, "nl", "nl", "Zij hebben", ["Zij hebben"], "listen"),
                self.create_quiz(plural, "nl", "nl", "Wij hebben", ["Jullie hebben"], "give second person"),
                self.create_quiz(plural, "nl", "nl", "Wij hebben", ["Zij hebben"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "Jullie hebben", ["Wij hebben"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "Jullie hebben", ["Zij hebben"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "Zij hebben", ["Wij hebben"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "Zij hebben", ["Jullie hebben"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "Ik heb", ["Wij hebben"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Wij hebben", ["Ik heb"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Jij hebt", ["Jullie hebben"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Jullie hebben", ["Jij hebt"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Zij heeft", ["Zij hebben"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Zij hebben", ["Zij heeft"], "singularize"),
            },
            self.create_quizzes(concept, "nl", "fi"),
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        concept = self.create_concept(
            "cat",
            dict(
                female=dict(singular=dict(en="Her cat", nl="Haar kat"), plural=dict(en="Her cats", nl="Haar katten")),
                male=dict(singular=dict(en="His cat", nl="Zijn kat"), plural=dict(en="His cats", nl="Zijn katten")),
            ),
        )
        female, male = concept.constituents
        female_singular, female_plural, male_singular, male_plural = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(female_singular, "nl", "en", "Haar kat", ["Her cat"], "read"),
                self.create_quiz(female_singular, "nl", "nl", "Haar kat", ["Haar kat"], "listen"),
                self.create_quiz(female_singular, "en", "nl", "Her cat", ["Haar kat"], "write"),
                self.create_quiz(female_plural, "nl", "en", "Haar katten", ["Her cats"], "read"),
                self.create_quiz(female_plural, "nl", "nl", "Haar katten", ["Haar katten"], "listen"),
                self.create_quiz(female_plural, "en", "nl", "Her cats", ["Haar katten"], "write"),
                self.create_quiz(female, "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                self.create_quiz(female, "nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                self.create_quiz(male_singular, "nl", "en", "Zijn kat", ["His cat"], "read"),
                self.create_quiz(male_singular, "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"),
                self.create_quiz(male_singular, "en", "nl", "His cat", ["Zijn kat"], "write"),
                self.create_quiz(male_plural, "nl", "en", "Zijn katten", ["His cats"], "read"),
                self.create_quiz(male_plural, "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"),
                self.create_quiz(male_plural, "en", "nl", "His cats", ["Zijn katten"], "write"),
                self.create_quiz(male, "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                self.create_quiz(male, "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                self.create_quiz(concept, "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                self.create_quiz(concept, "nl", "nl", "Zijn katten", ["Haar katten"], "feminize"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        concept = self.create_concept(
            "to be",
            dict(female=dict(en="She is|She's", fi="Hän on;female"), male=dict(en="He is|He's", fi="Hän on;male")),
        )
        female, male = concept.constituents
        self.assertEqual(
            {
                self.create_quiz(female, "fi", "en", Label("Hän on;female"), ("She is|She's",), "read"),
                self.create_quiz(female, "fi", "fi", "Hän on;female", ("Hän on;female",), "listen"),
                self.create_quiz(female, "en", "fi", "She is|She's", ("Hän on;female",), "write"),
                self.create_quiz(male, "fi", "en", "Hän on;male", ("He is|He's",), "read"),
                self.create_quiz(male, "en", "fi", "He is|He's", ("Hän on;male",), "write"),
            },
            self.create_quizzes(concept, "fi", "en"),
        )

    def test_infinitive_verb_form(self):
        """Test the infinitive verb form."""
        concept = self.create_concept(
            "to sleep",
            dict(
                infinitive=dict(en="To sleep", nl="Slapen"),
                singular=dict(en="I sleep", nl="Ik slaap"),
                plural=dict(en="We sleep", nl="Wij slapen"),
            ),
        )
        infinitive, singular, plural = concept.constituents
        self.assertEqual(
            {
                self.create_quiz(infinitive, "nl", "en", "Slapen", ["To sleep"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "Slapen", ["Slapen"], "listen"),
                self.create_quiz(infinitive, "en", "nl", "To sleep", ["Slapen"], "write"),
                self.create_quiz(singular, "nl", "en", "Ik slaap", ["I sleep"], "read"),
                self.create_quiz(singular, "nl", "nl", "Ik slaap", ["Ik slaap"], "listen"),
                self.create_quiz(singular, "en", "nl", "I sleep", ["Ik slaap"], "write"),
                self.create_quiz(plural, "nl", "en", "Wij slapen", ["We sleep"], "read"),
                self.create_quiz(plural, "nl", "nl", "Wij slapen", ["Wij slapen"], "listen"),
                self.create_quiz(plural, "en", "nl", "We sleep", ["Wij slapen"], "write"),
                self.create_quiz(concept, "nl", "nl", "Wij slapen", ["Slapen"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "Ik slaap", ["Slapen"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "Slapen", ["Wij slapen"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Ik slaap", ["Wij slapen"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Slapen", ["Ik slaap"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Wij slapen", ["Ik slaap"], "singularize"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_grammatical_number_nested_with_grammatical_person_and_infinitive(self):
        """Test generating quizzes for grammatical number, including infinitive, nested with grammatical person."""
        concept = self.create_concept(
            "to be",
            dict(
                infinitive=dict(fi="Olla", nl="Zijn"),
                singular={
                    "first person": dict(fi="Minä olen", nl="Ik ben"),
                    "second person": dict(fi="Sinä olet", nl="Jij bent"),
                    "third person": dict(fi="Hän on", nl="Zij is"),
                },
                plural={
                    "first person": dict(fi="Me olemme", nl="Wij zijn"),
                    "second person": dict(fi="Te olette", nl="Jullie zijn"),
                    "third person": dict(fi="He ovat", nl="Zij zijn"),
                },
            ),
        )
        infinitive, singular, plural = concept.constituents
        first_person_singular, second_person_singular, third_person_singular = singular.constituents
        first_person_plural, second_person_plural, third_person_plural = plural.constituents
        self.assertEqual(
            {
                self.create_quiz(first_person_singular, "nl", "fi", "Ik ben", ["Minä olen"], "read"),
                self.create_quiz(first_person_singular, "nl", "nl", "Ik ben", ["Ik ben"], "listen"),
                self.create_quiz(first_person_singular, "fi", "nl", "Minä olen", ["Ik ben"], "write"),
                self.create_quiz(concept, "nl", "nl", "Ik ben", ["Zijn"], "give infinitive"),
                self.create_quiz(second_person_singular, "nl", "fi", "Jij bent", ["Sinä olet"], "read"),
                self.create_quiz(second_person_singular, "nl", "nl", "Jij bent", ["Jij bent"], "listen"),
                self.create_quiz(second_person_singular, "fi", "nl", "Sinä olet", ["Jij bent"], "write"),
                self.create_quiz(concept, "nl", "nl", "Jij bent", ["Zijn"], "give infinitive"),
                self.create_quiz(third_person_singular, "nl", "fi", "Zij is", ["Hän on"], "read"),
                self.create_quiz(third_person_singular, "nl", "nl", "Zij is", ["Zij is"], "listen"),
                self.create_quiz(third_person_singular, "fi", "nl", "Hän on", ["Zij is"], "write"),
                self.create_quiz(concept, "nl", "nl", "Zij is", ["Zijn"], "give infinitive"),
                self.create_quiz(singular, "nl", "nl", "Ik ben", ["Jij bent"], "give second person"),
                self.create_quiz(singular, "nl", "nl", "Ik ben", ["Zij is"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "Jij bent", ["Ik ben"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "Jij bent", ["Zij is"], "give third person"),
                self.create_quiz(singular, "nl", "nl", "Zij is", ["Ik ben"], "give first person"),
                self.create_quiz(singular, "nl", "nl", "Zij is", ["Jij bent"], "give second person"),
                self.create_quiz(first_person_plural, "nl", "fi", "Wij zijn", ["Me olemme"], "read"),
                self.create_quiz(first_person_plural, "nl", "nl", "Wij zijn", ["Wij zijn"], "listen"),
                self.create_quiz(first_person_plural, "fi", "nl", "Me olemme", ["Wij zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "Wij zijn", ["Zijn"], "give infinitive"),
                self.create_quiz(second_person_plural, "nl", "fi", "Jullie zijn", ["Te olette"], "read"),
                self.create_quiz(second_person_plural, "nl", "nl", "Jullie zijn", ["Jullie zijn"], "listen"),
                self.create_quiz(second_person_plural, "fi", "nl", "Te olette", ["Jullie zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "Jullie zijn", ["Zijn"], "give infinitive"),
                self.create_quiz(third_person_plural, "nl", "fi", "Zij zijn", ["He ovat"], "read"),
                self.create_quiz(third_person_plural, "nl", "nl", "Zij zijn", ["Zij zijn"], "listen"),
                self.create_quiz(third_person_plural, "fi", "nl", "He ovat", ["Zij zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "Zij zijn", ["Zijn"], "give infinitive"),
                self.create_quiz(plural, "nl", "nl", "Wij zijn", ["Jullie zijn"], "give second person"),
                self.create_quiz(plural, "nl", "nl", "Wij zijn", ["Zij zijn"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "Jullie zijn", ["Wij zijn"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "Jullie zijn", ["Zij zijn"], "give third person"),
                self.create_quiz(plural, "nl", "nl", "Zij zijn", ["Wij zijn"], "give first person"),
                self.create_quiz(plural, "nl", "nl", "Zij zijn", ["Jullie zijn"], "give second person"),
                self.create_quiz(concept, "nl", "nl", "Ik ben", ["Wij zijn"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Wij zijn", ["Ik ben"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Jij bent", ["Jullie zijn"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Jullie zijn", ["Jij bent"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Zij is", ["Zij zijn"], "pluralize"),
                self.create_quiz(concept, "nl", "nl", "Zij zijn", ["Zij is"], "singularize"),
                self.create_quiz(infinitive, "nl", "fi", "Zijn", ["Olla"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "Zijn", ["Zijn"], "listen"),
                self.create_quiz(infinitive, "fi", "nl", "Olla", ["Zijn"], "write"),
                self.create_quiz(concept, "nl", "nl", "Zijn", ["Ik ben"], ("singularize", "give first person")),
                self.create_quiz(concept, "nl", "nl", "Zijn", ["Jij bent"], ("singularize", "give second person")),
                self.create_quiz(concept, "nl", "nl", "Zijn", ["Zij is"], ("singularize", "give third person")),
                self.create_quiz(concept, "nl", "nl", "Zijn", ["Wij zijn"], ("pluralize", "give first person")),
                self.create_quiz(concept, "nl", "nl", "Zijn", ["Jullie zijn"], ("pluralize", "give second person")),
                self.create_quiz(concept, "nl", "nl", "Zijn", ["Zij zijn"], ("pluralize", "give third person")),
            },
            self.create_quizzes(concept, "nl", "fi"),
        )


class TenseQuizzesTest(QuizFactoryTestCase):
    """Unit tests for concepts with tenses."""

    def test_tense_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for tense nested with grammatical person."""
        concept = self.create_verb_with_tense_and_person()
        present, past = concept.constituents
        present_singular, present_plural, past_singular, past_plural = concept.leaf_concepts()
        self.assertEqual(
            {
                self.create_quiz(present_singular, "nl", "en", "Ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "nl", "nl", "Ik eet", ["Ik eet"], "listen"),
                self.create_quiz(present_singular, "en", "nl", "I eat", ["Ik eet"], "write"),
                self.create_quiz(present_plural, "nl", "en", "Wij eten", ["We eat"], "read"),
                self.create_quiz(present_plural, "nl", "nl", "Wij eten", ["Wij eten"], "listen"),
                self.create_quiz(present_plural, "en", "nl", "We eat", ["Wij eten"], "write"),
                self.create_quiz(present, "nl", "nl", "Ik eet", ["Wij eten"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "Wij eten", ["Ik eet"], "singularize"),
                self.create_quiz(past_singular, "nl", "en", "Ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "nl", "nl", "Ik at", ["Ik at"], "listen"),
                self.create_quiz(past_singular, "en", "nl", "I ate", ["Ik at"], "write"),
                self.create_quiz(past_plural, "nl", "en", "Wij aten", ["We ate"], "read"),
                self.create_quiz(past_plural, "nl", "nl", "Wij aten", ["Wij aten"], "listen"),
                self.create_quiz(past_plural, "en", "nl", "We ate", ["Wij aten"], "write"),
                self.create_quiz(past, "nl", "nl", "Ik at", ["Wij aten"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "Wij aten", ["Ik at"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Ik at"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "Wij eten", ["Wij aten"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "Ik at", ["Ik eet"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "Wij aten", ["Wij eten"], "give present tense"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )

    def test_tense_nested_with_grammatical_person_and_infinitive(self):
        """Test that quizzes can be generated for tense nested with grammatical person and infinitive."""
        concept = self.create_concept(
            "to eat",
            {
                "infinitive": dict(en="To eat", nl="Eten"),
                "present tense": dict(singular=dict(en="I eat", nl="Ik eet"), plural=dict(en="We eat", nl="Wij eten")),
                "past tense": dict(singular=dict(en="I ate", nl="Ik at"), plural=dict(en="We ate", nl="Wij aten")),
            },
        )
        infinitive, present, past = concept.constituents
        present_singular, present_plural = present.constituents
        past_singular, past_plural = past.constituents
        self.assertEqual(
            {
                self.create_quiz(present_singular, "nl", "en", "Ik eet", ["I eat"], "read"),
                self.create_quiz(present_singular, "nl", "nl", "Ik eet", ["Ik eet"], "listen"),
                self.create_quiz(present_singular, "en", "nl", "I eat", ["Ik eet"], "write"),
                self.create_quiz(present_plural, "nl", "en", "Wij eten", ["We eat"], "read"),
                self.create_quiz(present_plural, "nl", "nl", "Wij eten", ["Wij eten"], "listen"),
                self.create_quiz(present_plural, "en", "nl", "We eat", ["Wij eten"], "write"),
                self.create_quiz(present, "nl", "nl", "Ik eet", ["Wij eten"], "pluralize"),
                self.create_quiz(present, "nl", "nl", "Wij eten", ["Ik eet"], "singularize"),
                self.create_quiz(past_singular, "nl", "en", "Ik at", ["I ate"], "read"),
                self.create_quiz(past_singular, "nl", "nl", "Ik at", ["Ik at"], "listen"),
                self.create_quiz(past_singular, "en", "nl", "I ate", ["Ik at"], "write"),
                self.create_quiz(past_plural, "nl", "en", "Wij aten", ["We ate"], "read"),
                self.create_quiz(past_plural, "nl", "nl", "Wij aten", ["Wij aten"], "listen"),
                self.create_quiz(past_plural, "en", "nl", "We ate", ["Wij aten"], "write"),
                self.create_quiz(past, "nl", "nl", "Ik at", ["Wij aten"], "pluralize"),
                self.create_quiz(past, "nl", "nl", "Wij aten", ["Ik at"], "singularize"),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Ik at"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "Wij eten", ["Wij aten"], "give past tense"),
                self.create_quiz(concept, "nl", "nl", "Ik at", ["Ik eet"], "give present tense"),
                self.create_quiz(concept, "nl", "nl", "Wij aten", ["Wij eten"], "give present tense"),
                self.create_quiz(infinitive, "nl", "en", "Eten", ["To eat"], "read"),
                self.create_quiz(infinitive, "nl", "nl", "Eten", ["Eten"], "listen"),
                self.create_quiz(infinitive, "en", "nl", "To eat", ["Eten"], "write"),
                self.create_quiz(concept, "nl", "nl", "Eten", ["Ik eet"], ("give present tense", "singularize")),
                self.create_quiz(concept, "nl", "nl", "Eten", ["Ik at"], ("give past tense", "singularize")),
                self.create_quiz(concept, "nl", "nl", "Eten", ["Wij eten"], ("give present tense", "pluralize")),
                self.create_quiz(concept, "nl", "nl", "Eten", ["Wij aten"], ("give past tense", "pluralize")),
                self.create_quiz(concept, "nl", "nl", "Ik eet", ["Eten"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "Wij eten", ["Eten"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "Ik at", ["Eten at"], "give infinitive"),
                self.create_quiz(concept, "nl", "nl", "Wij aten", ["Eten at"], "give infinitive"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )


class SentenceFormTest(ToistoTestCase):
    """Unit tests for concepts with different sentence forms."""

    def test_declarative_and_interrogative_sentence_types(self):
        """Test that quizzes can be generated for the declarative and interrogative sentence forms."""
        concept = self.create_concept(
            "car",
            {
                "declarative": dict(en="The car is black", nl="De auto is zwart"),
                "interrogative": dict(en="Is the car black?", nl="Is de auto zwart?"),
            },
        )
        declarative, interrogative = concept.constituents
        self.assertEqual(
            {
                self.create_quiz(declarative, "nl", "en", "De auto is zwart", ["The car is black"], "read"),
                self.create_quiz(declarative, "nl", "nl", "De auto is zwart", ["De auto is zwart"], "listen"),
                self.create_quiz(declarative, "en", "nl", "The car is black", ["De auto is zwart"], "write"),
                self.create_quiz(interrogative, "nl", "en", "Is de auto zwart?", ["Is the car black?"], "read"),
                self.create_quiz(interrogative, "nl", "nl", "Is de auto zwart?", ["Is de auto zwart?"], "listen"),
                self.create_quiz(interrogative, "en", "nl", "Is the car black?", ["Is de auto zwart?"], "write"),
                self.create_quiz(concept, "nl", "nl", "De auto is zwart", ["Is de auto zwart"], "make interrogative"),
                self.create_quiz(concept, "nl", "nl", "Is de auto zwart?", ["De auto is zwart"], "make declarative"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )


class GrammaticalPolarityTest(ToistoTestCase):
    """Unit tests for concepts with different grammatical polarities."""

    def test_affirmative_and_negative_polarities(self):
        """Test that quizzes can be generated for the affirmative and negative polarities."""
        concept = self.create_concept(
            "car",
            {
                "affirmative": dict(en="The car is black", nl="De auto is zwart"),
                "negative": dict(en="The car is not black", nl="De auto is niet zwart"),
            },
        )
        affirmative, negative = concept.constituents
        self.assertEqual(
            {
                self.create_quiz(affirmative, "nl", "en", "De auto is zwart", ["The car is black"], "read"),
                self.create_quiz(affirmative, "nl", "nl", "De auto is zwart", ["De auto is zwart"], "listen"),
                self.create_quiz(affirmative, "en", "nl", "The car is black", ["De auto is zwart"], "write"),
                self.create_quiz(negative, "nl", "en", "De auto is niet zwart", ["The car is not black"], "read"),
                self.create_quiz(negative, "nl", "nl", "De auto is niet zwart", ["De auto is niet zwart"], "listen"),
                self.create_quiz(negative, "en", "nl", "The car is not black", ["De auto is niet zwart"], "write"),
                self.create_quiz(concept, "nl", "nl", "De auto is zwart", ["De auto is niet zwart"], "negate"),
                self.create_quiz(concept, "nl", "nl", "De auto is niet zwart", ["De auto is zwart"], "affirm"),
            },
            self.create_quizzes(concept, "nl", "en"),
        )
