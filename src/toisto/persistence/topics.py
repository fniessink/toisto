"""Load topics concepts from topic files."""

from argparse import ArgumentParser
from collections.abc import Collection
from typing import NoReturn, TypedDict, cast

from ..metadata import TOPIC_FILES
from ..model.language.concept import ConceptId
from ..model.topic.topic import Topic, TopicId
from .loader import Loader


class TopicJSON(TypedDict):
    """Topic JSON."""

    name: TopicId
    concepts: list[ConceptId]
    topics: list[TopicId]


class TopicLoader(Loader[TopicId, Topic]):
    """Class to load topics."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        super().__init__("topic", TOPIC_FILES, argument_parser)

    def _parse_json(self, json: dict) -> set[Topic] | NoReturn:
        """Parse the topics from the loaded JSON."""
        topic_json = cast(TopicJSON, json)
        return {Topic(topic_json["name"], frozenset(topic_json["concepts"]), frozenset(topic_json.get("topics", [])))}

    def _identifiers(self, domain_objects: Collection[Topic]) -> tuple[TopicId, ...]:
        """Return the identifiers of the topics."""
        return tuple(topic.name for topic in domain_objects)
