"""Output for the user."""

import sys
from collections.abc import Callable, Sequence
from configparser import ConfigParser
from itertools import zip_longest
from typing import Final, cast

from rich.console import Console
from rich.panel import Panel

from ..metadata import CHANGELOG_URL, NAME, README_URL, VERSION
from ..model.language import Language, LanguagePair
from ..model.language.concept import Concept
from ..model.language.iana_language_subtag_registry import ALL_LANGUAGES
from ..model.language.label import END_OF_SENTENCE_PUNCTUATION, Label, Labels
from ..model.quiz.evaluation import Evaluation
from ..model.quiz.progress import Progress
from ..model.quiz.quiz import Quiz
from .dictionary import DICTIONARY_URL, linkified
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


class Feedback:
    """Return feedback on answers to a quiz."""

    CORRECT: Final[str] = "✅ Correct.\n"
    INCORRECT: Final[str] = "❌ Incorrect. "
    TRY_AGAIN: Final[str] = "⚠️  Incorrect. Please try again."
    TRY_AGAIN_IN_ANSWER_LANGUAGE: Final[str] = (
        "⚠️  Incorrect. Please try again, in [yellow][bold]%(language)s[/bold][/yellow]."
    )

    def __init__(self, quiz: Quiz, language_pair: LanguagePair) -> None:
        self.quiz = quiz
        self.language_pair = language_pair

    def __call__(self, evaluation: Evaluation, guess: Label | None = None) -> str:
        """Return the feedback about the user's guess."""
        if evaluation == Evaluation.TRY_AGAIN:
            return self._try_again(cast(Label, guess))
        feedback = ""
        if evaluation == Evaluation.CORRECT:
            feedback += self.CORRECT
        elif evaluation == Evaluation.INCORRECT:
            feedback += self.INCORRECT + self._correct_answer(cast(Label, guess))
        else:
            feedback += self._correct_answers()
        feedback += self._colloquial() + self._meaning()
        if evaluation == Evaluation.CORRECT:
            feedback += self._other_answers(cast(Label, guess))
        elif evaluation == Evaluation.INCORRECT:
            feedback += self._other_answers(self.quiz.answer)
        feedback += self._answer_notes()
        if evaluation == Evaluation.CORRECT:
            feedback += self._examples()
        return feedback

    def _try_again(self, guess: Label) -> str:
        """Return the feedback when the first attempt is incorrect."""
        if self.quiz.is_question(guess) and not self.quiz.is_grammatical:
            return self.TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language=ALL_LANGUAGES[self.quiz.answer.language])
        return self.TRY_AGAIN

    def _correct_answer(self, guess: Label) -> str:
        """Return the quiz's correct answer."""
        answer = quoted(colored_diff(guess, self.quiz.answer))
        return punctuated(f"The correct answer is {answer}") + "\n"

    def _correct_answers(self) -> str:
        """Return the quiz's correct answers."""
        label = "The correct answer is" if len(self.quiz.non_generated_answers) == 1 else "The correct answers are"
        answers = linkified_and_enumerated(*self.quiz.non_generated_answers)
        return punctuated(f"{label} {answers}") + "\n"

    def _other_answers(self, guess: Label) -> str:
        """Return the quiz's other answers, if any."""
        if other_answers := self.quiz.other_answers(guess):
            label = "Another correct answer is" if len(other_answers) == 1 else "Other correct answers are"
            answers = linkified_and_enumerated(*other_answers)
            return wrapped(punctuated(f"{label} {answers}"), SECONDARY)
        return ""

    def _colloquial(self) -> str:
        """Return the feedback about the colloquial label, if any."""
        if self.quiz.question.is_colloquial:
            language = ALL_LANGUAGES[self.quiz.question.language]
            question = quoted(self.quiz.question.strip("*"))
            return wrapped(punctuated(f"The colloquial {language} spoken was {question}"), SECONDARY)
        return ""

    def _meaning(self) -> str:
        """Return the quiz's meaning, if any."""
        if self.quiz.question_meanings and self.quiz.answer_meanings:
            question_meanings = linkified_and_enumerated(*self.quiz.question_meanings)
            answer_meanings = linkified_and_enumerated(*self.quiz.answer_meanings)
            meanings = f"{question_meanings}, respectively {answer_meanings}"
        else:
            meanings = linkified_and_enumerated(*(self.quiz.question_meanings + self.quiz.answer_meanings))
        return wrapped(punctuated(f"Meaning {meanings}"), SECONDARY) if meanings else ""

    def _answer_notes(self) -> str:
        """Return the answer notes, if any."""
        return bulleted_list("Note", self.quiz.answer_notes)

    def _examples(self) -> str:
        """Return the quiz's examples, if any."""
        examples: list[str] = []
        for example in self.quiz.concept.get_related_concepts("example"):
            example_labels = labels(example, self.language_pair.target)
            example_meanings = labels(example, self.language_pair.source)
            shorter = example_labels if len(example_labels) < len(example_meanings) else example_meanings
            for label, meaning in zip_longest(example_labels, example_meanings, fillvalue=shorter[-1]):
                examples.append(f"{quoted(label)} meaning {quoted(meaning)}")
        return bulleted_list("Example", examples)


