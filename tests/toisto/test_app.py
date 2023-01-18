"""Unit tests for the app."""

import argparse
import os
import unittest
from unittest.mock import Mock, patch
import sys

import requests

from toisto.app import main
from toisto.metadata import VERSION


class AppTest(unittest.TestCase):
    """Unit tests for the main method."""

    @patch.object(argparse.ArgumentParser, "_print_message")
    def test_no_arguments(self, write):
        """Test that the app exits if the user does not provide arguments."""
        os.environ["COLUMNS"] = "120"  # Fake that the terminal is wide enough.
        self.assertRaises(SystemExit, main)
        self.assertEqual(
            f"usage: {sys.argv[0].rsplit('/', maxsplit=1)[-1]} [-h] [-V] {{practice,progress,topics}} ...\n",
            write.call_args_list[0][0][0],
        )

    @patch("os.system", Mock())
    @patch("builtins.input", Mock(side_effect=[EOFError]))
    @patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name="v9999")]))))
    @patch.object(sys, "argv", ["toisto", "practice", "fi", "nl"])
    def test_practice(self):
        """Test that the practice command can be invoked."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue(patched_print.call_args_list[0][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch("os.system", Mock())
    @patch("builtins.input", Mock(side_effect=[EOFError]))
    @patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name="v9999")]))))
    @patch.object(sys, "argv", ["toisto", "practice", "fi", "nl"])
    def test_new_version(self):
        """Test that the practice command shows a new version."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue("v9999" in patched_print.call_args_list[1][0][0].renderable)

    @patch("os.system", Mock())
    @patch("builtins.input", Mock(side_effect=[EOFError]))
    @patch("requests.get", Mock(return_value=Mock(json=Mock(return_value=[dict(name=VERSION)]))))
    @patch.object(sys, "argv", ["toisto", "practice", "fi", "nl"])
    def test_current_version(self):
        """Test that the practice command does not show the current version."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue("[quiz]" in patched_print.call_args_list[1][0][0])

    @patch("os.system", Mock())
    @patch("builtins.input", Mock(side_effect=[EOFError]))
    @patch("requests.get", Mock(side_effect=requests.ConnectionError))
    @patch.object(sys, "argv", ["toisto", "practice", "fi", "nl"])
    def test_github_connection_error(self):
        """Test that the practice command starts even if GitHub cannot be reached to get the latest version."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue(patched_print.call_args_list[0][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "progress", "fi", "nl"])
    def test_progress(self):
        """Test that the progress command can be invoked."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue(patched_print.call_args_list[0][0][0].title.startswith("Progress"))

    @patch.object(sys, "argv", ["toisto", "topics", "fi", "nl"])
    def test_topics(self):
        """Test that the topics command can be invoked."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue(patched_print.call_args_list[0][0][0].title.startswith("Topic"))
