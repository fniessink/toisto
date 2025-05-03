"""Store and load progress data."""

from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import UTC, datetime
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


def get_progress_filepaths(target_language: Language, folder: Path) -> list[Path]:
    """Return the filenames of the progress files for the specified language in the folder."""
    return list(folder.glob(f".{NAME.lower()}*-progress-{target_language}.json"))


def load_progress(
    target_language: Language, quizzes: Quizzes, argument_parser: ArgumentParser, config: ConfigParser
) -> Progress:
    """Load the progress from the configured progress folder."""
    folder = Path(config["progress"]["folder"])
    uuid = config["identity"]["uuid"]
    progress_filepath = get_progress_filepath(target_language, folder, uuid)
    progress_dict = load_progress_file(progress_filepath, quizzes, argument_parser)
    progress_filepaths = get_progress_filepaths(target_language, folder)
    other_progress_dicts = [
        load_progress_file(other_progress_filepath, quizzes, argument_parser)
        for other_progress_filepath in progress_filepaths
        if other_progress_filepath != progress_filepath
    ]
    update_progress_dict(progress_dict, *other_progress_dicts)
    return Progress(target_language, quizzes, progress_dict)


def load_progress_file(progress_filepath: Path, quizzes: Quizzes, argument_parser: ArgumentParser) -> ProgressDict:
    """Load progress from one progress file."""
    try:
        progress_dict = load_json(progress_filepath, default={})
    except Exception as reason:  # noqa: BLE001
        return argument_parser.error(
            f"""{NAME} cannot parse the progress information in {progress_filepath}: {reason}.
To fix this, remove or rename {progress_filepath} and start {NAME} again. Unfortunately, this will reset your
progress. Please consider opening a bug report at https://github.com/fniessink/{NAME.lower()}. Be sure to attach
the invalid progress file to the issue.
""",
        )
    update_quiz_keys(progress_dict, quizzes)
    return progress_dict


def save_progress(progress: Progress, config: ConfigParser) -> None:
    """Save the progress to the user's home folder."""
    folder = Path(config["progress"]["folder"])
    progress_filepath = get_progress_filepath(progress.target_language, folder, config["identity"]["uuid"])
    dump_json(progress_filepath, progress.as_dict())
    # Remove the progress file without UUID as saved by Toisto <= v0.26.0 if it still exists:
    get_progress_filepath(progress.target_language, folder).unlink(missing_ok=True)


def update_progress_dict(progress_dict: ProgressDict, *progress_dicts: ProgressDict) -> None:
    """Update the progress dict with the pauses from the other progress dicts."""
    min_date = datetime.min.replace(tzinfo=UTC).isoformat()
    for other_progress_dict in progress_dicts:
        for key in other_progress_dict:
            if "skip_until" in other_progress_dict[key]:
                other_skip_until = other_progress_dict[key].get("skip_until", min_date)
                if key in progress_dict:
                    current_skip_until = progress_dict[key].get("skip_until", min_date)
                    progress_dict[key]["skip_until"] = max(current_skip_until, other_skip_until)
                else:
                    progress_dict[key] = {"skip_until": other_skip_until}


def update_quiz_keys(progress_dict: ProgressDict, quizzes: Quizzes) -> None:
    """Replace old quiz keys with new keys in the progress dict."""
    for quiz in quizzes:
        if quiz.old_key in progress_dict:
            progress_dict[quiz.key] = progress_dict[quiz.old_key]
            del progress_dict[quiz.old_key]
