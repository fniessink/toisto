"""Command to show progress information."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from rich.console import JustifyMethod
from rich.table import Table

from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.ui.format import format_datetime, format_duration
from toisto.ui.text import console

SortColumn = Literal["attempts", "retention"]


@dataclass(frozen=True)
class QuizSorter:
    """Class to provide a sort function to sort quizzes."""

    progress: Progress
    sort: SortColumn

    def get_sort_key(self, quiz: Quiz) -> int | timedelta:
        """Return the retention attribute to sort by."""
        retention = self.progress.get_retention(quiz)
        if self.sort == "attempts":
            return retention.count
        return retention.length


def show_progress(progress: Progress, sort: SortColumn) -> None:
    """Show progress."""
    table = Table(title=f"Progress {ALL_LANGUAGES[progress.target_language]}")
    justify: dict[str, JustifyMethod] = dict(Attempts="right")
    for column in ("Quiz type", "Question", "From", "To", "Answer(s)", "Attempts", "Retention", "Not quizzed until"):
        table.add_column(column, justify=justify.get(column, "left"))
    sorted_quizzes = sorted(progress.quizzes, key=QuizSorter(progress, sort).get_sort_key, reverse=True)
    for quiz in sorted_quizzes:
        retention = progress.get_retention(quiz)
        skip = retention.skip_until
        quiz_types = " and ".join(quiz.quiz_types).capitalize()
        table.add_row(
            quiz_types,
            quiz.question,
            quiz.question.language,
            quiz.answer.language,
            "\n".join(quiz.answers),
            str(retention.count),
            format_duration(retention.length) if retention.length else "",
            format_datetime(skip) if skip and skip > datetime.now() else "",
        )
    with console.pager():
        console.print(table)
