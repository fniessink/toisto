"""Topic model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, NewType

from ..language.concept import ConceptId

TopicId = NewType("TopicId", str)


@dataclass(frozen=True)
class Topic:
    """Topic model."""

    name: TopicId
    _concepts: frozenset[ConceptId] = frozenset()
    topics: frozenset[TopicId] = frozenset()

    instances: ClassVar[dict[TopicId, Topic]] = {}

    def __post_init__(self) -> None:
        """Add the topic to the topic name -> topic mapping."""
        self.instances[self.name] = self

    @property
    def concepts(self) -> frozenset[ConceptId]:
        """Return this topic's concepts."""
        concepts = set(self._concepts)
        for topic in self.topics:
            concepts |= self.instances[topic].concepts
        return frozenset(concepts)
