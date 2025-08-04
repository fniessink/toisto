"""Concept classes."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import ClassVar, Literal, NewType, cast, get_args

from toisto.tools import Registry, first

from . import Language
from .label import Label, Labels

ConceptId = NewType("ConceptId", str)
ConceptIds = tuple[ConceptId, ...]
ConceptIdListOrString = ConceptId | list[ConceptId]
ConceptIdDictOrListOrString = dict[Language, ConceptIdListOrString] | ConceptIdListOrString

InvertedConceptRelation = Literal["hyponym", "involved_by", "meronym"]
RecursiveConceptRelation = Literal["holonym", "hypernym", "involves"]
NonInvertedConceptRelation = Literal[RecursiveConceptRelation, "antonym", "answer", "example"]
ConceptRelation = Literal[InvertedConceptRelation, NonInvertedConceptRelation]
RelatedConceptIds = dict[ConceptRelation, ConceptIds]


def inverted(relation: InvertedConceptRelation) -> ConceptRelation:
    """Return the inverted relation."""
    return cast("ConceptRelation", {"hyponym": "hypernym", "involved_by": "involves", "meronym": "holonym"}[relation])


HomonymRegistry = Registry[Label, "Concept"]


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
    capitonyms: ClassVar[HomonymRegistry] = HomonymRegistry(lambda label: label.lower_case)
    homographs: ClassVar[HomonymRegistry] = HomonymRegistry(lambda label: label)

    def __post_init__(self) -> None:
        """Add the concept to the concept registry."""
        self.instances.add_item(self.concept_id, self)
        for label in self._labels:
            self.homographs.add_item(label, self)
            if not label.is_complete_sentence:
                self.capitonyms.add_item(label, self)

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

    def get_homographs(self, label: Label) -> Concepts:
        """Return the homographs for the label, provided it is a label of this concept."""
        return self._get_homonyms(label, self.homographs)

    def get_capitonyms(self, label: Label) -> Concepts:
        """Return the capitonyms for the label, provided it is a label of this concept."""
        if self._labels.lower_case.count(label.lower_case) > 1:
            return Concepts([self])
        capitonyms = self._get_homonyms(label, self.capitonyms)
        # Weed out the homographs:
        return Concepts(concept for concept in capitonyms if label not in concept.labels(label.language))

    def _get_homonyms(self, label: Label, homonym_registry: HomonymRegistry) -> Concepts:
        """Return the homonyms for the label as registered in the given homonym registry."""
        if self._labels.count(label) > 1:
            return Concepts([self])
        if label not in self._labels:
            return Concepts()
        return Concepts(homonym for homonym in homonym_registry.get_values(label) if homonym != self)

    def labels(self, language: Language) -> Labels:
        """Return the labels of the concept for the specified language."""
        labels = Labels(label for label in self._labels if not label.meaning_only)
        return labels.with_language(language)

    def meanings(self, language: Language) -> Labels:
        """Return the meanings of the concept for the specified language."""
        return self._labels.non_colloquial.with_language(language)

    @property
    def is_complete_sentence(self) -> bool:
        """Return whether this concept is a complete sentence."""
        return first(self._labels).is_complete_sentence if self._labels else False


class Concepts(tuple[Concept, ...]):
    """Tuple of concepts."""

    __slots__ = ()

    def labels(self, language: Language) -> Labels:
        """Return the labels of the concepts."""
        return Labels(chain(*(concept.labels(language) for concept in self)))
