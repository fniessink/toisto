"""Entry unit tests."""

import unittest

from toisto.model import entry_factory, Quiz


class EntryTest(unittest.TestCase):
    """Unit tests for the entry class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from an entry."""
        entry = entry_factory(dict(en=["English"], nl=["Engels"]))
        self.assertEqual(
            [
                Quiz("nl", "en", "Engels", ["English"]),
                Quiz("en", "nl", "English", ["Engels"])
            ],
            entry.quizzes("nl", "en")
        )

    def test_multiple_answers(self):
        """Test that quizzes can be generated from an entry with multiple answers."""
        entry = entry_factory(dict(nl=["Bank"], en=["Couch", "Bank"]))
        self.assertEqual(
            [
                Quiz("nl", "en", "Bank", ["Couch", "Bank"]),
                Quiz("en", "nl", "Couch", ["Bank"]),
                Quiz("en", "nl", "Bank", ["Bank"])
            ],
            entry.quizzes("nl", "en")
        )

    def test_noun(self):
        """Test that quizzes can be generated from a noun entry."""
        entry = entry_factory(
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
            entry.quizzes("fi", "nl")
        )

    def test_noun_with_missing_plural(self):
        """Test that quizzes can be generated even if one language has no plural for the noun."""
        entry = entry_factory(dict(singular=dict(fi="Ketsuppi", nl="De ketchup"), plural=dict(fi="Ketsupit")))
        self.assertEqual(
            [
                Quiz("fi", "nl", "Ketsuppi", ["De ketchup"]),
                Quiz("nl", "fi", "De ketchup", ["Ketsuppi"]),
                Quiz("fi", "fi", "Ketsuppi", ["Ketsupit"], "pluralize"),
                Quiz("fi", "fi", "Ketsupit", ["Ketsuppi"], "singularize")
            ],
            entry.quizzes("fi", "nl")
        )

    def test_noun_with_one_language(self):
        """Test that quizzes can be generated from a noun with one language."""
        entry = entry_factory(dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(
            [
                Quiz("fi", "fi", "Mämmi", ["Mämmit"], "pluralize"),
                Quiz("fi", "fi", "Mämmit", ["Mämmi"], "singularize")
            ],
            entry.quizzes("fi", "en")
        )
