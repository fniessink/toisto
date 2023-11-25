"""Practice command."""

from collections.abc import Callable
from configparser import ConfigParser
from typing import get_args

from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Label
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import ListenQuizType, Quiz, Quizzes
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkify
from toisto.ui.speech import say
from toisto.ui.text import (
    DONE,
    TRY_AGAIN,
    TRY_AGAIN_IN_ANSWER_LANGUAGE,
    feedback_correct,
    feedback_incorrect,
    instruction,
)


def do_quiz_attempt(quiz: Quiz, config: ConfigParser, attempt: int = 1) -> Label:
    """Present the question and get the answer from the user."""
    while True:
        say(quiz.question_language, quiz.question.pronounceable, config, slow=attempt > 1)
        if answer := Label(input("> ").strip()):
            break
        print("\033[F", end="")  # noqa: T201  # Move cursor one line up
    return answer


def evaluate_quiz(quiz: Quiz, progress: Progress, answer: Label) -> str:
    """Evaluate the quiz and return the user feedback."""
    if quiz.is_correct(answer):
        progress.mark_correct_answer(quiz)
        feedback = feedback_correct
    else:
        progress.mark_incorrect_answer(quiz)
        feedback = feedback_incorrect
    return feedback(answer, quiz)


def do_quiz(write_output: Callable[..., None], quiz: Quiz, progress: Progress, config: ConfigParser) -> None:
    """Do one quiz and update the progress."""
    write_output(instruction(quiz))
    if quiz.quiz_types[0] not in get_args(ListenQuizType):
        write_output(linkify(quiz.question))
    answer = do_quiz_attempt(quiz, config)
    if not quiz.is_correct(answer) and answer != "?":
        if quiz.is_question(answer):
            try_again = TRY_AGAIN_IN_ANSWER_LANGUAGE % dict(language=ALL_LANGUAGES[quiz.answer_language])
        else:
            try_again = TRY_AGAIN
        write_output(try_again)
        answer = do_quiz_attempt(quiz, config, attempt=2)
    feedback = evaluate_quiz(quiz, progress, answer)
    write_output(feedback)


def practice(write_output: Callable[..., None], quizzes: Quizzes, progress: Progress, config: ConfigParser) -> None:
    """Practice a language."""
    try:
        while quiz := progress.next_quiz(quizzes):
            do_quiz(write_output, quiz, progress, config)
        write_output(DONE)
    except (KeyboardInterrupt, EOFError):
        write_output()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
