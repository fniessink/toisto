"""Output for the user."""

import sys
from collections.abc import Callable
from typing import Final

from rich.console import Console
from rich.panel import Panel

from ..metadata import CHANGELOG_URL, NAME, VERSION
from ..model.language.label import Label
from ..model.quiz.quiz import Quiz
from .dictionary import DICTIONARY_URL, linkify_and_enumerate
from .diff import colored_diff
from .style import QUIZ, SECONDARY

console = Console()

LINK_KEY: Final = "⌘ (the command key)" if sys.platform == "darwin" else "Ctrl (the control key)"

WELCOME: Final = f"""👋 Welcome to [underline]{NAME} [white not bold]v{VERSION}[/white not bold][/underline]!

Practice as many words and phrases as you like, for as long as you like.

[{SECONDARY}]{NAME} quizzes you on words and phrases repeatedly. Each time you answer
a quiz correctly, {NAME} will wait longer before repeating it. If you
answer incorrectly, you get one additional attempt to give the correct
answer. If the second attempt is not correct either, {NAME} will reset
the quiz interval.

How does it work?
● To answer a quiz: type the answer, followed by Enter.
● To repeat the spoken text: type Enter without answer.
● To skip to the answer immediately: type ?, followed by Enter.
● To read more about an [link={DICTIONARY_URL}/underlined]underlined[/link] word: keep {LINK_KEY} pressed
  while clicking the word. Not all terminals may support this.
● To quit: type Ctrl-C or Ctrl-D.
[/{SECONDARY}]"""

NEWS: Final = (
    f"🎉 {NAME} [white not bold]{{0}}[/white not bold] is [link={CHANGELOG_URL}]available[/link]. "
    f"Upgrade with [code]pipx upgrade {NAME}[/code]."
    ""
)

DONE: Final = f"""👍 Good job. You're done for now. Please come back later or try a different topic.
[{SECONDARY}]Type `{NAME.lower()} -h` for more information.[/{SECONDARY}]
"""

TRY_AGAIN: Final = "⚠️  Incorrect. Please try again."

TRY_AGAIN_IN_ANSWER_LANGUAGE: Final = "⚠️  Incorrect. Please try again, in [yellow][bold]%(language)s[/bold][/yellow]."

CORRECT: Final = "✅ Correct.\n"

INCORRECT: Final = "❌ Incorrect. "


def feedback_correct(guess: Label, quiz: Quiz) -> str:
    """Return the feedback about a correct result."""
    return CORRECT + meaning(quiz) + other_answers(guess, quiz) + answer_notes(quiz)


def feedback_incorrect(guess: Label, quiz: Quiz) -> str:
    """Return the feedback about an incorrect result."""
    if guess == Label(quiz.answer_language, "?"):
        label = "The correct answer is" if len(quiz.answers) == 1 else "The correct answers are"
        feedback = f"{label} {linkify_and_enumerate(*quiz.answers)}.\n" + meaning(quiz)
    else:
        label = f'{INCORRECT}The correct answer is "{colored_diff(guess, quiz.answer)}".\n'
        feedback = label + meaning(quiz) + other_answers(quiz.answer, quiz)
    return feedback + answer_notes(quiz)


def meaning(quiz: Quiz) -> str:
    """Return the quiz's meaning, if any."""
    if quiz.question_meanings and quiz.answer_meanings:
        question_meanings = linkify_and_enumerate(*quiz.question_meanings)
        answer_meanings = linkify_and_enumerate(*quiz.answer_meanings)
        meanings = f"{question_meanings}, respectively {answer_meanings}"
    else:
        meanings = linkify_and_enumerate(*(quiz.question_meanings + quiz.answer_meanings))
    return f"[{SECONDARY}]Meaning {meanings}.[/{SECONDARY}]\n" if meanings else ""


def other_answers(guess: Label, quiz: Quiz) -> str:
    """Return the quiz's other answers, if any."""
    if answers := quiz.other_answers(guess):
        label = "Another correct answer is" if len(answers) == 1 else "Other correct answers are"
        return f"""[{SECONDARY}]{label} {linkify_and_enumerate(*answers)}.[/{SECONDARY}]\n"""
    return ""


def answer_notes(quiz: Quiz) -> str:
    """Return the answer notes, if any."""
    notes = quiz.answer_notes
    if len(notes) == 0:
        return ""
    if len(notes) == 1:
        return f"[{SECONDARY}]Note: {notes[0]}.[/{SECONDARY}]\n"
    return "\n".join([f"[{SECONDARY}]Notes:"] + [f"- {note}." for note in notes] + [f"[/{SECONDARY}]\n"])


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return f"[{QUIZ}]{quiz.instruction}:[/{QUIZ}]"


def show_welcome(write_output: Callable[..., None], latest_version: str | None) -> None:
    """Show the welcome message."""
    write_output(WELCOME)
    if latest_version and latest_version.strip("v") > VERSION:
        write_output(Panel(NEWS.format(latest_version), expand=False))
        write_output()
