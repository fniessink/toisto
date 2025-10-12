"""Command-line interface."""

import sys
from argparse import ArgumentError, ArgumentParser, ArgumentTypeError, Namespace
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, get_args

from rich_argparse import RichHelpFormatter

from toisto.command.show_progress import SortColumn
from toisto.metadata import BUILT_IN_LANGUAGES, README_URL, SUMMARY, latest_version
from toisto.model.language import Language
from toisto.model.language.concept import Concept
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES, IANA_LANGUAGE_SUBTAG_REGISTRY_URL
from toisto.model.quiz.quiz_type import QUIZ_TYPES
from toisto.persistence.folder import home
from toisto.tools import first
from toisto.ui.text import version_message

if TYPE_CHECKING:
    from argparse import _SubParsersAction


def check_language(language: str) -> str:
    """Check that the language is valid."""
    if language in ALL_LANGUAGES:
        return language
    message = f"invalid choice: '{language}' (see {IANA_LANGUAGE_SUBTAG_REGISTRY_URL} for valid choices)"
    raise ArgumentTypeError(message)


def check_path_exists(path_name: str) -> Path:
    """Check that the path exists."""
    path = Path(path_name)
    if not path.exists():
        message = f"path '{path}' does not exist"
        raise ArgumentTypeError(message)
    return path


def check_folder(path_name: str) -> Path:
    """Check that the path is a folder and exists."""
    path = check_path_exists(path_name)
    if not path.is_dir():
        message = f"path '{path}' is not a folder"
        raise ArgumentTypeError(message)
    return path


def check_folder_or_file(path_name: str) -> Path:
    """Check that the path is a file or folder and exists."""
    path = check_path_exists(path_name)
    if not path.is_file() and not path.is_dir():
        message = f"path '{path}' is not a file or folder"
        raise ArgumentTypeError(message)
    return path.resolve()


@dataclass(frozen=True)
class OptionChecker:
    """Class to check whether the given option is present in the list of options."""

    options: tuple[str, ...]

    def __call__(self, option: str) -> str:
        """Check whether the given option is present in the list of options."""
        if option not in self.options:
            message = f"invalid choice '{option}' (run `toisto practice -h` to see the valid choices)"
            raise ArgumentTypeError(message)
        return option


