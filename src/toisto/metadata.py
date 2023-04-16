"""Meta data about this application."""

import pathlib
from importlib.metadata import metadata, version
from typing import Final

import requests

from toisto.model.language import Language

_metadata = metadata("Toisto")
NAME: Final = _metadata["name"]
SUMMARY: Final = _metadata["summary"]
_homepage_url = _metadata["Project-URL"].split(", ")[1]
README_URL: Final = f"{_homepage_url}/blob/main/README.md"
CHANGELOG_URL: Final = [url for url in _metadata.get_all("Project-URL") if "Changelog" in url][0].split(", ")[1]
TAGS_API_URL: Final = "https://api.github.com/repos/fniessink/toisto/tags"

VERSION: Final = version(NAME)
BUILT_IN_LANGUAGES: Final = [Language("en"), Language("fi"), Language("nl")]

# File locations
_data_folder = pathlib.Path(__file__).parent.parent
TOPIC_JSON_FILES: Final = sorted((_data_folder / "topics").glob("*.json"))
LANGUAGES_FILE: Final = _data_folder / "languages" / "iana-language-subtag-registry.txt"


def get_progress_filepath(target_language: Language) -> pathlib.Path:
    """Return the filename of the progress file for the specified target language."""
    return pathlib.Path.home() / f".{NAME.lower()}-progress-{target_language}.json"


TOPICS: Final = sorted([json_file.stem for json_file in TOPIC_JSON_FILES])


def latest_version() -> str | None:
    """Return the latest version."""
    try:
        return requests.get(TAGS_API_URL, timeout=2).json()[0]["name"]
    except requests.RequestException:
        return None
