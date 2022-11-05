"""Command to show progress information."""

from rich.table import Table

from toisto.metadata import Language, SUPPORTED_LANGUAGES
from toisto.model import Progress, Quizzes
from toisto.output import console


def show_progress(language: Language, quizzes: Quizzes, progress: Progress) -> None:
    """Show progress."""
    table = Table(title=f"Progress {SUPPORTED_LANGUAGES[language]}")
    table.add_column("Quiz type")
    table.add_column("Question")
    table.add_column("From")
    table.add_column("To")
    table.add_column("Answer(s)")
    table.add_column("Streak", justify="right")
    sorted_quizzes = sorted(quizzes, key=lambda quiz: progress.get_progress(quiz).count, reverse=True)
    for quiz in sorted_quizzes:
        quiz_progress = progress.get_progress(quiz)
        table.add_row(
            quiz.quiz_type.capitalize(),
            quiz.question,
            quiz.question_language,
            quiz.answer_language,
            "\n".join(quiz.answers),
            str(quiz_progress.count) if quiz_progress.count > 0 else ""
        )
    with console.pager():
        console.print(table)
