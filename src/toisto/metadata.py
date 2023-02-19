"""Meta data about this application."""

import pathlib
from importlib.metadata import metadata, version

import requests

from toisto.model.language import Language

_metadata = metadata("Toisto")
NAME = _metadata["name"]
SUMMARY = _metadata["summary"]
HOMEPAGE_URL = _metadata["Project-URL"].split(", ")[1]
CHANGELOG_URL = [url for url in _metadata.get_all("Project-URL") if "Changelog" in url][0].split(", ")[1]
TAGS_API_URL = "https://api.github.com/repos/fniessink/toisto/tags"

VERSION = version(NAME)
BUILT_IN_LANGUAGES = [Language("en"), Language("fi"), Language("nl")]

# File locations
_data_folder = pathlib.Path(__file__).parent.parent
TOPIC_JSON_FILES = sorted((_data_folder / "topics").glob("*.json"))
LANGUAGES_FILE = _data_folder / "languages" / "iana-language-subtag-registry.txt"
PROGRESS_JSON = pathlib.Path.home() / f".{NAME.lower()}-progress.json"

TOPICS = [json_file.stem for json_file in TOPIC_JSON_FILES]


def latest_version() -> str | None:
    """Return the latest version."""
    try:
        return requests.get(TAGS_API_URL, timeout=2).json()[0]["name"]
    except requests.RequestException:
        return None
