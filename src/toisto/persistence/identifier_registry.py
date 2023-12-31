"""Identifier registry."""

from abc import abstractmethod
from argparse import ArgumentParser
from pathlib import Path
from typing import Generic, TypeVar

from ..metadata import NAME

Identifier = TypeVar("Identifier")


class IdentifierRegistry(Generic[Identifier]):
    """Registry to check the uniqueness of identifiers across files."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.files_by_id: dict[Identifier, Path] = {}

    def check_and_register_identifiers(self, identifiers: tuple[Identifier, ...], file_path: Path) -> None:
        """Check and register the identifiers."""
        for identifier in identifiers:
            self._check_and_register_identifier(identifier, file_path)

    def _check_and_register_identifier(self, identifier: Identifier, file_path: Path) -> None:
        """Check that the identifier is unique and if so, register it. Otherwise, exit with an error message."""
        if identifier in self.files_by_id:
            other_file_path = self.files_by_id[identifier]
            occurs = "occurs multiple times" if file_path == other_file_path else "also occurs"
            name = self._identifier_name()
            self.argument_parser.error(
                f"{NAME} cannot read {name} file {file_path}: {name} identifier '{identifier}' {occurs} in {name} file "
                f"{other_file_path}.\n{name.capitalize()} identifiers must be unique across {name} files.\n",
            )
        self.files_by_id[identifier] = file_path

    @abstractmethod
    def _identifier_name(self) -> str:
        """Return the name of the identifier."""
