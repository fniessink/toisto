"""Unit tests for the show progress command."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from toisto.command.show_progress import SortColumn, show_progress
from toisto.model.language import FI
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import READ
from toisto.tools import first

from ...base import FI_NL, ToistoTestCase


class ShowProgressTestCase(ToistoTestCase):
    """Base class for unit tests for the show progress command."""

    SORT_COLUMN: SortColumn = "attempts"

    def setUp(self) -> None:
        """Set up test fixtures."""
        super().setUp()
        concept = self.create_concept("hello", dict(fi="Terve!", nl="Hoi!"))
        self.quiz = first(create_quizzes(FI_NL, concept).by_quiz_type(READ))
        self.quizzes = Quizzes({self.quiz})

    @patch("rich.console.Console.pager", MagicMock())
    def show_progress(self, progress: Progress) -> Mock:
        """Run the show progress command."""
        with patch("rich.console.Console.print") as console_print:
            show_progress(progress, sort=self.SORT_COLUMN)
        return console_print


class ShowProgressTest(ShowProgressTestCase):
    """Test the show progress command."""

    def setUp(self) -> None:
        """Extend to set up retention."""
        super().setUp()
        self.now = datetime.now()
        start = (self.now - timedelta(hours=1)).isoformat(timespec="seconds")
        end = self.now.isoformat(timespec="seconds")
        self.progress = Progress({self.quiz.key: dict(start=start, end=end)}, FI, self.quizzes)

    def test_title(self):
        """Test the table title."""
        console_print = self.show_progress(self.progress)
        self.assertEqual("Progress Finnish", console_print.call_args[0][0].title)

    def test_column_headers(self):
        """Test that the column headers are shown."""
        console_print = self.show_progress(self.progress)
        for index, value in enumerate(
            ["Quiz type", "Question", "From", "To", "Answer(s)", "Attempts", "Retention", "Not quizzed until"],
        ):
            self.assertEqual(value, console_print.call_args[0][0].columns[index].header)

    def test_quiz(self):
        """Test that quizzes are shown."""
        console_print = self.show_progress(self.progress)
        for index, value in enumerate(["read", "Terve!", "fi", "nl", "Hoi!", "0", "60 minutes", ""]):
            self.assertEqual(value, first(console_print.call_args[0][0].columns[index].cells))

    def test_quiz_silenced_until_time_in_the_future(self):
        """Test that if the time until which a quiz is silenced lies in the future, it is shown."""
        skip_until = self.progress.get_retention(self.quiz).skip_until = self.now + timedelta(days=1)
        formatted_skip_until = skip_until.isoformat(sep=" ", timespec="minutes")
        console_print = self.show_progress(self.progress)
        self.assertEqual(formatted_skip_until, first(console_print.call_args[0][0].columns[7].cells))

    def test_quiz_silenced_until_time_in_the_past(self):
        """Test that if the time until which a quiz is silenced lies in the past, it is not shown."""
        self.progress.get_retention(self.quiz).skip_until = self.now - timedelta(days=1)
        console_print = self.show_progress(self.progress)
        self.assertEqual("", first(console_print.call_args[0][0].columns[7].cells))


class ShowProgressSortTestCase(ShowProgressTestCase):
    """Base class for unit tests that test the sorting of the show progress command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        super().setUp()
        another_concept = self.create_concept("carpet", dict(fi="matto", nl="het tapijt"))
        self.another_quiz = first(create_quizzes(FI_NL, another_concept).by_quiz_type(READ))
        self.quizzes = Quizzes({self.quiz, self.another_quiz})


class ShowProgressByAttemptsTest(ShowProgressSortTestCase):
    """Test the show progress command, when sorting by atrempts."""

    SORT_COLUMN = "attempts"

    def test_sort_by_attempts_when_one_quiz_has_no_attempts(self):
        """Test that the quizzes can be sorted by retention length."""
        progress = Progress(
            {self.quiz.key: dict(count=21), self.another_quiz.key: {}},
            FI,
            self.quizzes,
        )
        console_print = self.show_progress(progress)
        self.assertEqual(["21", "0"], list(console_print.call_args[0][0].columns[5].cells))

    def test_sort_by_attempts_numerically(self):
        """Test that the quizzes are sorted by attempts numerically, not lexically."""
        progress = Progress(
            {self.quiz.key: dict(count=21), self.another_quiz.key: dict(count=4)},
            FI,
            self.quizzes,
        )
        console_print = self.show_progress(progress)
        self.assertEqual(["21", "4"], list(console_print.call_args[0][0].columns[5].cells))


class ShowProgressByRetentionTest(ShowProgressSortTestCase):
    """Test the show progress command, when sorting by retention."""

    SORT_COLUMN = "retention"

    def setUp(self) -> None:
        """Extend to set up retentions."""
        super().setUp()
        self.now = datetime.now()
        self.start = (self.now - timedelta(days=88)).isoformat(timespec="seconds")
        self.end = self.now.isoformat(timespec="seconds")

    def test_sort_by_retention_when_one_quiz_has_no_retention(self):
        """Test that the quizzes can be sorted by retention length, even when a quiz has no retention."""
        progress = Progress(
            {self.quiz.key: dict(start=self.start, end=self.end), self.another_quiz.key: {}},
            FI,
            self.quizzes,
        )
        console_print = self.show_progress(progress)
        self.assertEqual(["88 days", ""], list(console_print.call_args[0][0].columns[6].cells))

    def test_sort_by_retention_numerically(self):
        """Test that the quizzes are sorted by retention length numerically, not lexically."""
        another_start = (self.now - timedelta(days=9)).isoformat(timespec="seconds")
        progress = Progress(
            {
                self.quiz.key: dict(start=self.start, end=self.end),
                self.another_quiz.key: dict(start=another_start, end=self.end),
            },
            FI,
            self.quizzes,
        )
        console_print = self.show_progress(progress)
        self.assertEqual(["88 days", "9 days"], list(console_print.call_args[0][0].columns[6].cells))
