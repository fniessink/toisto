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
    concept_json: ConceptJSON
    labels_json: list[LabelJSON]

    def __post_init__(self) -> None:
        """Create the label factory."""
        self.label_factory = LabelFactory()

    def create_concept(self) -> Concept:
        """Create a concept from the concept JSON."""
        return Concept(
            self.concept_id,
            self.label_factory.create_labels(self.labels_json),
            self._related_concepts(),
            self._answer_only(),
        )

    def _related_concepts(self) -> RelatedConceptIds:
        """Create the related concepts."""
        return {relation: self._related_concept_ids(relation) for relation in get_args(ConceptRelation)}

    def _related_concept_ids(self, relation: ConceptRelation) -> ConceptIds:
        """Return the ids of the related concept(s)."""
        related = cast("ConceptIdListOrString", self.concept_json.get(relation, []))
        return tuple(related) if isinstance(related, list) else (related,)

    def _answer_only(self) -> bool:
        """Return whether the concept is answer-only."""
        return bool(self.concept_json.get("answer-only"))


def create_concept(concept_id: ConceptId, concept_json: ConceptJSON, labels_json: list[LabelJSON]) -> Concept:
    """Create a concept from the concept and labels JSON."""
    return ConceptFactory(concept_id, concept_json, labels_json).create_concept()
