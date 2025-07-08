"""Meta data about this application."""

from contextlib import suppress
from importlib.metadata import metadata, version
from pathlib import Path
from subprocess import DEVNULL, SubprocessError, check_output  # nosec import_subprocess
from typing import Final

import requests

from toisto.model.language import EN, FI, NL
from toisto.tools import first

_metadata = metadata("Toisto")
NAME: Final = _metadata["name"].capitalize()
SUMMARY: Final = _metadata["summary"]
_homepage_url = _metadata["Project-URL"].split(", ")[1]
README_URL: Final = f"{_homepage_url}?tab=readme-ov-file#toisto"
CHANGELOG_URL: Final = first(_metadata.get_all("Project-URL", []), lambda url: "Changelog" in url).split(", ")[1]
TAGS_API_URL: Final = "https://api.github.com/repos/fniessink/toisto/tags"
VERSION: Final = version(NAME)
BUILT_IN_LANGUAGES: Final = [EN, FI, NL]

# File locations
_data_folder = Path(__file__).parent.parent
BUILT_IN_CONCEPT_JSON_FILES: Final = sorted((_data_folder / "concepts").glob("**/*.json"))
_languages_folder = _data_folder / "languages"
LANGUAGES_FILE: Final = _languages_folder / "iana-language-subtag-registry.txt"
SPELLING_ALTERNATIVES_FILE: Final = _languages_folder / "spelling_alternatives.json"


def latest_version() -> str | None:
    """Return the latest version."""
    timeout: Final = 2
    try:
        response = requests.get(TAGS_API_URL, timeout=timeout)
        response.raise_for_status()  # We get a 403 if rate limited
        return str(response.json()[0]["name"])
    except requests.RequestException:
        return None


def installation_tool() -> str:
    """Return how the app was installed: 'uv tool', 'pipx' or 'pip'."""
    for tool, list_command in {"uv tool": ["uv", "tool", "list"], "pipx": ["pipx", "list"]}.items():
        with suppress(OSError, SubprocessError):
            if "toisto" in check_output(list_command, stderr=DEVNULL, text=True).lower():  # noqa: S603 # nosec
                return tool
    return "pip"
