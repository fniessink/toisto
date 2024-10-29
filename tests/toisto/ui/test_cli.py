"""Unit tests for the CLI module."""

import os
import re
import unittest
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from pathlib import Path
from unittest.mock import Mock, patch

from toisto.metadata import README_URL
from toisto.model.language import Language
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.label import Label, Labels
from toisto.persistence.config import default_config
from toisto.persistence.folder import home
from toisto.ui.cli import create_argument_parser, parse_arguments

CONFIGURE_USAGE = (
    "Usage: toisto configure [-h] [-t {language}] [-s {language}] [-f {file}] [--progress-folder {folder}] "
    "[-p {frequency}]\n"
    "                        [-m {mp3player}]"
)
PRACTICE_USAGE = "Usage: toisto practice [-h] -t {language} -s {language} [-f {file}] [-p {frequency}] [{concept} ...]"
CONFIGURE_DESCRIPTION = f"Configure options and save them in {home()!s}/.toisto.cfg."
PRACTICE_USAGE_OPTIONAL_TARGET = (
    "Usage: toisto practice [-h] [-t {language}] -s {language} [-f {file}] [-p {frequency}] [{concept} ...]"
)
PRACTICE_DESCRIPTION = "Practice a language."
POSITIONAL_ARGUMENTS = """Positional Arguments:
  {concept}             concept to use, can be repeated; default: all; built-in concepts:%s"""
HELP_OPTION = "-h, --help            show this help message and exit"
TARGET_OPTION = """-t, --target {language}
                        target language; %slanguages available in built-in concepts: en, fi, nl"""
SOURCE_OPTION = """-s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl"""
FILE_OPTION = "-f, --file {file}     file with extra concepts to read, can be repeated; default: none"
PROGRESS_FOLDER = f"""--progress-folder {{folder}}
                        folder where to save progress; default: {home()!s}"""
PROGRESS_OPTION = """-p, --progress-update {frequency}
                        show a progress update after each {frequency} quizzes; default: %s (0 means never)"""
MP3PLAYER_OPTION = """-m, --mp3player {mp3player}
                        mp3 player to play sounds; default: afplay"""


class ParserTest(unittest.TestCase):
    """Unit tests for the CLI parser."""

    ANSI_ESCAPE_CODES = re.compile(r"\x1B\[\d+(;\d+){0,2}m")

    def setUp(self) -> None:
        """Set up the test fixtures."""
        os.environ["COLUMNS"] = "120"  # Set the width of the terminal to match the formatting of the expected results

    def argument_parser(
        self,
        config_parser: ConfigParser | None = None,
        concepts: set[Concept] | None = None,
    ) -> ArgumentParser:
        """Create the argument parser."""
        with patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name="v9999")])))):
            return create_argument_parser(config_parser or default_config(), concepts)

    @patch("sys.argv", ["toisto", "--help"])
    @patch("sys.stdout.write")
    def test_help(self, sys_stdout_write: Mock) -> None:
        """Test that the help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            f"""Usage: toisto [-h] [-V] {{configure,practice,progress}} ...

Toisto is a command-line terminal app to practice languages.

Options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit

Commands:
  {{configure,practice,progress}}
                        default: practice; type `toisto {{command}} --help` for more information on a command
    configure           configure options, for example `toisto configure --target fi --source en` to make practicing
                        Finnish from English the default
    practice            practice a language, for example `toisto practice --target fi --source en` to practice Finnish
                        from English
    progress            show progress, for example `toisto progress --target fi --source en` to show progress on
                        practicing Finnish from English

