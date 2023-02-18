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
from .persistence.config import default_config, read_config
from .persistence.progress import load_progress
from .persistence.topics import load_topics
from .ui.cli import create_argument_parser
from .ui.text import show_welcome


def main() -> None:
    """Run the main program."""
    config = read_config(create_argument_parser(default_config()))
    argument_parser = create_argument_parser(config)
    args = argument_parser.parse_args()
    topics = load_topics(
        args.target_language,
        args.source_language,
        args.levels,
        args.topic,
        args.topic_file,
        argument_parser,
    )
    progress = load_progress(topics, argument_parser)
    if args.command == "practice":
        show_welcome(latest_version())
        practice(progress, config)
    elif args.command == "topics":
        show_topics(args.target_language, args.source_language, topics)
    else:
        show_progress(args.target_language, topics, progress, args.sort)
