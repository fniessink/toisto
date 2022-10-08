"""Classes for storing and loading data."""

import json
import pathlib
import sys

from .metadata import NAME
from .model import Entry, Progress


PROGRESS_JSON = pathlib.Path.home() / f".{NAME.lower()}-progress.json"
DECKS_FOLDER = pathlib.Path(__file__).parent / "decks"


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


def load_entries() -> list[Entry]:
    """Load the entries from the decks."""
    entries = []
    for deck in DECKS_FOLDER.glob("*.json"):
        for entry in load_json(deck):
            entry = Entry("nl", "fi", entry["nl"], entry["fi"])
            entries.extend([entry, entry.reversed()])
    return entries


def load_progress() -> Progress:
    """Load the progress from the user's home folder."""
    try:
        return Progress(load_json(PROGRESS_JSON, default={}))
    except json.decoder.JSONDecodeError as reason:
        sys.stderr.write(
            f"""{NAME} cannot parse the progress information in {PROGRESS_JSON}: {reason}.
To fix this, remove or rename {PROGRESS_JSON} and start {NAME} again. Unfortunately, this will reset your progress.
Please consider opening a bug report at https://github.com/fniessink/{NAME.lower()}. Be sure to attach the invalid
progress file to the issue.
""")
        sys.exit(1)


def save_progress(progress: Progress) -> None:
    """Save the progress to the user's home folder."""
    dump_json(PROGRESS_JSON, progress.as_dict())
