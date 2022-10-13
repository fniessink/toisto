"""Main module for the application."""

import readline  # pylint: disable=unused-import

from .cli import parser
from .output import feedback_correct, feedback_incorrect, DONE, WELCOME
from .persistence import load_quizzes, load_progress, save_progress
from .speech import say


def main():
    """Main program."""
    namespace = parser.parse_args()
    quizzes = load_quizzes(namespace.deck)
    progress = load_progress()
    print(WELCOME)
    try:
        while quiz := progress.next_quiz(quizzes):
            say(quiz.question_language, quiz.question)
            guess = input("> ")
            correct = quiz.is_correct(guess)
            progress.update(quiz, correct)
            quiz_progress = progress.get_progress(quiz)
            print(feedback_correct(guess, quiz, quiz_progress) if correct else feedback_incorrect(guess, quiz))
        print(DONE)
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
