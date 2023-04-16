"""Unit tests for the CLI module."""

import unittest
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from unittest.mock import Mock, patch

from toisto.metadata import SUMMARY
from toisto.ui.cli import create_argument_parser


class ParserTest(unittest.TestCase):
    """Unit tests for the CLI parser."""

    @property
    def argument_parser(self) -> ArgumentParser:
        """Create the argument parser."""
        with patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name="v9999")])))):
            return create_argument_parser(ConfigParser(), [])

    @patch("sys.argv", ["toisto", "--help"])
    @patch("sys.stdout.write")
    def test_help(self, sys_stdout_write: Mock):
        """Test that a help message is displayed."""
        self.assertRaises(SystemExit, self.argument_parser.parse_args)
        self.assertIn(SUMMARY, sys_stdout_write.call_args_list[2][0][0])

    @patch("sys.argv", ["toisto", "practice", "--target", "nl", "--source", "fi"])
    def test_practice_command(self):
        """Test that the practice command can be specified."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            levels=[],
            topic=[],
            topic_file=[],
        )
        self.assertEqual(expected_namespace, self.argument_parser.parse_args())

    @patch("sys.argv", ["toisto", "--target", "nl", "--source", "fi"])
    def test_no_command(self):
        """Test that the practice command is returned if the user did not specify a command."""
        expected_namespace = Namespace(
            command="practice",
            target_language="nl",
            source_language="fi",
            levels=[],
            topic=[],
            topic_file=[],
        )
        self.assertEqual(expected_namespace, self.argument_parser.parse_args())

    @patch("sys.argv", ["toisto", "--version"])
    @patch.object(ArgumentParser, "_print_message")
    def test_version(self, print_message: Mock):
        """Test that the app writes the version number to stdout."""
        self.assertRaises(SystemExit, self.argument_parser.parse_args)
        self.assertRegex(print_message.call_args_list[0][0][0], r"\d+.\d+.\d+")

    @patch("sys.argv", ["toisto", "practice", "--target", "42", "--source", "@@"])
    @patch("sys.stderr.write")
    def test_invalid_language(self, sys_stderr_write: Mock):
        """Test that an error message is displayed if an invalid language is supplied."""
        self.assertRaises(SystemExit, self.argument_parser.parse_args)
        self.assertIn(
            "invalid choice: '42' (see https://www.iana.org/assignments/language-subtag-registry for valid choices)",
            sys_stderr_write.call_args_list[1][0][0],
        )
