"""Concept unit tests."""

import unittest

from toisto.model import concept_factory, Quiz


class ConceptTest(unittest.TestCase):
    """Unit tests for the concept class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from a concept."""
        concept = concept_factory(dict(en=["English"], nl=["Engels"]))
        self.assertEqual(
            [
                Quiz("nl", "en", "Engels", ["English"]),
                Quiz("en", "nl", "English", ["Engels"])
            ],
            concept.quizzes("nl", "en")
        )

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        concept = concept_factory(dict(nl=["Bank"], en=["Couch", "Bank"]))
        self.assertEqual(
            [
                Quiz("nl", "en", "Bank", ["Couch", "Bank"]),
                Quiz("en", "nl", "Couch", ["Bank"]),
                Quiz("en", "nl", "Bank", ["Bank"])
            ],
            concept.quizzes("nl", "en")
        )

    def test_missing_language(self):
        """Test that quizzes can be generated from a concept even if it's missing one of the languages."""
        concept = concept_factory(dict(en=["English"], nl=["Engels"]))
        self.assertEqual([], concept.quizzes("fi", "en"))

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        concept = concept_factory(
            dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        self.assertEqual(
            [
                Quiz("fi", "nl", "Aamu", ["De ochtend"]),
                Quiz("nl", "fi", "De ochtend", ["Aamu"]),
                Quiz("fi", "nl", "Aamut", ["De ochtenden"]),
                Quiz("nl", "fi", "De ochtenden", ["Aamut"]),
                Quiz("fi", "fi", "Aamu", ["Aamut"], "pluralize"),
                Quiz("fi", "fi", "Aamut", ["Aamu"], "singularize")
            ],
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        concept = concept_factory(dict(singular=dict(fi="Ketsuppi", nl="De ketchup"), plural=dict(fi="Ketsupit")))
        self.assertEqual(
            [
                Quiz("fi", "nl", "Ketsuppi", ["De ketchup"]),
                Quiz("nl", "fi", "De ketchup", ["Ketsuppi"]),
                Quiz("fi", "fi", "Ketsuppi", ["Ketsupit"], "pluralize"),
                Quiz("fi", "fi", "Ketsupit", ["Ketsuppi"], "singularize")
            ],
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the practice language only."""
        concept = concept_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(
            [
                Quiz("fi", "fi", "Mämmi", ["Mämmit"], "pluralize"),
                Quiz("fi", "fi", "Mämmit", ["Mämmi"], "singularize")
            ],
            concept.quizzes("fi", "en")
        )

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes can be generated from a noun concept with labels in the native language."""
        concept = concept_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual([], concept.quizzes("en", "fi"))

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat"))
        )
        self.assertEqual(
            [
                Quiz("nl", "en", "Haar kat", ["Her cat"], "translate"),
                Quiz("en", "nl", "Her cat", ["Haar kat"], "translate"),
                Quiz("nl", "en", "Zijn kat", ["His cat"], "translate"),
                Quiz("en", "nl", "His cat", ["Zijn kat"], "translate"),
                Quiz("nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                Quiz("nl", "nl", "Zijn kat", ["Haar kat"], "feminize")
            ],
            concept.quizzes("nl", "en")
        )

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = concept_factory(
            dict(
                positive_degree=dict(en="Big", nl="Groot"),
                comparitive_degree=dict(en="Bigger", nl="Groter"),
                superlative_degree=dict(en="Biggest", nl="Grootst")
            )
        )
        self.assertEqual(
            [
                Quiz("nl", "en", "Groot", ["Big"], "translate"),
                Quiz("en", "nl", "Big", ["Groot"], "translate"),
                Quiz("nl", "en", "Groter", ["Bigger"], "translate"),
                Quiz("en", "nl", "Bigger", ["Groter"], "translate"),
                Quiz("nl", "en", "Grootst", ["Biggest"], "translate"),
                Quiz("en", "nl", "Biggest", ["Grootst"], "translate"),
                Quiz("nl", "nl", "Groot", ["Groter"], "give comparitive degree"),
                Quiz("nl", "nl", "Groot", ["Grootst"], "give superlative degree"),
                Quiz("nl", "nl", "Groter", ["Groot"], "give positive degree"),
                Quiz("nl", "nl", "Groter", ["Grootst"], "give superlative degree"),
                Quiz("nl", "nl", "Grootst", ["Groot"], "give positive degree"),
                Quiz("nl", "nl", "Grootst", ["Groter"], "give comparitive degree"),
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = concept_factory(
            dict(
                first_person=dict(en="I eat", nl="Ik eet"),
                second_person=dict(en="You eat", nl="Jij eet"),
                third_person=dict(en="She eats", nl="Zij eet")
            )
        )
        self.assertEqual(
            [
                Quiz("nl", "en", "Ik eet", ["I eat"], "translate"),
                Quiz("en", "nl", "I eat", ["Ik eet"], "translate"),
                Quiz("nl", "en", "Jij eet", ["You eat"], "translate"),
                Quiz("en", "nl", "You eat", ["Jij eet"], "translate"),
                Quiz("nl", "en", "Zij eet", ["She eats"], "translate"),
                Quiz("en", "nl", "She eats", ["Zij eet"], "translate"),
                Quiz("nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                Quiz("nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                Quiz("nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                Quiz("nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                Quiz("nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                Quiz("nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        concept = concept_factory(
            dict(
                first_person=dict(en="I eat", nl="Ik eet"),
                second_person=dict(en="You eat", nl="Jij eet"),
                third_person=dict(female=dict(en="She eats", nl="Zij eet"), male=dict(en="He eats", nl="Hij eet"))
            )
        )
        self.assertEqual(
            [
                Quiz("nl", "en", "Ik eet", ["I eat"], "translate"),
                Quiz("en", "nl", "I eat", ["Ik eet"], "translate"),
                Quiz("nl", "en", "Jij eet", ["You eat"], "translate"),
                Quiz("en", "nl", "You eat", ["Jij eet"], "translate"),
                Quiz("nl", "en", "Zij eet", ["She eats"], "translate"),
                Quiz("en", "nl", "She eats", ["Zij eet"], "translate"),
                Quiz("nl", "en", "Hij eet", ["He eats"], "translate"),
                Quiz("en", "nl", "He eats", ["Hij eet"], "translate"),
                Quiz("nl", "nl", "Zij eet", ["Hij eet"], "masculinize"),
                Quiz("nl", "nl", "Hij eet", ["Zij eet"], "feminize"),
                Quiz("nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                Quiz("nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                Quiz("nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                Quiz("nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                Quiz("nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                Quiz("nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            ],
            concept.quizzes("nl", "en")
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = concept_factory(
            dict(
                singular=dict(
                    first_person=dict(fi="Minulla on", nl="Ik heb"),
                    second_person=dict(fi="Sinulla on", nl="Jij hebt"),
                    third_person=dict(fi="Hänellä on", nl="Zij heeft"),
                ),
                plural=dict(
                    first_person=dict(fi="Meillä on", nl="Wij hebben"),
                    second_person=dict(fi="Teillä on", nl="Jullie hebben"),
                    third_person=dict(fi="Heillä on", nl="Zij hebben"),
                )
            )
        )
        self.assertEqual(
            [
                Quiz("nl", "fi", "Ik heb", ["Minulla on"], "translate"),
                Quiz("fi", "nl", "Minulla on", ["Ik heb"], "translate"),
                Quiz("nl", "fi", "Jij hebt", ["Sinulla on"], "translate"),
                Quiz("fi", "nl", "Sinulla on", ["Jij hebt"], "translate"),
                Quiz("nl", "fi", "Zij heeft", ["Hänellä on"], "translate"),
                Quiz("fi", "nl", "Hänellä on", ["Zij heeft"], "translate"),
                Quiz("nl", "nl", "Ik heb", ["Jij hebt"], "give second person"),
                Quiz("nl", "nl", "Ik heb", ["Zij heeft"], "give third person"),
                Quiz("nl", "nl", "Jij hebt", ["Ik heb"], "give first person"),
                Quiz("nl", "nl", "Jij hebt", ["Zij heeft"], "give third person"),
                Quiz("nl", "nl", "Zij heeft", ["Ik heb"], "give first person"),
                Quiz("nl", "nl", "Zij heeft", ["Jij hebt"], "give second person"),
                Quiz("nl", "fi", "Wij hebben", ["Meillä on"], "translate"),
                Quiz("fi", "nl", "Meillä on", ["Wij hebben"], "translate"),
                Quiz("nl", "fi", "Jullie hebben", ["Teillä on"], "translate"),
                Quiz("fi", "nl", "Teillä on", ["Jullie hebben"], "translate"),
                Quiz("nl", "fi", "Zij hebben", ["Heillä on"], "translate"),
                Quiz("fi", "nl", "Heillä on", ["Zij hebben"], "translate"),
                Quiz("nl", "nl", "Wij hebben", ["Jullie hebben"], "give second person"),
                Quiz("nl", "nl", "Wij hebben", ["Zij hebben"], "give third person"),
                Quiz("nl", "nl", "Jullie hebben", ["Wij hebben"], "give first person"),
                Quiz("nl", "nl", "Jullie hebben", ["Zij hebben"], "give third person"),
                Quiz("nl", "nl", "Zij hebben", ["Wij hebben"], "give first person"),
                Quiz("nl", "nl", "Zij hebben", ["Jullie hebben"], "give second person"),
                Quiz("nl", "nl", "Ik heb", ["Wij hebben"], "pluralize"),
                Quiz("nl", "nl", "Wij hebben", ["Ik heb"], "singularize"),
                Quiz("nl", "nl", "Jij hebt", ["Jullie hebben"], "pluralize"),
                Quiz("nl", "nl", "Jullie hebben", ["Jij hebt"], "singularize"),
                Quiz("nl", "nl", "Zij heeft", ["Zij hebben"], "pluralize"),
                Quiz("nl", "nl", "Zij hebben", ["Zij heeft"], "singularize"),
            ],
            concept.quizzes("nl", "fi")
        )

    def test_nested_concepts(self):
        """Test that quizzes can be generated for nested concepts."""
        concept = concept_factory(
            dict(
                male=dict(singular=dict(en="His cat", nl="Zijn kat"), plural=dict(en="His cats", nl="Zijn katten")),
                female=dict(singular=dict(en="Her cat", nl="Haar kat"), plural=dict(en="Her cats", nl="Haar katten"))
            )
        )
        self.assertEqual(
            [
                Quiz("nl", "en", "Haar kat", ["Her cat"], "translate"),
                Quiz("en", "nl", "Her cat", ["Haar kat"], "translate"),
                Quiz("nl", "en", "Haar katten", ["Her cats"], "translate"),
                Quiz("en", "nl", "Her cats", ["Haar katten"], "translate"),
                Quiz("nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                Quiz("nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                Quiz("nl", "en", "Zijn kat", ["His cat"], "translate"),
                Quiz("en", "nl", "His cat", ["Zijn kat"], "translate"),
                Quiz("nl", "en", "Zijn katten", ["His cats"], "translate"),
                Quiz("en", "nl", "His cats", ["Zijn katten"], "translate"),
                Quiz("nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                Quiz("nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"),
                Quiz("nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                Quiz("nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                Quiz("nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                Quiz("nl", "nl", "Zijn katten", ["Haar katten"], "feminize")
            ],
            concept.quizzes("nl", "en")
        )
