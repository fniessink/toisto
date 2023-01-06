"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast, get_args, Literal, Union

from toisto.metadata import Language

from ..model_types import ConceptId
from .concept import Concept, Labels
from .grammar import GrammaticalCategory, AUTO_USES
from .label import label_factory

ConceptRelation = Literal["uses"]
LeafConceptDict = dict[Language | ConceptRelation, str | list[str] | ConceptId | list[ConceptId]]
CompositeConceptDict = dict[GrammaticalCategory | ConceptRelation, Union["CompositeConceptDict", LeafConceptDict]]
ConceptDict = LeafConceptDict | CompositeConceptDict


@dataclass
class ConceptFactory:
    """Create concepts from the concept dict."""

    concept_id: ConceptId
    concept_dict: ConceptDict

    def create_concept(self) -> Concept:
        """Create a concept from the concept_dict"""
        return self.composite_concept() if self.get_grammatical_categories() else self.leaf_concept()

    def composite_concept(self) -> Concept:
        """Create a composite concept from a composite concept dict."""
        uses = self.get_uses()
        constituent_concepts = []
        for category in self.get_grammatical_categories():
            constituent_concept_id = ConceptId(f"{self.concept_id}/{category}")
            constituent_concept_dict = cast(CompositeConceptDict, self.concept_dict)[category] | dict(uses=uses)
            concept_factory = self.__class__(constituent_concept_id, cast(ConceptDict, constituent_concept_dict))
            constituent_concepts.append(concept_factory.create_concept())
        return Concept(self.concept_id, tuple(uses), tuple(constituent_concepts))

    def leaf_concept(self) -> Concept:
        """Create a leaf concept from a leaf concept dict."""
        uses = self.get_uses()
        for category, used_category in AUTO_USES.items():
            if category in self.concept_id:
                uses.append(cast(ConceptId, self.concept_id.replace(category, used_category)))
                break
        labels = {
            key: label_factory(cast(str | list[str], value))
            for key, value in self.concept_dict.items()
            if key in get_args(Language)
        }
        return Concept(self.concept_id, tuple(uses), (), cast(dict[Language, Labels], labels))

    def get_grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        return tuple(
            cast(GrammaticalCategory, key) for key in self.concept_dict if key in get_args(GrammaticalCategory)
        )

    def get_uses(self) -> list[ConceptId]:
        """Retrieve the uses relationship from the concept dict."""
        uses = cast(list[ConceptId] | ConceptId, self.concept_dict.get("uses") or [])
        return uses if isinstance(uses, list) else [uses]
