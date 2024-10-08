"""Store and load progress data."""

from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

from toisto.metadata import NAME
from toisto.model.language import Language
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes

from .json_file import dump_json, load_json


def get_progress_filepath(target_language: Language, folder: Path, uuid: str = "") -> Path:
    """Return the filename of the progress file for the specified target language."""
    return folder / f".{NAME.lower()}{f'-{uuid}' if uuid else ''}-progress-{target_language}.json"


def load_progress(
    target_language: Language, quizzes: Quizzes, argument_parser: ArgumentParser, config: ConfigParser
) -> Progress:
    """Load the progress from the user's home folder."""
    folder = Path(config["progress"]["folder"])
    progress_filepath = get_progress_filepath(target_language, folder, config["identity"]["uuid"])
    if not progress_filepath.exists():
        # Read the progress file without UUID as saved by Toisto <= v0.26.0:
        progress_filepath = get_progress_filepath(target_language, folder)
    try:
        progress_dict = load_json(progress_filepath, default={})
    except Exception as reason:  # noqa: BLE001
        return argument_parser.error(
            f"""{NAME} cannot parse the progress information in {progress_filepath}: {reason}.
To fix this, remove or rename {progress_filepath} and start {NAME} again. Unfortunately, this will reset your progress.
Please consider opening a bug report at https://github.com/fniessink/{NAME.lower()}. Be sure to attach the invalid
progress file to the issue.
""",
        )
    return Progress(progress_dict, target_language, quizzes)


def save_progress(progress: Progress, config: ConfigParser) -> None:
    """Save the progress to the user's home folder."""
    folder = Path(config["progress"]["folder"])
    progress_filepath = get_progress_filepath(progress.target_language, folder, config["identity"]["uuid"])
    dump_json(progress_filepath, progress.as_dict())
    # Remove the progress file without UUID as saved by Toisto <= v0.26.0 if it still exists:
    get_progress_filepath(progress.target_language, folder).unlink(missing_ok=True)
