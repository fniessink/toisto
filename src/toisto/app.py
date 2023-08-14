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
from .metadata import TOPIC_JSON_FILES, TOPICS, latest_version
from .model.language.concept import Topic, filter_concepts
from .model.quiz.quiz_factory import create_quizzes
from .persistence.concepts import ConceptIdRegistry, load_concepts
from .persistence.config import default_config, read_config
from .persistence.progress import load_progress
from .ui.cli import create_argument_parser
from .ui.text import show_welcome


def main() -> None:
    """Run the main program."""
    argument_parser = create_argument_parser(default_config())
    config = read_config(argument_parser)
    registry = ConceptIdRegistry(argument_parser)
    concepts = load_concepts(TOPIC_JSON_FILES, registry, argument_parser)
    argument_parser = create_argument_parser(config, concepts)
    args = argument_parser.parse_args()
    extra_topic_files = [Path(topic_file) for topic_file in args.topic_file]
    concepts |= load_concepts(extra_topic_files, registry, argument_parser)
    selected_topics = (args.topic or TOPICS) + [Topic(filepath.stem) for filepath in extra_topic_files]
    concepts = filter_concepts(concepts, args.concept, args.levels, selected_topics)
    quizzes = create_quizzes(args.target_language, args.source_language, *concepts)
    progress = load_progress(args.target_language, argument_parser)
    match args.command:
        case "topics":
            show_topics(args.target_language, args.source_language, concepts)
        case "progress":
            show_progress(args.target_language, quizzes, progress, args.sort)
        case _:  # Default command is "practice"
            show_welcome(latest_version())
            practice(quizzes, progress, config)
