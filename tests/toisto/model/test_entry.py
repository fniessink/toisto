"""Entry unit tests."""

import unittest

from toisto.model import Entry, Quiz


class EntryTest(unittest.TestCase):
    """Unit tests for the entry class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from an entry."""
        entry = Entry("en", "nl", ["English"], ["Engels"])
        self.assertEqual(
            [Quiz("en", "nl", "English", ["Engels"]), Quiz("nl", "en", "Engels", ["English"])], entry.quizzes()
        )

    def test_multiple_answers(self):
        """Test that quizzes can be generated from an entry."""
        entry = Entry("nl", "en", ["Bank"], ["Couch", "Bank"])
        self.assertEqual(
            [
                Quiz("nl", "en", "Bank", ["Couch", "Bank"]),
                Quiz("en", "nl", "Couch", ["Bank"]),
                Quiz("en", "nl", "Bank", ["Bank"])
            ],
            entry.quizzes()
        )
