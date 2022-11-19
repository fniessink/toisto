"""Retention unit tests."""

from datetime import datetime, timedelta
import unittest

from toisto.model import Retention


class RetentionTest(unittest.TestCase):
    """Unit tests for the retention class."""

    def setUp(self) -> None:
        """Override to set up fixtures."""
        self.retention = Retention()

    def guess(self, *guesses: bool) -> None:
        """Register the guesses with the retention."""
        for guess in guesses:
            self.retention.update(guess)
            self.retention.start = (self.retention.start or datetime.now()) - timedelta(minutes=30)

    def test_equality(self):
        """Test that two retentions with the same attributes are equal."""
        self.assertEqual(self.retention, Retention())

    def test_is_not_silenced_by_default(self):
        """Test that a new retention is not silenced."""
        self.assertFalse(self.retention.is_silenced())
        self.assertIsNone(self.retention.skip_until)

    def test_is_not_silenced_after_one_correct_guess(self):
        """Test that a retention is not silenced after one correct guess."""
        self.guess(True)
        self.assertFalse(self.retention.is_silenced())
        self.assertIsNone(self.retention.skip_until)

    def test_is_silenced_after_two_correct_guesses(self):
        """Test that a retention is silenced after two correct guesses."""
        self.guess(True, True)
        self.assertTrue(self.retention.is_silenced())
        self.assertTrue(self.retention.skip_until > datetime.now() + timedelta(minutes=1))

    def test_is_reset_after_an_incorrect_guess(self):
        """Test that a retention is reset after an incorrect guess."""
        self.guess(True, True, False)
        self.assertFalse(self.retention.is_silenced())
        self.assertIsNone(self.retention.skip_until)

    def test_no_guesses_as_dict(self):
        """Test that the retention can be serialized."""
        self.assertEqual({}, self.retention.as_dict())

    def test_one_guess_as_dict(self):
        """Test that the retention can be serialized."""
        self.guess(True)
        start = self.retention.start.isoformat(timespec="seconds")
        end = self.retention.end.isoformat(timespec="seconds")
        self.assertEqual(dict(start=start, end=end), self.retention.as_dict())

    def test_two_guesses_as_dict(self):
        """Test that the retention can be serialized."""
        self.guess(True, True)
        self.assertIn("start", self.retention.as_dict())
        self.assertIn("end", self.retention.as_dict())
        self.assertIn("skip_until", self.retention.as_dict())

    def test_no_guesses_from_dict(self):
        """Test that a retention can be deserialized."""
        self.assertEqual(Retention(), Retention.from_dict(self.retention.as_dict()))

    def test_one_guess_from_dict(self):
        """Test that a retention can be deserialized."""
        self.guess(True)
        start = self.retention.start.replace(microsecond=0)
        end = self.retention.end.replace(microsecond=0)
        self.assertEqual(Retention(start=start, end=end), Retention.from_dict(self.retention.as_dict()))