See {README_URL} for more information.
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--target", "nl", "--source", "fi"])
    def test_configure_command(self) -> None:
        """Test that the configure command can be specified."""
        expected_namespace = Namespace(
            command="configure",
            file=[],
            mp3player="afplay",
            progress_folder=str(home()),
            progress_update=0,
            source_language="fi",
            target_language="nl",
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--progress-folder", "/home/user/toisto"])
    @patch("toisto.ui.cli.Path.is_dir", Mock(return_value=True))
    def test_configure_progress_folder(self) -> None:
        """Test that the progress folder can be configured."""
        expected_namespace = Namespace(
            command="configure",
            file=[],
            mp3player="afplay",
            progress_folder="/home/user/toisto",
            progress_update=0,
            source_language=None,
            target_language=None,
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--progress-folder", "/home/user/toisto"])
    @patch("toisto.ui.cli.Path.is_dir", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_configure_non_existing_progress_folder(self, sys_stderr_write: Mock) -> None:
        """Test that the progress folder is checked for existence."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "error: argument --progress-folder: folder '/home/user/toisto' does not exist or is not a folder",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--file", "/home/user/extra.json"])
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=True))
    def test_configure_concept_file(self) -> None:
        """Test that a concept file folder can be configured."""
        expected_namespace = Namespace(
            command="configure",
            file=[Path("/home/user/extra.json")],
            mp3player="afplay",
            progress_folder=str(home()),
            progress_update=0,
            source_language=None,
            target_language=None,
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--file", "/home/user/extra.json"])
    @patch("toisto.ui.cli.Path.is_file", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_configure_non_existing_concept_file(self, sys_stderr_write: Mock) -> None:
        """Test that the concept file is checked for existence."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "error: argument -f/--file: file '/home/user/extra.json' does not exist or is not a file",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "configure", "--help"])
    @patch("sys.stdout.write")
    def test_configure_help(self, sys_stdout_write: Mock) -> None:
        """Test that the configure help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            f"""{CONFIGURE_USAGE}

{CONFIGURE_DESCRIPTION}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION}
  {FILE_OPTION}
  {PROGRESS_FOLDER}
  {PROGRESS_OPTION % "0"}
  {MP3PLAYER_OPTION}
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--target", "nl", "--source", "fi"])
    def test_practice_command(self) -> None:
        """Test that the practice command can be specified."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            concepts=[],
            file=[],
            progress_update=0,
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help(self, sys_stdout_write: Mock) -> None:
        """Test that the practice help message is displayed."""
        foo = ConceptId("foo")
        bar = ConceptId("bar")
        english = Language("en")
        concepts = {
            Concept(foo, None, (), Labels((Label(english, "foo"),)), Labels(), {}, {}, False),
            Concept(bar, None, (), Labels((Label(english, "bar"),)), Labels(), {}, {}, False),
        }
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(concepts=concepts))
        self.assertEqual(
            f"""{PRACTICE_USAGE}

{PRACTICE_DESCRIPTION}

{POSITIONAL_ARGUMENTS % " bar, foo"}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION}
  {FILE_OPTION}
  {PROGRESS_OPTION % "0"}
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_languages_in_config(self, sys_stdout_write: Mock) -> None:
        """Test that the practice help message is displayed."""
        config_parser = default_config()
        config_parser.add_section("languages")
        config_parser.set("languages", "target", "fi")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assertEqual(
            f"""{PRACTICE_USAGE_OPTIONAL_TARGET}

{PRACTICE_DESCRIPTION}

{POSITIONAL_ARGUMENTS % ""}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % "default: fi; "}
  {SOURCE_OPTION}
  {FILE_OPTION}
  {PROGRESS_OPTION % "0"}
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_progress_update_in_config(self, sys_stdout_write: Mock) -> None:
        """Test that the practice help message is displayed."""
        config_parser = default_config()
        config_parser.set("practice", "progress_update", "42")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assertEqual(
            f"""{PRACTICE_USAGE}

{PRACTICE_DESCRIPTION}

{POSITIONAL_ARGUMENTS % ""}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION}
  {FILE_OPTION}
  {PROGRESS_OPTION % 42}
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "progress", "--help"])
    @patch("sys.stdout.write")
    def test_progress_help(self, sys_stdout_write: Mock) -> None:
        """Test that the progress help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            f"""Usage: toisto progress [-h] -t {{language}} -s {{language}} [-f {{file}}] [-S {{option}}] \
[{{concept}} ...]

Show progress.

{POSITIONAL_ARGUMENTS % ""}

Options:
  {HELP_OPTION}
  {TARGET_OPTION % ""}
  {SOURCE_OPTION}
  {FILE_OPTION}
  -S, --sort {{option}}   how to sort progress information; default: by retention; available options: attempts,
                        retention
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.platform", "darwin")
    @patch("sys.argv", ["toisto", "--target", "nl", "--source", "fi"])
    def test_no_command(self) -> None:
        """Test that the practice command is returned if the user did not specify a command."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            concepts=[],
            file=[],
            progress_update=0,
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "--version"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_long_option(self, print_message: Mock) -> None:
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "-V"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_short_option(self, print_message: Mock) -> None:
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "practice", "--target", "42", "--source", "@@"])
    @patch("sys.stderr.write")
    def test_invalid_language(self, sys_stderr_write: Mock) -> None:
        """Test that an error message is displayed if an invalid language is supplied."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "invalid choice: '42' (see https://www.iana.org/assignments/language-subtag-registry for valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "fi", "--source", "fi"])
    @patch("sys.stderr.write")
    def test_equal_target_and_source_language(self, sys_stderr_write: Mock) -> None:
        """Test that an error message is displayed if the target and source language are equal."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "toisto: error: target and source language are the same: 'fi' \n",
            sys_stderr_write.call_args_list[1][0][0],
        )
