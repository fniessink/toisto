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
from .label import Label, Labels

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


HomonymRegistry = Registry[Label, "Concept"]


@dataclass(frozen=True)
class Concept:
    """Class representing language concepts.

    A concept can be a composite and/or a leaf concept, or neither. Composite concepts have two or more constituent
    concepts, representing different grammatical categories, for example singular and plural forms. Leaf concepts have
    labels in one or more languages. Concepts can be constituent in one language and leaf in another concepts. For
    example, the third person singular form of English verbs has both a female ("she walks") and a male form ("he
    walks"), but Finnish does not ("hän kävelee"). This means that the third person singular female form "she walks" is
    leaf in English, but neiter leaf nor composite in Finnish, since no such label exists in Finnish.

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

    Next to the relations that are based on the meaning of the concepts, concepts can also be related via their labels:

    - The roots relation is used to capture the relation between compound labels and their roots. For example, the
      word 'blackboard' contains two roots, 'black' and 'board'. The concept with the compound label refers to its
      roots with the roots attribute. The roots relation can also be used for sentences, in which case the individual
      words of a sentence are the roots. The roots relation is transitive. The relationships can be different for
      different languages. For example, the Dutch label 'schoolbord' has different roots than the English equivalent
      'blackboard'.

    - Toisto automatically keeps track of two types of homonyms: capitonyms and homographs. Concept labels are
      capitonyms when they only differ in capitalization. Concept labels are homographs when they are written exactly
      the same.
    """

    concept_id: ConceptId
    _parent: ConceptId | None
    _constituents: ConceptIds
    _labels: Labels
    _meanings: Labels
    _related_concepts: RelatedConceptIds
    _roots: RootConceptIds
    answer_only: bool

    instances: ClassVar[Registry[ConceptId, Concept]] = Registry[ConceptId, "Concept"]()
    capitonyms: ClassVar[HomonymRegistry] = HomonymRegistry(lambda label: label.without_notes.lower_case)
    homographs: ClassVar[HomonymRegistry] = HomonymRegistry(lambda label: label.without_notes)

    def __post_init__(self) -> None:
        """Add the concept to the concept registry."""
        self.instances.add_item(self.concept_id, self)
        for label in self._labels:
            self.capitonyms.add_item(label, self)
            self.homographs.add_item(label, self)

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

    def get_homographs(self, label: Label) -> Concepts:
        """Return the homographs for the label, provided it is a label of this concept."""
        return self._get_homonyms(label, self.homographs)

    def get_capitonyms(self, label: Label) -> Concepts:
        """Return the capitonyms for the label, provided it is a label of this concept."""
        return self._get_homonyms(label, self.capitonyms)

    def _get_homonyms(self, label: Label, homonym_registry: HomonymRegistry) -> Concepts:
        """Return the homonyms for the label as registered in the given homonym registry."""
        if label not in self._labels:
            return ()
        return tuple(homonym for homonym in homonym_registry.get_values(label) if homonym != self)

    @property
    def parent(self) -> Concept | None:
        """Return the parent concept."""
        return self.instances.get_values(self._parent)[0] if self._parent else None

    @cached_property
    def base_concept(self) -> Concept:
        """Return the base concept of this concept."""
        return self.parent.base_concept if self.parent else self

    def same_base_concept(self, *concepts: Concept) -> bool:
        """Return whether the concepts have the same base concept as this concept."""
        return all(self.base_concept == concept.base_concept for concept in concepts)

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
        """Return the labels of the concept for the specified language."""
        return self.own_labels(language) or self.ancestor_labels(language) or self._constituent_labels(language)

    def own_labels(self, language: Language) -> Labels:
        """Return the labels of this concept for the specified language."""
        return self._labels.with_language(language) if self._has_own_labels_or_meanings(language) else Labels()

    def ancestor_labels(self, language: Language) -> Labels:
        """Return the labels of the first ancestor concept that has labels for the specified language."""
        if parent := self.parent:
            return parent.own_labels(language) or parent.ancestor_labels(language)
        return Labels()

    def _constituent_labels(self, language: Language) -> Labels:
        """Return the labels of the constituent concepts for the specified language."""
        return Labels(chain.from_iterable(concept.labels(language) for concept in self.constituents))

    def meanings(self, language: Language) -> Labels:
        """Return the meanings of the concept for the specified language."""
        return self.own_meanings(language) or self.ancestor_meanings(language) or self._constituent_meanings(language)

    def own_meanings(self, language: Language) -> Labels:
        """Return the meanings of this concept for the specified language."""
        return self._meanings.with_language(language) if self._has_own_labels_or_meanings(language) else Labels()

    def ancestor_meanings(self, language: Language) -> Labels:
        """Return the meanings of the first ancestor concept that has meanings for the specified language."""
        if parent := self.parent:
            return parent.own_meanings(language) or parent.ancestor_meanings(language)
        return Labels()

    def _constituent_meanings(self, language: Language) -> Labels:
        """Return the meanings of the constituent concepts for the specified language."""
        return Labels(chain.from_iterable(concept.meanings(language) for concept in self.constituents))

    @property
    def grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Return the grammatical categories of this concept."""
        keys = self.concept_id.split("/")
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def grammatical_differences(self, *concepts: Concept) -> list[GrammaticalCategory]:
        """Return the grammatical differences between this concept and the concepts.

        Precondition is that this concept and the specified concepts share the same base concept.
        """
        grammatical_differences = set()
        for index, grammatical_category in enumerate(self.grammatical_categories):
            for concept in concepts:
                if concept.grammatical_categories[index] != grammatical_category:
                    grammatical_differences.add(grammatical_category)
        return sorted(grammatical_differences)

    def is_composite(self, language: Language) -> bool:
        """Return whether this concept is a composite concept.

        A concept is composite if it has no labels or meanings and none of its ancestors has either, for the specified
        language.
        """
        return not (
            self._has_own_labels_or_meanings(language)
            or self.ancestor_labels(language)
            or self.ancestor_meanings(language)
        )

    def _has_own_labels_or_meanings(self, language: Language) -> bool:
        """Return whether this concept has its own labels or meanings for the specified language."""
        return any((self._labels + self._meanings).with_language(language))

    def compounds(self, language: Language) -> Concepts:
        """Return the compounds of the concept."""
        return tuple(concept for concept in self.instances.get_all_values() if self in concept.roots(language))

    def roots(self, language: Language) -> Concepts:
        """Return the root concepts recursively, for the specified language."""
        concept_ids_of_roots = self._roots.get(language, ()) if isinstance(self._roots, dict) else self._roots
        direct_roots = self.instances.get_values(*concept_ids_of_roots)
        return direct_roots + tuple(chain.from_iterable(root.roots(language) for root in direct_roots))


Concepts = tuple[Concept, ...]
