"""Concept factory."""

from __future__ import annotations

from typing import cast, get_args, Literal, Union

from toisto.metadata import Language

from ..model_types import ConceptId
from .concept import Concept, CompositeConcept, LeafConcept
from .grammar import GrammaticalCategory
from .label import label_factory

ConceptRelation = Literal["uses"]
LeafConceptDict = dict[Language | ConceptRelation, str | ConceptId | list[str] | list[ConceptId]]
CompositeConceptDict = dict[GrammaticalCategory | ConceptRelation, Union["CompositeConceptDict", LeafConceptDict]]
ConceptDict = LeafConceptDict | CompositeConceptDict


def composite_concept(concept_id: ConceptId, concept_dict: CompositeConceptDict) -> CompositeConcept:
    """Create a composite concept."""
    uses = get_uses(concept_dict)
    constituent_concepts = []
    for category in get_grammatical_categories(concept_dict):
        constituent_concept_id = ConceptId(f"{concept_id}/{category}")
        constituent_concept_dict = cast(ConceptDict, concept_dict[category] | dict(uses=uses))
        constituent_concepts.append(concept_factory(constituent_concept_id, constituent_concept_dict))
    return CompositeConcept(concept_id, tuple(uses), tuple(constituent_concepts))


def leaf_concept(concept_id: ConceptId, concept_dict: LeafConceptDict) -> LeafConcept:
    """Create a leaf concept."""
    uses = get_uses(concept_dict)
    if "plural" in concept_id:
        uses.append(cast(ConceptId, concept_id.replace("plural", "singular")))
    elif "past tense" in concept_id:
        uses.append(cast(ConceptId, concept_id.replace("past tense", "present tense")))
    languages = cast(list[Language], [key for key in concept_dict if key in get_args(Language)])
    labels = {language: label_factory(cast(str | list[str], concept_dict[language])) for language in languages}
    return LeafConcept(concept_id, tuple(uses), labels)


def get_uses(concept_dict: ConceptDict) -> list[ConceptId]:
    """Retrieve the uses relationship from the concept dict."""
    uses = cast(list[ConceptId] | ConceptId, concept_dict.get("uses") or [])
    return uses if isinstance(uses, list) else [uses]


def get_grammatical_categories(concept_dict: CompositeConceptDict) -> tuple[GrammaticalCategory, ...]:
    """Retrieve the grammatical categories from the concept dict."""
    return tuple(cast(GrammaticalCategory, key) for key in concept_dict if key in get_args(GrammaticalCategory))


def concept_factory(concept_id: ConceptId, concept_dict: ConceptDict) -> Concept:
    """Create a concept from the concept dict."""
    if set(get_args(GrammaticalCategory)) & set(concept_dict):
        return composite_concept(concept_id, cast(CompositeConceptDict, concept_dict))
    return leaf_concept(concept_id, cast(LeafConceptDict, concept_dict))
