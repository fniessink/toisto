"""Progress unit tests."""

import unittest

from toisto.model import Progress, Quiz


class ProgressTest(unittest.TestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("en", "nl", "English", ["Engels"])
        self.progress = Progress({})

    def test_progress_new_entry(self):
        """Test that the progress of a quiz without progress."""
        self.assertEqual(0, self.progress.get_progress(self.quiz).count)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.update(self.quiz, correct=True)
        self.assertEqual(1, self.progress.get_progress(self.quiz).count)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.update(self.quiz, correct=False)
        self.assertEqual(0, self.progress.get_progress(self.quiz).count)

    def test_next_quiz(self):
        """Test that the next quiz has the lowest score."""
        self.progress.update(self.quiz, correct=True)
        another_quiz = Quiz("nl", "en", "Engels", "English")
        self.progress.update(another_quiz, correct=False)
        self.assertEqual(another_quiz, self.progress.next_quiz([self.quiz, another_quiz]))

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        self.progress.update(self.quiz, correct=True)
        self.progress.update(self.quiz, correct=True)
        self.assertEqual(None, self.progress.next_quiz([self.quiz]))

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
