"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, cast, get_args

from .concept import Concept, ConceptId, ConceptIdListOrString, ConceptIds, ConceptRelation, RelatedConceptIds
from .grammar import GrammaticalCategory
from .label import Labels
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

    def create_concept(self, parent: ConceptId | None = None) -> Concept:
        """Create a concept from the concept_dict."""
        grammatical_categories = cast("tuple[GrammaticalCategory]", tuple(self.concept_id.split("/")[1:]))
        return Concept(
            self.concept_id,
            parent,
            self._constituent_concepts(),
            Labels(
                [
                    label
                    for label in self.label_factory.create_labels(grammatical_categories)
                    if not label.grammatical_base
                ]
            ),
            self._related_concepts(),
            self._answer_only(),
        )

    def _constituent_concepts(self) -> ConceptIds:
        """Create a constituent concept for each grammatical category."""
        return tuple(self._constituent_concept(category) for category in self._grammatical_categories())

    def _related_concepts(self) -> RelatedConceptIds:
        """Create the related concepts."""
        return {relation: self._related_concept_ids(relation) for relation in get_args(ConceptRelation)}

    def _answer_only(self) -> bool:
        """Return whether the concept is answer-only."""
        return bool(self.concept_dict.get("answer-only"))

    def _constituent_concept(self, category: GrammaticalCategory) -> ConceptId:
        """Create a constituent concept for the specified grammatical category."""
        constituent_concept_id = ConceptId(f"{self.concept_id}/{category}")
        constituent_concept_dict = self._constituent_concept_dict(category)
        constituent_concept_labels = self._constituent_concept_labels(category)
        concept_factory = self.__class__(constituent_concept_id, constituent_concept_dict, constituent_concept_labels)
        concept_factory.create_concept(self.concept_id)
        return constituent_concept_id

    def _constituent_concept_dict(self, category: GrammaticalCategory) -> ConceptJSON:
        """Create a constituent concept dict that can be used to create a constituent concept."""
        antonym_concept_ids = self._related_concept_ids("antonym")
        antonyms_dict = {"antonym": [ConceptId(f"{antonym}/{category}") for antonym in antonym_concept_ids]}
        answer_concept_ids = self._related_concept_ids("answer")
        answers_dict = {"answer": [ConceptId(f"{answer}/{category}") for answer in answer_concept_ids]}
        constituent_concept_dict = antonyms_dict | answers_dict
        return cast("ConceptJSON", constituent_concept_dict)

    def _constituent_concept_labels(self, category: GrammaticalCategory) -> list[LabelJSON]:
        """Filter the labels by grammatical category."""
        labels: list[LabelJSON] = []
        for label in self.labels:
            if isinstance(label["label"], dict) and category in label["label"]:
                sliced = LabelJSON(
                    concept=label["concept"],
                    language=label["language"],
                    label=label["label"][category],
                    note=label.get("note", []),
                    roots=label.get("roots", []),
                    tip=label.get("tip", ""),
                    colloquial=label.get("colloquial", False),
                )
                labels.append(sliced)
        return labels

    def _grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        grammatical_categories = set()
        for label in self.labels:
            if isinstance(label["label"], dict):
                grammatical_categories |= {key for key in label["label"] if key in get_args(GrammaticalCategory)}
        return tuple(category for category in get_args(GrammaticalCategory) if category in grammatical_categories)

    def _related_concept_ids(self, relation: ConceptRelation) -> ConceptIds:
        """Return the ids of the related concept(s)."""
        related = cast("ConceptIdListOrString", self.concept_dict.get(relation, []))
        return tuple(related) if isinstance(related, list) else (related,)


def create_concept(concept_id: ConceptId, concept_dict: ConceptJSON, labels: list[LabelJSON]) -> Concept:
    """Create a concept from the concept dict."""
    return ConceptFactory(concept_id, concept_dict, labels).create_concept()
