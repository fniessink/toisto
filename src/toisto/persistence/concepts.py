"""Load concepts from concept files."""

from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn

from ..metadata import NAME
from ..model.language.concept import Concept, ConceptId
from ..model.language.concept_factory import create_concept
from .identifier_registry import IdentifierRegistry
from .json_file import load_json


class ConceptIdRegistry(IdentifierRegistry[ConceptId]):
    """Registry to check the uniqueness of concept identifiers across concept files."""

    def _identifier_name(self) -> str:
        return "concept"


def load_concepts(
    concept_files: list[Path],
    concept_id_registry: ConceptIdRegistry,
    argument_parser: ArgumentParser,
) -> set[Concept] | NoReturn:
    """Load the concepts from the specified concept files."""
    all_concepts = set()
    for concept_file in concept_files:
        concepts = []
        try:
            for concept_key, concept_value in load_json(concept_file).items():
                concept = create_concept(concept_key, concept_value)
                concepts.append(concept)
        except Exception as reason:  # noqa: BLE001
            argument_parser.error(f"{NAME} cannot read concept file {concept_file}: {reason}.\n")
        concept_ids = tuple(concept.concept_id for concept in concepts)
        concept_id_registry.check_and_register_identifiers(concept_ids, concept_file)
        all_concepts |= set(concepts)
    return all_concepts
