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
