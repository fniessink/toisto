"""Store and load progress data."""

from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

from toisto.metadata import NAME
from toisto.model.language import Language
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes

from .json_file import dump_json, load_json
from .progress_format import ProgressDict


def get_progress_filepath(target_language: Language, folder: Path, uuid: str = "") -> Path:
    """Return the filename of the progress file for the specified target language."""
    return folder / f".{NAME.lower()}{f'-{uuid}' if uuid else ''}-progress-{target_language}.json"


def get_other_progress_filepaths(target_language: Language, folder: Path, uuid: str) -> list[Path]:
    """Return the filenames of the progress files for the specified language in the folder, except for the uuid."""
    progress_filepath_with_uuid = get_progress_filepath(target_language, folder, uuid)
    progress_filepaths = folder.glob(f".{NAME.lower()}*-progress-{target_language}.json")
    return [fp for fp in progress_filepaths if fp != progress_filepath_with_uuid]


def load_progress(
    target_language: Language, quizzes: Quizzes, argument_parser: ArgumentParser, config: ConfigParser
) -> Progress:
    """Load the progress from the configured progress folder."""
    folder = Path(config["progress"]["folder"])
    uuid = config["identity"]["uuid"]
    progress_filepath = get_progress_filepath(target_language, folder, uuid)
    other_progress_filepaths = get_other_progress_filepaths(target_language, folder, uuid)
    try:
        progress_dict = load_json(progress_filepath, default={})
        other_progress_dicts = [
            load_json(other_progress_filepath) for other_progress_filepath in other_progress_filepaths
        ]
    except Exception as reason:  # noqa: BLE001
        return argument_parser.error(f"{NAME} cannot parse the progress information in {folder}: {reason}.")
    update_progress_dict(progress_dict, *other_progress_dicts)
    return Progress(target_language, quizzes, progress_dict)


def save_progress(progress: Progress, config: ConfigParser) -> None:
    """Save the progress to the user's home folder."""
    folder = Path(config["progress"]["folder"])
    progress_filepath = get_progress_filepath(progress.target_language, folder, config["identity"]["uuid"])
    dump_json(progress_filepath, progress.as_dict())
    # Remove the progress file without UUID as saved by Toisto <= v0.26.0 if it still exists:
    get_progress_filepath(progress.target_language, folder).unlink(missing_ok=True)


def update_progress_dict(progress_dict: ProgressDict, *progress_dicts: ProgressDict) -> None:
    """Update the progress dict with the pauses from the other progress dicts."""
    min_date = datetime.min.isoformat()
    for other_progress_dict in progress_dicts:
        for key in other_progress_dict:
            if "skip_until" in other_progress_dict[key]:
                other_skip_until = other_progress_dict[key].get("skip_until", min_date)
                if key in progress_dict:
                    current_skip_until = progress_dict[key].get("skip_until", min_date)
                    progress_dict[key]["skip_until"] = max(current_skip_until, other_skip_until)
                else:
                    progress_dict[key] = {"skip_until": other_skip_until}
