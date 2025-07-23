"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, cast, get_args

from .concept import Concept, ConceptId, ConceptIdListOrString, ConceptIds, ConceptRelation, RelatedConceptIds
from .label_factory import LabelFactory, LabelJSON

ConceptJSON = TypedDict(
    "ConceptJSON",
    {
        "antonym": ConceptIdListOrString,
        "answer": ConceptIdListOrString,
        "answer-only": bool,
        "example": ConceptIdListOrString,
        "holonym": ConceptIdListOrString,
        "hypernym": ConceptIdListOrString,
        "involves": ConceptIdListOrString,
    },
    total=False,
)


@dataclass()
class ConceptFactory:
    """Create concepts from the concept JSON."""

    concept_id: ConceptId
    concept_dict: ConceptJSON
    labels: list[LabelJSON]

    def __post_init__(self) -> None:
        """Create the label factory."""
        self.label_factory = LabelFactory(self.labels)

    def create_concept(self) -> Concept:
        """Create a concept from the concept_dict."""
        return Concept(
            self.concept_id,
            self.label_factory.create_labels(),
            self._related_concepts(),
            self._answer_only(),
        )

    def _related_concepts(self) -> RelatedConceptIds:
        """Create the related concepts."""
        return {relation: self._related_concept_ids(relation) for relation in get_args(ConceptRelation)}

    def _answer_only(self) -> bool:
        """Return whether the concept is answer-only."""
        return bool(self.concept_dict.get("answer-only"))

    def _related_concept_ids(self, relation: ConceptRelation) -> ConceptIds:
        """Return the ids of the related concept(s)."""
        related = cast("ConceptIdListOrString", self.concept_dict.get(relation, []))
        return tuple(related) if isinstance(related, list) else (related,)


def create_concept(concept_id: ConceptId, concept_dict: ConceptJSON, labels: list[LabelJSON]) -> Concept:
    """Create a concept from the concept dict."""
    return ConceptFactory(concept_id, concept_dict, labels).create_concept()
