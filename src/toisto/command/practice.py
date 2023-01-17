"""Practice command."""

from toisto.model import Label, Progress, Quiz
from toisto.ui.dictionary import linkify
from toisto.ui.speech import say
from toisto.ui.text import console, feedback_correct, feedback_incorrect, instruction, DONE, TRY_AGAIN
from toisto.persistence import save_progress


def do_quiz_attempt(quiz: Quiz, second_attempt: bool = False) -> tuple[Label, bool]:
    """Present the question, get the answer from the user, and evaluate it."""
    while True:
        say(quiz.question_language, quiz.question, slow=second_attempt)
        if answer := Label(input("> ").strip()):
            break
        print("\033[F", end="")  # Move cursor one line up
    return answer, quiz.is_correct(answer)


def do_quiz(quiz: Quiz, progress: Progress) -> None:
    """Do one quiz and update the progress."""
    console.print(instruction(quiz))
    if "listen" not in quiz.quiz_types:
        console.print(linkify(quiz.question))
    answer, correct = do_quiz_attempt(quiz)
    if not correct and answer != "?":
        console.print(TRY_AGAIN)
        answer, correct = do_quiz_attempt(quiz, second_attempt=True)
    progress.update(quiz, correct)
    console.print(feedback_correct(answer, quiz) if correct else feedback_incorrect(answer, quiz))


def practice(progress: Progress) -> None:
    """Practice a language."""
    try:
        while quiz := progress.next_quiz():
            do_quiz(quiz, progress)
        console.print(DONE)
    except (KeyboardInterrupt, EOFError):
        console.print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
