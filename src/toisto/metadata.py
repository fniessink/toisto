"""Meta data about this application."""

from importlib.metadata import metadata, version
from pathlib import Path
from typing import Final

import requests

from toisto.model.language import Language
from toisto.tools import first

_metadata = metadata("Toisto")
NAME: Final = _metadata["name"]
SUMMARY: Final = _metadata["summary"]
_homepage_url = _metadata["Project-URL"].split(", ")[1]
README_URL: Final = f"{_homepage_url}/blob/main/README.md"
CHANGELOG_URL: Final = first(_metadata.get_all("Project-URL", []), lambda url: "Changelog" in url).split(", ")[1]
TAGS_API_URL: Final = "https://api.github.com/repos/fniessink/toisto/tags"

VERSION: Final = version(NAME)
BUILT_IN_LANGUAGES: Final = [Language("en"), Language("fi"), Language("nl")]

# File locations
_data_folder = Path(__file__).parent.parent
CONCEPT_JSON_FILES: Final = sorted((_data_folder / "concepts").glob("*.json"))
TOPIC_FILES: Final = sorted((_data_folder / "topics").glob("**/*.json"))
LANGUAGES_FILE: Final = _data_folder / "languages" / "iana-language-subtag-registry.txt"


def get_progress_filepath(target_language: Language) -> Path:
    """Return the filename of the progress file for the specified target language."""
    return Path.home() / f".{NAME.lower()}-progress-{target_language}.json"


def latest_version() -> str | None:
    """Return the latest version."""
    timeout: Final = 2
    try:
        response = requests.get(TAGS_API_URL, timeout=timeout)
        response.raise_for_status()  # We get a 403 if rate limited
        return response.json()[0]["name"]
    except requests.RequestException:
        return None
