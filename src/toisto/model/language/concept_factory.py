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
MetaData = Literal["level", "antonym", "roots"]
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

    def create_concept(self, parent_concept_id: ConceptId | None = None) -> Concept:
        """Create a concept from the concept_dict."""
        if self._get_grammatical_categories():
            return self._create_composite_concept(parent_concept_id)
        return self._create_leaf_concept(parent_concept_id)

    def _create_composite_concept(self, parent_concept_id: ConceptId | None = None) -> Concept:
        """Create a composite concept from a composite concept dict."""
        constituent_concept_ids = []
        roots_dict = cast(CompositeConceptDict, dict(roots=self._get_roots()))
        antonyms = self._get_antonym_concepts()
        levels = self._get_levels()
        for category in self._get_grammatical_categories():
            constituent_concept_id = ConceptId(f"{self.concept_id}/{category}")
            constituent_concept_ids.append(constituent_concept_id)
            antonym_concept_ids = [ConceptId(f"{antonym}/{category}") for antonym in antonyms]
            antonyms_dict = dict(antonym=antonym_concept_ids)
            constituent_concept_dict = (
                cast(CompositeConceptDict, self.concept_dict)[category] | roots_dict | antonyms_dict
            )
            constituent_concept_dict.setdefault("level", levels)
            concept_factory = self.__class__(constituent_concept_id, cast(ConceptDict, constituent_concept_dict))
            concept_factory.create_concept(self.concept_id)
        return Concept(
            self.concept_id,
            parent_concept_id,
            tuple(constituent_concept_ids),
            self._get_root_concepts(),
            self._get_antonym_concepts(),
            level=self._get_level(),
        )

    def _create_leaf_concept(self, parent_concept_id: ConceptId | None = None) -> Concept:
        """Create a leaf concept from a leaf concept dict."""
        labels = {
            cast(Language, key): label_factory(cast(str | list[str], value))
            for key, value in self.concept_dict.items()
            if key in get_args(Language)
        }
        return Concept(
            self.concept_id,
            parent_concept_id,
            (),
            self._get_root_concepts(),
            self._get_antonym_concepts(),
            labels,
            self._get_level(),
        )

    def _get_grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        return tuple(
            cast(GrammaticalCategory, key) for key in self.concept_dict if key in get_args(GrammaticalCategory)
        )

    def _get_root_concepts(self) -> dict[Language, tuple[ConceptId, ...]]:
        """Retrieve the roots from the concept dict."""
        roots = self._get_roots()
        if not isinstance(roots, dict):
            roots = {language: roots for language in get_args(Language)}  # Roots are the same for all languages
        return {
            language: tuple(concept_ids) if isinstance(concept_ids, list) else (concept_ids,)
            for language, concept_ids in roots.items()
        }

    def _get_roots(self) -> ConceptIdDictOrListOrString:
        """Get the roots from the concept dict."""
        return cast(ConceptIdDictOrListOrString, self.concept_dict.get("roots", {}))

    def _get_antonym_concepts(self) -> tuple[ConceptId, ...]:
        """Return the antonym concepts."""
        antonyms = self._get_antonyms()
        return tuple(antonyms) if isinstance(antonyms, list) else (antonyms,)

    def _get_antonyms(self) -> ConceptIdListOrString:
        """Get the antonyms from the concept dict."""
        return cast(ConceptIdListOrString, self.concept_dict.get("antonym", []))

    def _get_levels(self) -> CommonReferenceLevelDict:
        """Get the Common Reference Levels from the concept dict."""
        return cast(CommonReferenceLevelDict, self.concept_dict.get("level", {}))

    def _get_level(self) -> CommonReferenceLevel | None:
        """Determine the Common Reference Level for this concept.

        At the moment, just use the highest language level specified by the available sources.
        """
        concept_levels = [level for level in self._get_levels() if level in get_args(CommonReferenceLevel)]
        return max(concept_levels, default=None)
