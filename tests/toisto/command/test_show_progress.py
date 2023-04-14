"""Unit tests for the show progress command."""

from datetime import datetime, timedelta
from unittest.mock import patch

from toisto.command.show_progress import show_progress
from toisto.model.language.concept_factory import create_concept
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes

from ...base import ToistoTestCase


class ShowProgressTest(ToistoTestCase):
    """Test the show progress command."""

    def setUp(self):
        """Set up test fixtures."""
        self.concept = create_concept("hello", dict(fi="Terve!", nl="Hoi!"))
        self.quizzes = create_quizzes("fi", "nl", self.concept).by_quiz_type("read")
        self.quiz = list(self.quizzes)[0]

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", Quizzes(), Progress({}, "fi"))
        self.assertEqual("Progress Finnish", console_print.call_args[0][0].title)

    def test_quiz(self):
        """Test that quizzes are shown."""
        now = datetime.now()
        start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
        end = now.isoformat(timespec="seconds")
        progress = Progress({self.quiz.key: dict(start=start, end=end)}, "fi")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", self.quizzes, progress)
        for index, value in enumerate(["Read", "Terve!", "fi", "nl", "Hoi!", "0", "60 minutes", ""]):
            self.assertEqual(value, list(console_print.call_args[0][0].columns[index].cells)[0])

    def test_quiz_silenced_until_time_in_the_future(self):
        """Test that if the time until which a quiz is silenced lies in the future, it is shown."""
        skip_until = (datetime.now() + timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        progress = Progress({self.quiz.key: dict(skip_until=skip_until)}, "fi")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", self.quizzes, progress)
        self.assertEqual(skip_until, list(console_print.call_args[0][0].columns[7].cells)[0])

    def test_quiz_silenced_until_time_in_the_past(self):
        """Test that if the time until which a quiz is silenced lies in the past, it is not shown."""
        skip_until = (datetime.now() - timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        progress = Progress({self.quiz.key: dict(skip_until=skip_until)}, "fi")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", self.quizzes, progress)
        self.assertEqual("", list(console_print.call_args[0][0].columns[7].cells)[0])

    def test_sort_by_retention(self):
        """Test that the quizzes can be sorted by retention length."""
        now = datetime.now()
        start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
        end = now.isoformat(timespec="seconds")
        another_concept = create_concept("carpet", dict(fi="matto", nl="het tapijt"))
        another_quiz = create_quizzes("fi", "nl", another_concept).by_quiz_type("read").pop()
        quizzes = Quizzes({self.quiz, another_quiz})
        progress = Progress(
            {self.quiz.key: dict(count=21, start=start, end=end), another_quiz.key: dict(count=42)},
            "fi",
        )
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", quizzes, progress, sort="retention")
        self.assertEqual(["21", "42"], list(console_print.call_args[0][0].columns[5].cells))
