"""Unit tests for the app."""

import argparse
import os
import unittest
from unittest.mock import Mock, patch
import sys

from toisto.app import main


class AppTest(unittest.TestCase):
    """Unit tests for the main method."""

    @patch.object(argparse.ArgumentParser, "_print_message")
    def test_no_arguments(self, write):
        """Test that the app exits if the user does not provide arguments."""
        os.environ['COLUMNS'] = "120"  # Fake that the terminal is wide enough.
        self.assertRaises(SystemExit, main)
        self.assertEqual(
            f"usage: {sys.argv[0].rsplit('/', maxsplit=1)[-1]} [-h] [-V] {{practice,progress}} ...\n",
            write.call_args_list[0][0][0]
        )

    @patch("os.system", Mock())
    @patch("builtins.input", Mock(side_effect=[EOFError]))
    @patch.object(sys, "argv", ["toisto", "practice", "fi", "nl"])
    def test_practice(self):
        """Test that the practice command can be invoked."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue(patched_print.call_args_list[0][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "progress", "fi", "nl"])
    def test_progress(self):
        """Test that the progress command can be invoked."""
        with patch("rich.console.Console.print") as patched_print:
            main()
        self.assertTrue(patched_print.call_args_list[0][0][0].title.startswith("Progress"))
