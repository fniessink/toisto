"""Output for the user."""

from datetime import datetime, timedelta
from typing import NoReturn
import sys

from rich.console import Console
from rich.theme import Theme

from .diff import colored_diff
from ..metadata import NAME, VERSION
from ..model import Label, Quiz, Retention


theme = Theme({
    "secondary": "grey69",
    "quiz": "medium_purple1",
    "inserted": "bright_green",
    "deleted": "bright_red"
})

console = Console(theme=theme)

WELCOME = f"""👋 Welcome to {NAME} [white not bold]v{VERSION}[/white not bold]!

Practice as many words and phrases as you like, for as long as you like.
Hit Ctrl-C or Ctrl-D to quit.

[secondary]{NAME} quizzes you on words and phrases repeatedly. Each time you answer a
quiz correctly, {NAME} will wait longer before repeating it. If you answer
a quiz incorrectly, you get one additional attempt to give the correct
answer. If the second attempt is not correct either, {NAME} will reset the
quiz interval.[/secondary]
"""

DONE = f"""👍 Good job. You're done for now. Please come back later or try a different topic.
[secondary]Type `{NAME.lower()} -h` for more information.[/secondary]
"""

TRY_AGAIN = "⚠️  Incorrect. Please try again."

CORRECT = "✅ Correct.\n"


def format_duration(duration: timedelta) -> str:
    """Format the duration in a human friendly way."""
    if duration.days > 1:
        return f"{duration.days} days"
    seconds = duration.seconds + (24 * 3600 if duration.days else 0)
    if seconds >= 1.5 * 3600:  # 1.5 hours
        hours = round(seconds / 3600)
        return f"{hours} hours"
    if seconds >= 1.5 * 60:  # 1.5 minutes
        minutes = round(seconds / 60)
        return f"{minutes} minutes"
    return f"{seconds} seconds"


def format_datetime(date_time: datetime) -> str:
    """Return a human readable version of the datetime"""
    return date_time.isoformat(sep=" ", timespec="minutes")


def feedback_correct(guess: Label, quiz: Quiz, quiz_progress: Retention) -> str:
    """Return the feedback about a correct result."""
    text = CORRECT
    if quiz_progress.skip_until:
        silence_duration = format_duration(quiz_progress.skip_until - datetime.now())
        long_initial_skip_explanation = " as you already seem to know this" if quiz_progress.count == 1 else ""
        text += f"[secondary]Skipping this quiz for {silence_duration}{long_initial_skip_explanation}.[/secondary]\n"
    if other_answers := quiz.other_answers(guess):
        label = "Another correct answer is" if len(other_answers) == 1 else "Other correct answers are"
        enumerated_answers = ", ".join([f'"{answer}"' for answer in other_answers])
        text += f"""[secondary]{label} {enumerated_answers}.[/secondary]\n"""
    return text


def feedback_incorrect(guess: Label, quiz: Quiz) -> str:
    """Return the feedback about an incorrect result."""
    diff = colored_diff(guess, quiz.answer)
    return f'❌ Incorrect. The correct answer is "{diff}".\n'


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return f"[quiz]{quiz.instruction()}:[/quiz]"


def show_error_and_exit(message: str) -> NoReturn:
    """Print the error message to stderr and exit."""
    sys.stderr.write(message)
    sys.exit(2)
