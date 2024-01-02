"""Main module for the application."""

import logging
from argparse import Namespace
from configparser import ConfigParser
from contextlib import suppress
from pathlib import Path

with suppress(ImportError):
    import readline  # noqa: F401 `readline` imported but unused

# Suppress warning messages printed by the playsound module.
logging.getLogger().setLevel(logging.ERROR)

from .command.practice import practice
from .command.show_progress import show_progress
from .command.show_topics import show_topics
from .metadata import latest_version
from .model.filter import filter_concepts
from .model.language.concept import Concept
from .model.quiz.progress import Progress
from .model.quiz.quiz import Quizzes
from .model.quiz.quiz_factory import create_quizzes
from .model.topic.topic import Topic
from .persistence.config import default_config, read_config
from .persistence.loader import Loader
from .persistence.progress import load_progress
from .persistence.spelling_alternatives import load_spelling_alternatives
from .ui.cli import create_argument_parser, parse_arguments
from .ui.text import console, show_welcome


def init() -> tuple[ConfigParser, Namespace, set[Concept], set[Topic], Quizzes, Progress]:
    """Initialize the main program."""
    argument_parser = create_argument_parser(default_config())
    config = read_config(argument_parser)
    loader = Loader(argument_parser)
    concepts, topics = loader.load()
    argument_parser = create_argument_parser(config, concepts, topics)
    args = parse_arguments(argument_parser)
    load_spelling_alternatives(args.target_language, args.source_language)
    extra_files = [Path(file_path) for file_path in args.file]
    extra_concepts, extra_topics = loader.load(extra_files)
    concepts |= extra_concepts
    topics |= extra_topics
    concepts = filter_concepts(concepts, topics, args.concept, args.topic, argument_parser)
    quizzes = create_quizzes(args.target_language, args.source_language, *concepts)
    progress = load_progress(args.target_language, argument_parser)
    return config, args, concepts, topics, quizzes, progress


def main() -> None:
    """Run the main program."""
    config, args, concepts, topics, quizzes, progress = init()
    match args.command:
        case "topics":
            show_topics(args.target_language, args.source_language, topics, concepts)
        case "progress":
            show_progress(args.target_language, quizzes, progress, args.sort)
        case _:  # Default command is "practice"
            show_welcome(console.print, latest_version())
            practice(console.print, quizzes, progress, config)
