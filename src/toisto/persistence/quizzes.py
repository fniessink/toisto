"""Load quizzes from topic files."""

import pathlib

from ..metadata import NAME, TOPIC_JSON_FILES, Language
from ..model import concept_factory, Quizzes
from ..ui.text import show_error_and_exit

from .json_file import load_json


def load_quizzes(
    language: Language, source_language: Language, topics_to_load: list[str], topic_files_to_load: list[str]
) -> Quizzes:
    """Load the entries from the topics and generate the quizzes."""
    quizzes = set()
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
                quizzes.update(concept.quizzes(language, source_language))
        except Exception as reason:  # pylint: disable=broad-except
            show_error_and_exit(f"{NAME} cannot read topic {topic}: {reason}.\n")
    return quizzes
