"""Meta data about this application."""

import pathlib
from importlib.metadata import metadata, version
from typing import Literal

import requests


_metadata = metadata("Toisto")
NAME = _metadata["name"]
SUMMARY = _metadata["summary"]
CHANGELOG_URL = [url for url in _metadata.get_all("Project-URL") if "Changelog" in url][0].split(", ")[1]
TAGS_API_URL = "https://api.github.com/repos/fniessink/toisto/tags"

VERSION = version(NAME)
SUPPORTED_LANGUAGES = dict(en="English", fi="Finnish", nl="Dutch")
Language = Literal["en", "fi", "nl"]

_topics_folder = pathlib.Path(__file__).parent.parent / "topics"
TOPIC_JSON_FILES = sorted(list(_topics_folder.glob("*.json")))
TOPICS = [json_file.stem for json_file in TOPIC_JSON_FILES]


def latest_version() -> str | None:
    """Return the latest version."""
    try:
        return requests.get(TAGS_API_URL, timeout=2).json()[0]["name"]
    except requests.ConnectionError:
        return None
