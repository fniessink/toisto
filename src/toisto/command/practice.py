"""Practice command."""

from ..color import purple
from ..model import Progress, Quiz
from ..output import feedback_correct, feedback_incorrect, DONE, WELCOME, TRY_AGAIN
from ..persistence import save_progress
from ..speech import say


def do_quiz(quiz: Quiz, progress: Progress) -> None:
    """Do one quiz and update the progress."""
    print(purple(f"{quiz.instruction()}:"))
    say(quiz.question_language, quiz.question)
    guess = input("> ")
    correct = quiz.is_correct(guess)
    if not correct:
        print(TRY_AGAIN)
        guess = input("> ")
        correct = quiz.is_correct(guess)
    progress.update(quiz, correct)
    quiz_progress = progress.get_progress(quiz)
    print(feedback_correct(guess, quiz, quiz_progress) if correct else feedback_incorrect(guess, quiz))


def practice(quizzes, progress: Progress) -> None:
    """Practice a language."""
    print(WELCOME)
    try:
        while quiz := progress.next_quiz(quizzes):
            do_quiz(quiz, progress)
        print(DONE)
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
