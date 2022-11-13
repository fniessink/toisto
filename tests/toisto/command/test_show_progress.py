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

    def test_quiz(self):
        """Test that quizzes are shown."""
        quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(count=1)}))
        self.assertEqual("1", list(console_print.call_args[0][0].columns[5].cells)[0])

    def test_quiz_silenced_until_time_in_the_future(self):
        """Test that if the time until which a quiz is silenced lies in the future, it is shown."""
        quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])
        silence_until = (datetime.now() + timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(count=2, silence_until=silence_until)}))
        self.assertEqual(silence_until, list(console_print.call_args[0][0].columns[6].cells)[0])

    def test_quiz_silenced_until_time_in_the_past(self):
        """Test that if the time until which a quiz is silenced lies in the past, it is not shown."""
        quiz = self.create_quiz("fi", "nl", "Terve", ["Hoi"])
        silence_until = (datetime.now() - timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(count=2, silence_until=silence_until)}))
        self.assertEqual("", list(console_print.call_args[0][0].columns[6].cells)[0])
