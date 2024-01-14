"""Unit tests for the CLI module."""

import os
import re
import unittest
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from unittest.mock import Mock, patch

from toisto.model.language import Language
from toisto.model.language.concept import Concept, ConceptId, RelatedConcepts
from toisto.model.language.label import Label
from toisto.ui.cli import create_argument_parser, parse_arguments


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
            return create_argument_parser(config_parser or ConfigParser(), concepts)

    @patch("sys.argv", ["toisto", "--help"])
    @patch("sys.stdout.write")
    def test_help(self, sys_stdout_write: Mock):
        """Test that the help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.maxDiff = None
        self.assertEqual(
            """Usage: toisto [-h] [-V] {practice,progress} ...

Toisto is a command-line terminal app to practice languages.

Options:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit

Commands:
  {practice,progress}  default: practice; type `toisto {command} --help` for more information on a command
    practice           practice a language, for example type `toisto practice --target fi --source en` to practice
                       Finnish from English
    progress           show progress, for example `toisto progress --target fi --source en` shows progress on
                       practicing Finnish from English

See https://github.com/fniessink/toisto/blob/main/README.md for more information.
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "nl", "--source", "fi"])
    def test_practice_command(self):
        """Test that the practice command can be specified."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            concept=[],
            file=[],
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help(self, sys_stdout_write: Mock):
        """Test that the practice help message is displayed."""
        foo = ConceptId("foo")
        bar = ConceptId("bar")
        related_foo = RelatedConcepts(foo, None, (), {}, (), (), (), (), ())
        related_bar = RelatedConcepts(bar, None, (), {}, (), (), (), (), ())
        english = Language("en")
        concepts = {
            Concept(foo, {english: (Label(english, "foo"),)}, {}, related_foo, False),
            Concept(bar, {english: (Label(english, "bar"),)}, {}, related_bar, False),
        }
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(concepts=concepts))
        self.assertEqual(
            """Usage: toisto practice [-h] -t {language} -s {language} [-c {concept}] [-f {file}]

Practice a language.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts: bar, foo
  -f, --file {file}     file with extra concepts to read, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_default_languages_in_config(self, sys_stdout_write: Mock):
        """Test that the practice help message is displayed."""
        config_parser = ConfigParser()
        config_parser.add_section("languages")
        config_parser.set("languages", "target", "fi")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assertEqual(
            """Usage: toisto practice [-h] [-t {language}] -s {language} [-c {concept}] [-f {file}]

Practice a language.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; default: fi; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -f, --file {file}     file with extra concepts to read, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "practice", "--help"])
    @patch("sys.stdout.write")
    def test_practice_help_with_default_levels_in_config(self, sys_stdout_write: Mock):
        """Test that the practice help message is displayed."""
        config_parser = ConfigParser()
        config_parser.add_section("languages")
        config_parser.set("languages", "levels", "A1 A2")
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser(config_parser))
        self.assertEqual(
            """Usage: toisto practice [-h] -t {language} -s {language} [-c {concept}] [-f {file}]

Practice a language.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -f, --file {file}     file with extra concepts to read, can be repeated
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "progress", "--help"])
    @patch("sys.stdout.write")
    def test_progress_help(self, sys_stdout_write: Mock):
        """Test that the progress help message is displayed."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertEqual(
            """Usage: toisto progress [-h] -t {language} -s {language} [-c {concept}] [-f {file}] \
[-S {option}]

Show progress.

Options:
  -h, --help            show this help message and exit
  -t, --target {language}
                        target language; languages available in built-in concepts: en, fi, nl
  -s, --source {language}
                        source language; languages available in built-in concepts: en, fi, nl
  -c, --concept {concept}
                        concept to use, can be repeated; default: all; built-in concepts:
  -f, --file {file}     file with extra concepts to read, can be repeated
  -S, --sort {option}   how to sort progress information; default: by retention; available options: attempts,
                        retention
""",
            self.ANSI_ESCAPE_CODES.sub("", sys_stdout_write.call_args_list[2][0][0]),
        )

    @patch("sys.argv", ["toisto", "--target", "nl", "--source", "fi"])
    def test_no_command(self):
        """Test that the practice command is returned if the user did not specify a command."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            concept=[],
            file=[],
        )
        self.assertEqual(expected_namespace, parse_arguments(self.argument_parser()))

    @patch("sys.argv", ["toisto", "--version"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_long_option(self, print_message: Mock):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "-V"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version_short_option(self, print_message: Mock):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "practice", "--target", "42", "--source", "@@"])
    @patch("sys.stderr.write")
    def test_invalid_language(self, sys_stderr_write: Mock):
        """Test that an error message is displayed if an invalid language is supplied."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "invalid choice: '42' (see https://www.iana.org/assignments/language-subtag-registry for valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )

    @patch("sys.argv", ["toisto", "practice", "--target", "fi", "--source", "fi"])
    @patch("sys.stderr.write")
    def test_equal_target_and_source_language(self, sys_stderr_write: Mock):
        """Test that an error message is displayed if the target and source language are equal."""
        self.assertRaises(SystemExit, parse_arguments, self.argument_parser())
        self.assertIn(
            "toisto: error: target and source language are the same: 'fi' \n",
            sys_stderr_write.call_args_list[1][0][0],
        )
