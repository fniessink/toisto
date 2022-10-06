"""Main module for Toisto."""

import random
import readline  # pylint: disable=unused-import
from importlib.metadata import version

from .diff import colored_diff
from .model import Entry
from .persistence import dump_json, load_json, DECKS_FOLDER, PROGRESS_JSON
from .speech import say


def next_entry(entries, progress) -> Entry:
    """Return the next entry to quiz the user with."""
    min_progress = min(progress.get(str(entry), 0) for entry in entries)
    next_entries = [entry for entry in entries if progress.get(str(entry), 0) == min_progress]
    entry_dict = random.choice(next_entries)
    question_language, answer_language = entry_dict.keys()
    question, answer = entry_dict.values()
    return Entry(question_language, answer_language, question, answer)


def main():
    """Main program."""
    entries = []
    for deck in DECKS_FOLDER.glob("*.json"):
        for entry in load_json(deck):
            entries.extend([entry, dict(reversed(entry.items()))])

    progress = load_json(PROGRESS_JSON, default={})

    print(f"""Welcome to 'Toisto' v{version('Toisto')}!

    Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
    Toisto tracks how many times you correctly translate words and phrases. The fewer times you have
    translated a word or phrase successfully, the more often it is presented for you to translate.
    """)
    try:
        while True:
            entry = next_entry(entries, progress)
            say(entry.question_language, entry.question)
            guess = input("> ")
            correct = entry.is_correct(guess)
            key = str(entry)
            progress[key] = progress.setdefault(key, 0) + 2 if correct else -1
            diff = colored_diff(guess, entry.answer)
            print(("✅ Correct" if correct else f'❌ Incorrect. The correct answer is "{diff}"') + ".\n")
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        dump_json(PROGRESS_JSON, progress)
