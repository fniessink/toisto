"""Topic model."""

from dataclasses import dataclass

from ..language.concept import ConceptId


@dataclass(frozen=True)
class Topic:
    """Topic model."""

    name: str
    concepts: frozenset[ConceptId]
