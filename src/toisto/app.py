"""Main module for the application."""

import readline  # pylint: disable=unused-import

from .cli import parser
from .diff import colored_diff
from .metadata import NAME, VERSION
from .persistence import load_entries, load_progress, save_progress
from .speech import say


def main():
    """Main program."""
    namespace = parser.parse_args()
    entries = load_entries(namespace.deck)
    progress = load_progress()

    print(f"""Welcome to '{NAME}' v{VERSION}!

    Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
    {NAME} tracks how many times you correctly translate words and phrases. The fewer times you have
    translated a word or phrase successfully, the more often it is presented for you to translate.
    """)
    try:
        while True:
            entry = progress.next_entry(entries)
            say(entry.question_language, entry.get_question())
            guess = input("> ")
            correct = entry.is_correct(guess)
            progress.update(entry, correct)
            if correct:
                print("✅ Correct.\n")
            else:
                diff = colored_diff(guess, entry.get_answer())
                print(f'❌ Incorrect. The correct answer is "{diff}".\n')
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        save_progress(progress)
