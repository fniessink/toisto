"""Load topics concepts from topic files."""

from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn, TypedDict, cast

from ..metadata import NAME
from ..model.language.concept import ConceptId
from ..model.topic.topic import Topic
from .identifier_registry import IdentifierRegistry
from .json_file import load_json


class TopicIdRegistry(IdentifierRegistry[str]):
    """Registry to check the uniqueness of topic identifiers across topic files."""

    def _identifier_name(self) -> str:
        return "topic"


class TopicJSON(TypedDict):
    """Topic JSON."""

    name: str
    concepts: list[ConceptId]
    topics: list[str]


def load_topics(
    topic_files: list[Path], topic_id_registry: TopicIdRegistry, argument_parser: ArgumentParser
) -> set[Topic] | NoReturn:
    """Load the topics from the specified topic files."""
    topics = set()
    try:
        for topic_file in topic_files:
            topic_json = cast(TopicJSON, load_json(topic_file))
            name = topic_json["name"]
            topic_id_registry.check_and_register_identifiers((name,), topic_file)
            topics.add(Topic(name, frozenset(topic_json["concepts"]), frozenset(topic_json.get("topics", []))))
    except Exception as reason:  # noqa: BLE001
        argument_parser.error(f"{NAME} cannot read topic file {topic_file}: {reason}.\n")
    return topics
