"""Loader."""

from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn, TypedDict

from ..metadata import CONCEPT_JSON_FILES, NAME, TOPIC_FILES
from ..model.language.concept import Concept, ConceptId
from ..model.language.concept_factory import ConceptDict, create_concept
from ..model.topic.topic import Topic, TopicId
from .identifier_registry import IdentifierRegistry
from .json_file import load_json


class TopicJSON(TypedDict):
    """Topic JSON."""

    concepts: list[ConceptId]
    topics: list[TopicId]


class Loader:
    """Concept and topic loader."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.concept_id_registry = IdentifierRegistry[ConceptId]("concept", argument_parser)
        self.topic_id_registry = IdentifierRegistry[TopicId]("topic", argument_parser)
        self.builtin_files = CONCEPT_JSON_FILES + TOPIC_FILES

    def load(self, files: list[Path] | None = None) -> tuple[set[Concept], set[Topic]] | NoReturn:
        """Load the domain objects from the files."""
        all_concepts = set()
        all_topics = set()
        try:
            for file_path in self.builtin_files if files is None else files:
                concepts, topics = self._parse_json(load_json(file_path))
                self.concept_id_registry.check_and_register_identifiers(self._concept_identifiers(concepts), file_path)
                self.topic_id_registry.check_and_register_identifiers(self._topic_identifiers(topics), file_path)
                all_concepts |= concepts
                all_topics |= topics
        except Exception as reason:  # noqa: BLE001
            self.argument_parser.error(f"{NAME} cannot read file {file_path}: {reason}.\n")
        return all_concepts, all_topics

    def _parse_json(self, json: dict) -> tuple[set[Concept], set[Topic]]:
        """Parse the domain objects from the JSON loaded from the domain object file."""
        return self._create_concepts(json.get("concepts", {})), self._create_topics(json.get("topics", {}))

    def _create_concepts(self, concept_dict: dict[ConceptId, ConceptDict]) -> set[Concept]:
        """Parse the concepts from the JSON."""
        return {create_concept(concept_key, concept_value) for concept_key, concept_value in concept_dict.items()}

    def _create_topics(self, topic_dict: dict[TopicId, TopicJSON]) -> set[Topic]:
        """Parse the topics from the JSON."""
        return {self._create_topic(topic_key, topic_value) for topic_key, topic_value in topic_dict.items()}

    def _create_topic(self, topic_identifier: TopicId, topic_json: TopicJSON) -> Topic:
        """Create a topic from the JSON-object."""
        concepts = topic_json.get("concepts", [])
        subtopics = topic_json.get("topics", [])
        return Topic(topic_identifier, frozenset(concepts), frozenset(subtopics))

    def _concept_identifiers(self, concepts: set[Concept]) -> tuple[ConceptId, ...]:
        """Return the identifiers of the concepts."""
        return tuple(concept.concept_id for concept in concepts)

    def _topic_identifiers(self, topics: set[Topic]) -> tuple[TopicId, ...]:
        """Return the identifiers of the topics."""
        return tuple(topic.name for topic in topics)
