"""Command to show progress information."""

from datetime import datetime

from rich.table import Table

from toisto.metadata import Language, SUPPORTED_LANGUAGES
from toisto.model import Progress, Quizzes
from toisto.ui.text import console


def format_datetime(date_time: datetime) -> str:
    """Return a human readable version of the datetime"""
    return date_time.isoformat(sep=" ", timespec="minutes")


def show_progress(language: Language, quizzes: Quizzes, progress: Progress) -> None:
    """Show progress."""
    table = Table(title=f"Progress {SUPPORTED_LANGUAGES[language]}")
    table.add_column("Quiz type")
    table.add_column("Question")
    table.add_column("From")
    table.add_column("To")
    table.add_column("Answer(s)")
    table.add_column("Streak", justify="right")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Skip until")
    sorted_quizzes = sorted(quizzes, key=lambda quiz: progress.get_progress(quiz).streak, reverse=True)
    for quiz in sorted_quizzes:
        quiz_progress = progress.get_progress(quiz)
        skip = quiz_progress.skip_until
        start = quiz_progress.start
        end = quiz_progress.end
        table.add_row(
            quiz.quiz_type.capitalize(),
            quiz.question,
            quiz.question_language,
            quiz.answer_language,
            "\n".join(quiz.answers),
            str(quiz_progress.streak) if quiz_progress.streak > 0 else "",
            format_datetime(start) if start else "",
            format_datetime(end) if end else "",
            format_datetime(skip) if skip and skip > datetime.now() else ""
        )
    with console.pager():
        console.print(table)
