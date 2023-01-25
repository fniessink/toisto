"""Store and load progress data."""

from argparse import ArgumentParser
from typing import NoReturn
import pathlib

from ..metadata import NAME
from ..model import Progress, Topics

from .json_file import load_json, dump_json


PROGRESS_JSON = pathlib.Path.home() / f".{NAME.lower()}-progress.json"


def load_progress(topics: Topics, argument_parser: ArgumentParser) -> Progress | NoReturn:
    """Load the progress from the user's home folder."""
    try:
        progress_dict = load_json(PROGRESS_JSON, default={})
        return Progress(progress_dict, topics)
    except Exception as reason:  # pylint: disable=broad-except
        return argument_parser.error(
            f"""{NAME} cannot parse the progress information in {PROGRESS_JSON}: {reason}.
To fix this, remove or rename {PROGRESS_JSON} and start {NAME} again. Unfortunately, this will reset your progress.
Please consider opening a bug report at https://github.com/fniessink/{NAME.lower()}. Be sure to attach the invalid
progress file to the issue.
"""
        )


def save_progress(progress: Progress) -> None:
    """Save the progress to the user's home folder."""
    dump_json(PROGRESS_JSON, progress.as_dict())
