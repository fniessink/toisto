"""Concept loader."""

from argparse import ArgumentParser
from pathlib import Path
from typing import TypedDict, cast

from ..metadata import NAME
from ..model.language import Language
from ..model.language.concept import Concept, ConceptId
from ..model.language.concept_factory import ConceptJSON, create_concept
from ..model.language.label_factory import LabelJSON
from .identifier_registry import IdentifierRegistry
from .json_file import load_json


class JSON(TypedDict):
    """Concept-and-label JSON file."""

    concepts: dict[ConceptId, ConceptJSON]
    labels: dict[Language, list[LabelJSON]]


class ConceptLoader:
    """Class to load concepts from concept JSON files."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.concept_id_registry = IdentifierRegistry[str]("concept", argument_parser)

    def load_concepts(self, *paths: Path) -> set[Concept]:
        """Load the concept from the concept JSON files."""
        concepts: dict[ConceptId, ConceptJSON] = {}
        labels: list[LabelJSON] = []
        for file_path in self._json_paths(*paths):
            json = self._load_file(file_path)
            concepts |= json.get("concepts", {})
            for language, language_labels in json.get("labels", {}).items():
                for label in language_labels:
                    label["language"] = language
                    labels.append(label)
        return self._create_concepts(concepts, labels)

    def _load_file(self, file_path: Path) -> JSON:
        """Load JSON file and check that concept identifiers are unique."""
        try:
            json = cast("JSON", load_json(file_path))
            concept_ids = tuple(json.get("concepts", {}).keys())
            self.concept_id_registry.check_and_register_identifiers(concept_ids, file_path)
        except Exception as reason:  # noqa: BLE001
            self.argument_parser.error(f"{NAME} cannot read file {file_path}: {reason}.\n")
        return json

    def _create_concepts(self, concepts: dict[ConceptId, ConceptJSON], labels: list[LabelJSON]) -> set[Concept]:
        """Create the concepts."""
        concept_id_to_labels_mapping: dict[ConceptId, list[LabelJSON]] = {}
        for label in labels:
            concept_ids = label["concept"] if isinstance(label["concept"], list) else [label["concept"]]
            for concept_id in concept_ids:
                concept_id_to_labels_mapping.setdefault(concept_id, []).append(label)
        return {
            create_concept(concept_key, concept_value, concept_id_to_labels_mapping.get(concept_key, []))
            for concept_key, concept_value in concepts.items()
        }

    def _json_paths(self, *paths: Path) -> list[Path]:
        """Return the JSON file paths."""
        json_paths: list[Path] = []
        for path in paths:
            json_paths.extend(path.rglob("*.json") if path.is_dir() else [path])
        return json_paths
