"""Unit tests for the formatting functions."""

from datetime import timedelta
from unittest import TestCase

from toisto.ui.format import format_duration


class FormatDurationTest(TestCase):
    """Unit tests for the format duration method."""

    def test_format_duration_seconds(self):
        """Test format seconds."""
        self.assertEqual("2 seconds", format_duration(timedelta(seconds=2)))

    def test_format_duration_minutes(self):
        """Test format minutes."""
        self.assertEqual("2 minutes", format_duration(timedelta(seconds=90)))

    def test_format_duration_hours(self):
        """Test format hours."""
        self.assertEqual("2 hours", format_duration(timedelta(seconds=7200)))

    def test_format_duration_daya(self):
        """Test format days."""
        self.assertEqual("2 days", format_duration(timedelta(days=2)))
