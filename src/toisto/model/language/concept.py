"""Concept classes."""

from __future__ import annotations

from typing import cast, get_args, Iterable

from toisto.metadata import Language

from ..model_types import ConceptId
from .grammar import GrammaticalCategory
from .label import Labels, Label


class Concept:
    """Class representing language concepts.

    A concept is either a composite or a leaf concept. Composite concepts have have two or more constituent concepts,
    representing different grammatical categories, for example singular and plural forms. Leaf concepts have labels
    in different languages.
    """

    def __init__(
        self,
        concept_id: ConceptId,
        uses: tuple[ConceptId, ...],
        constituent_concepts: tuple[Concept, ...] = (),
        labels: dict[Language, Labels] | None = None,
    ) -> None:
        self.concept_id = concept_id
        self.uses = uses
        self.constituent_concepts = constituent_concepts
        self._labels = labels or {}

    def leaf_concepts(self) -> Iterable[Concept]:
        """Return this concept's leaf concepts, or self if this concept is a leaf concept."""
        if self.constituent_concepts:
            for concept in self.constituent_concepts:
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
