"""Main module for the application."""

import logging
from contextlib import suppress

with suppress(ImportError):
    import readline  # noqa: F401 `readline` imported but unused

# Suppress warning messages printed by the playsound module.
logging.getLogger().setLevel(logging.ERROR)

from .command.practice import practice
from .command.show_progress import show_progress
from .command.show_topics import show_topics
from .metadata import latest_version
from .model.quiz.quiz_factory import create_quizzes
from .persistence.concepts import load_concepts
from .persistence.config import default_config, read_config
from .persistence.progress import load_progress
from .ui.cli import create_argument_parser
from .ui.text import show_welcome


def main() -> None:
    """Run the main program."""
    config = read_config(create_argument_parser(default_config()))
    argument_parser = create_argument_parser(config)
    args = argument_parser.parse_args()
    concepts = load_concepts(args.levels, args.topic, args.topic_file, argument_parser)
    quizzes = create_quizzes(args.target_language, args.source_language, *concepts)
    progress = load_progress(args.target_language, argument_parser)
    if args.command == "practice":
        show_welcome(latest_version())
        practice(quizzes, progress, config)
    elif args.command == "topics":
        show_topics(args.target_language, args.source_language, concepts)
    else:
        show_progress(args.target_language, quizzes, progress, args.sort)
