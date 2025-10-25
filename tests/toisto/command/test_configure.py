"""Unit tests for the configure command."""

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from toisto.command.configure import configure
from toisto.persistence.config import default_config

from ...base import ToistoTestCase


class ConfigParserUnderTest(ConfigParser):
    """Config parser under test."""

    def optionxform(self, optionstr: str) -> str:
        """Return the option string unchanged."""
        return optionstr


@patch("toisto.command.configure.CONFIG_FILENAME", config_filename := MagicMock())
@patch("toisto.command.configure.write_config", write_config := Mock())
@patch("toisto.ui.text.console.print", Mock())
class ConfigureTest(ToistoTestCase):
    """Unit tests for the configure command."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.argument_parser = ArgumentParser()
        config_filename.reset_mock()
        write_config.reset_mock()

    def assert_configured(self, config: ConfigParser, *options: tuple[str, str, str]) -> None:
        """Check that the correct languages have been set in the config and it has been written."""
        write_config.assert_called_once_with(self.argument_parser, config, config_filename)
        self.assertEqual({}, config.defaults())
        for section, option, value in options:
            self.assertEqual(value, config[section][option])
        config_filename.open.assert_called_once()

    def test_default_config(self) -> None:
        """Test writing the default config."""
        config = default_config()
        configure(self.argument_parser, config, Namespace(target_language="en", source_language="fi"))
        self.assert_configured(config, ("languages", "target", "en"), ("languages", "source", "fi"))

    def test_changing_a_config(self) -> None:
        """Test changing a config."""
        config = default_config()
        config.add_section("languages")
        config["languages"]["target"] = "fi"
        config["languages"]["source"] = "nl"
        configure(self.argument_parser, config, Namespace(target_language="en", source_language="fi"))
        self.assert_configured(config, ("languages", "target", "en"), ("languages", "source", "fi"))

    def test_change_progess_update(self) -> None:
        """Test changing the progress update frequency."""
        config = ConfigParserUnderTest()
        configure(self.argument_parser, config, Namespace(progress_update="12"))
        self.assert_configured(config, ("practice", "progress_update", "12"))

    def test_change_show_quiz_retention(self) -> None:
        """Test changing whether quiz retention should be shown."""
        config = ConfigParserUnderTest()
        configure(self.argument_parser, config, Namespace(show_quiz_retention="yes"))
        self.assert_configured(config, ("practice", "show_quiz_retention", "yes"))

    def test_change_mp3_player(self) -> None:
        """Test changing the mp3 player."""
        config = ConfigParserUnderTest()
        configure(self.argument_parser, config, Namespace(mp3player="/bin/mp3player"))
        self.assert_configured(config, ("commands", "mp3player", "/bin/mp3player"))

    def test_change_extra_paths(self) -> None:
        """Test changing the extra paths."""
        config = ConfigParserUnderTest()
        configure(self.argument_parser, config, Namespace(extra=[Path("/home/user/extra.json")]))
        self.assert_configured(config, ("files", "/home/user/extra.json", ""))

    def test_progress_folder(self) -> None:
        """Test changing the progress folder."""
        config = ConfigParserUnderTest()
        configure(self.argument_parser, config, Namespace(progress_folder=Path("/home/user/toisto")))
        self.assert_configured(config, ("progress", "folder", "/home/user/toisto"))
