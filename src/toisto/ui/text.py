"""Output for the user."""

import sys
from collections.abc import Callable
from configparser import ConfigParser
from datetime import datetime
from random import sample
from typing import Final

from rich.console import Console
from rich.panel import Panel

from toisto.metadata import CHANGELOG_URL, NAME, README_URL, VERSION
from toisto.model.language import LanguagePair
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Label
from toisto.model.language.translation import meanings
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import GrammaticalQuizType
from toisto.model.quiz.retention import Retention
from toisto.tools import unique

from .dictionary import DICTIONARY_URL, linkified
from .diff import colored_diff
from .format import bulleted_list, enumerated, format_duration, linkified_and_enumerated, punctuated, quoted, wrapped
from .style import theme

console = Console(theme=theme, highlight=False)

LINK_KEY: Final[str] = "⌘ (the command key)" if sys.platform == "darwin" else "Ctrl (the control key)"

WELCOME: Final[str] = f"""👋 Welcome to [underline]{NAME} [white not bold]v{VERSION}[/white not bold][/underline]!

Practice as many words and phrases as you like, for as long as you like.

[secondary]{NAME} quizzes you on words and phrases repeatedly. Each time you answer
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
[/secondary]"""

NEWS: Final[str] = (
    f"🎉 {NAME} [white not bold]{{0}}[/white not bold] is [link={CHANGELOG_URL}]available[/link]. "
    f"Upgrade with [code]{NAME.lower()} self upgrade[/code]."
)

CONFIG_LANGUAGE_TIP: Final[str] = (
    "️️👉 You may want to use `toisto configure` to store your language preferences.\n"
    f"See {README_URL.replace('#toisto', '#how-to-configure-toisto')}."
)

DONE: Final[str] = f"""👍 Good job. You're done for now. Please come back later or try a different concept.
[secondary]Type `{NAME.lower()} -h` for more information.[/secondary]
"""


