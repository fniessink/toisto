"""Main module for the application."""

import logging
from contextlib import suppress
from pathlib import Path

with suppress(ImportError):
    import readline  # noqa: F401 `readline` imported but unused

# Suppress warning messages printed by the playsound module.
logging.getLogger().setLevel(logging.ERROR)

from .command.practice import practice
from .command.show_progress import show_progress
from .command.show_topics import show_topics
from .metadata import CONCEPT_JSON_FILES, TOPIC_FILES, latest_version
from .model.filter import filter_concepts
from .model.quiz.quiz_factory import create_quizzes
from .persistence.concepts import ConceptIdRegistry, load_concepts
from .persistence.config import default_config, read_config
from .persistence.progress import load_progress
from .persistence.topics import load_topics
from .ui.cli import create_argument_parser, parse_arguments
from .ui.text import show_welcome


def main() -> None:
    """Run the main program."""
    argument_parser = create_argument_parser(default_config())
    config = read_config(argument_parser)
    registry = ConceptIdRegistry(argument_parser)
    concepts = load_concepts(CONCEPT_JSON_FILES, registry, argument_parser)
    topics = load_topics(TOPIC_FILES, argument_parser)
    argument_parser = create_argument_parser(config, concepts, topics)
    args = parse_arguments(argument_parser)
    extra_concept_files = [Path(concept_file) for concept_file in args.concept_file]
    concepts |= load_concepts(extra_concept_files, registry, argument_parser)
    extra_topic_files = [Path(topic_file) for topic_file in args.topic_file]
    topics |= load_topics(extra_topic_files, argument_parser)
    concepts = filter_concepts(concepts, topics, args.concept, args.topic, argument_parser)
    quizzes = create_quizzes(args.target_language, args.source_language, *concepts)
    progress = load_progress(args.target_language, argument_parser)
    match args.command:
        case "topics":
            show_topics(args.target_language, args.source_language, topics, concepts)
        case "progress":
            show_progress(args.target_language, quizzes, progress, args.sort)
        case _:  # Default command is "practice"
            show_welcome(latest_version())
            practice(quizzes, progress, config)
