"""Load quizzes from topic files."""

import pathlib

from ..metadata import NAME, TOPIC_JSON_FILES, Language
from ..model import concept_factory, Topic, Topics
from ..ui.text import show_error_and_exit

from .json_file import load_json


def load_quizzes(
    language: Language, source_language: Language, builtin_topics_to_load: list[str], topic_files_to_load: list[str]
) -> Topics:
    """Load the concepts from the topics and generate the quizzes."""
    topics = set()
    topic_files: list[pathlib.Path] = []
    if builtin_topics_to_load or topic_files_to_load:
        topic_files.extend(topic for topic in TOPIC_JSON_FILES if topic.stem in builtin_topics_to_load)
        topic_files.extend(pathlib.Path(topic) for topic in topic_files_to_load)
    else:
        topic_files.extend(TOPIC_JSON_FILES)
    for topic_file in topic_files:
        topic_quizzes = set()
        try:
            for concept_dict in load_json(topic_file):
                concept = concept_factory(concept_dict)
                topic_quizzes.update(concept.quizzes(language, source_language))
        except Exception as reason:  # pylint: disable=broad-except
            show_error_and_exit(f"{NAME} cannot read topic {topic_file}: {reason}.\n")
        topics.add(Topic(topic_file.stem, topic_quizzes))
    return Topics(topics)
