"""Unit tests for the show progress command."""

from datetime import datetime, timedelta
from unittest.mock import patch

from toisto.command import show_progress
from toisto.model import Progress, Topic, Topics

from ..base import ToistoTestCase


class ShowProgressTest(ToistoTestCase):
    """Test the show progress command."""

    def setUp(self):
        """Set up test fixtures."""
        self.quiz = self.create_quiz("hello", "fi", "nl", "Terve", ["Hoi"])
        self.topics = Topics(set([Topic("topic", set([self.quiz]))]))

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", Topics(), Progress({}))
        self.assertEqual("Progress Finnish", console_print.call_args[0][0].title)

    def test_quiz(self):
        """Test that quizzes are shown."""
        now = datetime.now()
        start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
        end = now.isoformat(timespec="seconds")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", self.topics, Progress({str(self.quiz): dict(start=start, end=end)}))
        for index, value in enumerate(["Translate", "Terve", "fi", "nl", "Hoi", "0", "60 minutes", ""]):
            self.assertEqual(value, list(console_print.call_args[0][0].columns[index].cells)[0])

    def test_quiz_silenced_until_time_in_the_future(self):
        """Test that if the time until which a quiz is silenced lies in the future, it is shown."""
        skip_until = (datetime.now() + timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", self.topics, Progress({str(self.quiz): dict(skip_until=skip_until)}))
        self.assertEqual(skip_until, list(console_print.call_args[0][0].columns[7].cells)[0])

    def test_quiz_silenced_until_time_in_the_past(self):
        """Test that if the time until which a quiz is silenced lies in the past, it is not shown."""
        skip_until = (datetime.now() - timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", self.topics, Progress({str(self.quiz): dict(skip_until=skip_until)}))
        self.assertEqual("", list(console_print.call_args[0][0].columns[7].cells)[0])
