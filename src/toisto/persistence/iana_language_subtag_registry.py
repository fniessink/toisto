"""IANA language subtag registry loader.

Toisto includes the IANA language subtag registry located at https://www.iana.org/assignments/language-subtag-registry.
This allows Toisto to check language command line arguments for correctness.
"""

from pathlib import Path

from toisto.metadata import LANGUAGES_FILE
from toisto.model.language import Language
from toisto.tools import first


def load_languages() -> dict[Language, str]:
    """Load the languages from the IANA language subtag registry."""
    languages: dict[Language, str] = {}
    record_lines: list[str] = []
    with Path(LANGUAGES_FILE).open(encoding="utf-8") as language_registry:
        for line in language_registry.readlines():
            if line.startswith("%%"):
                if "Type: language\n" in record_lines:
                    languages.update(parse_record(record_lines))
                record_lines = []  # Reset the lines for the next record
            elif line.startswith("  "):  # Continuation line
                record_lines[-1] += line[1:]  # Skip one space of the continuation
            else:
                record_lines.append(line)
    return languages


def parse_record(lines: list[str]) -> dict[Language, str]:
    """Parse a language record."""
    language = first(lines, lambda line: line.startswith("Subtag")).split(": ", maxsplit=1)[1].strip()
    description = first(lines, lambda line: line.startswith("Description")).split(": ", maxsplit=1)[1].strip()
    return {Language(language): description}
