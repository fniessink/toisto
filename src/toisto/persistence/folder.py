"""Platform independent way get the home folder."""

from pathlib import Path

from ..tools import platform


def home() -> Path:
    """Return the home folder."""
    return Path("~/Documents").expanduser() if platform() == "ashell" else Path.home()
