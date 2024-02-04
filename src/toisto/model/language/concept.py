"""Concept classes."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import ClassVar, NewType, cast, get_args

from . import Language
from .grammar import GrammaticalCategory
from .label import Labels

ConceptId = NewType("ConceptId", str)
ConceptIds = tuple[ConceptId, ...]


@dataclass(frozen=True)
class RelatedConcepts:
    """Class representing the relations of a concept with other concepts.

    The following types of concept relations are supported:

    - Concepts can be composites, meaning they consists of subconcepts (called constituent concepts).
      For example, a noun concept may have a singular and plural form. These forms are represented as constituent
      concepts of the parent concept. The parent and constituent attributes keep track of these relations.

    - Another relation type that may exist between concepts is roots. Compound concepts such as 'blackboard'
      contain two roots, 'black' and 'board'. The concept for the compound concept refers to its roots with the
      roots attribute. The roots relation can also be used for sentences, in which case the individual words of a
      sentence are the roots.

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
    """

    _concept: ConceptId
    _parent: ConceptId | None
    _constituents: ConceptIds
    _roots: dict[Language, ConceptIds] | ConceptIds  # Tuple if all languages have the same roots
    _antonyms: ConceptIds
    _hypernyms: ConceptIds
    _holonyms: ConceptIds
    _involves: ConceptIds
    _answers: ConceptIds
    _examples: ConceptIds

    @property
    def concept(self) -> Concept:
        """Return the concept that has these relations."""
        return self._get_concepts(self._concept)[0]

    @property
    def parent(self) -> Concept | None:
        """Return the parent concept."""
        return self._get_concepts(self._parent)[0] if self._parent else None

    @property
    def constituents(self) -> Concepts:
        """Return the constituent concepts."""
        return self._get_concepts(*self._constituents)

    @property
    def antonyms(self) -> Concepts:
        """Return the antonym (opposite) concepts."""
        return self._get_concepts(*self._antonyms)

    @property
    def hypernyms(self) -> Concepts:
        """Return the hypernym concepts."""
        hypernyms = list(self._get_concepts(*self._hypernyms))
        for hypernym in hypernyms[:]:
            hypernyms.extend(hypernym.hypernyms)
        return tuple(hypernyms)

    @property
    def hyponyms(self) -> Concepts:
        """Return the hyponym concepts."""
        return tuple(concept for concept in Concept.instances.values() if self.concept in concept.hypernyms)

    @property
    def holonyms(self) -> Concepts:
        """Return the holonym concepts."""
        holonyms = list(self._get_concepts(*self._holonyms))
        for holonym in holonyms[:]:
            holonyms.extend(holonym.holonyms)
        return tuple(holonyms)

    @property
    def meronyms(self) -> Concepts:
        """Return the meronym concepts."""
        return tuple(concept for concept in Concept.instances.values() if self.concept in concept.holonyms)

    @property
    def involves(self) -> Concepts:
        """Return the involved concepts."""
        return self._get_concepts(*self._involves)

    @property
    def involved_by(self) -> Concepts:
        """Return the concepts that involve this concept."""
        return tuple(concept for concept in Concept.instances.values() if self.concept in concept.involves)

    @property
    def answers(self) -> Concepts:
        """Return the answers to the question that this concept poses."""
        return self._get_concepts(*self._answers)

    @property
    def examples(self) -> Concepts:
        """Return the examples for this concept."""
        return self._get_concepts(*self._examples)

    def roots(self, language: Language) -> Concepts:
        """Return the root concepts, for the specified language."""
        concept_ids_of_roots = self._roots.get(language, ()) if isinstance(self._roots, dict) else self._roots
        return self._get_concepts(*concept_ids_of_roots)

    def compounds(self, language: Language) -> Concepts:
        """Return the compound concepts, for the specified language."""
        return tuple(concept for concept in Concept.instances.values() if self.concept in concept.roots(language))

    def _get_concepts(self, *concept_ids: ConceptId) -> Concepts:
        """Return the concepts with the given concept ids."""
        return tuple(Concept.instances[concept_id] for concept_id in concept_ids if concept_id in Concept.instances)


@dataclass(frozen=True)
class Concept:
    """Class representing language concepts.

    A concept is either a composite or a leaf concept. Composite concepts have have two or more constituent concepts,
    representing different grammatical categories, for example singular and plural forms. Leaf concepts have labels
    in different languages.
    """

    concept_id: ConceptId
    _labels: dict[Language, Labels]
    _meanings: dict[Language, Labels]
    related_concepts: RelatedConcepts
    answer_only: bool

    instances: ClassVar[dict[ConceptId, Concept]] = {}

    def __post_init__(self) -> None:
        """Add the concept to the concept id -> concept mapping."""
        self.instances[self.concept_id] = self

    def __hash__(self) -> int:
        """Return the concept hash."""
        return hash(self.concept_id)

    def __getattr__(self, attribute: str) -> Concepts:
        """Forward properties to related concepts."""
        return getattr(self.related_concepts, attribute)

    @cached_property
    def base_concept(self) -> Concept:
        """Return the base concept of this concept."""
        return self.related_concepts.parent.base_concept if self.related_concepts.parent else self

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
            return tuple(chain.from_iterable([concept.labels(language) for concept in self.constituents]))
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
            return tuple(chain.from_iterable([concept.meanings(language) for concept in self.constituents]))
        return self._meanings.get(language, Labels())

    def grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Return the grammatical categories of this concept."""
        keys = self.concept_id.split("/")
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def is_composite(self, language: Language) -> bool:
        """Return whether this concept is composite."""
        return self._labels.get(language) is None

    def roots(self, language: Language) -> Concepts:
        """Return the roots of the concept."""
        return self.related_concepts.roots(language)

    def compounds(self, language: Language) -> Concepts:
        """Return the compounds of the concept."""
        return self.related_concepts.compounds(language)


Concepts = tuple[Concept, ...]
