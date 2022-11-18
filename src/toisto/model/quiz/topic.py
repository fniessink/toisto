"""Topic class."""

from dataclasses import dataclass, field
from itertools import chain

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

    def quizzes(self) -> Quizzes:
        """Return all quizzes."""
        return set(chain.from_iterable(topic.quizzes for topic in self.topics))
