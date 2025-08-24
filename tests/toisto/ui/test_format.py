"""Unit tests for the formatting functions."""

from datetime import timedelta
from unittest import TestCase

from toisto.ui.format import format_duration


class FormatDurationTest(TestCase):
    """Unit tests for the format duration method."""

    def test_format_duration_zero_seconds(self):
        """Test format seconds."""
        self.assertEqual("0 seconds", format_duration(timedelta()))

    def test_format_duration_one_second(self):
        """Test format seconds."""
        self.assertEqual("1 second", format_duration(timedelta(seconds=1)))

    def test_format_duration_two_seconds(self):
        """Test format seconds."""
        self.assertEqual("2 seconds", format_duration(timedelta(seconds=2)))

    def test_format_duration_max_seconds_that_result_in_second_unit(self):
        """Test format seconds."""
        self.assertEqual("89 seconds", format_duration(timedelta(seconds=89)))

    def test_format_duration_max_seconds_that_result_in_second_unit_plus_one(self):
        """Test format seconds."""
        self.assertEqual("2 minutes", format_duration(timedelta(seconds=90)))

    def test_format_duration_one_minute(self):
        """Test format minutes."""
        self.assertEqual("60 seconds", format_duration(timedelta(minutes=1)))

    def test_format_duration_two_minutes(self):
        """Test format minutes."""
        self.assertEqual("2 minutes", format_duration(timedelta(minutes=2)))

    def test_format_duration_max_minutes_that_result_in_minute_unit(self):
        """Test format minutes."""
        self.assertEqual("89 minutes", format_duration(timedelta(minutes=89)))

    def test_format_duration_max_minutes_that_result_in_minute_unit_plus_one(self):
        """Test format minutes."""
        self.assertEqual("2 hours", format_duration(timedelta(minutes=90)))

    def test_format_duration_one_hour(self):
        """Test format hours."""
        self.assertEqual("60 minutes", format_duration(timedelta(hours=1)))

    def test_format_duration_two_hours(self):
        """Test format hours."""
        self.assertEqual("2 hours", format_duration(timedelta(hours=2)))

    def test_format_duration_max_hours_that_result_in_hour_unit(self):
        """Test format hours."""
        self.assertEqual("35 hours", format_duration(timedelta(hours=35)))

    def test_format_duration_max_hours_that_result_in_hour_unit_plus_one(self):
        """Test format hours."""
        self.assertEqual("2 days", format_duration(timedelta(hours=36)))

    def test_format_duration_one_day(self):
        """Test format days."""
        self.assertEqual("24 hours", format_duration(timedelta(days=1)))

    def test_format_duration_two_days(self):
        """Test format days."""
        self.assertEqual("2 days", format_duration(timedelta(days=2)))

    def test_format_duration_max_days_that_result_in_day_unit(self):
        """Test format days."""
        self.assertEqual("10 days", format_duration(timedelta(days=10)))

    def test_format_duration_max_days_that_result_in_day_unit_plus_one(self):
        """Test format days."""
        self.assertEqual("2 weeks", format_duration(timedelta(days=11)))

    def test_format_duration_one_week(self):
        """Test format weeks."""
        self.assertEqual("7 days", format_duration(timedelta(weeks=1)))

    def test_format_duration_two_weeks(self):
        """Test format weeks."""
        self.assertEqual("2 weeks", format_duration(timedelta(weeks=2)))

    def test_format_duration_max_weeks_that_result_in_week_unit(self):
        """Test format weeks."""
        self.assertEqual("6 weeks", format_duration(timedelta(weeks=6)))

    def test_format_duration_max_weeks_that_result_in_week_unit_plus_one(self):
        """Test format weeks."""
        self.assertEqual("2 months", format_duration(timedelta(weeks=7)))

    def test_format_duration_one_month(self):
        """Test format months."""
        self.assertEqual("4 weeks", format_duration(timedelta(days=30)))

    def test_format_duration_two_months(self):
        """Test format months."""
        self.assertEqual("2 months", format_duration(timedelta(days=61)))

    def test_format_duration_max_months_that_result_in_month_unit(self):
        """Test format months."""
        self.assertEqual("18 months", format_duration(timedelta(days=30 * 18)))

    def test_format_duration_max_months_that_result_in_month_unit_plus_one(self):
        """Test format months."""
        self.assertEqual("2 years", format_duration(timedelta(days=30 * 19)))

    def test_format_duration_one_year(self):
        """Test format years."""
        self.assertEqual("12 months", format_duration(timedelta(days=365)))

    def test_format_duration_two_years(self):
        """Test format years."""
        self.assertEqual("2 years", format_duration(timedelta(days=2 * 365)))
