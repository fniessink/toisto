"""Unit tests for the show progress command."""

from datetime import datetime, timedelta
from unittest.mock import patch

from toisto.command import show_progress
from toisto.model import Progress

from ..base import ToistoTestCase


class ShowProgressTest(ToistoTestCase):
    """Test the show progress command."""

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [], Progress({}))
        self.assertEqual("Progress Finnish", console_print.call_args[0][0].title)

    def assert_row(*values):
        """Assert that the first row has the specified values"""

    def test_quiz(self):
        """Test that quizzes are shown."""
        now = datetime.now()
        formatted_now = now.isoformat(sep=" ", timespec="minutes")
        quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(streak=1, start=now, end=now)}))
        for index, value in enumerate(["Translate", "Terve", "fi", "nl", "Hoi", "1", formatted_now, formatted_now, ""]):
            self.assertEqual(value, list(console_print.call_args[0][0].columns[index].cells)[0])

    def test_quiz_silenced_until_time_in_the_future(self):
        """Test that if the time until which a quiz is silenced lies in the future, it is shown."""
        quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])
        skip_until = (datetime.now() + timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(streak=2, skip_until=skip_until)}))
        self.assertEqual(skip_until, list(console_print.call_args[0][0].columns[8].cells)[0])

    def test_quiz_silenced_until_time_in_the_past(self):
        """Test that if the time until which a quiz is silenced lies in the past, it is not shown."""
        quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])
        skip_until = (datetime.now() - timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(streak=2, skip_until=skip_until)}))
        self.assertEqual("", list(console_print.call_args[0][0].columns[6].cells)[0])
