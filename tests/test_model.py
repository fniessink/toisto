"""Model unit tests."""

import unittest

from toisto.model import Entry, Progress


class EntryTest(unittest.TestCase):
    """Unit tests for the entry class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.entry = Entry("en", "nl", "English", "Engels")

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.entry.is_correct("engels"))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.entry.is_correct("engles"))

    def test_reversed(self):
        """Test that an entry can be reversed."""
        self.assertEqual(Entry("nl", "en", "Engels", "English"), self.entry.reversed())

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual("Engels", self.entry.get_answer())

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        entry = Entry("en", "nl", "One", ["Een", "Eén"])
        self.assertEqual("Een", entry.get_answer())

    def test_get_question(self):
        """Test that the question is returned."""
        self.assertEqual("English", self.entry.get_question())

    def test_get_first_question(self):
        """Test that the first answer is returned when there are multiple."""
        entry = Entry("en", "nl", "One", ["Een", "Eén"]).reversed()
        self.assertEqual("Een", entry.get_question())


class ProgressTest(unittest.TestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.entry = Entry("en", "nl", "English", "Engels")
        self.progress = Progress({})

    def test_progress_new_entry(self):
        """Test that the progress of an entry without progress."""
        self.assertEqual(0, self.progress.get_progress(self.entry))

    def test_update_progress_correct(self):
        """Test that the progress of an entry can be updated."""
        self.progress.update(self.entry, correct=True)
        self.assertEqual(2, self.progress.get_progress(self.entry))

    def test_update_progress_incorrect(self):
        """Test that the progress of an entry can be updated."""
        self.progress.update(self.entry, correct=False)
        self.assertEqual(-1, self.progress.get_progress(self.entry))

    def test_next_entry(self):
        """Test that the next entry has the lowest score."""
        self.progress.update(self.entry, correct=True)
        reversed_entry = self.entry.reversed()
        self.progress.update(reversed_entry, correct=False)
        self.assertEqual(reversed_entry, self.progress.next_entry([self.entry, reversed_entry]))

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
