"""Command to show progress information."""

from datetime import datetime

from rich.table import Table

from toisto.metadata import Language, SUPPORTED_LANGUAGES
from toisto.model import Progress, Topics
from toisto.ui.text import console, format_duration, format_datetime


def show_progress(language: Language, topics: Topics, progress: Progress) -> None:
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
    sorted_quizzes = sorted(topics.quizzes, key=lambda quiz: progress.get_retention(quiz).count, reverse=True)
    for quiz in sorted_quizzes:
        retention = progress.get_retention(quiz)
        skip = retention.skip_until
        table.add_row(
            quiz.quiz_type.capitalize(),
            quiz.question,
            quiz.question_language,
            quiz.answer_language,
            "\n".join(quiz.answers),
            str(retention.count),
            format_duration(retention.length) if retention.length else "",
            format_datetime(skip) if skip and skip > datetime.now() else ""
        )
    with console.pager():
        console.print(table)
