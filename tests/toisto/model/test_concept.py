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

    def test_noun_concept(self):
        """Test that quizzes can be generated from a noun concept."""
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

    def test_noun_concept_with_missing_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the noun concept."""
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

    def test_noun_concept_with_one_language(self):
        """Test that quizzes can be generated from a noun concept with labels in the practice language."""
        concept = concept_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(
            [
                Quiz("fi", "fi", "Mämmi", ["Mämmit"], "pluralize"),
                Quiz("fi", "fi", "Mämmit", ["Mämmi"], "singularize")
            ],
            concept.quizzes("fi", "en")
        )

    def test_noun_concept_with_one_language_reversed(self):
        """Test that no quizzes can be generated from a noun concept with labels in the native language."""
        concept = concept_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual([], concept.quizzes("en", "fi"))
