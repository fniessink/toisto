"""Meta data about this application."""

import pathlib
from importlib.metadata import metadata, version


_metadata = metadata("Toisto")
NAME = _metadata["name"]
SUMMARY = _metadata["summary"]

VERSION = version(NAME)

_decks_folder = pathlib.Path(__file__).parent / "decks"
DECKS_JSON_FILES = list(_decks_folder.glob("*.json"))
DECKS = [json_file.stem for json_file in DECKS_JSON_FILES]
