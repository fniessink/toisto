"""Topic class."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import chain
from typing import Iterator

from .quiz import Quizzes


@dataclass(frozen=True)
class Topic:
    """Collection of quizzes centered around a topic."""

    name: str
    quizzes: Quizzes

    def __hash__(self) -> int:
        """Return the hash of the file name."""
        return hash(self.name)


@dataclass
class Topics:
    """Collection of topics."""

    topics: set[Topic] = field(default_factory=set)

    @property
    def quizzes(self) -> Quizzes:
        """Return all quizzes."""
        return set(chain.from_iterable(topic.quizzes for topic in self.topics))

    def __iter__(self) -> Iterator[Topic]:
        """Return an iterator over self.topics."""
        return iter(self.topics)
