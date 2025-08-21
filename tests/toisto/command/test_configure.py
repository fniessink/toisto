"""Unit tests for the configure command."""

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from toisto.command.configure import configure
from toisto.persistence.config import default_config

from ...base import ToistoTestCase


@patch("toisto.command.configure.CONFIG_FILENAME", config_filename := MagicMock())
@patch("toisto.command.configure.write_config")
@patch("toisto.ui.text.console.print", Mock())
class ConfigureTest(ToistoTestCase):
    """Unit tests for the configure command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.argument_parser = ArgumentParser()

    def assert_configured(self, write_config: Mock, config: ConfigParser, *options: tuple[str, str, str]) -> None:
        """Check that the correct languages have been set in the config and it has been written."""
        write_config.assert_called_once_with(self.argument_parser, config, config_filename)
        for section, option, value in options:
            self.assertEqual(value, config[section][option])

    def test_default_config(self, write_config: Mock) -> None:
        """Test writing the default config."""
        config = default_config()
        configure(self.argument_parser, config, Namespace(target_language="en", source_language="fi"))
        self.assert_configured(write_config, config, ("languages", "target", "en"), ("languages", "source", "fi"))

    def test_changing_a_config(self, write_config: Mock) -> None:
        """Test changing a config."""
        config = default_config()
        config.add_section("languages")
        config["languages"]["target"] = "fi"
        config["languages"]["source"] = "nl"
        configure(self.argument_parser, config, Namespace(target_language="en", source_language="fi"))
        self.assert_configured(write_config, config, ("languages", "target", "en"), ("languages", "source", "fi"))

    def test_change_progess_update(self, write_config: Mock) -> None:
        """Test changing the progress update frequency."""
        config = ConfigParser()
        configure(self.argument_parser, config, Namespace(progress_update="12"))
        self.assert_configured(write_config, config, ("practice", "progress_update", "12"))

    def test_change_show_quiz_retention(self, write_config: Mock) -> None:
        """Test changing whether quiz retention should be shown."""
        config = ConfigParser()
        configure(self.argument_parser, config, Namespace(show_quiz_retention="yes"))
        self.assert_configured(write_config, config, ("practice", "show_quiz_retention", "yes"))

    def test_change_mp3_player(self, write_config: Mock) -> None:
        """Test changing the mp3 player."""
        config = ConfigParser()
        configure(self.argument_parser, config, Namespace(mp3player="/bin/mp3player"))
        self.assert_configured(write_config, config, ("commands", "mp3player", "/bin/mp3player"))

    def test_change_extra_paths(self, write_config: Mock) -> None:
        """Test changing the extra paths."""
        config = ConfigParser()
        configure(self.argument_parser, config, Namespace(extra=[Path("/home/user/extra.json")]))
        self.assert_configured(write_config, config, ("files", "/home/user/extra.json", ""))

    def test_progress_folder(self, write_config: Mock) -> None:
        """Test changing the progress folder."""
        config = ConfigParser()
        configure(self.argument_parser, config, Namespace(progress_folder=Path("/home/user/toisto")))
        self.assert_configured(write_config, config, ("progress", "folder", "/home/user/toisto"))
