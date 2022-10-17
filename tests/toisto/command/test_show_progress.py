"""Unit tests for the show progress command."""

import unittest
from unittest.mock import patch

from toisto.command import show_progress
from toisto.model import Progress, Quiz


class ShowProgressTest(unittest.TestCase):
    """Test the show progress command."""

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [], Progress({}))
        self.assertEqual("Progress Finnish", console_print.call_args[0][0].title)

    def test_quiz(self):
        """Test that quizzes are shown."""
        quiz = Quiz("fi", "nl", "Terve", "Hoi")
        with patch("rich.console.Console.print") as console_print:
            show_progress("fi", [quiz], Progress({str(quiz): dict(count=1)}))
        self.assertEqual("1", list(console_print.call_args[0][0].columns[5].cells)[0])
