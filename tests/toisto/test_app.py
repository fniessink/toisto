"""Unit tests for the app."""

import sys
from contextlib import suppress
from unittest.mock import MagicMock, Mock, patch

import requests

from toisto.metadata import VERSION
from toisto.persistence.config import default_config
from toisto.ui.text import CONFIG_LANGUAGE_TIP

from ..base import ToistoTestCase


@patch("toisto.ui.speech.gTTS", Mock())
class AppTest(ToistoTestCase):
    """Unit tests for the main method."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.concept_file_count = 0  # Counter for generating unique concept files
        self.current_version = Mock(json=Mock(return_value=[dict(name=VERSION)]))
        self.latest_version = Mock(json=Mock(return_value=[dict(name="v9999")]))
        self.config = default_config()

    @patch("rich.console.Console.pager", MagicMock())
    @patch("toisto.persistence.spelling_alternatives.load_spelling_alternatives", Mock(return_value={}))
    @patch("toisto.ui.speech.Popen", Mock())
    @patch("builtins.input", Mock(side_effect=EOFError))
    @patch("pathlib.Path.exists", Mock(return_value=True))
    @patch("pathlib.Path.open")
    @patch("toisto.app.read_config")
    def run_main(self, read_config: Mock, path_open: Mock) -> Mock:
        """Run the main function and return the patched print method."""
        read_config.return_value = self.config
        path_open.return_value.__enter__.return_value.read.side_effect = self.read_concept_file
        with patch("rich.console.Console.print") as patched_print, suppress(SystemExit):
            from toisto.app import main

            main()
        return patched_print

    def read_concept_file(self) -> str:
        """Return a unique concept file."""
        count = self.concept_file_count
        self.concept_file_count += 1
        return f"""{{
            "concept-{count}": {{"fi": "concept-{count} in fi", "nl": "concept-{count} in nl"}}
        }}
        """

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("requests.get")
    def test_practice(self, requests_get: Mock) -> None:
        """Test that the practice command can be invoked."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl", "concept-1 in fi"])
    @patch("requests.get")
    def test_practice_concept(self, requests_get: Mock) -> None:
        """Test that the practice command can be invoked with a specific concept."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("toisto.metadata.check_output", Mock(return_value="toisto"))
    @patch("requests.get")
    def test_new_version_when_current_version_was_installed_with_uv(self, requests_get: Mock) -> None:
        """Test that the practice command shows a new version and an upgrade instruction."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertIn("v9999", patched_print.call_args_list[3][0][0].renderable)
        self.assertIn("uv tool upgrade", patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("toisto.metadata.check_output", Mock(side_effect=["", "toisto"]))
    @patch("requests.get")
    def test_new_version_when_current_version_was_installed_with_pipx(self, requests_get: Mock) -> None:
        """Test that the practice command shows a new version and an upgrade instruction."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertIn("v9999", patched_print.call_args_list[3][0][0].renderable)
        self.assertIn("pipx upgrade", patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("toisto.metadata.check_output", Mock(side_effect=["", ""]))
    @patch("requests.get")
    def test_new_version_when_current_version_was_installed_with_pip(self, requests_get: Mock) -> None:
        """Test that the practice command shows a new version and an upgrade instruction."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertIn("v9999", patched_print.call_args_list[3][0][0].renderable)
        self.assertIn("pip upgrade", patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("toisto.metadata.check_output", Mock(side_effect=[OSError, "toisto"]))
    @patch("requests.get")
    def test_new_version_when_checking_for_installation_tool_fails(self, requests_get: Mock) -> None:
        """Test that the practice command shows a new version and an upgrade instruction."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertIn("v9999", patched_print.call_args_list[3][0][0].renderable)
        self.assertIn("pipx upgrade", patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("requests.get")
    def test_current_version(self, requests_get: Mock) -> None:
        """Test that the practice command does not show the current version."""
        requests_get.return_value = self.current_version
        patched_print = self.run_main()
        self.assertNotEqual(VERSION, patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("requests.get")
    def test_github_connection_error(self, requests_get: Mock) -> None:
        """Test that the practice command starts even if GitHub cannot be reached to get the latest version."""
        requests_get.side_effect = requests.ConnectionError
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].startswith("👋 Welcome to [underline]Toisto"))

    @patch.object(sys, "argv", ["toisto", "progress", "--target", "fi", "--source", "nl"])
    @patch("requests.get")
    def test_progress(self, requests_get: Mock) -> None:
        """Test that the progress command can be invoked."""
        requests_get.return_value = self.latest_version
        patched_print = self.run_main()
        self.assertTrue(patched_print.call_args_list[2][0][0].title.startswith("Progress"))

    @patch.object(sys, "argv", ["toisto", "practice", "--target", "fi", "--source", "nl"])
    @patch("requests.get")
    def test_language_configuration_tip(self, requests_get: Mock) -> None:
        """Test that the practice command shows a tip when the user hasn't configured their languages."""
        requests_get.return_value = self.current_version
        patched_print = self.run_main()
        self.assertEqual(CONFIG_LANGUAGE_TIP, patched_print.call_args_list[3][0][0].renderable)

    @patch.object(sys, "argv", ["toisto", "practice"])
    @patch("requests.get")
    def test_no_language_configuration_tip(self, requests_get: Mock) -> None:
        """Test that the practice command does not show a tip when the user has configured their languages."""
        requests_get.return_value = self.current_version
        self.config.add_section("languages")
        self.config.set("languages", "target", "fi")
        self.config.set("languages", "source", "nl")
        patched_print = self.run_main()
        self.assertNotIn(CONFIG_LANGUAGE_TIP, patched_print.call_args_list[3][0][0])

    @patch.object(sys, "argv", ["toisto", "configure", "--target", "fi", "--source", "nl"])
    @patch("requests.get")
    def test_configure(self, requests_get: Mock) -> None:
        """Test that the configure command can be invoked."""
        requests_get.return_value = self.latest_version
        self.assertFalse(self.config.has_option("languages", "target"))
        self.assertFalse(self.config.has_option("languages", "source"))
        self.run_main()
        self.assertEqual("fi", self.config["languages"]["target"])
        self.assertEqual("nl", self.config["languages"]["source"])
