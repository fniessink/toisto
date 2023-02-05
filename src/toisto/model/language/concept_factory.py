"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union, cast, get_args

from toisto.metadata import Language

from ..model_types import ConceptId
from .cefr import CommonReferenceLevel, CommonReferenceLevelSource
from .concept import Concept
from .grammar import GrammaticalCategory
from .label import label_factory

CommonReferenceLevelDict = dict[CommonReferenceLevel, CommonReferenceLevelSource | list[CommonReferenceLevelSource]]
ConceptIdListOrString = ConceptId | list[ConceptId]
ConceptIdDictOrListOrString = dict[Language, ConceptIdListOrString] | ConceptIdListOrString
MetaData = Literal["level", "uses"]
LeafConceptDict = dict[
    Language | MetaData,
    ConceptId | list[ConceptId] | ConceptIdDictOrListOrString | CommonReferenceLevelDict,
]
CompositeConceptDict = dict[
    GrammaticalCategory | MetaData,
    Union["CompositeConceptDict", LeafConceptDict, CommonReferenceLevelDict],  # noqa: UP037
]
ConceptDict = LeafConceptDict | CompositeConceptDict


@dataclass
class ConceptFactory:
    """Create concepts from the concept dict."""

    concept_id: ConceptId
    concept_dict: ConceptDict

    def create_concept(self) -> Concept:
        """Create a concept from the concept_dict."""
        return self.composite_concept() if self.get_grammatical_categories() else self.leaf_concept()

    def composite_concept(self) -> Concept:
        """Create a composite concept from a composite concept dict."""
        constituent_concepts = []
        uses = cast(CompositeConceptDict, dict(uses=self.get_uses()))
        levels = self.get_levels()
        for category in self.get_grammatical_categories():
            constituent_concept_id = ConceptId(f"{self.concept_id}/{category}")
            constituent_concept_dict = cast(CompositeConceptDict, self.concept_dict)[category] | uses
            constituent_concept_dict.setdefault("level", levels)
            concept_factory = self.__class__(constituent_concept_id, cast(ConceptDict, constituent_concept_dict))
            constituent_concepts.append(concept_factory.create_concept())
        return Concept(self.concept_id, self.get_used_concepts(), tuple(constituent_concepts), level=self.get_level())

    def leaf_concept(self) -> Concept:
        """Create a leaf concept from a leaf concept dict."""
        labels = {
            cast(Language, key): label_factory(cast(str | list[str], value))
            for key, value in self.concept_dict.items()
            if key in get_args(Language)
        }
        return Concept(self.concept_id, self.get_used_concepts(), (), labels, self.get_level())

    def get_grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        return tuple(
            cast(GrammaticalCategory, key) for key in self.concept_dict if key in get_args(GrammaticalCategory)
        )

    def get_used_concepts(self) -> dict[Language, tuple[ConceptId, ...]]:
        """Retrieve the uses relationships from the concept dict."""
        uses = self.get_uses()
        if not isinstance(uses, dict):
            uses = {language: uses for language in get_args(Language)}  # Uses are the same for all languages
        return {
            language: tuple(concept_ids) if isinstance(concept_ids, list) else (concept_ids,)
            for language, concept_ids in uses.items()
        }

    def get_uses(self) -> ConceptIdDictOrListOrString:
        """Get the uses from the concept dict."""
        return cast(ConceptIdDictOrListOrString, self.concept_dict.get("uses", {}))

    def get_levels(self) -> CommonReferenceLevelDict:
        """Get the Common Reference Levels from the concept dict."""
        return cast(CommonReferenceLevelDict, self.concept_dict.get("level", {}))

    def get_level(self) -> CommonReferenceLevel | None:
        """Determine the Common Reference Level for this concept.

        At the moment, just use the highest language level specified by the available sources.
        """
        concept_levels = [level for level in self.get_levels() if level in get_args(CommonReferenceLevel)]
        return max(concept_levels, default=None)
