"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union, cast, get_args

from toisto.metadata import Language

from .cefr import CommonReferenceLevel, CommonReferenceLevelSource
from .concept import Concept, ConceptId, ConceptIds, RelatedConcepts
from .grammar import GrammaticalCategory
from .label import Labels, label_factory

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
    Union["CompositeConceptDict", LeafConceptDict, CommonReferenceLevelDict],
]
ConceptDict = LeafConceptDict | CompositeConceptDict


@dataclass
class ConceptFactory:
    """Create concepts from the concept dict."""

    concept_id: ConceptId
    concept_dict: ConceptDict

    def create_concept(self, parent: ConceptId | None = None) -> Concept:
        """Create a concept from the concept_dict."""
        return Concept(self.concept_id, self._labels(), self._level(), self._related_concepts(parent))

    def _labels(self) -> dict[Language, Labels]:
        """Return the concept labels."""
        return {
            cast(Language, key): label_factory(cast(str | list[str], value))
            for key, value in self.concept_dict.items()
            if key in get_args(Language)
        }

    def _level(self) -> CommonReferenceLevel | None:
        """Determine the Common Reference Level for this concept.

        At the moment, just use the highest language level specified by the available sources.
        """
        concept_levels = [level for level in self._get_levels() if level in get_args(CommonReferenceLevel)]
        return max(concept_levels, default=None)

    def _related_concepts(self, parent: ConceptId | None) -> RelatedConcepts:
        """Create the related concepts."""
        return RelatedConcepts(parent, self._constituent_concepts(), self._root_concepts(), self._antonym_concepts())

    def _constituent_concepts(self) -> ConceptIds:
        """Create a constituent concept for each grammatical category."""
        return tuple(self._constituent_concept(category) for category in self._grammatical_categories())

    def _constituent_concept(self, category: GrammaticalCategory) -> ConceptId:
        """Create a constituent concept for the specified grammatical category."""
        constituent_concept_id = ConceptId(f"{self.concept_id}/{category}")
        concept_factory = self.__class__(constituent_concept_id, self._constituent_concept_dict(category))
        concept_factory.create_concept(self.concept_id)
        return constituent_concept_id

    def _constituent_concept_dict(self, category: GrammaticalCategory) -> ConceptDict:
        """Create a constituent concept dict that can be used to create a constituent concept."""
        antonym_concept_ids = [ConceptId(f"{antonym}/{category}") for antonym in self._antonym_concepts()]
        antonyms_dict = dict(antonym=antonym_concept_ids)
        roots_dict = cast(CompositeConceptDict, dict(roots=self._get_roots()))
        constituent_concept_dict = cast(CompositeConceptDict, self.concept_dict)[category] | roots_dict | antonyms_dict
        constituent_concept_dict.setdefault("level", self._get_levels())
        return cast(ConceptDict, constituent_concept_dict)

    def _grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        keys = self.concept_dict.keys()
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def _root_concepts(self) -> dict[Language, ConceptIds]:
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

    def _antonym_concepts(self) -> ConceptIds:
        """Return the antonym concepts."""
        antonyms = cast(ConceptIdListOrString, self.concept_dict.get("antonym", []))
        return tuple(antonyms) if isinstance(antonyms, list) else (antonyms,)

    def _get_levels(self) -> CommonReferenceLevelDict:
        """Get the Common Reference Levels from the concept dict."""
        return cast(CommonReferenceLevelDict, self.concept_dict.get("level", {}))
