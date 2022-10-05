"""Main module for Toisto."""

import json
import os
import pathlib
import random
import readline  # pylint: disable=unused-import

from .diff import colored_diff
from .match import match


VOICES = dict(fi="Satu", nl="Xander")

def say(language: str, text: str) -> None:
    """Say the text in the specified language."""
    voice = VOICES[language]
    os.system(f"say --voice={voice} --interactive=bold '{text}'")


def load_json(json_file_path: pathlib.Path, default=None):
    """Load the JSON from the file. Return default if file does not exist."""
    if json_file_path.exists():
        with json_file_path.open(encoding="utf-8") as json_file:
            return json.load(json_file)
    return default


def dump_json(json_file_path: pathlib.Path, contents) -> None:
    """Dump the JSON into the file."""
    with json_file_path.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file)


def next_entry(entries, progress):
    """Return the next entry to quiz the user with."""
    min_progress = min(progress.get(str(entry), 0) for entry in entries)
    next_entries = [entry for entry in entries if progress.get(str(entry), 0) == min_progress]
    return random.choice(next_entries)


PROGRESS_JSON = pathlib.Path.home() / ".toisto-progress.json"
DECKS_FOLDER = pathlib.Path(__file__).parent / "decks"


def main():
    """Main program."""
    entries = []
    for deck in DECKS_FOLDER.glob("*.json"):
        for entry in load_json(deck):
            entries.extend([entry, dict(reversed(entry.items()))])

    progress = load_json(PROGRESS_JSON, default={})

    print("""Welcome to 'Toisto'!

    Practice as many words and phrases as you like, as long as you like. Hit Ctrl-C or Ctrl-D to quit.
    Toisto tracks how many times you correctly translate words and phrases. The fewer times you have
    translated a word or phrase successfully, the more often it is presented for you to translate.
    """)
    try:
        while True:
            entry = next_entry(entries, progress)
            question, answer = entry.values()
            question_language = list(entry.keys())[0]
            say(question_language, question)
            guess = input("> ")
            correct = match(guess, answer)
            key = str(entry)
            progress[key] = progress.setdefault(key, 0) + 2 if correct else -1
            diff = colored_diff(guess, answer)
            print(("✅ Correct" if correct else f'❌ Incorrect. The correct answer is "{diff}"') + ".\n")
    except (KeyboardInterrupt, EOFError):
        print()  # Make sure the shell prompt is displayed on a new line
    finally:
        dump_json(PROGRESS_JSON, progress)
