"""Concept loader."""

from argparse import ArgumentParser
from collections.abc import Iterator
from pathlib import Path
from typing import TypedDict, cast, get_args

from ..metadata import NAME
from ..model.language import Language
from ..model.language.concept import Concept, ConceptId, ConceptIdListOrString, NonInvertedConceptRelation
from ..model.language.concept_factory import ConceptJSON, create_concept
from ..model.language.label import Label
from ..model.language.label_factory import LabelJSON
from .identifier_registry import IdentifierRegistry
from .json_file import load_json

RELATION_KEYS = get_args(NonInvertedConceptRelation)


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
        concept_files: dict[ConceptId, Path] = {}
        labeled: list[tuple[Path, LabelJSON]] = []
        for file_path in self._json_paths(*paths):
            json = self._load_file(file_path)
            for concept_id, concept_json in json.get("concepts", {}).items():
                concepts[concept_id] = concept_json
                concept_files[concept_id] = file_path
            for language, language_labels in json.get("labels", {}).items():
                for label in language_labels:
                    label["language"] = language
                    labeled.append((file_path, label))
        self._check_references(concepts, concept_files, labeled)
        created_concepts = self._create_concepts(concepts, [label for _, label in labeled])
        self._check_roots(labeled)
        return created_concepts

    def _load_file(self, file_path: Path) -> JSON:
        """Load JSON file and check that concept identifiers are unique."""
        try:
            json = cast("JSON", load_json(file_path))  # pragma: no mutate
            concept_ids = tuple(json.get("concepts", {}).keys())
            self.concept_id_registry.check_and_register_identifiers(concept_ids, file_path)
        except Exception as reason:  # noqa: BLE001
            self.argument_parser.error(f"{NAME} cannot read file {file_path}: {reason}.\n")
        return json

    def _check_references(
        self,
        concepts: dict[ConceptId, ConceptJSON],
        concept_files: dict[ConceptId, Path],
        labeled: list[tuple[Path, LabelJSON]],
    ) -> None:
        """Check that concept relations and label concepts refer to defined concepts."""
        errors = list(self._relation_errors(concepts, concept_files))
        errors.extend(
            f"file {file_path}: label refers to concept '{concept_id}' that is not a defined concept"
            for file_path, label in labeled
            for concept_id in (label["concept"] if isinstance(label["concept"], list) else [label["concept"]])
            if concept_id not in concepts
        )
        if errors:
            self.argument_parser.error(f"{NAME} cannot read concepts:\n" + "\n".join(sorted(set(errors))) + "\n")

    def _check_roots(self, labeled: list[tuple[Path, LabelJSON]]) -> None:
        """Check that label roots refer to existing labels in the same language."""
        spellings = set(Label.homograph_mapping)
        errors: list[str] = []
        for file_path, label in labeled:
            language = label["language"]
            root_or_roots = label.get("roots", [])
            roots = [root_or_roots] if isinstance(root_or_roots, str) else root_or_roots
            concept = label["concept"]
            concept_id = ", ".join(concept) if isinstance(concept, list) else concept
            errors.extend(
                f"file {file_path}: root '{root}' of concept '{concept_id}' ({language}) is not a defined label"
                for root in roots
                if (language, root) not in spellings
            )
        if errors:
            self.argument_parser.error(f"{NAME} cannot read concepts:\n" + "\n".join(sorted(set(errors))) + "\n")

    @staticmethod
    def _relation_errors(concepts: dict[ConceptId, ConceptJSON], concept_files: dict[ConceptId, Path]) -> Iterator[str]:
        """Yield an error for each concept relation that refers to a concept that is not defined."""
        for concept_id, concept_json in concepts.items():
            relations = cast("dict[str, ConceptIdListOrString]", concept_json)
            for relation in RELATION_KEYS:
                related = relations.get(relation, [])
                for related_concept_id in related if isinstance(related, list) else [related]:
                    if related_concept_id not in concepts:
                        yield (
                            f"file {concept_files[concept_id]}: concept '{concept_id}' has "
                            f"{relation} '{related_concept_id}' that is not a defined concept"
                        )

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
