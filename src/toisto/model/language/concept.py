"""Concept classes."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import ClassVar, Literal, NewType, cast, get_args

from ...tools import Registry
from . import Language
from .grammar import GrammaticalCategory
from .label import Labels

ConceptId = NewType("ConceptId", str)
ConceptIds = tuple[ConceptId, ...]
InvertedConceptRelation = Literal["hyponym", "involved_by", "meronym"]
RecursiveConceptRelation = Literal["holonym", "hypernym", "involves"]
NonInvertedConceptRelation = Literal[RecursiveConceptRelation, "antonym", "answer", "example"]
ConceptRelation = Literal[InvertedConceptRelation, NonInvertedConceptRelation]
RelatedConceptIds = dict[ConceptRelation, ConceptIds]
RootConceptIds = dict[Language, ConceptIds] | ConceptIds  # Tuple if all languages have the same roots


def inverted(relation: InvertedConceptRelation) -> ConceptRelation:
    """Return the inverted relation."""
    return cast(ConceptRelation, {"hyponym": "hypernym", "involved_by": "involves", "meronym": "holonym"}[relation])


@dataclass(frozen=True)
class Concept:
    """Class representing language concepts.

    A concept is either a composite or a leaf concept. Composite concepts have two or more constituent concepts,
    representing different grammatical categories, for example singular and plural forms. Leaf concepts have labels
    in different languages.

    Concepts can have following types of relations to other concepts:

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

    - The roots relation is used to capture the relation between compound concepts and their roots. For example,
      the word 'blackboard' contains two roots, 'black' and 'board'. The concept for the compound concept refers to its
      roots with the roots attribute. The roots relation can also be used for sentences, in which case the individual
      words of a sentence are the roots. The roots relation is transitive.

      Note that this relationship is different from the other types of concept relations because the roots relationship
      is based on the label of the concept. It also means that the relationships can be different for different
      languages. For example, the Dutch label 'schoolbord' has different roots than the English equivalent 'blackboard'.

    NOTE: This class keeps track of the related concepts using their concept identifier (ConceptId) and only when
    the client asks for a concept is the concept instance looked up in the concept registry (Concept.instances). This
    prevents the need for a second pass after instantiating concepts from the concept files to create the relations.
    """

    concept_id: ConceptId
    _parent: ConceptId | None
    _constituents: ConceptIds
    _labels: dict[Language, Labels]
    _meanings: dict[Language, Labels]
    _related_concepts: RelatedConceptIds
    _roots: RootConceptIds
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
            return ()  # Prevent recursion error
        if relation in get_args(InvertedConceptRelation):
            inverted_relation = inverted(cast(InvertedConceptRelation, relation))
            return tuple(
                concept
                for concept in self.instances.get_all_values()
                if self in concept.get_related_concepts(inverted_relation, self, *visited_concepts)
            )
        related_concepts = self.instances.get_values(*self._related_concepts[relation])
        if relation not in get_args(RecursiveConceptRelation):
            return related_concepts
        related_concepts_list = list(related_concepts)
        for concept in related_concepts:
            related_concepts_list.extend(concept.get_related_concepts(relation, self, *visited_concepts))
        return tuple(related_concepts_list)

    @property
    def parent(self) -> Concept | None:
        """Return the parent concept."""
        return self.instances.get_values(self._parent)[0] if self._parent else None

    @cached_property
    def base_concept(self) -> Concept:
        """Return the base concept of this concept."""
        return self.parent.base_concept if self.parent else self

    @property
    def constituents(self) -> Concepts:
        """Return the constituent concepts."""
        return self.instances.get_values(*self._constituents)

    def leaf_concepts(self, language: Language) -> Generator[Concept, None, None]:
        """Return this concept's leaf concepts, or self if this concept is a leaf concept."""
        if self.is_composite(language):
            for concept in self.constituents:
                yield from concept.leaf_concepts(language)
        else:
            yield self

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        if self.is_composite(language):
            return tuple(chain.from_iterable(concept.labels(language) for concept in self.constituents))
        return self._labels.get(language, Labels())

    def colloquial_labels(self, language: Language) -> Labels:
        """Return the colloquial labels for the language."""
        return Labels(label for label in self.labels(language) if label.is_colloquial)

    def non_colloquial_labels(self, language: Language) -> Labels:
        """Return the non-colloquial labels for the language."""
        return Labels(label for label in self.labels(language) if not label.is_colloquial)

    def meanings(self, language: Language) -> Labels:
        """Return the meanings of the concept in the specified language."""
        if self.is_composite(language):
            return tuple(chain.from_iterable(concept.meanings(language) for concept in self.constituents))
        return self._meanings.get(language, Labels())

    def grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Return the grammatical categories of this concept."""
        keys = self.concept_id.split("/")
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def is_composite(self, language: Language) -> bool:
        """Return whether this concept is composite."""
        return self._labels.get(language) is None

    def compounds(self, language: Language) -> Concepts:
        """Return the compounds of the concept."""
        return tuple(concept for concept in self.instances.get_all_values() if self in concept.roots(language))

    def roots(self, language: Language) -> Concepts:
        """Return the root concepts recursively, for the specified language."""
        concept_ids_of_roots = self._roots.get(language, ()) if isinstance(self._roots, dict) else self._roots
        direct_roots = self.instances.get_values(*concept_ids_of_roots)
        return direct_roots + tuple(chain.from_iterable(root.roots(language) for root in direct_roots))


Concepts = tuple[Concept, ...]
