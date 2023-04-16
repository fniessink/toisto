"""Command to show progress information."""

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Literal

from rich.console import JustifyMethod
from rich.table import Table

from toisto.model.language import Language
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz, Quizzes
from toisto.ui.format import format_datetime, format_duration
from toisto.ui.text import console

SortColumn = Literal["attempts", "retention"]
RETENTION_ATTRIBUTE: Final = dict(attempts="count", retention="length")


@dataclass(frozen=True)
class QuizSorter:
    """Class to provide a sort function to sort quizzes."""

    progress: Progress
    sort: SortColumn

    def get_sort_key(self, quiz: Quiz) -> str:
        """Return the retention attribute to sort by."""
        return getattr(self.progress.get_retention(quiz), RETENTION_ATTRIBUTE[self.sort])


def show_progress(language: Language, quizzes: Quizzes, progress: Progress, sort: SortColumn = "attempts") -> None:
    """Show progress."""
    table = Table(title=f"Progress {ALL_LANGUAGES[language]}")
    justify: dict[str, JustifyMethod] = dict(Attempts="right")
    for column in ("Quiz type", "Question", "From", "To", "Answer(s)", "Attempts", "Retention", "Not quizzed until"):
        table.add_column(column, justify=justify.get(column, "left"))
    sorted_quizzes = sorted(quizzes, key=QuizSorter(progress, sort).get_sort_key, reverse=True)
    for quiz in sorted_quizzes:
        retention = progress.get_retention(quiz)
        skip = retention.skip_until
        quiz_types = " and ".join(quiz.quiz_types).capitalize()
        table.add_row(
            quiz_types,
            quiz.question,
            quiz.question_language,
            quiz.answer_language,
            "\n".join(quiz.answers),
            str(retention.count),
            format_duration(retention.length) if retention.length else "",
            format_datetime(skip) if skip and skip > datetime.now() else "",
        )
    with console.pager():
        console.print(table)
