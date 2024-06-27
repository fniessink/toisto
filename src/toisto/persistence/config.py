"""Config file parser."""

import sys
from argparse import ArgumentParser
from collections.abc import Callable, Iterable
from configparser import ConfigParser, Error
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final, NoReturn

from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES

# The schema for the config file. Top-level keys are sections, values are a dict per option with the key being the
# option name and the value being an option consisting of the option quantifier, the allowed option values, and a
# function evaluating the validity of the option value.


class Quantifier(Enum):
    """Quantifier enumeration."""

    ANY = "any"
    INTEGER = "whole numbers"
    ONE_OF = "one of"


@dataclass
class Option:
    """Configuration option."""

    quantifier: Quantifier
    allowed_values: Iterable[str] = field(default_factory=list)
    is_valid: Callable[[str], bool] = field(default=lambda _value: True)
    default_value: Callable[[], str] | str = ""


CONFIG_SCHEMA: Final[dict[str, dict[str, Option]]] = dict(
    languages=dict(
        target=Option(Quantifier.ONE_OF, ALL_LANGUAGES.keys(), ALL_LANGUAGES.__contains__),
        source=Option(Quantifier.ONE_OF, ALL_LANGUAGES.keys(), ALL_LANGUAGES.__contains__),
    ),
    commands=dict(
        mp3player=Option(
            Quantifier.ANY,
            default_value=lambda: dict(darwin="afplay", linux="mpg123 --quiet").get(sys.platform, "builtin"),
        ),
    ),
    practice=dict(
        progress_update=Option(Quantifier.INTEGER, ["0", "1", "2", "3", "..."], lambda value: value.isdigit(), "0"),
    ),
)
CONFIG_FILENAME = Path("~/.toisto.cfg").expanduser()


class ConfigSchemaValidator:
    """Class to validate a config against the schema."""

    def __init__(self, config_parser: ConfigParser, argument_parser: ArgumentParser, config_filename: Path) -> None:
        self._argument_parser = argument_parser
        self._config_parser = config_parser
        self._config_filename = config_filename

    def _error(self, message: str) -> NoReturn:
        """Report the error and exit."""
        self._argument_parser.error(f"While reading from '{self._config_filename}': {message}")

    def validate(self) -> None:
        """Validate the config file against the schema."""
        for section in self._config_parser.sections():
            self._validate_section(section)

    def _validate_section(self, section: str) -> None:
        """Validate the section, including its options."""
        if section not in (allowed_sections := CONFIG_SCHEMA.keys()):
            self._error(f"unknown section '{section}'. Allowed sections are: {', '.join(allowed_sections)}.")
        for option in self._config_parser[section]:
            self._validate_option(section, option)

    def _validate_option(self, section: str, option_name: str) -> None:
        """Validate the option, including its value(s)."""
        if option_name not in (allowed_options := CONFIG_SCHEMA[section].keys()):
            self._error(
                f"unknown option '{option_name}' in section '{section}'. "
                f"Allowed options are: {', '.join(allowed_options)}.",
            )
        option = CONFIG_SCHEMA[section][option_name]
        value = self._config_parser.get(section, option_name)
        if not option.is_valid(value):
            self._error(
                f"incorrect value '{value}' for option '{option_name}' in section '{section}'. "
                f"Allowed values are {option.quantifier.value}: {', '.join(option.allowed_values)}.",
            )


def read_config(argument_parser: ArgumentParser, config_filename: Path = CONFIG_FILENAME) -> ConfigParser:
    """Read the config file, validate it, and exit with an error message if it doesn't pass."""
    parser = ConfigParser()
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
    for section in CONFIG_SCHEMA:
        if section not in parser.sections():
            parser.add_section(section)
        for option_name, option in CONFIG_SCHEMA[section].items():
            default = option.default_value
            if default and option_name not in parser[section]:
                parser[section][option_name] = default if isinstance(default, str) else default()
