"""Main module for Toisto."""

import readline  # pylint: disable=unused-import
from importlib.metadata import version

from .diff import colored_diff
from .model import Entry, Progress
from .persistence import dump_json, load_json, DECKS_FOLDER, PROGRESS_JSON
from .speech import say


def main():
    """Main program."""
    entries = []
    for deck in DECKS_FOLDER.glob("*.json"):
        for entry in load_json(deck):
            entry = Entry("nl", "fi", entry["nl"], entry["fi"])
            entries.extend([entry, entry.reversed()])

    progress = Progress(load_json(PROGRESS_JSON, default={}))

    print(f"""Welcome to 'Toisto' v{version('Toisto')}!

    Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
    Toisto tracks how many times you correctly translate words and phrases. The fewer times you have
    translated a word or phrase successfully, the more often it is presented for you to translate.
    """)
    try:
        while True:
            entry = progress.next_entry(entries)
            say(entry.question_language, entry.get_question())
            guess = input("> ")
            correct = entry.is_correct(guess)
            progress.update(entry, correct)
            diff = colored_diff(guess, entry.get_answer())
            print(("✅ Correct" if correct else f'❌ Incorrect. The correct answer is "{diff}"') + ".\n")
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        dump_json(PROGRESS_JSON, progress.as_dict())
