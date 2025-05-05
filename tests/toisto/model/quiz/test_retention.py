"""Retention unit tests."""

import unittest
from datetime import datetime, timedelta, timezone
from typing import cast

from toisto.model.quiz.retention import Retention


class RetentionTest(unittest.TestCase):
    """Unit tests for the retention class."""

    def setUp(self) -> None:
        """Override to set up fixtures."""
        self.retention = Retention()

    def guess(self, *guesses: bool) -> None:
        """Register the guesses with the retention."""
        for guess in guesses:
            if guess:
                self.retention.increase()
                self.retention.start = (self.retention.start or datetime.now().astimezone()) - timedelta(minutes=30)
            else:
                self.retention.reset()

    def test_equality(self):
        """Test that two retentions with the same attributes are equal."""
        self.assertEqual(self.retention, Retention())

    def test_is_not_silenced_by_default(self):
        """Test that a new retention is not silenced."""
        self.assertFalse(self.retention.is_silenced())
        self.assertIsNone(self.retention.skip_until)

    def test_is_silenced_if_initial_answer_is_correct(self):
        """Test that a retention is silenced if the initial guess is correct."""
        self.guess(True)
        self.assertTrue(self.retention.is_silenced())
        self.assertGreaterEqual(
            (self.retention.skip_until or datetime.min.replace(tzinfo=timezone.utc)).replace(microsecond=0),
            (datetime.now().astimezone() + timedelta(days=1)).replace(microsecond=0)
        )

    def test_is_not_silenced_after_one_correct_guess(self):
        """Test that a retention is not silenced after one correct guess."""
        self.guess(False, True)
        self.assertFalse(self.retention.is_silenced())
        self.assertIsNone(self.retention.skip_until)

    def test_is_silenced_after_two_correct_guesses(self):
        """Test that a retention is silenced after two correct guesses."""
        self.guess(False, True, True)
        self.assertTrue(self.retention.is_silenced())
        self.assertGreater(
            self.retention.skip_until or datetime.min.replace(tzinfo=timezone.utc),
            datetime.now().astimezone() + timedelta(minutes=1)
        )

    def test_is_reset_after_an_incorrect_guess(self):
        """Test that a retention is reset after an incorrect guess."""
        self.guess(True, False)
        self.assertFalse(self.retention.is_silenced())
        self.assertIsNone(self.retention.skip_until)
        self.assertEqual(2, self.retention.count)

    def test_no_guesses_as_dict(self):
        """Test that the retention can be serialized."""
        self.assertEqual({}, self.retention.as_dict())

    def test_one_guess_as_dict(self):
        """Test that the retention can be serialized."""
        self.guess(True)
        start = cast(datetime, self.retention.start).isoformat(timespec="seconds")
        end = cast(datetime, self.retention.end).isoformat(timespec="seconds")
        skip_until = cast(datetime, self.retention.skip_until).isoformat(timespec="seconds")
        self.assertEqual(dict(start=start, end=end, skip_until=skip_until, count=1), self.retention.as_dict())

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
        start = cast(datetime, self.retention.start).replace(microsecond=0)
        end = cast(datetime, self.retention.end).replace(microsecond=0)
        skip_until = cast(datetime, self.retention.skip_until).replace(microsecond=0)
        self.assertEqual(
            Retention(start=start, end=end, skip_until=skip_until, count=1),
            Retention.from_dict(self.retention.as_dict()),
        )
