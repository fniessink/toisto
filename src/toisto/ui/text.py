"""Output for the user."""

from datetime import datetime, timedelta
from typing import NoReturn
import random
import sys

from rich.console import Console
from rich.theme import Theme

from .diff import colored_diff
from ..metadata import NAME, VERSION
from ..model import Label, Quiz, QuizProgress


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
    "A+ work",
    "Admirable",
    "Amazing",
    "Astonishing",
    "Astounding",
    "Awe-inspiring",
    "Awesome",
    "Beautiful",
    "Bravo",
    "Brilliant",
    "Champ",
    "Champion",
    "Cheers",
    "Class act",
    "Clever",
    "Cool",
    "Crushed it",
    "Delightful",
    "Epic",
    "Exactly right",
    "Excellent",
    "Excellent job",
    "Excellent work",
    "Extraordinary",
    "Fabulous",
    "Fantastic",
    "Far out",
    "Fine job",
    "Flawless",
    "Genius",
    "Glorious",
    "Good job",
    "Good work",
    "Grand",
    "Great",
    "Great job",
    "Great performance",
    "Great work",
    "Impeccable",
    "Impressive",
    "Impressive work",
    "Incredible",
    "Inspirational",
    "Kudos",
    "Legendary",
    "Lovely",
    "Magnificent",
    "Marvellous",
    "Masterful",
    "Masterly",
    "Miraculous",
    "Nailed it",
    "Nice",
    "Nice going",
    "Nice job",
    "Nice work",
    "Nicely done",
    "Outstanding",
    "Perfect",
    "Perfection",
    "Phenomenal",
    "Remarkable",
    "Right on",
    "Sensational",
    "Skilful",
    "Impeccable",
    "Smashing",
    "Smooth",
    "Spectacular",
    "Splendid",
    "Stellar",
    "Sterling work",
    "Sublime",
    "Super",
    "Superb",
    "Sweet",
    "Swell",
    "Terrific",
    "That's it",
    "Thumbs up",
    "Top class",
    "Top notch",
    "Top performance",
    "Tremendous",
    "Unbelievable",
    "Way to go",
    "Well-done",
    "Winning",
    "Wizard",
    "Wonderful",
    "Wow",
    "You make it look easy"
]


def format_duration(duration: timedelta) -> str:
    """Format the duration in a human friendly way."""
    if duration.days > 1:
        return f"{duration.days} days"
    seconds = duration.seconds + (24 * 3600 if duration.days else 0)
    if seconds >= 1.5 * 3600:  # 1.5 hours
        hours = round(seconds / 3600)
        return f"{hours} hours"
    minutes = round(seconds / 60)
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
