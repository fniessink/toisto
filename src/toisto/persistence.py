"""Classes for storing and loading data."""

import errno
import json
import os
import pathlib

from .metadata import NAME, TOPIC_JSON_FILES, Language
from .model import concept_factory, Progress, Quizzes
from .output import show_error_and_exit


PROGRESS_JSON = pathlib.Path.home() / f".{NAME.lower()}-progress.json"


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


def load_quizzes(
    language: Language, source_language: Language, topics_to_load: list[str], topic_files_to_load: list[str]
) -> Quizzes:
    """Load the entries from the topics and generate the quizzes."""
    quizzes = []
    topics: list[pathlib.Path] = []
    if topics_to_load or topic_files_to_load:
        topics.extend(topic for topic in TOPIC_JSON_FILES if topic.stem in topics_to_load)
        topics.extend(pathlib.Path(topic) for topic in topic_files_to_load)
    else:
        topics.extend(TOPIC_JSON_FILES)
    for topic in topics:
        try:
            for concept_dict in load_json(topic):
                concept = concept_factory(concept_dict)
                quizzes.extend(concept.quizzes(language, source_language))
        except Exception as reason:  # pylint: disable=broad-except
            show_error_and_exit(f"{NAME} cannot read topic {topic}: {reason}.\n")
    return quizzes


def load_progress() -> Progress:
    """Load the progress from the user's home folder."""
    try:
        progress_dict = load_json(PROGRESS_JSON, default={})
        return Progress(progress_dict)
    except Exception as reason:  # pylint: disable=broad-except
        show_error_and_exit(
            f"""{NAME} cannot parse the progress information in {PROGRESS_JSON}: {reason}.
To fix this, remove or rename {PROGRESS_JSON} and start {NAME} again. Unfortunately, this will reset your progress.
Please consider opening a bug report at https://github.com/fniessink/{NAME.lower()}. Be sure to attach the invalid
progress file to the issue.
""")


def save_progress(progress: Progress) -> None:
    """Save the progress to the user's home folder."""
    dump_json(PROGRESS_JSON, progress.as_dict())
