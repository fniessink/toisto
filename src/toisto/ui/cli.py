"""Command-line interface."""

import sys
from argparse import ArgumentParser, ArgumentTypeError
from configparser import ConfigParser
from typing import get_args

from rich_argparse import RichHelpFormatter

from ..command.show_progress import SortColumn
from ..metadata import BUILT_IN_LANGUAGES, README_URL, SUMMARY, VERSION, latest_version
from ..model.language.cefr import CommonReferenceLevel
from ..model.language.concept import Concept, Topic, topics
from ..model.language.iana_language_subtag_registry import ALL_LANGUAGES, IANA_LANGUAGE_SUBTAG_REGISTRY_URL


def add_language_arguments(parser: ArgumentParser, config: ConfigParser) -> None:
    """Add the language arguments to the parser."""
    languages = ", ".join(sorted(BUILT_IN_LANGUAGES))
    for argument in ("target", "source"):
        default = config.get("languages", argument, fallback=None)
        default_help = f"default: {default}; " if default else ""
        parser.add_argument(
            f"-{argument[0]}",
            f"--{argument}",
            default=default,
            dest=f"{argument}_language",
            help=f"{argument} language; {default_help}languages available in built-in topics: {languages}",
            metavar="{language}",
            required=not default,
            type=check_language,
        )


def check_language(language: str) -> str:
    """Check that the language is valid."""
    if language in ALL_LANGUAGES:
        return language
    message = f"invalid choice: '{language}' (see {IANA_LANGUAGE_SUBTAG_REGISTRY_URL} for valid choices)"
    raise ArgumentTypeError(message)


def add_topic_arguments(parser: ArgumentParser, topics: list[Topic]) -> None:
    """Add the topic arguments to the parser."""
    parser.add_argument(
        "-T",
        "--topic",
        action="append",
        default=[],
        metavar="{topic}",
        help=f"topic to use, can be repeated; default: all; built-in topics: {', '.join(topics)}",
    )
    parser.add_argument(
        "-f",
        "--topic-file",
        action="append",
        default=[],
        metavar="{topic file}",
        help="topic file to use, can be repeated",
    )


def add_concept_arguments(parser: ArgumentParser, concepts: set[Concept]) -> None:
    """Add the concept arguments to the parser."""
    concept_ids = sorted(concept.concept_id for concept in concepts)
    parser.add_argument(
        "-c",
        "--concept",
        action="append",
        default=[],
        metavar="{concept}",
        help=f"concept to use, can be repeated; default: all; built-in concepts: {', '.join(concept_ids)}",
    )


def add_level_arguments(parser: ArgumentParser, config: ConfigParser) -> None:
    """Add the language level arguments to the parser."""
    levels = get_args(CommonReferenceLevel)
    default = [level for level in levels if level in config.get("languages", "levels", fallback="")]
    default_help = ", ".join(default) if default else "all"
    parser.add_argument(
        "-l",
        "--level",
        action="append",
        default=default,
        dest="levels",
        metavar="{level}",
        choices=levels,
        help=f"language levels to use, can be repeated; default: {default_help}; available levels: %(choices)s",
    )


class CommandBuilder:
    """Add commands to the argument parser."""

    def __init__(self, argument_parser: ArgumentParser, concepts: set[Concept], config: ConfigParser) -> None:
        command_help = "default: practice; type `%(prog)s {command} --help` for more information on a command"
        self.subparsers = argument_parser.add_subparsers(dest="command", title="commands", help=command_help)
        self.concepts = concepts
        self.config = config

    def add_command(self, command: str, description: str, command_help: str) -> ArgumentParser:
        """Add a command."""
        parser = self.subparsers.add_parser(
            command,
            description=description,
            help=command_help,
            formatter_class=RichHelpFormatter,
        )
        add_language_arguments(parser, self.config)
        add_level_arguments(parser, self.config)
        add_topic_arguments(parser, topics(self.concepts))
        add_concept_arguments(parser, self.concepts)
        return parser

    def add_practice_command(self) -> None:
        """Add a practice command."""
        command_help = (
            "practice a language, for example type `%(prog)s practice --target fi --source en` to "
            "practice Finnish from English"
        )
        self.add_command("practice", "Practice a language.", command_help)

    def add_progress_command(self) -> None:
        """Add a command to show progress."""
        command_help = (
            "show progress, for example `%(prog)s progress --target fi --source en` shows progress "
            "on practicing Finnish from English"
        )
        parser = self.add_command("progress", "Show progress.", command_help)
        parser.add_argument(
            "-S",
            "--sort",
            metavar="{option}",
            choices=sorted(get_args(SortColumn)),
            default="retention",
            help="how to sort progress information; default: by retention; available options: %(choices)s",
        )

    def add_topics_command(self) -> None:
        """Add a command to show topics."""
        command_help = (
            "show topics, for example `%(prog)s topics --topic nature` shows the contents of the nature topic"
        )
        self.add_command("topics", "Show topics.", command_help)


def create_argument_parser(config: ConfigParser, concepts: set[Concept] | None = None) -> ArgumentParser:
    """Create the argument parser."""
    epilog = f"See {README_URL} for more information."
    argument_parser = ArgumentParser(description=SUMMARY, epilog=epilog, formatter_class=RichHelpFormatter)
    latest = latest_version()
    version = f"v{VERSION}" + (f" ({latest} is available)" if latest and latest.strip("v") > VERSION else "")
    argument_parser.add_argument("-V", "--version", action="version", version=version)
    builder = CommandBuilder(argument_parser, concepts or set(), config)
    builder.add_practice_command()
    builder.add_progress_command()
    builder.add_topics_command()
    if not {"practice", "progress", "topics", "-h", "--help", "-V", "--version"} & set(sys.argv):
        sys.argv.insert(1, "practice")  # Insert practice as default subcommand
    return argument_parser
