"""Loader."""

from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn

from ..metadata import CONCEPT_JSON_FILES, NAME
from ..model.language.concept import Concept, ConceptId
from ..model.language.concept_factory import ConceptDict, create_concept
from .identifier_registry import IdentifierRegistry
from .json_file import load_json


class Loader:
    """Domain object loader."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.concept_id_registry = IdentifierRegistry[ConceptId]("concept", argument_parser)
        self.builtin_files = CONCEPT_JSON_FILES

    def load(self, files: list[Path] | None = None) -> set[Concept] | NoReturn:
        """Load the domain objects from the files."""
        all_concepts = set()
        try:
            for file_path in self.builtin_files if files is None else files:
                concepts = self._parse_json(load_json(file_path))
                self.concept_id_registry.check_and_register_identifiers(self._concept_identifiers(concepts), file_path)
                all_concepts |= concepts
        except Exception as reason:  # noqa: BLE001
            self.argument_parser.error(f"{NAME} cannot read file {file_path}: {reason}.\n")
        return all_concepts

    def _parse_json(self, json: dict) -> set[Concept]:
        """Parse the domain objects from the JSON loaded from the domain object file."""
        return self._create_concepts(json.get("concepts", {}))

    def _create_concepts(self, concept_dict: dict[ConceptId, ConceptDict]) -> set[Concept]:
        """Parse the concepts from the JSON."""
        return {create_concept(concept_key, concept_value) for concept_key, concept_value in concept_dict.items()}

    def _concept_identifiers(self, concepts: set[Concept]) -> tuple[ConceptId, ...]:
        """Return the identifiers of the concepts."""
        return tuple(concept.concept_id for concept in concepts)