class CommandBuilder:
    """Command builder."""

    LANGUAGE_ARGUMENT_REQUIRED = True

    def __init__(self, subparsers: "_SubParsersAction[ArgumentParser]", config: ConfigParser | None = None) -> None:
        self.subparsers = subparsers
        self.config = ConfigParser() if config is None else config

    def _add_command(self, command: str, description: str, command_help: str) -> ArgumentParser:
        """Add a command."""
        return self.subparsers.add_parser(
            command, description=description, help=command_help, formatter_class=RichHelpFormatter
        )

    def add_language_arguments(self, parser: ArgumentParser, required: bool | None = None) -> None:  # noqa: FBT001
        """Add the language arguments to the parser."""
        required = self.LANGUAGE_ARGUMENT_REQUIRED if required is None else required
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
                required=not default if required else False,
                type=check_language,
            )

    def add_concept_argument(self, parser: ArgumentParser, concepts: set[Concept]) -> None:
        """Add the concept argument."""
        concepts = {
            concept
            for concept in concepts
            if not concept.is_complete_sentence
            and not concept.get_related_concepts("hypernym")
            and not concept.answer_only
        }
        language = self.get_target_language()
        all_labels = sorted({str(first(labels)) for concept in concepts if (labels := concept.meanings(language))})
        parser.add_argument(
            "concepts",
            metavar="{concept}",
            nargs="*",
            help=f"concept to use, can be repeated; default: all; built-in concepts: {', '.join(all_labels)}",
            type=OptionChecker(tuple(all_labels)),
        )

    def get_target_language(self) -> Language:
        """Return the target language as specified on the command-line or in the config file. Fallback to English."""
        language_parser = ArgumentParser(add_help=False, exit_on_error=False)
        self.add_language_arguments(language_parser, required=False)
        try:
            namespace = language_parser.parse_known_args()[0]
        except ArgumentError:
            namespace = Namespace()  # Don't fail on invalid languages here, but let the main parser handle that
        if "target_language" in namespace and namespace.target_language is not None:
            language_str = namespace.target_language
        else:
            language_str = self.config.get("languages", "target", fallback="en")
        return Language(language_str)

    def add_extra_concepts_arguments(self, parser: ArgumentParser) -> None:
        """Add the extra concepts argument."""
        default = [Path(path) for path in self.config["files"]] if self.config.has_section("files") else []
        default_help = ", ".join(str(path) for path in default) if default else "none"
        parser.add_argument(
            "-e",
            "--extra",
            action="append",
            default=default,
            metavar="{path}",
            help=f"file or folder with extra concepts to read, can be repeated; default: {default_help}",
            type=check_folder_or_file,
        )

    def add_progress_folder_argument(self, parser: ArgumentParser) -> None:
        """Add the progress folder argument to the command."""
        default = Path(self.config.get("progress", "folder"))
        parser.add_argument(
            "-p",
            "--progress-folder",
            metavar="{path}",
            type=check_folder,
            default=default,
            help=f"folder where to save progress; default: {default}",
        )

    def add_progress_update_argument(self, parser: ArgumentParser) -> None:
        """Add the progress update argument to the command."""
        default = self.config.get("practice", "progress_update")
        parser.add_argument(
            "-u",
            "--progress-update",
            metavar="{frequency}",
            type=int,
            default=default,
            help=f"show a progress update after each {{frequency}} quizzes; default: {default} (0 means never)",
        )

    def add_show_quiz_retention_argument(self, parser: ArgumentParser) -> None:
        """Add the show quiz retention argument to the command."""
        default = self.config.get("practice", "show_quiz_retention")
        parser.add_argument(
            "-r",
            "--show-quiz-retention",
            choices=["yes", "no"],
            default=default,
            help=f"show the quiz retention after each quiz; default: {default}",
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

    def add_quiz_type_argument(self, parser: ArgumentParser) -> None:
        """Add the quiz type argument to the command."""
        quiz_types = sorted([quiz_type.action for quiz_type in QUIZ_TYPES])
        parser.add_argument(
            "-q",
            "--quiz-type",
            action="append",
            default=[],
            metavar="{quiz type}",
            help=f"quiz types to use, can be repeated; default: all; available quiz types: {', '.join(quiz_types)}",
            type=OptionChecker(tuple(quiz_types)),
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
        self.add_extra_concepts_arguments(parser)
        self.add_progress_folder_argument(parser)
        self.add_progress_update_argument(parser)
        self.add_show_quiz_retention_argument(parser)
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
        self.add_extra_concepts_arguments(parser)
        self.add_quiz_type_argument(parser)
        self.add_progress_update_argument(parser)
        self.add_show_quiz_retention_argument(parser)


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
        self.add_extra_concepts_arguments(parser)
        self.add_quiz_type_argument(parser)
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


class SelfUpgradeCommandBuilder(CommandBuilder):
    """Self-upgrade command builder."""

    LANGUAGE_ARGUMENT_REQUIRED = False

    def add_command(self) -> None:
        """Add a command to upgrade Toisto."""
        self._add_command("upgrade", "Upgrade Toisto.", "upgrade Toisto to the latest version")


class SelfUninstallCommandBuilder(CommandBuilder):
    """Self-uninstall command builder."""

    LANGUAGE_ARGUMENT_REQUIRED = False

    def add_command(self) -> None:
        """Add a command to uninstall Toisto."""
        self._add_command(
            "uninstall",
            "Uninstall Toisto.",
            "uninstall Toisto, excluding configuration and progress files",
        )


class SelfVersionCommandBuilder(CommandBuilder):
    """Self-version command builder."""

    LANGUAGE_ARGUMENT_REQUIRED = False

    def add_command(self) -> None:
        """Add a command to show the current version."""
        self._add_command(
            "version",
            "Show the current version.",
            "show the installed version and the latest version available if it is newer",
        )


class SelfCommandsBuilder(CommandBuilder):
    """Self commands builder."""

    LANGUAGE_ARGUMENT_REQUIRED = False

    def add_commands(self) -> None:
        """Add a self command group."""
        command_help = (
            "manage Toisto itself, for example `%(prog)s self upgrade` to upgrade Toisto to the latest version"
        )
        parser = self._add_command("self", "Manage Toisto itself.", command_help)
        subparsers = parser.add_subparsers(
            dest="self",
            title="commands",
            required=True,
            help="type `toisto self {command} --help` for more information on a command",
        )
        SelfUpgradeCommandBuilder(subparsers).add_command()
        SelfUninstallCommandBuilder(subparsers).add_command()
        SelfVersionCommandBuilder(subparsers).add_command()


def create_argument_parser(config: ConfigParser, concepts: set[Concept] | None = None) -> ArgumentParser:
    """Create the argument parser."""
    epilog = f"See {README_URL} for more information."
    argument_parser = ArgumentParser(description=SUMMARY, epilog=epilog, formatter_class=RichHelpFormatter)
    argument_parser.add_argument("-V", "--version", action="version", version=version_message(latest_version()))
    command_help = "default: practice; type `%(prog)s {command} --help` for more information on a command"
    subparsers = argument_parser.add_subparsers(dest="command", title="commands", help=command_help)
    ConfigureCommandBuilder(subparsers, config).add_command()
    PracticeCommandBuilder(subparsers, config).add_command(concepts or set())
    ProgressCommandBuilder(subparsers, config).add_command(concepts or set())
    SelfCommandsBuilder(subparsers, config).add_commands()
    if not {"configure", "practice", "progress", "self", "-h", "--help", "-V", "--version"} & set(sys.argv):
        sys.argv.insert(1, "practice")  # Insert practice as default subcommand
    if sys.argv[1:] == ["self"]:
        sys.argv.append("--help")
    return argument_parser


def parse_arguments(argument_parser: ArgumentParser) -> Namespace:
    """Parse and validate the command-line arguments."""
    namespace = argument_parser.parse_args()
    if namespace.command not in ("configure", "self") and namespace.target_language == namespace.source_language:
        message = f"target and source language are the same: '{namespace.target_language}' "
        argument_parser.error(message)
    return namespace
