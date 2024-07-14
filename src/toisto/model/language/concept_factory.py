"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union, cast, get_args

from . import Language
from .concept import Concept, ConceptId, ConceptIds, ConceptRelation, RelatedConceptIds, RootConceptIds
from .grammar import GrammaticalCategory
from .iana_language_subtag_registry import ALL_LANGUAGES
from .label import LabelFactory, Labels, label_factory, meaning_factory

ConceptIdListOrString = ConceptId | list[ConceptId]
ConceptIdDictOrListOrString = dict[Language, ConceptIdListOrString] | ConceptIdListOrString
ConceptAttribute = Literal["antonym", "answer", "answer-only", "example", "holonym", "hypernym", "involves", "roots"]
LeafConceptDict = dict[Language | ConceptAttribute, ConceptId | list[ConceptId] | ConceptIdDictOrListOrString | bool]
CompositeConceptDict = dict[
    GrammaticalCategory | ConceptAttribute, Union["CompositeConceptDict", LeafConceptDict, bool]
]
ConceptDict = LeafConceptDict | CompositeConceptDict


@dataclass(frozen=True)
class ConceptFactory:
    """Create concepts from the concept dict."""

    concept_id: ConceptId
    concept_dict: ConceptDict

    def create_concept(self, parent: ConceptId | None = None) -> Concept:
        """Create a concept from the concept_dict."""
        return Concept(
            self.concept_id,
            parent,
            self._constituent_concepts(),
            self._labels(label_factory),
            self._labels(meaning_factory),
            self._related_concepts(),
            self._root_concepts(),
            self._answer_only(),
        )

    def _labels(self, factory: LabelFactory) -> Labels:
        """Create the labels from the concept dict, using the label factory passed."""
        return Labels(
            [
                label
                for key, value in self.concept_dict.items()
                if key in ALL_LANGUAGES
                for label in factory(cast(Language, key), cast(str | list[str], value))
            ]
        )

    def _related_concepts(self) -> RelatedConceptIds:
        """Create the related concepts."""
        return {relation: self._related_concept_ids(relation) for relation in get_args(ConceptRelation)}

    def _answer_only(self) -> bool:
        """Return whether the concept is answer-only."""
        return bool(self.concept_dict.get("answer-only"))

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
        antonym_concept_ids = self._related_concept_ids("antonym")
        antonyms_dict = dict(antonym=[ConceptId(f"{antonym}/{category}") for antonym in antonym_concept_ids])
        answer_concept_ids = self._related_concept_ids("answer")
        answers_dict = dict(answer=[ConceptId(f"{answer}/{category}") for answer in answer_concept_ids])
        roots_dict = cast(CompositeConceptDict, dict(roots=self._get_roots()))
        constituent_concept_dict = (
            cast(ConceptDict, cast(CompositeConceptDict, self.concept_dict)[category])
            | roots_dict
            | antonyms_dict
            | answers_dict
        )
        return cast(ConceptDict, constituent_concept_dict)

    def _grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        keys = self.concept_dict.keys()
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def _root_concepts(self) -> RootConceptIds:
        """Retrieve the roots from the concept dict."""
        roots = self._get_roots()
        if isinstance(roots, dict):  # Roots are not the same for all languages
            return {
                language: tuple(concept_ids) if isinstance(concept_ids, list) else (concept_ids,)
                for language, concept_ids in roots.items()
            }
        return tuple(roots) if isinstance(roots, list) else (roots,)

    def _get_roots(self) -> ConceptIdDictOrListOrString:
        """Get the roots from the concept dict."""
        return cast(ConceptIdDictOrListOrString, self.concept_dict.get("roots", {}))

    def _related_concept_ids(self, relation: ConceptAttribute) -> ConceptIds:
        """Return the ids of the related concept(s)."""
        related = cast(ConceptIdListOrString, self.concept_dict.get(relation, []))
        return tuple(related) if isinstance(related, list) else (related,)


def create_concept(concept_id: ConceptId, concept_dict: ConceptDict) -> Concept:
    """Create a concept from the concept dict."""
    return ConceptFactory(concept_id, concept_dict or cast(ConceptDict, {})).create_concept()
