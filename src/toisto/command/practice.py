"""Practice command."""

from toisto.model import Label, Progress, Quiz, Topics
from toisto.ui.text import console, feedback_correct, feedback_incorrect, linkify, instruction, DONE, WELCOME, TRY_AGAIN
from toisto.ui.speech import say
from toisto.persistence import save_progress


def do_quiz_attempt(quiz: Quiz, first_attempt: bool = True) -> tuple[Label, bool]:
    """Present the question, get the answer from the user, and evaluate it."""
    if first_attempt and "listen" not in quiz.quiz_types:
        console.print(linkify(quiz.question))
    try_again_shown = False
    while True:
        say(quiz.question_language, quiz.question, slow=not first_attempt)
        if not first_attempt and not try_again_shown:
            console.print(TRY_AGAIN)
            try_again_shown = True
        if answer := Label(input("> ").strip()):
            break
        print("\033[F", end="")  # Move cursor one line up
    correct = quiz.is_correct(answer)
    return answer, correct


def do_quiz(quiz: Quiz, progress: Progress) -> None:
    """Do one quiz and update the progress."""
    console.print(instruction(quiz))
    answer, correct = do_quiz_attempt(quiz)
    if not correct and answer != "?":
        answer, correct = do_quiz_attempt(quiz, first_attempt=False)
    progress.update(quiz, correct)
    console.print(feedback_correct(answer, quiz) if correct else feedback_incorrect(answer, quiz))


def practice(topics: Topics, progress: Progress) -> None:
    """Practice a language."""
    console.print(WELCOME)
    try:
        while quiz := progress.next_quiz(topics):
            do_quiz(quiz, progress)
        console.print(DONE)
    except (KeyboardInterrupt, EOFError):
        console.print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
