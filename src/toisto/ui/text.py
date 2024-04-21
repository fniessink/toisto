"""Output for the user."""

import sys
from collections.abc import Callable, Sequence
from configparser import ConfigParser
from typing import Final

from rich.console import Console
from rich.panel import Panel

from ..metadata import CHANGELOG_URL, NAME, README_URL, VERSION
from ..model.language import Language, LanguagePair
from ..model.language.concept import Concept
from ..model.language.iana_language_subtag_registry import ALL_LANGUAGES
from ..model.language.label import END_OF_SENTENCE_PUNCTUATION, Label, Labels
from ..model.quiz.quiz import Quiz
from .dictionary import DICTIONARY_URL, linkify_and_enumerate
from .diff import colored_diff
from .style import QUIZ, SECONDARY

console = Console()

LINK_KEY: Final[str] = "⌘ (the command key)" if sys.platform == "darwin" else "Ctrl (the control key)"

WELCOME: Final[str] = f"""👋 Welcome to [underline]{NAME} [white not bold]v{VERSION}[/white not bold][/underline]!

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

NEWS: Final[str] = (
    f"🎉 {NAME} [white not bold]{{0}}[/white not bold] is [link={CHANGELOG_URL}]available[/link]. "
    f"Upgrade with [code]pipx upgrade {NAME}[/code]."
)

CONFIG_LANGUAGE_TIP: Final[str] = (
    "️️👉 You may want to use a configuration file to store your language preferences.\n"
    f"See {README_URL.replace('#toisto', '#how-to-configure-toisto')}."
)

DONE: Final[str] = f"""👍 Good job. You're done for now. Please come back later or try a different concept.
[{SECONDARY}]Type `{NAME.lower()} -h` for more information.[/{SECONDARY}]
"""

TRY_AGAIN: Final[str] = "⚠️  Incorrect. Please try again."

TRY_AGAIN_IN_ANSWER_LANGUAGE: Final[str] = (
    "⚠️  Incorrect. Please try again, in [yellow][bold]%(language)s[/bold][/yellow]."
)

CORRECT: Final[str] = "✅ Correct.\n"

INCORRECT: Final[str] = "❌ Incorrect. "


def feedback_correct(guess: Label, quiz: Quiz, language_pair: LanguagePair) -> str:
    """Return the feedback about a correct result."""
    return (
        CORRECT
        + colloquial(quiz)
        + meaning(quiz)
        + other_answers(guess, quiz)
        + answer_notes(quiz)
        + examples(quiz, language_pair)
    )


def feedback_incorrect(guess: Label, quiz: Quiz) -> str:
    """Return the feedback about an incorrect result."""
    return (
        INCORRECT
        + correct_answer(guess, quiz)
        + colloquial(quiz)
        + meaning(quiz)
        + other_answers(quiz.answer, quiz)
        + answer_notes(quiz)
    )


def feedback_try_again(guess: Label, quiz: Quiz) -> str:
    """Return the feedback when the first attempt is incorrect."""
    if quiz.is_question(guess) and not quiz.is_grammatical:
        return TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language=ALL_LANGUAGES[quiz.answer.language])
    return TRY_AGAIN


def feedback_skip(quiz: Quiz) -> str:
    """Return the feedback when the user skips to the answer."""
    return correct_answers(quiz) + colloquial(quiz) + meaning(quiz) + answer_notes(quiz)


def colloquial(quiz: Quiz) -> str:
    """Return the feedback about colloquial label, if any."""
    if quiz.question.is_colloquial:
        feedback = f'The colloquial {ALL_LANGUAGES[quiz.question.language]} spoken was "{quiz.question.strip("*")}".'
        return wrap(feedback, SECONDARY)
    return ""


def meaning(quiz: Quiz) -> str:
    """Return the quiz's meaning, if any."""
    if quiz.question_meanings and quiz.answer_meanings:
        question_meanings = linkify_and_enumerate(*quiz.question_meanings)
        answer_meanings = linkify_and_enumerate(*quiz.answer_meanings)
        meanings = f"{question_meanings}, respectively {answer_meanings}"
    else:
        meanings = linkify_and_enumerate(*(quiz.question_meanings + quiz.answer_meanings))
    return wrap(f"Meaning {meanings}.", SECONDARY) if meanings else ""


def correct_answer(guess: Label, quiz: Quiz) -> str:
    """Return the quiz's correct answer."""
    return f'The correct answer is "{colored_diff(guess, quiz.answer)}".\n'


def correct_answers(quiz: Quiz) -> str:
    """Return the quiz's correct answers."""
    answers = quiz.non_generated_answers
    label = "The correct answer is" if len(answers) == 1 else "The correct answers are"
    return f"{label} {linkify_and_enumerate(*answers)}.\n"


def other_answers(guess: Label, quiz: Quiz) -> str:
    """Return the quiz's other answers, if any."""
    if answers := quiz.other_answers(guess):
        label = "Another correct answer is" if len(answers) == 1 else "Other correct answers are"
        return wrap(f"{label} {linkify_and_enumerate(*answers)}.", SECONDARY)
    return ""


def labels(concept: Concept, language: Language) -> Labels:
    """Return the first non-generated spelling alternative of the labels of a concept in the given language."""
    return Labels(label.non_generated_spelling_alternatives[0] for label in concept.labels(language))


def examples(quiz: Quiz, language_pair: LanguagePair) -> str:
    """Return the quiz's examples, if any."""
    examples: list[str] = []
    for example in quiz.concept.get_related_concepts("example"):
        example_labels, example_meanings = labels(example, language_pair.target), labels(example, language_pair.source)
        for label, meaning in zip(example_labels, example_meanings, strict=False):
            examples.append(f'"{label}" meaning "{meaning}"')
    return bulleted_list("Example", examples)


def answer_notes(quiz: Quiz) -> str:
    """Return the answer notes, if any."""
    return bulleted_list("Note", quiz.answer_notes)


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return wrap(f"{quiz.instruction}:", QUIZ, postfix="")


def show_welcome(write_output: Callable[..., None], latest_version: str | None, config: ConfigParser) -> None:
    """Show the welcome message."""
    write_output(WELCOME)
    if latest_version and latest_version.strip("v") > VERSION:
        write_output(Panel(NEWS.format(latest_version), expand=False))
        write_output()
    elif not config.has_section("languages"):
        write_output(Panel(CONFIG_LANGUAGE_TIP, expand=False))
        write_output()


def bulleted_list(label: str, items: Sequence[str], style: str = SECONDARY, bullet: str = "-") -> str:
    """Create a bulleted list of the items."""
    items = [item if item[-1] in END_OF_SENTENCE_PUNCTUATION else f"{item}." for item in items]
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return wrap(f"{label}: {items[0]}", style)
    return wrap(f"{label}s:\n" + "\n".join([f"{bullet} {item}" for item in items]), style)


def wrap(text: str, style: str, postfix: str = "\n") -> str:
    """Wrap the text with the style."""
    return f"[{style}]{text}[/{style}]{postfix}"
