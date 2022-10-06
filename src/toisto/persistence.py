"""Classes for storing and loading data."""

import json
import pathlib


PROGRESS_JSON = pathlib.Path.home() / ".toisto-progress.json"
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
