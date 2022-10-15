"""Output for the user."""

from datetime import datetime, timedelta
from .color import grey, purple
from .diff import colored_diff
from .metadata import NAME, VERSION
from .model import Quiz, QuizProgress


WELCOME = f"""👋 Welcome to {NAME} v{VERSION}!

Practice as many words and phrases as you like, for as long as you like.
Hit Ctrl-C or Ctrl-D to quit.

{grey(f'''{NAME} tracks how many times you correctly translate words and phrases.
When you correctly translate a word or phrase multiple times in a row,
{NAME} will not quiz you on it for a while. The more correct translations
in a row, the longer words and phrases are silenced.''')}
"""

DONE = f"""👍 Good job. You're done for now. Please come back later or try a different deck.
{grey(f'Type `{NAME.lower()} -h` for more information.')}
"""


def format_duration(duration: timedelta) -> str:
    """Format the duration in a human friendly way."""
    if duration.days >= 1.5:
        return f"{duration.days} days"
    if duration.seconds >= 1.5 * 3600:  # 1.5 hours
        hours = round(duration.seconds / 3600)
        return f"{hours} hours"
    minutes = round(duration.seconds / 60)
    return f"{minutes} minutes"


def feedback_correct(guess: str, quiz: Quiz, quiz_progress: QuizProgress) -> str:
    """Return the feedback about a correct result."""
    text = "✅ Correct.\n"
    if quiz_progress.silence_until:
        silence_duration = format_duration(quiz_progress.silence_until - datetime.now())
        text += grey(
            f"Since you answered correctly {quiz_progress.count} times in a row, "
            f"I won't quiz you again for {silence_duration}.\n"
        )
    if other_answers := quiz.other_answers(guess):
        label = "Another correct answer is" if len(other_answers) == 1 else "Other correct answers are"
        enumerated_answers = ", ".join([f'"{answer}"' for answer in other_answers])
        text += f"""{grey(f'{label} {enumerated_answers}.')}\n"""
    return text


def feedback_incorrect(guess: str, quiz: Quiz) -> str:
    """Return the feedback about an incorrect result."""
    diff = colored_diff(guess, quiz.get_answer())
    return f'❌ Incorrect. The correct answer is "{diff}".\n'


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return purple(f"{quiz.instruction()}:")
