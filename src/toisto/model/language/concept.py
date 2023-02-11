"""Concept classes."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import permutations
from typing import ClassVar, cast, get_args

from toisto.metadata import Language
from toisto.tools import zip_and_cycle

from ..model_types import ConceptId
from .cefr import CommonReferenceLevel
from .grammar import GrammaticalCategory
from .label import Label, Labels


@dataclass
class Concept:
    """Class representing language concepts.

    A concept is either a composite or a leaf concept. Composite concepts have have two or more constituent concepts,
    representing different grammatical categories, for example singular and plural forms. Leaf concepts have labels
    in different languages.
    """

    concept_id: ConceptId
    _parent_concept: ConceptId | None = None
    _constituent_concepts: tuple[ConceptId, ...] = ()
    _root_concepts: dict[Language, tuple[ConceptId, ...]] = field(default_factory=dict)
    _antonym_concepts: tuple[ConceptId, ...] = ()
    _labels: dict[Language, Labels] = field(default_factory=dict)
    level: CommonReferenceLevel | None = None

    instances: ClassVar[dict[ConceptId, Concept]] = {}

    def __post_init__(self) -> None:
        """Add the concept to the concept id -> concept mapping."""
        self.instances[self.concept_id] = self

    def __hash__(self) -> int:
        """Return the concept hash."""
        return hash(self.concept_id)

    def leaf_concepts(self) -> Iterable[Concept]:
        """Return this concept's leaf concepts, or self if this concept is a leaf concept."""
        if self.constituent_concepts:
            for concept in self.constituent_concepts:
                yield from concept.leaf_concepts()
        else:
            yield self

    def paired_leaf_concepts(self) -> Iterable[tuple[Concept, Concept]]:
        """Pair the leaf concepts from the constituent concepts."""
        for concept_group in zip_and_cycle(*[list(concept.leaf_concepts()) for concept in self.constituent_concepts]):
            for permutation in permutations(concept_group, r=2):
                yield cast(tuple[Concept, Concept], permutation)

    @property
    def constituent_concepts(self) -> tuple[Concept, ...]:
        """Return the constituent concepts of this concept."""
        return self._get_concepts(self._constituent_concepts)

    @property
    def base_concept(self) -> Concept:
        """Return the base concept of this concept."""
        return self.instances[self._parent_concept].base_concept if self._parent_concept in self.instances else self

    def root_concepts(self, language: Language) -> tuple[Concept, ...]:
        """Return the root concepts of this compound concept, for the specified language."""
        return self._get_concepts(self._root_concepts.get(language, ()))

    @property
    def antonym_concepts(self) -> tuple[Concept, ...]:
        """Return the antonym concepts of this concept."""
        return self._get_concepts(self._antonym_concepts)

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        return self._labels.get(language, Labels())

    def meanings(self, language: Language) -> Labels:
        """Return the meaning of the concept in the specified language."""
        meaning = Label(self._labels.get(language, [""])[0])
        return (meaning,) if meaning else ()

    def grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Return the grammatical categories of this concept."""
        keys = self.concept_id.split("/")
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def _get_concepts(self, concept_ids: tuple[ConceptId, ...]) -> tuple[Concept, ...]:
        """Return the concepts with the given concept ids."""
        return tuple(self.instances[concept_id] for concept_id in concept_ids if concept_id in self.instances)
