"""Load and dump JSON."""

import errno
import json
import os
import pathlib


def load_json(json_file_path: pathlib.Path, default=None):
    """Load the JSON from the file. Return default if file does not exist."""
    if json_file_path.exists():
        with json_file_path.open(encoding="utf-8") as json_file:
            return json.load(json_file)
    if default is None:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(json_file_path))
    return default


def dump_json(json_file_path: pathlib.Path, contents) -> None:
    """Dump the JSON into the file."""
    with json_file_path.open("w", encoding="utf-8") as json_file:
        json.dump(contents, json_file)
