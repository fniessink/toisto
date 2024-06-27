"""Practice command."""

from collections.abc import Callable
from configparser import ConfigParser
from typing import get_args

from toisto.model.language import LanguagePair
from toisto.model.language.label import Label
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import ListenQuizType, Quiz
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkified
from toisto.ui.speech import say
from toisto.ui.text import DONE, Feedback, ProgressUpdate, instruction


def do_quiz_attempt(quiz: Quiz, config: ConfigParser, attempt: int) -> Label:
    """Present the question and get the answer from the user."""
    while True:
        say(quiz.question.language, quiz.question.pronounceable, config, slow=attempt > 1)
        if answer := Label(quiz.answer.language, input("> ").strip()):
            break
        print("\033[F", end="")  # noqa: T201  # Move cursor one line up
    return answer


def do_quiz(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    quiz: Quiz,
    progress: Progress,
    config: ConfigParser,
) -> None:
    """Do one quiz and update the progress."""
    feedback = Feedback(quiz, language_pair)
    write_output(instruction(quiz))
    if quiz.quiz_types[0] not in get_args(ListenQuizType):
        write_output(linkified(quiz.question))
    for attempt in range(1, 3):
        guess = do_quiz_attempt(quiz, config, attempt)
        evaluation = quiz.evaluate(guess, attempt)
        progress.mark_evaluation(quiz, evaluation)
        write_output(feedback(evaluation, guess))
        if evaluation in (Evaluation.CORRECT, Evaluation.SKIPPED):
            break


def practice(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    progress: Progress,
    config: ConfigParser,
    progress_update_frequency: int,
) -> None:
    """Practice a language."""
    progress_update = ProgressUpdate(progress, progress_update_frequency)
    try:
        while quiz := progress.next_quiz():
            do_quiz(write_output, language_pair, quiz, progress, config)
            write_output(progress_update())
        write_output(DONE)
    except (KeyboardInterrupt, EOFError):
        write_output()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
