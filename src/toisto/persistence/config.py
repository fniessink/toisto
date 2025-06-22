"""Config file parser."""

from argparse import ArgumentParser
from collections.abc import Callable, Iterable
from configparser import ConfigParser, Error
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Final, NoReturn
from uuid import uuid1

from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.tools import platform

from .folder import home

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


DEFAULT_MP3PLAYERS = {"darwin": "afplay", "linux": "mpg123 --quiet"}
CONFIG_SCHEMA: Final[dict[str, dict[str, Option] | list[str]]] = {
    "languages": {
        "target": Option(Quantifier.ONE_OF, ALL_LANGUAGES.keys(), ALL_LANGUAGES.__contains__),
        "source": Option(Quantifier.ONE_OF, ALL_LANGUAGES.keys(), ALL_LANGUAGES.__contains__),
    },
    "commands": {
        "mp3player": Option(Quantifier.ANY, default_value=lambda: DEFAULT_MP3PLAYERS.get(platform(), "builtin")),
    },
    "practice": {
        "progress_update": Option(Quantifier.INTEGER, ["0", "1", "2", "3", "..."], lambda value: value.isdigit(), "0"),
    },
    "progress": {
        "folder": Option(Quantifier.ANY, default_value=str(home())),
    },
    "identity": {"uuid": Option(Quantifier.ANY, default_value=str(uuid1()))},
    "files": [],
}
CONFIG_FILENAME = home() / ".toisto.cfg"


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
        section_schema = CONFIG_SCHEMA[section]
        if isinstance(section_schema, dict):
            for option in self._config_parser[section]:
                self._validate_option(section, option, list(section_schema.keys()), section_schema.get(option))

    def _validate_option(
        self, section: str, option_name: str, allowed_options: list[str], option: Option | None
    ) -> None:
        """Validate the option, including its value(s)."""
        if option is None:
            self._error(
                f"unknown option '{option_name}' in section '{section}'. "
                f"Allowed options are: {', '.join(allowed_options)}.",
            )
        value = self._config_parser.get(section, option_name)
        if not option.is_valid(value):
            self._error(
                f"incorrect value '{value}' for option '{option_name}' in section '{section}'. "
                f"Allowed values are {option.quantifier.value}: {', '.join(option.allowed_values)}.",
            )


def read_config(argument_parser: ArgumentParser, config_filename: Path = CONFIG_FILENAME) -> ConfigParser:
    """Read the config file, validate it, and exit with an error message if it doesn't pass."""
    parser = _create_config_parser()
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


def write_config(
    argument_parser: ArgumentParser, config_parser: ConfigParser, config_filename: Path = CONFIG_FILENAME
) -> None:
    """Write the config file, and exit with an error message if writing it fails."""
    try:
        config_file_text = StringIO()
        config_parser.write(config_file_text, space_around_delimiters=False)
        # Remove the equal sign from lines that only have keys, such as in the files section:
        stripped_config_file_text = "\n".join([line.rstrip("=") for line in config_file_text.getvalue().splitlines()])
        with config_filename.open("w", encoding="utf-8") as config_file:
            config_file.write(stripped_config_file_text)
    except OSError as reason:
        argument_parser.error(str(reason))


def default_config() -> ConfigParser:
    """Return the default configuration."""
    parser = _create_config_parser()
    _add_defaults(parser)
    return parser


def _create_config_parser() -> ConfigParser:
    """Return a config parser without configuration."""
    parser = ConfigParser(allow_no_value=True)
    # The files section has options that are file names, we don't want those to be lower cased:
    parser.optionxform = lambda optionstr: optionstr  # type: ignore[method-assign]
    return parser


def _add_defaults(parser: ConfigParser) -> None:
    """Add the default configuration to the parser."""
    for section, section_schema in CONFIG_SCHEMA.items():
        if isinstance(section_schema, dict):  # Only dict sections have defaults
            _add_defaults_to_section(parser, section, section_schema)


def _add_defaults_to_section(parser: ConfigParser, section: str, section_schema: dict[str, Option]) -> None:
    """Add the default configuration for the section to the parser."""
    for option_name, option in section_schema.items():
        default = option.default_value
        if default and (section not in parser.sections() or option_name not in parser[section]):
            if section not in parser.sections():
                parser.add_section(section)
            parser[section][option_name] = default if isinstance(default, str) else default()