class ProgressUpdate:
    """Return feedback about the user's progress in the current session."""

    def __init__(self, progress: Progress, frequency: int) -> None:
        self.progress = progress
        self.frequency = frequency
        self.count = 0

    def __call__(self) -> str:
        """Return feedback about the user's progress with the given frequency."""
        self.count += 1
        if self.frequency == 0 or self.count % self.frequency != 0:
            return ""
        correct = self.progress.answers[Evaluation.CORRECT]
        incorrect = self.progress.answers[Evaluation.INCORRECT]
        skipped = self.progress.answers[Evaluation.SKIPPED]
        total = correct + incorrect + skipped
        feedback = []
        if correct:
            feedback.append(f"answered {correct} ({correct/total:.0%}) correctly")
        if incorrect:
            feedback.append(f"answered {incorrect} ({incorrect/total:.0%}) incorrectly")
        if skipped:
            feedback.append(f"skipped {skipped} ({skipped/total:.0%})")
        return wrapped(
            f"🚧 Progress update: of {total} quiz{'zes' if total > 1 else ''}, you {enumerated(*feedback)}.",
            "gold1",
        )


def labels(concept: Concept, language: Language) -> Labels:
    """Return the first non-generated spelling alternative of the labels of a concept in the given language."""
    return Labels(label.non_generated_spelling_alternatives[0] for label in concept.labels(language))


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return wrapped(f"{quiz.instruction}:", QUIZ, postfix="")


def show_welcome(write_output: Callable[..., None], latest_version: str | None, config: ConfigParser) -> None:
    """Show the welcome message."""
    write_output(WELCOME)
    if latest_version and latest_version.strip("v") > VERSION:
        write_output(Panel(NEWS.format(latest_version), expand=False))
        write_output()
    elif "target" not in config["languages"] or "source" not in config["languages"]:
        write_output(Panel(CONFIG_LANGUAGE_TIP, expand=False))
        write_output()


def bulleted_list(label: str, items: Sequence[str], style: str = SECONDARY, bullet: str = "-") -> str:
    """Create a bulleted list of the items."""
    if len(items) == 0:
        return ""
    items = [punctuated(item) for item in items]
    if len(items) == 1:
        return wrapped(f"{label}: {items[0]}", style)
    return wrapped(f"{label}s:\n" + "\n".join([f"{bullet} {item}" for item in items]), style)


def linkified_and_enumerated(*texts: str) -> str:
    """Return a linkified and enumerated version of the texts."""
    return enumerated(*(f"{quoted(linkified(text))}" for text in texts))


def wrapped(text: str, style: str, postfix: str = "\n") -> str:
    """Return the text wrapped with the style."""
    return f"[{style}]{text}[/{style}]{postfix}"


def punctuated(text: str) -> str:
    """Return the text with an added period, if it has no punctuation yet."""
    return text if set(text[-2:]) & set(END_OF_SENTENCE_PUNCTUATION) else f"{text}."


def quoted(text: str, quote: str = "'") -> str:
    """Return a quoted version of the text."""
    return f"{quote}{text}{quote}"


def enumerated(*texts: str, min_enumeration_length: int = 2) -> str:
    """Return an enumerated version of the text."""
    match len(texts):
        case length if length > min_enumeration_length:
            comma_separated_texts = ", ".join(texts[:-1]) + ","
            return enumerated(comma_separated_texts, texts[-1])
        case length if length == min_enumeration_length:
            return " and ".join(texts)
        case length if length == 1:
            return texts[0]
        case _:
            return ""
