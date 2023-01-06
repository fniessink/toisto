"""Load concepts from topic files and generate quizzes."""

import pathlib

from ..metadata import NAME, TOPIC_JSON_FILES, Language
from ..model import ConceptFactory, QuizFactory, Topic, Topics
from ..ui.text import show_error_and_exit

from .json_file import load_json


def load_topics(
    language: Language,
    source_language: Language,
    builtin_topics_to_load: list[str],
    topic_files_to_load: list[str],
) -> Topics:
    """Load the topics with the concepts and generate the quizzes."""
    topics = set()
    topic_files: list[pathlib.Path] = []
    if builtin_topics_to_load or topic_files_to_load:
        topic_files.extend(topic for topic in TOPIC_JSON_FILES if topic.stem in builtin_topics_to_load)
        topic_files.extend(pathlib.Path(topic) for topic in topic_files_to_load)
    else:
        topic_files.extend(TOPIC_JSON_FILES)
    quiz_factory = QuizFactory(language, source_language)
    for topic_file in topic_files:
        concepts = []
        topic_quizzes = set()
        try:
            topic_json = load_json(topic_file)
            for concept_key, concept_value in topic_json.items():
                concept = ConceptFactory(concept_key, concept_value).create_concept()
                concepts.append(concept)
                topic_quizzes.update(quiz_factory.create_quizzes(concept))
        except Exception as reason:  # pylint: disable=broad-except
            show_error_and_exit(f"{NAME} cannot read topic {topic_file}: {reason}.\n")
        topics.add(Topic(topic_file.stem, tuple(concepts), topic_quizzes))
    return Topics(topics)
