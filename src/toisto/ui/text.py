"""Output for the user."""

import sys
from collections.abc import Callable, Sequence
from configparser import ConfigParser
from typing import Final, cast

from rich.console import Console
from rich.panel import Panel

from toisto.metadata import CHANGELOG_URL, NAME, README_URL, VERSION, installation_tool
from toisto.model.language import LanguagePair
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import END_OF_SENTENCE_PUNCTUATION, Label
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import GrammaticalQuizType

from .dictionary import DICTIONARY_URL, linkified
from .diff import colored_diff
from .style import theme

console = Console(theme=theme)

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
    f"Upgrade with [code]{{1}} upgrade {NAME}[/code]."
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

    def __call__(self, evaluation: Evaluation, guess: Label | None = None) -> str:
        """Return the feedback about the user's guess."""
        if evaluation == Evaluation.TRY_AGAIN:
            return self._try_again(cast("Label", guess))
        feedback = ""
        if evaluation == Evaluation.CORRECT:
            feedback += self.CORRECT
        elif evaluation == Evaluation.INCORRECT:
            feedback += self.INCORRECT + self._correct_answer(cast("Label", guess))
        else:
            feedback += self._correct_answers()
        feedback += self._colloquial() + self._meaning()
        if evaluation == Evaluation.CORRECT:
            feedback += self._other_answers(cast("Label", guess))
        elif evaluation == Evaluation.INCORRECT:
            feedback += self._other_answers(self.quiz.answer)
        feedback += self._notes()
        if evaluation == Evaluation.CORRECT:
            feedback += self._examples()
        return feedback

    def _try_again(self, guess: Label) -> str:
        """Return the feedback when the first attempt is incorrect."""
        if self.quiz.is_question(guess) and not self.quiz.has_quiz_type(GrammaticalQuizType):
            standard = self.quiz.question.colloquial and self.quiz.question.language == self.quiz.answer.language
            try_again = self.TRY_AGAIN_IN_ANSWER_STANDARD_LANGUAGE if standard else self.TRY_AGAIN_IN_ANSWER_LANGUAGE
            return try_again % {"language": ALL_LANGUAGES[self.quiz.answer.language]}
        return self.TRY_AGAIN

    def _correct_answer(self, guess: Label) -> str:
        """Return the quiz's correct answer."""
        answer = quoted(colored_diff(str(guess), str(self.quiz.answer)))
        return punctuated(f"The correct answer is {answer}") + "\n"

    def _correct_answers(self) -> str:
        """Return the quiz's correct answers."""
        label = "The correct answer is" if len(self.quiz.non_generated_answers) == 1 else "The correct answers are"
        answers = linkified_and_enumerated(*self.quiz.non_generated_answers.as_strings)
        return punctuated(f"{label} {answers}") + "\n"

    def _other_answers(self, guess: Label) -> str:
        """Return the quiz's other answers, if any."""
        if other_answers := self.quiz.other_answers(guess):
            label = "Another correct answer is" if len(other_answers) == 1 else "Other correct answers are"
            answers = linkified_and_enumerated(*other_answers.as_strings)
            return wrapped(punctuated(f"{label} {answers}"), "secondary")
        return ""

    def _colloquial(self) -> str:
        """Return the feedback about the colloquial label, if any."""
        if self.quiz.question.colloquial:
            language = ALL_LANGUAGES[self.quiz.question.language]
            question = quoted(str(self.quiz.question).strip("*"))
            return wrapped(punctuated(f"The colloquial {language} spoken was {question}"), "secondary")
        return ""

    def _meaning(self) -> str:
        """Return the quiz's meaning, if any."""
        question_meanings = linkified_and_enumerated(*self.quiz.question_meanings.as_strings)
        answer_meanings = linkified_and_enumerated(*self.quiz.answer_meanings.as_strings)
        if question_meanings and answer_meanings:
            meanings = f"{question_meanings}, respectively {answer_meanings}"
        else:
            meanings = question_meanings or answer_meanings
        return wrapped(punctuated(f"Meaning {meanings}"), "secondary") if meanings else ""

    def _notes(self) -> str:
        """Return the notes, if any."""
        return bulleted_list("Note", self.quiz.notes)

    def _examples(self) -> str:
        """Return the quiz's examples, if any."""
        examples: list[str] = []
        for example in self.quiz.concept.get_related_concepts("example"):
            example_labels = example.labels(self.language_pair.target).first_non_generated_spelling_alternatives
            example_meanings = example.labels(self.language_pair.source).first_non_generated_spelling_alternatives
            enumerated_meanings = enumerated(*[self._example_label(meaning) for meaning in example_meanings])
            examples.extend(f"{self._example_label(label)} meaning {enumerated_meanings}" for label in example_labels)
        return bulleted_list("Example", examples)

    def _example_label(self, label: Label) -> str:
        """Format the label as example."""
        label_str = quoted(str(label))
        return f"{label_str} (colloquial)" if label.colloquial else label_str


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
            "light_sky_blue3",
            postfix="\n\n",
        )


def instruction(quiz: Quiz) -> str:
    """Return the instruction for the quiz."""
    return wrapped(f"{quiz.instruction}:", "quiz", postfix="")


def show_welcome(write_output: Callable[..., None], latest_version: str | None, config: ConfigParser) -> None:
    """Show the welcome message."""
    write_output(WELCOME)
    new_version_available = latest_version and latest_version.strip("v") > VERSION
    languages_configured = config.has_option("languages", "target") and config.has_option("languages", "source")
    if new_version_available:
        news = NEWS.format(latest_version, installation_tool())
        write_output(Panel(news, expand=False))
    elif not languages_configured:
        write_output(Panel(CONFIG_LANGUAGE_TIP, expand=False))
    if new_version_available or not languages_configured:
        write_output()


def bulleted_list(label: str, items: Sequence[str], style: str = "secondary", bullet: str = "-") -> str:
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
