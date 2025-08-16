"""Concept classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal, NewType, cast, get_args

from toisto.tools import Registry, first

from . import Language
from .label import Labels

ConceptId = NewType("ConceptId", str)
ConceptIds = tuple[ConceptId, ...]
ConceptIdListOrString = ConceptId | list[ConceptId]

InvertedConceptRelation = Literal["hyponym", "involved_by", "meronym"]
RecursiveConceptRelation = Literal["holonym", "hypernym", "involves"]
NonInvertedConceptRelation = Literal[RecursiveConceptRelation, "antonym", "answer", "example"]
ConceptRelation = Literal[InvertedConceptRelation, NonInvertedConceptRelation]
RelatedConceptIds = dict[ConceptRelation, ConceptIds]


def inverted(relation: InvertedConceptRelation) -> ConceptRelation:
    """Return the inverted relation."""
    return cast("ConceptRelation", {"hyponym": "hypernym", "involved_by": "involves", "meronym": "holonym"}[relation])


@dataclass(frozen=True)
class Concept:
    """Class representing language concepts.

    Concepts can have the following types of relations to other concepts:

    - The antonym relation is used to capture opposites. For example 'bad' has 'good' as antonym and 'good' has 'bad'
      as antonym.

    - The hypernym relation is used to capture "is a (kind of)" relations. Y is a hypernym of X if every X is a
      (kind of) Y. For example, canine is a hypernym of dog. The hypernym relation is transitive.

    - The holonym relation is used to capture "part of" relations. Y is a holonym of X if X is a part of Y.
      For example, sentences are holonym of words. The holonym relation is transitive.

    - The involves relation is used to link verbs with nouns.

    - The answer relation is used to specify possible answers to questions. Using the answer relation it is possible to
      specify that, for example, 'Do you like ice cream?' has the yes and no concepts as possible answers.

    - The examples relation is used to specify other concepts that exemplify the concept.

    NOTE: This class keeps track of the related concepts using their concept identifier (ConceptId) and only when
    the client asks for a concept is the concept instance looked up in the concept registry (Concept.instances). This
    prevents the need for a second pass after instantiating concepts from the concept files to create the relations.

    Next to the relations that are based on the meaning of the concepts, concepts can also be related via their labels.
    Toisto automatically keeps track of two types of homonyms: capitonyms and homographs. Concept labels are capitonyms
    when they only differ in capitalization. Concept labels are homographs when they are written exactly the same.
    """

    concept_id: ConceptId
    _labels: Labels
    _related_concepts: RelatedConceptIds
    answer_only: bool

    instances: ClassVar[Registry[ConceptId, Concept]] = Registry[ConceptId, "Concept"]()

    def __post_init__(self) -> None:
        """Add the concept to the concept registry."""
        self.instances.add_item(self.concept_id, self)

    def __hash__(self) -> int:
        """Return the concept hash."""
        return hash(self.concept_id)

    def get_related_concepts(self, relation: ConceptRelation, *visited_concepts: Concept) -> Concepts:
        """Return the related concepts."""
        if self in visited_concepts:
            return Concepts()  # Prevent recursion error
        if relation in get_args(InvertedConceptRelation):
            inverted_relation = inverted(cast("InvertedConceptRelation", relation))
            return Concepts(
                concept
                for concept in Concepts(self.instances.get_all_values())
                if self in concept.get_related_concepts(inverted_relation, self, *visited_concepts)
            )
        related_concepts = Concepts(self.instances.get_values(*self._related_concepts.get(relation, [])))
        if relation not in get_args(RecursiveConceptRelation):
            return related_concepts
        related_concepts_list = list(related_concepts)
        for concept in related_concepts:
            related_concepts_list.extend(concept.get_related_concepts(relation, self, *visited_concepts))
        return Concepts(related_concepts_list)

    def labels(self, language: Language) -> Labels:
        """Return the labels of the concept for the specified language."""
        return self._labels.with_language(language).not_meaning_only

    def meanings(self, language: Language) -> Labels:
        """Return the meanings of the concept for the specified language."""
        return self._labels.with_language(language).non_colloquial

    @property
    def is_complete_sentence(self) -> bool:
        """Return whether this concept is a complete sentence."""
        return first(self._labels).is_complete_sentence if self._labels else False


Concepts = tuple[Concept, ...]
