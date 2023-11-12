"""Unit tests for the config module."""

import argparse
import configparser
import unittest
from unittest.mock import Mock, patch

from toisto.persistence.config import CONFIG_FILENAME, default_config, read_config


class ConfigTestCase(unittest.TestCase):
    """Base class for config unit tests."""

    def read_config(self, path_open: Mock | None = None, *contents: str) -> configparser.ConfigParser:
        """Read the config file."""
        if path_open:
            path_open.return_value.__enter__.return_value.__iter__.return_value = iter(contents)
        return read_config(argparse.ArgumentParser())


@patch("pathlib.Path.open", Mock(side_effect=FileNotFoundError))
class MissingConfigTest(ConfigTestCase):
    """Unit tests for missing configs."""

    def test_missing_config(self):
        """Test reading a missing config."""
        self.assertEqual(default_config(), self.read_config())

    @patch("sys.platform", "linux")
    def test_default_mp3player_on_linux(self):
        """Test default mp3 player on Linux."""
        self.assertEqual("mpg123 --quiet", self.read_config().get("commands", "mp3player"))

    @patch("sys.platform", "darwin")
    def test_default_mp3player_on_macos(self):
        """Test default mp3 player on MacOS."""
        self.assertEqual("afplay", self.read_config().get("commands", "mp3player"))

    @patch("sys.platform", "windows")
    def test_default_mp3player_on_windows(self):
        """Test default mp3 player on Windows."""
        self.assertEqual("playsound", self.read_config().get("commands", "mp3player"))


@patch("pathlib.Path.open")
class ReadValidConfigTest(ConfigTestCase):
    """Unit tests for valid configs."""

    def test_valid_commands(self, path_open: Mock):
        """Test reading a valid config."""
        config = self.read_config(path_open, "[commands]\n", "mp3player = some mp3 player\n")
        self.assertEqual("some mp3 player", config.get("commands", "mp3player"))

    @patch("sys.platform", "darwin")
    def test_incomplete_config(self, path_open: Mock):
        """Test reading an incomplete config."""
        config = self.read_config(path_open, "[commands]\n")
        self.assertEqual("afplay", config.get("commands", "mp3player"))


@patch("sys.stderr.write")
@patch("pathlib.Path.open")
class ReadInvalidConfigTest(ConfigTestCase):
    """Unit tests for reading invalid configs."""

    def test_no_section_headers(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an invalid config (no section headers)."""
        self.assertRaises(SystemExit, self.read_config, path_open, "invalid\n")
        self.assertIn("File contains no section headers", sys_stderr_write.call_args_list[1][0][0])

    def test_repeated_section(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an invalid config (repeated section)."""
        config_file_contents = ["[commands]\n", "mp3player = afplay\n"] * 2
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn("section 'commands' already exists", sys_stderr_write.call_args_list[1][0][0])

    def test_repeated_option(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an invalid config (repeated option)."""
        config_file_contents = ["[commands]\n", "mp3player = afplay\n", "mp3player = vlc"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            "option 'mp3player' in section 'commands' already exists",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_invalid_section(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an invalid config (invalid section)."""
        config_file_contents = ["[command]\n", "mp3player = afplay\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': unknown section 'command'. "
            "Allowed sections are: languages, commands",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_invalid_option(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an invalid config (invalid option)."""
        config_file_contents = ["[commands]\n", "mp4player = afplay\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': unknown option 'mp4player' in section 'commands'. "
            "Allowed options are: mp3player.",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_invalid_one_of_option_value(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an invalid config (invalid option value, one of)."""
        config_file_contents = ["[languages]\n", "target = foo\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': unknown value 'foo' for option 'target' in section 'languages'. "
            "Allowed values are one of: aa, ab",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_valid_one_of_option_values(self, path_open: Mock, sys_stderr_write: Mock):
        """Test reading an valid config (one of option)."""
        config_file_contents = ["[languages]\n", "target = nl\n"]
        self.read_config(path_open, *config_file_contents)
        sys_stderr_write.assert_not_called()
