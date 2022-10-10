"""Unit tests for the output."""

import unittest

from toisto.color import green
from toisto.model import Entry, Progress
from toisto.output import feedback


class FeedbackTestCase(unittest.TestCase):
    """Unit tests for the feedback function."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.entry = Entry("nl", "fi", "Hoi", "Terve")
        self.progress = Progress({})

    def update_progress(self, nr_correct: int) -> None:
        """Update the progress with a number of correct guess."""
        for _ in range(nr_correct):
            self.progress.update(self.entry, True)

    def assert_feedback_contains(self, feedback_text: str, *expected_strings: str) -> None:
        """Assert that the expected strings are in the feedback."""
        for expected_string in expected_strings:
            self.assertIn(expected_string, feedback_text)

    def test_correct_first_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        feedback_text = feedback(True, "terve", "Terve", self.progress.get_progress(self.entry))
        self.assertEqual("✅ Correct.\n", feedback_text)

    def test_correct_second_time(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(2)
        feedback_text = feedback(True, "terve", "Terve", self.progress.get_progress(self.entry))
        self.assert_feedback_contains(feedback_text, ", 2 times in a row. I won't quiz", "minutes")

    def test_correct_silenced_for_hours(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(10)
        feedback_text = feedback(True, "terve", "Terve", self.progress.get_progress(self.entry))
        self.assert_feedback_contains(feedback_text, ", 10 times in a row. I won't quiz", "hours")

    def test_correct_silenced_for_days(self):
        """Test that the correct feedback is given when the user guesses correctly."""
        self.update_progress(20)
        feedback_text = feedback(True, "terve", "Terve", self.progress.get_progress(self.entry))
        self.assert_feedback_contains(feedback_text, ", 20 times in a row. I won't quiz", "days")

    def test_incorrect(self):
        """Test that the correct feedback is given when the user guesses incorrectly."""
        feedback_text = feedback(False, "", "Terve", self.progress.get_progress(self.entry))
        self.assertEqual(f"""❌ Incorrect. The correct answer is "{green('Terve')}".\n""", feedback_text)
