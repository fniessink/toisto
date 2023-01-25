"""Unit tests for the config module."""

from unittest.mock import patch, Mock
import unittest

from toisto.persistence.config import read_config


class ReadConfigTest(unittest.TestCase):
    """Unit tests for reading the config."""

    @patch("pathlib.Path.open", Mock(side_effect=FileNotFoundError))
    def test_missing_config(self):
        """Test reading a missing config."""
        self.assertIn("commands", read_config().sections())

    @patch("pathlib.Path.open")
    def test_invalid_config(self, path_open):
        """Test reading an invalid config."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = iter(["invalid\n"])
        self.assertIn("commands", read_config().sections())

    @patch("pathlib.Path.open")
    def test_valid_config(self, path_open):
        """Test reading a valid config."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = iter(
            ["[commands]\n", "mp3player = afplay\n"]
        )
        self.assertEqual("afplay", read_config().get("commands", "mp3player"))

    @patch("sys.platform", "darwin")
    @patch("pathlib.Path.open")
    def test_incomplete_config(self, path_open):
        """Test reading an incomplete config."""
        path_open.return_value.__enter__.return_value.__iter__.return_value = iter(["[commands]\n"])
        self.assertEqual("afplay", read_config().get("commands", "mp3player"))

    @patch("pathlib.Path.open", Mock(side_effect=FileNotFoundError))
    @patch("sys.platform", "linux")
    def test_default_mp3player_on_linux(self):
        """Test default mp3 player on Linux."""
        self.assertEqual("mpg123 --quiet", read_config().get("commands", "mp3player"))

    @patch("pathlib.Path.open", Mock(side_effect=FileNotFoundError))
    @patch("sys.platform", "darwin")
    def test_default_mp3player_on_macos(self):
        """Test default mp3 player on MacOS."""
        self.assertEqual("afplay", read_config().get("commands", "mp3player"))
