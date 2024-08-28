"""Platform independent way get the home folder."""

from pathlib import Path


def home() -> Path:
    """Return the home folder."""
    return Path.home()
