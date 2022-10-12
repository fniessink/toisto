"""Main module for the application."""

import readline  # pylint: disable=unused-import

from .cli import parser
from .output import feedback, DONE, WELCOME
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
            print(feedback(correct, guess, quiz.get_answer(), progress.get_progress(quiz)))
        print(DONE)
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
