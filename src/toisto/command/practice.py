"""Practice command."""

from configparser import ConfigParser

from toisto.model.language.label import Label
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz
from toisto.persistence.progress import save_progress
from toisto.ui.dictionary import linkify
from toisto.ui.speech import say
from toisto.ui.text import DONE, TRY_AGAIN, console, feedback_correct, feedback_incorrect, instruction


def do_quiz_attempt(quiz: Quiz, config: ConfigParser, attempt: int = 1) -> tuple[Label, bool]:
    """Present the question, get the answer from the user, and evaluate it."""
    while True:
        say(quiz.question_language, quiz.question, config, slow=attempt > 1)
        if answer := Label(input("> ").strip()):
            break
        print("\033[F", end="")  # noqa: T201  # Move cursor one line up
    return answer, quiz.is_correct(answer)


def do_quiz(quiz: Quiz, progress: Progress, config: ConfigParser) -> None:
    """Do one quiz and update the progress."""
    console.print(instruction(quiz))
    if "listen" not in quiz.quiz_types:
        console.print(linkify(quiz.question))
    answer, correct = do_quiz_attempt(quiz, config)
    if not correct and answer != "?":
        console.print(TRY_AGAIN)
        answer, correct = do_quiz_attempt(quiz, config, attempt=2)
    if correct:
        progress.increase_retention(quiz)
        feedback = feedback_correct(answer, quiz)
    else:
        progress.reset_retention(quiz)
        feedback = feedback_incorrect(answer, quiz)
    console.print(feedback)


def practice(progress: Progress, config: ConfigParser) -> None:
    """Practice a language."""
    try:
        while quiz := progress.next_quiz():
            do_quiz(quiz, progress, config)
        console.print(DONE)
    except (KeyboardInterrupt, EOFError):
        console.print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
