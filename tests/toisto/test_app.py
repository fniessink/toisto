"""Unit tests for the app."""

import sys
import unittest
from contextlib import suppress
from unittest.mock import MagicMock, Mock, patch

import requests
from toisto.app import main
from toisto.metadata import TOPICS, VERSION
from toisto.model.language.concept import Concept


class AppTest(unittest.TestCase):
    """Unit tests for the main method."""

    topic_file_count = 0  # Counter for generating unique topic files

    def setUp(self):
        """Set up test fixtures."""
        Concept.instances.clear()
        self.latest_version = Mock(json=Mock(return_value=[dict(name="v9999")]))

    @patch("rich.console.Console.pager", MagicMock())
    @patch("toisto.ui.speech.Popen", Mock())
    @patch("builtins.input", Mock(side_effect=EOFError))
    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    def run_main(self, path_open: Mock) -> Mock:
        """Run the main function and return the patched print method."""
        path_open.return_value.__enter__.return_value.read.side_effect = self.read_topic_file
        with patch("rich.console.Console.print") as patched_print, suppress(SystemExit):
            main()
        return patched_print

    def read_topic_file(self):
        """Generate a unique topic file."""
        self.topic_file_count += 1
        count = self.topic_file_count
        return f'{{"concept-{count}": {{"fi": "concept-{count} in fi", "nl": "concept-{count} in nl"}}}}\n'

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl", "--topic-file", "test"])
    @patch("requests.get")
    def test_practice(self, requests_get: Mock):
        """Test that the practice command can be invoked."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl", "--topic-file", "test"])
    @patch("requests.get")
    def test_new_version(self, requests_get: Mock):
        """Test that the practice command shows a new version."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue("v9999" in patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl", "--topic-file", "test"])
    @patch("requests.get")
    def test_current_version(self, requests_get: Mock):
        """Test that the practice command does not show the current version."""
        requests_get.return_value = Mock(json=Mock(return_value=[dict(name=VERSION)]))
        patched_print = self.run_main()
        self.assertFalse(VERSION in patched_print.call_args_list[3][0][0])

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl", "--topic-file", "test"])
    @patch("requests.get")
    def test_github_connection_error(self, requests_get: Mock):
        """Test that the practice command starts even if GitHub cannot be reached to get the latest version."""
        requests_get.side_effect = requests.ConnectionError
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "progress", "--target", "fi", "--source", "nl", "--topic-file", "test"])
    @patch("requests.get")
    def test_progress(self, requests_get: Mock):
        """Test that the progress command can be invoked."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].title.startswith("Progress"))

    @patch.object(sys, "argv", ["toisto", "topics", "--target", "fi", "--source", "nl", "--topic-file", "test"])
    @patch("requests.get")
    def test_topics(self, requests_get: Mock):
        """Test that the topics command can be invoked."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].title.startswith("Topic"))
        last_concept = patched_print.call_args_list[2 + len(TOPICS)][0][0].columns[1]._cells[0]  # noqa: SLF001
        self.assertEqual(f"concept-{len(TOPICS)} in nl", last_concept)
