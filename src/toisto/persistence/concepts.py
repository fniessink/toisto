"""Load concepts from concept files."""

from argparse import ArgumentParser
from collections.abc import Collection
from typing import NoReturn

from ..metadata import CONCEPT_JSON_FILES
from ..model.language.concept import Concept, ConceptId
from ..model.language.concept_factory import create_concept
from .loader import Loader


class ConceptLoader(Loader[ConceptId, Concept]):
    """Class to load concepts."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        super().__init__("concept", CONCEPT_JSON_FILES, argument_parser)

    def _parse_json(self, json: dict) -> set[Concept] | NoReturn:
        """Parse the concepts from the loaded JSON."""
        return {create_concept(concept_key, concept_value) for concept_key, concept_value in json.items()}

    def _identifiers(self, domain_objects: Collection[Concept]) -> tuple[ConceptId, ...]:
        """Return the identifiers of the concepts."""
        return tuple(concept.concept_id for concept in domain_objects)
