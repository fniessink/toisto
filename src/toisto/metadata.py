"""Meta data about this application."""

import pathlib
from importlib.metadata import metadata, version
from typing import Literal


_metadata = metadata("Toisto")
NAME = _metadata["name"]
SUMMARY = _metadata["summary"]

VERSION = version(NAME)
SUPPORTED_LANGUAGES = dict(en="English", fi="Finnish", nl="Dutch")
Language = Literal["en", "fi", "nl"]

_topics_folder = pathlib.Path(__file__).parent.parent / "topics"
TOPIC_JSON_FILES = sorted(list(_topics_folder.glob("*.json")))
TOPICS = [json_file.stem for json_file in TOPIC_JSON_FILES]
