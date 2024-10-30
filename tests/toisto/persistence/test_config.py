"""Unit tests for the config module."""

import argparse
import unittest
from configparser import ConfigParser
from unittest.mock import MagicMock, Mock, call, patch

from toisto.persistence.config import CONFIG_FILENAME, default_config, read_config, write_config


class ConfigTestCase(unittest.TestCase):
    """Base class for config unit tests."""

    def read_config(self, path_open: Mock | None = None, *contents: str) -> ConfigParser:
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
        self.assertEqual("builtin", self.read_config().get("commands", "mp3player"))

    def test_default_practice_progress_update(self):
        """Test the default practice progress frequency value."""
        self.assertEqual("0", self.read_config().get("practice", "progress_update"))


@patch("pathlib.Path.open")
class ReadValidConfigTest(ConfigTestCase):
    """Unit tests for valid configs."""

    def test_valid_commands(self, path_open: Mock) -> None:
        """Test reading a valid config."""
        config = self.read_config(path_open, "[commands]\n", "mp3player = some mp3 player\n")
        self.assertEqual("some mp3 player", config.get("commands", "mp3player"))

    def test_valid_progress_update(self, path_open: Mock) -> None:
        """Test reading a valid config."""
        config = self.read_config(path_open, "[practice]\n", "progress_update = 42\n")
        self.assertEqual("42", config.get("practice", "progress_update"))

    def test_empty_file_section(self, path_open: Mock) -> None:
        """Test reading a valid config with an empty file section."""
        config = self.read_config(path_open, "[files]\n")
        self.assertEqual([], list(config["files"].keys()))

    def test_file_section_with_one_file(self, path_open: Mock) -> None:
        """Test reading a valid config with a file section with one file."""
        config = self.read_config(path_open, "[files]\n", "/home/user/toisto/extra.json\n")
        self.assertEqual(["/home/user/toisto/extra.json"], list(config["files"].keys()))

    def test_file_section_with_multiple_files(self, path_open: Mock) -> None:
        """Test reading a valid config with a file section with multiple files."""
        config = self.read_config(path_open, "[files]\n", "extra1.json\n", "extra2.json\n")
        self.assertEqual(["extra1.json", "extra2.json"], list(config["files"].keys()))

    def test_file_section_with_upper_case_characters_in_file_name(self, path_open: Mock) -> None:
        """Test reading a valid config with a file section with a file with uppercase characters."""
        config = self.read_config(path_open, "[files]\n", "/User/toisto/extra.json\n")
        self.assertEqual(["/User/toisto/extra.json"], list(config["files"].keys()))

    @patch("sys.platform", "darwin")
    def test_incomplete_config(self, path_open: Mock) -> None:
        """Test reading an incomplete config."""
        config = self.read_config(path_open, "[commands]\n\n[practice]\n")
        self.assertEqual("afplay", config.get("commands", "mp3player"))
        self.assertEqual("0", config.get("practice", "progress_update"))


@patch("sys.stderr.write")
@patch("pathlib.Path.open")
class ReadInvalidConfigTest(ConfigTestCase):
    """Unit tests for reading invalid configs."""

    def test_no_section_headers(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid config (no section headers)."""
        self.assertRaises(SystemExit, self.read_config, path_open, "invalid\n")
        self.assertIn("File contains no section headers", sys_stderr_write.call_args_list[1][0][0])

    def test_repeated_section(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid config (repeated section)."""
        config_file_contents = ["[commands]\n", "mp3player = afplay\n"] * 2
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn("section 'commands' already exists", sys_stderr_write.call_args_list[1][0][0])

    def test_repeated_option(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid config (repeated option)."""
        config_file_contents = ["[commands]\n", "mp3player = afplay\n", "mp3player = vlc"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            "option 'mp3player' in section 'commands' already exists",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_invalid_section(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid config (invalid section)."""
        config_file_contents = ["[command]\n", "mp3player = afplay\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': unknown section 'command'. "
            "Allowed sections are: languages, commands",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_invalid_option(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid config (invalid option)."""
        config_file_contents = ["[commands]\n", "mp4player = afplay\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': unknown option 'mp4player' in section 'commands'. "
            "Allowed options are: mp3player.",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_invalid_one_of_option_value(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid config (invalid option value, one of)."""
        config_file_contents = ["[languages]\n", "target = foo\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': "
            "incorrect value 'foo' for option 'target' in section 'languages'. Allowed values are one of: aa, ab",
            sys_stderr_write.call_args_list[1][0][0],
        )

    def test_valid_one_of_option_values(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an valid config (one of option)."""
        config_file_contents = ["[languages]\n", "target = nl\n"]
        self.read_config(path_open, *config_file_contents)
        sys_stderr_write.assert_not_called()

    def test_invalid_progress_update(self, path_open: Mock, sys_stderr_write: Mock) -> None:
        """Test reading an invalid progress frequency."""
        config_file_contents = ["[practice]\n", "progress_update = foo\n"]
        self.assertRaises(SystemExit, self.read_config, path_open, *config_file_contents)
        self.assertIn(
            f"While reading from '{CONFIG_FILENAME}': "
            "incorrect value 'foo' for option 'progress_update' in section 'practice'. "
            "Allowed values are whole numbers: 0, 1, 2, 3, ...",
            sys_stderr_write.call_args_list[1][0][0],
        )


class WriteConfigTest(ConfigTestCase):
    """Unit tests for writing a config."""

    def config_file(self, side_effect: OSError | None = None) -> MagicMock:
        """Create a mock config file."""
        config_file = MagicMock()
        config_file.open.return_value.__enter__.return_value = config_file
        config_file.open.return_value.__enter__.side_effect = side_effect
        return config_file

    def test_write_empty_config(self) -> None:
        """Test writing an empty config."""
        config_parser = ConfigParser()
        config_file = self.config_file()
        write_config(argparse.ArgumentParser(), config_parser, config_file)
        self.assertEqual([call("")], config_file.write.call_args_list)

    def test_write_config(self) -> None:
        """Test writing a config."""
        config_parser = ConfigParser()
        config_parser.add_section("languages")
        config_parser.set("languages", "target", "fi")
        config_parser.set("languages", "source", "en")
        config_file = self.config_file()
        write_config(argparse.ArgumentParser(), config_parser, config_file)
        self.assertEqual([call("[languages]\ntarget=fi\nsource=en\n")], config_file.write.call_args_list)

    def test_write_config_with_files(self) -> None:
        """Test writing a config with files."""
        config_parser = ConfigParser()
        config_parser.add_section("files")
        config_parser.set("files", "extra1", "")
        config_parser.set("files", "extra2", "")
        config_file = self.config_file()
        write_config(argparse.ArgumentParser(), config_parser, config_file)
        self.assertEqual([call("[files]\nextra1\nextra2\n")], config_file.write.call_args_list)

    @patch("sys.stderr.write")
    def test_write_failure(self, sys_stderr_write: Mock) -> None:
        """Test error message on write failure."""
        config_parser = ConfigParser()
        error_message = "Could not write file"
        config_file = self.config_file(PermissionError(error_message))
        self.assertRaises(SystemExit, write_config, argparse.ArgumentParser(), config_parser, config_file)
        self.assertIn(error_message, sys_stderr_write.call_args_list[1][0][0])
