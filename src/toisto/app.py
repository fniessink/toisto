"""Main module for the application."""

import readline  # pylint: disable=unused-import

from .cli import parser
from .output import feedback, DONE, WELCOME
from .persistence import load_entries, load_progress, save_progress
from .speech import say


def main():
    """Main program."""
    namespace = parser.parse_args()
    entries = load_entries(namespace.deck)
    progress = load_progress()
    print(WELCOME)
    try:
        while entry := progress.next_entry(entries):
            say(entry.question_language, entry.get_question())
            guess = input("> ")
            correct = entry.is_correct(guess)
            progress.update(entry, correct)
            print(feedback(correct, guess, entry.get_answer(), progress.get_progress(entry)))
        print(DONE)
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
