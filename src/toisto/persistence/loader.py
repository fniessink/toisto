"""Loader."""

from abc import abstractmethod
from argparse import ArgumentParser
from collections.abc import Collection
from pathlib import Path
from typing import Generic, NoReturn, TypeVar

from ..metadata import NAME
from .identifier_registry import IdentifierRegistry
from .json_file import load_json

DomainObjectIdentifierType = TypeVar("DomainObjectIdentifierType")
DomainObjectType = TypeVar("DomainObjectType")


class Loader(Generic[DomainObjectIdentifierType, DomainObjectType]):
    """Base class for domain objects loaders."""

    def __init__(self, domain_object_name: str, builtin_files: list[Path], argument_parser: ArgumentParser) -> None:
        self.domain_object_name = domain_object_name
        self.builtin_files = builtin_files
        self.argument_parser = argument_parser
        self.id_registry = IdentifierRegistry[DomainObjectIdentifierType](domain_object_name, argument_parser)

    def load(self, files: list[Path] | None = None) -> set[DomainObjectType] | NoReturn:
        """Load the domain objects from the files."""
        all_domain_objects = set()
        try:
            for file_path in files or self.builtin_files:
                domain_objects = self._parse_json(load_json(file_path))
                self.id_registry.check_and_register_identifiers(self._identifiers(domain_objects), file_path)
                all_domain_objects |= domain_objects
        except Exception as reason:  # noqa: BLE001
            self.argument_parser.error(f"{NAME} cannot read {self.domain_object_name} file {file_path}: {reason}.\n")
        return all_domain_objects

    @abstractmethod
    def _parse_json(self, json: dict) -> set[DomainObjectType] | NoReturn:
        """Parse the domain objects from the JSON loaded from the domain object file."""

    @abstractmethod
    def _identifiers(self, domain_objects: Collection[DomainObjectType]) -> tuple[DomainObjectIdentifierType, ...]:
        """Return the identifiers of the domain objects."""
