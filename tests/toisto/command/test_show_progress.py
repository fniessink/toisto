"""Unit tests for the show progress command."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from toisto.command.show_progress import SortColumn, show_progress
from toisto.model.language import Language
from toisto.model.language.concept_factory import create_concept
from toisto.model.language.label import Label
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.tools import first

from ...base import ToistoTestCase


class ShowProgressTest(ToistoTestCase):
    """Test the show progress command."""

    def setUp(self):
        """Set up test fixtures."""
        self.concept = create_concept("hello", dict(fi="Terve!", nl="Hoi!"))
        self.quizzes = create_quizzes("fi", "nl", self.concept).by_quiz_type("read")
        self.quiz = first(self.quizzes)

    @patch("rich.console.Console.pager", MagicMock())
    def show_progress(self, progress: Progress, sort: SortColumn = "attempts") -> Mock:
        """Run the show progress command."""
        with patch("rich.console.Console.print") as console_print:
            show_progress(Language("fi"), progress, sort=sort)
        return console_print

    def test_title(self):
        """Test the table title."""
        progress = Progress({}, "fi", self.quizzes)
        console_print = self.show_progress(progress)
        self.assertEqual("Progress Finnish", console_print.call_args[0][0].title)

    def test_column_headers(self):
        """Test that the column headers are shown."""
        now = datetime.now()
        start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
        end = now.isoformat(timespec="seconds")
        progress = Progress({self.quiz.key: dict(start=start, end=end)}, "fi", self.quizzes)
        console_print = self.show_progress(progress)
        for index, value in enumerate(
            ["Quiz type", "Question", "From", "To", "Answer(s)", "Attempts", "Retention", "Not quizzed until"],
        ):
            self.assertEqual(value, console_print.call_args[0][0].columns[index].header)

    def test_quiz(self):
        """Test that quizzes are shown."""
        now = datetime.now()
        start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
        end = now.isoformat(timespec="seconds")
        progress = Progress({self.quiz.key: dict(start=start, end=end)}, "fi", self.quizzes)
        console_print = self.show_progress(progress)
        for index, value in enumerate(["Read", Label("fi", "Terve!"), "fi", "nl", "Hoi!", "0", "60 minutes", ""]):
            self.assertEqual(value, first(console_print.call_args[0][0].columns[index].cells))

    def test_quiz_silenced_until_time_in_the_future(self):
        """Test that if the time until which a quiz is silenced lies in the future, it is shown."""
        skip_until = (datetime.now() + timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        progress = Progress({self.quiz.key: dict(skip_until=skip_until)}, "fi", self.quizzes)
        console_print = self.show_progress(progress)
        self.assertEqual(skip_until, first(console_print.call_args[0][0].columns[7].cells))

    def test_quiz_silenced_until_time_in_the_past(self):
        """Test that if the time until which a quiz is silenced lies in the past, it is not shown."""
        skip_until = (datetime.now() - timedelta(days=1)).isoformat(sep=" ", timespec="minutes")
        progress = Progress({self.quiz.key: dict(skip_until=skip_until)}, "fi", self.quizzes)
        console_print = self.show_progress(progress)
        self.assertEqual("", first(console_print.call_args[0][0].columns[7].cells))

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
            quizzes,
        )
        console_print = self.show_progress(progress, sort="retention")
        self.assertEqual(["21", "42"], list(console_print.call_args[0][0].columns[5].cells))
