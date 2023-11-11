"""Load topics concepts from topic files."""

from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn, TypedDict, cast

from ..metadata import NAME
from ..model.language.concept import ConceptId
from ..model.topic.topic import Topic
from .json_file import load_json


class TopicJSON(TypedDict):
    """Topic JSON."""

    name: str
    concepts: list[ConceptId]
    topics: list[str]


def load_topics(topic_files: list[Path], argument_parser: ArgumentParser) -> set[Topic] | NoReturn:
    """Load the topics from the specified topic files."""
    topics = set()
    try:
        for topic_file in topic_files:
            topic_json = cast(TopicJSON, load_json(topic_file))
            topics.add(
                Topic(topic_json["name"], frozenset(topic_json["concepts"]), frozenset(topic_json.get("topics", []))),
            )
    except Exception as reason:  # noqa: BLE001
        argument_parser.error(f"{NAME} cannot read topic file {topic_file}: {reason}.\n")
    return topics
