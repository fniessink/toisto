"""Identifier registry."""

from argparse import ArgumentParser
from pathlib import Path
from typing import Generic, TypeVar

from ..metadata import NAME

Identifier = TypeVar("Identifier")


class IdentifierRegistry(Generic[Identifier]):
    """Registry to check the uniqueness of domain object identifiers across files."""

    def __init__(self, domain_object_name: str, argument_parser: ArgumentParser) -> None:
        self.domain_object_name = domain_object_name
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
            name = self.domain_object_name
            self.argument_parser.error(
                f"{NAME} cannot read file {file_path}: {name} identifier '{identifier}' {occurs} in file "
                f"{other_file_path}.\n{name.capitalize()} identifiers must be unique across files.\n",
            )
        self.files_by_id[identifier] = file_path
