"""Output for the user."""

from datetime import datetime, timedelta
from typing import NoReturn
import random
import sys

from rich.console import Console
from rich.theme import Theme

from .diff import colored_diff
from .metadata import NAME, VERSION
from .model import Label, Quiz, QuizProgress


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

[secondary]{NAME} tracks how many times you correctly translate words and phrases.
When you correctly translate a word or phrase multiple times in a row,
{NAME} will not quiz you on it for a while. The more correct translations
in a row, the longer words and phrases are silenced.[/secondary]
"""

DONE = f"""👍 Good job. You're done for now. Please come back later or try a different topic.
[secondary]Type `{NAME.lower()} -h` for more information.[/secondary]
"""

TRY_AGAIN = "⚠️  Incorrect. Please try again."

CORRECT = "✅ Correct.\n"

PRAISE = [
    "Nice", "Cool", "Cheers", "Kudos", "Well-done", "Great", "Grand", "Swell", "Bravo", "Great job", "Nailed it",
    "Outstanding", "Excellent", "Awesome", "Terrific", "Brilliant", "Lovely", "Tremendous", "Wow", "Marvellous",
    "Beautiful", "Amazing", "Remarkable", "Magnificent", "Splendid", "Superb", "Wonderful", "Incredible", "Impressive",
    "Sensational", "Fantastic", "Extraordinary", "Sublime", "Spectacular", "Perfect", "Awe-inspiring"]


def format_duration(duration: timedelta) -> str:
    """Format the duration in a human friendly way."""
    if duration.days >= 1.5:
        return f"{duration.days} days"
    if duration.seconds >= 1.5 * 3600:  # 1.5 hours
        hours = round(duration.seconds / 3600)
        return f"{hours} hours"
    minutes = round(duration.seconds / 60)
    return f"{minutes} minutes"


def feedback_correct(guess: Label, quiz: Quiz, quiz_progress: QuizProgress) -> str:
    """Return the feedback about a correct result."""
    text = CORRECT
    if quiz_progress.silence_until:
        silence_duration = format_duration(quiz_progress.silence_until - datetime.now())
        praise = random.choice(PRAISE)
        text += (
            f"[secondary]{praise}! That's {quiz_progress.count} times in a row. "
            f"Skipping this quiz for {silence_duration}.[/secondary]\n"
        )
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
