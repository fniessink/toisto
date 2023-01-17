"""Command to show progress information."""

from datetime import datetime
from typing import Literal

from rich.table import Table

from toisto.metadata import Language, SUPPORTED_LANGUAGES
from toisto.model import Progress, Topics
from toisto.ui.format import format_datetime, format_duration
from toisto.ui.text import console


SortColumn = Literal["attempts", "retention"]
RETENTION_ATTRIBUTE = dict(attempts="count", retention="length")


def show_progress(language: Language, topics: Topics, progress: Progress, sort: SortColumn = "attempts") -> None:
    """Show progress."""
    table = Table(title=f"Progress {SUPPORTED_LANGUAGES[language]}")
    table.add_column("Quiz type")
    table.add_column("Question")
    table.add_column("From")
    table.add_column("To")
    table.add_column("Answer(s)")
    table.add_column("Attempts", justify="right")
    table.add_column("Retention")
    table.add_column("Not quizzed until")
    key = lambda quiz: getattr(  # pylint: disable=unnecessary-lambda-assignment
        progress.get_retention(quiz), RETENTION_ATTRIBUTE[sort]
    )
    sorted_quizzes = sorted(topics.quizzes, key=key, reverse=True)
    for quiz in sorted_quizzes:
        retention = progress.get_retention(quiz)
        skip = retention.skip_until
        quiz_types = " and ".join(quiz.quiz_types)
        table.add_row(
            quiz_types.capitalize(),
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
