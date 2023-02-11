"""Store and load progress data."""

from argparse import ArgumentParser
from typing import NoReturn

from ..metadata import NAME, PROGRESS_JSON
from ..model.quiz.progress import Progress
from ..model.quiz.topic import Topics
from .json_file import dump_json, load_json


def load_progress(topics: Topics, argument_parser: ArgumentParser) -> Progress | NoReturn:
    """Load the progress from the user's home folder."""
    try:
        progress_dict = load_json(PROGRESS_JSON, default={})
    except Exception as reason:  # noqa: BLE001
        return argument_parser.error(
            f"""{NAME} cannot parse the progress information in {PROGRESS_JSON}: {reason}.
To fix this, remove or rename {PROGRESS_JSON} and start {NAME} again. Unfortunately, this will reset your progress.
Please consider opening a bug report at https://github.com/fniessink/{NAME.lower()}. Be sure to attach the invalid
progress file to the issue.
""",
        )
    return Progress(progress_dict, topics)


def save_progress(progress: Progress) -> None:
    """Save the progress to the user's home folder."""
    dump_json(PROGRESS_JSON, progress.as_dict())
