"""Practice command."""

from collections.abc import Callable
from configparser import ConfigParser
from typing import get_args

from toisto.model.language import LanguagePair
from toisto.model.language.label import Label
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import ListenQuizType, Quiz
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkified
from toisto.ui.speech import say
from toisto.ui.text import (
    DONE,
    feedback_correct,
    feedback_incorrect,
    feedback_skip,
    feedback_try_again,
    instruction,
)


def do_quiz_attempt(quiz: Quiz, config: ConfigParser, attempt: int = 1) -> Label:
    """Present the question and get the answer from the user."""
    while True:
        say(quiz.question.language, quiz.question.pronounceable, config, slow=attempt > 1)
        if answer := Label(quiz.answer.language, input("> ").strip()):
            break
        print("\033[F", end="")  # noqa: T201  # Move cursor one line up
    return answer


def evaluate_answer(
    quiz: Quiz,
    progress: Progress,
    language_pair: LanguagePair,
    answer: Label,
    attempt: int = 1,
) -> str:
    """Evaluate the answer and return the user feedback."""
    if quiz.is_correct(answer):
        progress.mark_correct_answer(quiz)
        return feedback_correct(answer, quiz, language_pair)
    if str(answer) == "?":
        progress.mark_incorrect_answer(quiz)
        return feedback_skip(quiz)
    if attempt == 1:
        return feedback_try_again(answer, quiz)
    progress.mark_incorrect_answer(quiz)
    return feedback_incorrect(answer, quiz)


def do_quiz(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    quiz: Quiz,
    progress: Progress,
    config: ConfigParser,
) -> None:
    """Do one quiz and update the progress."""
    write_output(instruction(quiz))
    if quiz.quiz_types[0] not in get_args(ListenQuizType):
        write_output(linkified(quiz.question))
    for attempt in range(1, 3):
        answer = do_quiz_attempt(quiz, config, attempt)
        feedback = evaluate_answer(quiz, progress, language_pair, answer, attempt)
        write_output(feedback)
        if quiz.is_correct(answer) or answer == Label(quiz.answer.language, "?"):
            break


def practice(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    progress: Progress,
    config: ConfigParser,
) -> None:
    """Practice a language."""
    try:
        while quiz := progress.next_quiz():
            do_quiz(write_output, language_pair, quiz, progress, config)
        write_output(DONE)
    except (KeyboardInterrupt, EOFError):
        write_output()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
