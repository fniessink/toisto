"""Practice command."""

from toisto.model import Label, Progress, Quiz, Topics
from toisto.ui.text import console, feedback_correct, feedback_incorrect, instruction, DONE, WELCOME, TRY_AGAIN
from toisto.ui.speech import say
from toisto.persistence import save_progress


def do_quiz(quiz: Quiz, progress: Progress) -> None:
    """Do one quiz and update the progress."""
    console.print(instruction(quiz))
    if quiz.quiz_type != "listen":
        console.print(quiz.question)
    say(quiz.question_language, quiz.question)
    guess = Label(input("> "))
    correct = quiz.is_correct(guess)
    if not correct:
        say(quiz.question_language, quiz.question)
        console.print(TRY_AGAIN)
        guess = Label(input("> "))
        correct = quiz.is_correct(guess)
    progress.update(quiz, correct)
    quiz_progress = progress.get_retention(quiz)
    console.print(feedback_correct(guess, quiz, quiz_progress) if correct else feedback_incorrect(guess, quiz))


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
