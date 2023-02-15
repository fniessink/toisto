"""Concept classes."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import ClassVar, NewType, cast, get_args

from toisto.metadata import Language

from .cefr import CommonReferenceLevel
from .grammar import GrammaticalCategory
from .label import Label, Labels

ConceptId = NewType("ConceptId", str)
ConceptIds = tuple[ConceptId, ...]


@dataclass
class RelatedConcepts:
    """Class representing the relations of a concept with other concepts.

    Concepts can be composites, meaning they consists of subconcepts (called constituent concepts). For example, a noun
    concept may have a singular and plural form. These forms are represented as constituent concepts of the parent
    concept. The parent and constituent attributes keep track of these relations.

    Another relation type that may exist between concepts is roots. Compound concepts such as 'blackboard' contain two
    roots, 'black' and 'board'. The concept for the compound concept refers to its roots with the roots attribute. The
    roots relation can also be used for sentences, in which case the individual words of a sentence are the roots.

    The antonym relation is used to capture opposites. For example 'bad' has 'good' as antonym and 'good' has 'bad'
    as antonym.

    NOTE: This class keeps track of the related concepts using their concept identifier (ConceptId) and only when
    the client asks for a concept is the concept instance looked up in the concept registry (Concept.instances). This
    prevents to the need for a second pass after instantiating concepts from the topic files to create the relations.
    """

    _parent: ConceptId | None = None
    _constituents: ConceptIds = ()
    _roots: dict[Language, ConceptIds] = field(default_factory=dict)
    _antonyms: ConceptIds = ()

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

    def roots(self, language: Language) -> Concepts:
        """Return the root concepts, for the specified language."""
        return self._get_concepts(*self._roots.get(language, ()))

    def _get_concepts(self, *concept_ids: ConceptId) -> Concepts:
        """Return the concepts with the given concept ids."""
        return tuple(Concept.instances[concept_id] for concept_id in concept_ids if concept_id in Concept.instances)


@dataclass
class Concept:
    """Class representing language concepts.

    A concept is either a composite or a leaf concept. Composite concepts have have two or more constituent concepts,
    representing different grammatical categories, for example singular and plural forms. Leaf concepts have labels
    in different languages.
    """

    concept_id: ConceptId
    _labels: dict[Language, Labels] = field(default_factory=dict)
    level: CommonReferenceLevel | None = None
    related_concepts: RelatedConcepts = RelatedConcepts()

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

    @property
    def base_concept(self) -> Concept:
        """Return the base concept of this concept."""
        return self.related_concepts.parent.base_concept if self.related_concepts.parent else self

    def leaf_concepts(self) -> Iterable[Concept]:
        """Return this concept's leaf concepts, or self if this concept is a leaf concept."""
        if self.constituents:
            for concept in self.constituents:
                yield from concept.leaf_concepts()
        else:
            yield self

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


Concepts = tuple[Concept, ...]