class Feedback:
    """Return feedback on answers to a quiz."""

    CORRECT: Final[str] = "✅ Correct.\n"
    INCORRECT: Final[str] = "❌ Incorrect. "
    TRY_AGAIN_FRAGMENT: Final[str] = "⚠️ Incorrect. Please try again"
    TRY_AGAIN: Final[str] = TRY_AGAIN_FRAGMENT + "."
    TRY_AGAIN_IN_ANSWER_LANGUAGE: Final[str] = TRY_AGAIN_FRAGMENT + "️, in [language]%(language)s[/language]."
    TRY_AGAIN_IN_ANSWER_STANDARD_LANGUAGE: Final[str] = (
        TRY_AGAIN_FRAGMENT + ", in [language]standard %(language)s[/language]."
    )

    def __init__(self, quiz: Quiz, language_pair: LanguagePair) -> None:
        self.quiz = quiz
        self.language_pair = language_pair
        self.incorrect_guesses: list[str] = []

    def text(self, evaluation: Evaluation, guess: str, retention: Retention | None) -> str:
        """Return the feedback about the user's guess."""
        if evaluation == Evaluation.TRY_AGAIN:
            self.incorrect_guesses.append(guess)
            return self._try_again(guess)
        feedback = ""
        match evaluation:
            case Evaluation.CORRECT:
                feedback += self.CORRECT + self._other_answers(guess)
            case Evaluation.INCORRECT:
                self.incorrect_guesses.append(guess)
                feedback += self.INCORRECT + self._correct_answers(guess)
            case _:
                feedback += self._correct_answers()
        feedback += self._colloquial() + self._meaning() + self._notes()
        if evaluation == Evaluation.CORRECT:
            feedback += self._examples()
        if retention is not None:
            feedback += self._retention(retention, evaluation)
        return feedback

    def _try_again(self, guess: str) -> str:
        """Return the feedback when the first attempt is incorrect."""
        if self.quiz.is_question(guess) and not self.quiz.has_quiz_type(GrammaticalQuizType):
            standard = self.quiz.question.colloquial and self.quiz.question.language == self.quiz.answer.language
            try_again = self.TRY_AGAIN_IN_ANSWER_STANDARD_LANGUAGE if standard else self.TRY_AGAIN_IN_ANSWER_LANGUAGE
            return try_again % {"language": ALL_LANGUAGES[self.quiz.answer.language]}
        return self.TRY_AGAIN

    def _correct_answers(self, guess: str = "") -> str:
        """Return the quiz's correct answer."""
        correct_answers = self.quiz.non_generated_answers
        if guess and (closest_answer := correct_answers.most_similar_label(guess)):
            answer = quoted(colored_diff(guess, str(closest_answer)))
            return punctuated(f"The correct answer is {answer}") + "\n" + self._other_answers(str(closest_answer))
        label = "The correct answer is" if len(correct_answers) == 1 else "The correct answers are"
        answers = linkified_and_enumerated(*correct_answers.as_strings)
        return punctuated(f"{label} {answers}") + "\n"

    def _other_answers(self, answer: str) -> str:
        """Return the quiz's other answers, if any."""
        if other_answers := self.quiz.other_answers(answer):
            label = "Another correct answer is" if len(other_answers) == 1 else "Other correct answers are"
            answers = linkified_and_enumerated(*other_answers.as_strings)
            return wrapped(punctuated(f"{label} {answers}"), style="answer")
        return ""

    def _colloquial(self) -> str:
        """Return the feedback about the colloquial label, if any."""
        if self.quiz.question.colloquial:
            language = ALL_LANGUAGES[self.quiz.question.language]
            question = quoted(linkified(str(self.quiz.question)))
            return wrapped(punctuated(f"The colloquial {language} spoken was {question}"), style="colloquial")
        return ""

    def _meaning(self) -> str:
        """Return the quiz's meaning, if any."""
        question_meanings = linkified_and_enumerated(*self.quiz.question_meanings.as_strings)
        answer_meanings = linkified_and_enumerated(*self.quiz.answer_meanings.as_strings)
        if question_meanings and answer_meanings:
            quiz_meanings = f"{question_meanings}, respectively {answer_meanings}"
        else:
            quiz_meanings = question_meanings or answer_meanings
        return wrapped(punctuated(f"Meaning {quiz_meanings}"), style="meaning") if quiz_meanings else ""

    def _notes(self) -> str:
        """Return the notes, if any."""
        return bulleted_list("Note", list(self.quiz.notes) + self._notes_for_incorrect_guesses(), style="note")

    def _notes_for_incorrect_guesses(self) -> list[str]:
        """Create notes for incorrect guesses."""
        if self.quiz.question.language == self.quiz.answer.language:
            return []
        return [
            f"Your incorrect answer {quoted(linkified(str(guess)))} is "
            f"{linkified_and_enumerated(*guess_meanings.as_strings)} in {ALL_LANGUAGES[self.quiz.question.language]}"
            for guess in unique(self.incorrect_guesses)
            if (guess_meanings := meanings(guess, self.quiz.answer.language, self.quiz.question.language))
        ]

    def _examples(self, max_nr_examples: int = 3) -> str:
        """Return the quiz's examples, if any."""
        examples: list[str] = []
        for example in self.quiz.concept.get_related_concepts("example"):
            example_labels = example.labels(self.language_pair.target).first_non_generated_spelling_alternatives
            example_meanings = example.labels(self.language_pair.source).first_non_generated_spelling_alternatives
            enumerated_meanings = enumerated(*[self._example_label(meaning) for meaning in example_meanings])
            examples.extend(f"{self._example_label(label)} meaning {enumerated_meanings}" for label in example_labels)
        examples_to_show = sorted(sample(examples, min(len(examples), max_nr_examples)))  # nosec
        return bulleted_list("Example", examples_to_show, style="example")

    def _example_label(self, label: Label) -> str:
        """Format the label as example."""
        label_str = quoted(linkified(str(label)))
        return f"{label_str} (colloquial)" if label.colloquial else label_str

    def _retention(self, retention: Retention, evaluation: Evaluation) -> str:
        """Return the retention as text."""
        if retention.skip_until:
            next_up = f"Up next in {format_duration(retention.skip_until - datetime.now().astimezone())}."
        else:
            next_up = "Up next soon."
        count = retention.count
        if evaluation == Evaluation.CORRECT:
            count_description = f"Quizzed {count} times." if count > 1 else "Correct on the first try!"
        else:
            count_description = f"Quizzed {count} times." if count > 1 else "Quizzed once."
        retention_length = (
            f"Retention {format_duration(retention.length)}." if retention.length else "No retention yet."
        )
        return f"[retention]{count_description} {retention_length} {next_up}[/retention]\n"


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
            feedback.append(f"answered {correct} ({correct / total:.0%}) correctly")
        if incorrect:
            feedback.append(f"answered {incorrect} ({incorrect / total:.0%}) incorrectly")
        if skipped:
            feedback.append(f"skipped {skipped} ({skipped / total:.0%})")
        return wrapped(
            f"Progress update after {total} quiz{'zes' if total > 1 else ''}: you {enumerated(*feedback)}.",
            style="progress",
            postfix="\n\n",
        )


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return wrapped(f"{quiz.instruction}:", style="quiz", postfix="")


def show_welcome(write_output: Callable[..., None], latest_version: str | None, config: ConfigParser) -> None:
    """Show the welcome message."""
    write_output(WELCOME)
    new_version_available = latest_version and latest_version.strip("v") > VERSION
    languages_configured = config.has_option("languages", "target") and config.has_option("languages", "source")
    if new_version_available:
        news = NEWS.format(latest_version)
        write_output(Panel(news, expand=False))
    elif not languages_configured:
        write_output(Panel(CONFIG_LANGUAGE_TIP, expand=False))
    if new_version_available or not languages_configured:
        write_output()


def version_message(latest_version: str | None) -> str:
    """Return the version message."""
    newer = latest_version and latest_version.strip("v") > VERSION
    return f"[white not bold]v{VERSION}[/white not bold]" + (
        f" ([white not bold]{latest_version}[/white not bold] is available, "
        "run [code]toisto self upgrade[/code] to install)"
        if newer
        else ""
    )
