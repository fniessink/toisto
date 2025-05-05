"""Load and dump JSON."""

import errno
import json
import os
from pathlib import Path
from typing import cast


def load_json(json_file_path: Path, default: dict | None = None) -> dict:
    """Load the JSON from the file. Return default if file does not exist."""
    if json_file_path.exists():
        with json_file_path.open(encoding="utf-8") as json_file:
            return cast("dict", json.load(json_file))
    if default is None:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(json_file_path))
    return default or {}


def dump_json(json_file_path: Path, contents: dict | list) -> None:
    """Dump the JSON into the file."""
    with json_file_path.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file)
