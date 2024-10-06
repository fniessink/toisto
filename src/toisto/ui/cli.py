"""Command-line interface."""

import sys
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING, get_args

from rich_argparse import RichHelpFormatter

from toisto.command.show_progress import SortColumn
from toisto.metadata import BUILT_IN_LANGUAGES, README_URL, SUMMARY, VERSION, latest_version
from toisto.model.language.concept import Concept
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES, IANA_LANGUAGE_SUBTAG_REGISTRY_URL
from toisto.persistence.folder import home

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def check_language(language: str) -> str:
    """Check that the language is valid."""
    if language in ALL_LANGUAGES:
        return language
    message = f"invalid choice: '{language}' (see {IANA_LANGUAGE_SUBTAG_REGISTRY_URL} for valid choices)"
    raise ArgumentTypeError(message)


def check_folder(folder: str) -> str:
    """Check that the folder exists."""
    if Path(folder).is_dir():
        return folder
    message = f"folder '{folder}' does not exist or is not a folder"
    raise ArgumentTypeError(message)


class CommandBuilder:
    """Command builder."""

    LANGUAGE_ARGUMENT_REQUIRED = True

    def __init__(self, subparsers: "_SubParsersAction[ArgumentParser]", config: ConfigParser) -> None:
        self.subparsers = subparsers
        self.config = config

    def _add_command(self, command: str, description: str, command_help: str) -> ArgumentParser:
        """Add a command."""
        return self.subparsers.add_parser(
            command, description=description, help=command_help, formatter_class=RichHelpFormatter
        )

    def add_language_arguments(self, parser: ArgumentParser) -> None:
        """Add the language arguments to the parser."""
        languages = ", ".join(sorted(BUILT_IN_LANGUAGES))
        for argument in ("target", "source"):
            default = self.config.get("languages", argument, fallback=None)
            default_help = f"default: {default}; " if default else ""
            parser.add_argument(
                f"-{argument[0]}",
                f"--{argument}",
                default=default,
                dest=f"{argument}_language",
                help=f"{argument} language; {default_help}languages available in built-in concepts: {languages}",
                metavar="{language}",
                required=not default if self.LANGUAGE_ARGUMENT_REQUIRED else False,
                type=check_language,
            )

    def add_concept_argument(self, parser: ArgumentParser, concepts: set[Concept]) -> None:
        """Add the concept argument."""
        concept_ids = sorted(
            concept.concept_id
            for concept in concepts
            if not concept.is_complete_sentence and not concept.get_related_concepts("hypernym")
        )
        parser.add_argument(
            "concepts",
            metavar="{concept}",
            nargs="*",
            help=f"concept to use, can be repeated; default: all; built-in concepts: {', '.join(concept_ids)}",
        )

    def add_file_arguments(self, parser: ArgumentParser) -> None:
        """Add the file arguments."""
        parser.add_argument(
            "-f",
            "--file",
            action="append",
            default=[],
            metavar="{file}",
            help="file with extra concepts to read, can be repeated",
            type=Path,
        )

    def add_progress_folder_argument(self, parser: ArgumentParser) -> None:
        """Add the progress folder argument to the command."""
        default = self.config.get("progress", "folder")
        parser.add_argument(
            "--progress-folder",
            metavar="{folder}",
            type=check_folder,
            default=default,
            help=f"folder where to save progress; default: {default}",
        )

    def add_progress_update_argument(self, parser: ArgumentParser) -> None:
        """Add the progress update argument to the command."""
        default = self.config.get("practice", "progress_update")
        parser.add_argument(
            "-p",
            "--progress-update",
            metavar="{frequency}",
            type=int,
            default=default,
            help=f"show a progress update after each {{frequency}} quizzes; default: {default} (0 means never)",
        )

    def add_mp3player_argument(self, parser: ArgumentParser) -> None:
        """Add the mp3 player argument to the command."""
        default = self.config.get("commands", "mp3player")
        parser.add_argument(
            "-m",
            "--mp3player",
            metavar="{mp3player}",
            default=default,
            help=f"mp3 player to play sounds; default: {default}",
        )


class ConfigureCommandBuilder(CommandBuilder):
    """Configure command builder."""

    LANGUAGE_ARGUMENT_REQUIRED = False

    def add_command(self) -> None:
        """Add a configure command."""
        command_help = (
            "configure options, for example `%(prog)s configure --target fi --source en` to make "
            "practicing Finnish from English the default"
        )
        parser = self._add_command(
            "configure",
            f"Configure options and save them in {home()!s}/.toisto.cfg.",
            command_help,
        )
        self.add_language_arguments(parser)
        self.add_file_arguments(parser)
        self.add_progress_folder_argument(parser)
        self.add_progress_update_argument(parser)
        self.add_mp3player_argument(parser)


class PracticeCommandBuilder(CommandBuilder):
    """Practice command builder."""

    def add_command(self, concepts: set[Concept]) -> None:
        """Add a practice command."""
        command_help = (
            "practice a language, for example `%(prog)s practice --target fi --source en` to "
            "practice Finnish from English"
        )
        parser = self._add_command("practice", "Practice a language.", command_help)
        self.add_language_arguments(parser)
        self.add_concept_argument(parser, concepts)
        self.add_file_arguments(parser)
        self.add_progress_update_argument(parser)


class ProgressCommandBuilder(CommandBuilder):
    """Progress command builder."""

    def add_command(self, concepts: set[Concept]) -> None:
        """Add a command to show progress."""
        command_help = (
            "show progress, for example `%(prog)s progress --target fi --source en` to show progress "
            "on practicing Finnish from English"
        )
        parser = self._add_command("progress", "Show progress.", command_help)
        self.add_language_arguments(parser)
        self.add_concept_argument(parser, concepts)
        self.add_file_arguments(parser)
        self.add_sort_argument(parser)

    def add_sort_argument(self, parser: ArgumentParser) -> None:
        """Add the sort argument to the command."""
        parser.add_argument(
            "-S",
            "--sort",
            metavar="{option}",
            choices=sorted(get_args(SortColumn)),
            default="retention",
            help="how to sort progress information; default: by retention; available options: %(choices)s",
        )


def create_argument_parser(config: ConfigParser, concepts: set[Concept] | None = None) -> ArgumentParser:
    """Create the argument parser."""
    epilog = f"See {README_URL} for more information."
    argument_parser = ArgumentParser(description=SUMMARY, epilog=epilog, formatter_class=RichHelpFormatter)
    latest = latest_version()
    version = f"v{VERSION}" + (f" ({latest} is available)" if latest and latest.strip("v") > VERSION else "")
    argument_parser.add_argument("-V", "--version", action="version", version=version)
    command_help = "default: practice; type `%(prog)s {command} --help` for more information on a command"
    subparsers = argument_parser.add_subparsers(dest="command", title="commands", help=command_help)
    ConfigureCommandBuilder(subparsers, config).add_command()
    PracticeCommandBuilder(subparsers, config).add_command(concepts or set())
    ProgressCommandBuilder(subparsers, config).add_command(concepts or set())
    if not {"configure", "practice", "progress", "-h", "--help", "-V", "--version"} & set(sys.argv):
        sys.argv.insert(1, "practice")  # Insert practice as default subcommand
    return argument_parser


def parse_arguments(argument_parser: ArgumentParser) -> Namespace:
    """Parse and validate the command-line arguments."""
    namespace = argument_parser.parse_args()
    if namespace.target_language == namespace.source_language and namespace.command != "configure":
        message = f"target and source language are the same: '{namespace.target_language}' "
        argument_parser.error(message)
    return namespace
