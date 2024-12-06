"""Practice command."""

from argparse import Namespace
from collections.abc import Callable
from configparser import ConfigParser

import dramatic

from toisto.model.language import LanguagePair
from toisto.model.language.label import Label
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import ListenOnlyQuizType
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkified
from toisto.ui.speech import Speech
from toisto.ui.text import DONE, Feedback, ProgressUpdate, instruction


def do_quiz_attempt(quiz: Quiz, speech: Speech, attempt: int) -> Label:
    """Present the question and get the answer from the user."""
    repeat_speech = False
    while True:
        speech.say(quiz.question.language, quiz.question.pronounceable, slow=repeat_speech or attempt > 1)
        if answer := Label(quiz.answer.language, input("> ").strip()):
            break
        repeat_speech = True
        print("\033[F", end="")  # noqa: T201  # Move cursor one line up
    return answer


def do_quiz(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    quiz: Quiz,
    progress: Progress,
    speech: Speech,
) -> None:
    """Do one quiz and update the progress."""
    feedback = Feedback(quiz, language_pair)
    write_output(instruction(quiz))
    if not quiz.has_quiz_type(ListenOnlyQuizType):
        write_output(linkified(str(quiz.question)))
    for attempt in range(1, 3):
        guess = do_quiz_attempt(quiz, speech, attempt)
        evaluation = quiz.evaluate(guess, language_pair, attempt)
        progress.mark_evaluation(quiz, evaluation)
        write_output(feedback(evaluation, guess))
        if evaluation in (Evaluation.CORRECT, Evaluation.SKIPPED):
            break


def practice(
    write_output: Callable[..., None],
    language_pair: LanguagePair,
    progress: Progress,
    config: ConfigParser,
    args: Namespace,
) -> None:
    """Practice a language."""
    progress_update = ProgressUpdate(progress, args.progress_update)
    speech = Speech(config)
    try:
        while quiz := progress.next_quiz():
            do_quiz(write_output, language_pair, quiz, progress, speech)
            save_progress(progress, config)
            with dramatic.output.at_speed(120):
                # Turn off highlighting to work around https://github.com/treyhunner/dramatic/issues/8:
                write_output(progress_update(), end="", highlight=False)
        write_output(DONE)
    except (KeyboardInterrupt, EOFError):
        write_output()  # Make sure the shell prompt is displayed on a new line
