"""Quiz progress unit tests."""

from datetime import datetime, timedelta
import unittest

from toisto.model import QuizProgress


class QuizProgressTest(unittest.TestCase):
    """Unit tests for the quiz progress class."""

    def setUp(self) -> None:
        """Override to set up fixtures."""
        self.quiz_progress = QuizProgress()

    def guess(self, *guesses: bool) -> None:
        """Register the guesses with the quiz progress."""
        for guess in guesses:
            self.quiz_progress.update(guess)

    def test_equality(self):
        """Test that two quiz progresses with the same attributes are equal."""
        self.assertEqual(self.quiz_progress, QuizProgress())

    def test_is_not_silenced_by_default(self):
        """Test that a new quiz progress is not silenced."""
        self.assertFalse(self.quiz_progress.is_silenced())
        self.assertIsNone(self.quiz_progress.silence_until)

    def test_is_not_silenced_after_one_correct_guess(self):
        """Test that a quiz progress is not silenced after one correct guess."""
        self.guess(True)
        self.assertFalse(self.quiz_progress.is_silenced())
        self.assertIsNone(self.quiz_progress.silence_until)

    def test_is_silenced_after_two_correct_guesses(self):
        """Test that a quiz progress is silenced after two correct guesses."""
        self.guess(True, True)
        self.assertTrue(self.quiz_progress.is_silenced())
        self.assertTrue(self.quiz_progress.silence_until > datetime.now() + timedelta(minutes=1))

    def test_is_reset_after_an_incorrect_guess(self):
        """Test that a quiz progress is reset after an incorrect guess."""
        self.guess(True, True, False)
        self.assertFalse(self.quiz_progress.is_silenced())
        self.assertIsNone(self.quiz_progress.silence_until)

    def test_no_guesses_as_dict(self):
        """Test that the quiz progress can be serialized."""
        self.assertEqual(dict(count=0), self.quiz_progress.as_dict())

    def test_one_guess_as_dict(self):
        """Test that the quiz progress can be serialized."""
        self.guess(True)
        self.assertEqual(dict(count=1), self.quiz_progress.as_dict())

    def test_two_guesses_as_dict(self):
        """Test that the quiz progress can be serialized."""
        self.guess(True, True)
        self.assertEqual(2, self.quiz_progress.as_dict()["count"])

    def test_no_guesses_from_dict(self):
        """Test that a quiz progress can be deserialized."""
        self.assertEqual(QuizProgress(count=0), QuizProgress.from_dict(self.quiz_progress.as_dict()))

    def test_one_guess_from_dict(self):
        """Test that a quiz progress can be deserialized."""
        self.guess(True)
        self.assertEqual(QuizProgress(count=1), QuizProgress.from_dict(self.quiz_progress.as_dict()))

    def test_two_guesses_from_dict(self):
        """Test that a quiz progress can be deserialized."""
        self.guess(True, True)
        self.assertEqual(2, QuizProgress.from_dict(self.quiz_progress.as_dict()).count)
