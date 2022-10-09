"""Unit tests for the output."""

import unittest

from toisto.color import green, grey
from toisto.model import Entry, Progress
from toisto.output import feedback


class FeedbackTestCase(unittest.TestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.entry = Entry("nl", "fi", "Hoi", "Terve")
        self.progress = Progress({})

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.assertEqual("✅ Correct.\n", feedback(self.entry, True, "terve", self.progress))

    def test_correct_second_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.progress.update(self.entry, True)
        self.progress.update(self.entry, True)
        self.assertEqual(
            f"✅ Correct{grey(', 2 times in a row.')}\n", feedback(self.entry, True, "terve", self.progress)
        )

    def test_incorrect(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        self.assertEqual(
            f"""❌ Incorrect. The correct answer is "{green('Terve')}".\n""",
            feedback(self.entry, False, "", self.progress)
        )
