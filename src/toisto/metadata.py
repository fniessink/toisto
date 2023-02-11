"""Meta data about this application."""

import pathlib
from importlib.metadata import metadata, version
from typing import Literal

import requests

_metadata = metadata("Toisto")
NAME = _metadata["name"]
SUMMARY = _metadata["summary"]
HOMEPAGE_URL = _metadata["Project-URL"].split(", ")[1]
CHANGELOG_URL = [url for url in _metadata.get_all("Project-URL") if "Changelog" in url][0].split(", ")[1]
TAGS_API_URL = "https://api.github.com/repos/fniessink/toisto/tags"

VERSION = version(NAME)
Language = Literal["en", "fi", "nl"]
SUPPORTED_LANGUAGES: dict[Language, str] = dict(en="English", fi="Finnish", nl="Dutch")

_topics_folder = pathlib.Path(__file__).parent.parent / "topics"
TOPIC_JSON_FILES = sorted(_topics_folder.glob("*.json"))
TOPICS = [json_file.stem for json_file in TOPIC_JSON_FILES]
PROGRESS_JSON = pathlib.Path.home() / f".{NAME.lower()}-progress.json"


def latest_version() -> str | None:
    """Return the latest version."""
    try:
        return requests.get(TAGS_API_URL, timeout=2).json()[0]["name"]
    except requests.ConnectionError:
        return None
