"""Config file parser."""

import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from configparser import ConfigParser, Error
from pathlib import Path
from typing import NoReturn, get_args

from toisto.metadata import SUPPORTED_LANGUAGES
from toisto.model.language.cefr import CommonReferenceLevel

# The schema for the config file. Top-level keys are sections, values are a dict per option with the key being the
# option name and the value being a tuple of a specifier and the allowed option values.
CONFIG_SCHEMA: dict[str, dict[str, tuple[str, Iterable]]] = dict(
    languages=dict(
        target=("one of", SUPPORTED_LANGUAGES.keys()),
        source=("one of", SUPPORTED_LANGUAGES.keys()),
        levels=("one or more of", get_args(CommonReferenceLevel)),
    ),
    commands=dict(mp3player=("any", [])),
)


class ConfigSchemaValidator:
    """Class to validate a config against the schema."""

    def __init__(self, config_parser: ConfigParser, argument_parser: ArgumentParser, config_filename: Path) -> None:
        self._argument_parser = argument_parser
        self._config_parser = config_parser
        self._config_filename = config_filename

    def _error(self, message: str) -> NoReturn:
        """Report the error and exit."""
        self._argument_parser.error(f"While reading from '{self._config_filename}': {message}")

    def validate(self) -> None | NoReturn:  # type: ignore[return]
        """Validate the config file against the schema."""
        for section in self._config_parser.sections():
            self._validate_section(section)

    def _validate_section(self, section: str) -> None | NoReturn:  # type: ignore[return]
        """Validate the section, including its options."""
        if section not in (allowed_sections := CONFIG_SCHEMA.keys()):
            self._error(f"unknown section '{section}'. Allowed sections are: {', '.join(allowed_sections)}.")
        for option in self._config_parser[section]:
            self._validate_option(section, option)

    def _validate_option(self, section: str, option: str) -> None | NoReturn:  # type: ignore[return]
        """Validate the option, including its value(s)."""
        if option not in (allowed_options := CONFIG_SCHEMA[section].keys()):
            self._error(
                f"unknown option '{option}' in section '{section}'. Allowed options are: {', '.join(allowed_options)}.",
            )
        specifier, allowed_values = CONFIG_SCHEMA[section][option]
        if specifier == "any":
            return  # type: ignore[return-value]
        value = self._config_parser.get(section, option)
        values = [value] if specifier == "one of" else value.split()
        if any(value for value in values if value not in allowed_values):
            self._error(
                f"unknown value '{value}' for option '{option}' in section '{section}'. "
                f"Allowed values are {specifier}: {', '.join(allowed_values)}.",
            )


def read_config(argument_parser: ArgumentParser) -> ConfigParser | NoReturn:
    """Read the config file, validate it, and exit with an error message if it doesn't pass."""
    parser = ConfigParser()
    config_filename = Path("~/.toisto.cfg").expanduser()
    try:
        with config_filename.open("r", encoding="utf-8") as config_file:
            parser.read_file(config_file)
    except FileNotFoundError:
        pass
    except (OSError, Error) as reason:
        argument_parser.error(str(reason))
    ConfigSchemaValidator(parser, argument_parser, config_filename).validate()
    _add_defaults(parser)
    return parser


def default_config() -> ConfigParser:
    """Return the default configuration."""
    parser = ConfigParser()
    _add_defaults(parser)
    return parser


def _add_defaults(parser: ConfigParser) -> None:
    """Add the default configuration to the parser."""
    if parser.get("commands", "mp3player", fallback=None) is None:
        if "commands" not in parser.sections():
            parser.add_section("commands")
        defaults = dict(darwin="afplay", linux="mpg123 --quiet")
        parser["commands"]["mp3player"] = defaults.get(sys.platform, "playsound")
