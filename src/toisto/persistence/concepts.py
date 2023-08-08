"""Load concepts from topic files and generate quizzes."""

from argparse import ArgumentParser
from pathlib import Path
from typing import NoReturn

from ..metadata import NAME
from ..model.language.concept import Concept, ConceptId, ConceptIds
from ..model.language.concept_factory import Topic, create_concept
from .json_file import load_json


class ConceptIdRegistry:
    """Registry to check the uniqueness of concept identifiers across topic files."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.topic_files_by_concept_id: dict[ConceptId, Path] = {}

    def check_concept_ids(self, concept_ids: ConceptIds, topic_file: Path) -> None:
        """Check that the concept ids are unique."""
        for concept_id in concept_ids:
            self._check_concept_id(concept_id, topic_file)

    def _check_concept_id(self, concept_id: ConceptId, topic_file: Path) -> None:
        """Check that the concept id is unique."""
        if concept_id in self.topic_files_by_concept_id:
            other_topic_file = self.topic_files_by_concept_id[concept_id]
            self.argument_parser.error(
                f"{NAME} cannot read topic file {topic_file}: concept identifier '{concept_id}' also occurs in topic "
                f"file {other_topic_file}.\nConcept identifiers must be unique across topic files.\n",
            )

    def register_concept_ids(self, concept_ids: ConceptIds, topic_file: Path) -> None:
        """Register the concept ids."""
        for concept_id in concept_ids:
            self.topic_files_by_concept_id[concept_id] = topic_file


def load_concepts(
    topic_files: list[Path],
    concept_id_registry: ConceptIdRegistry,
    argument_parser: ArgumentParser,
) -> set[Concept] | NoReturn:
    """Load the concepts from the specified topics and with the specified levels."""
    all_concepts = set()
    for topic_file in topic_files:
        concepts = []
        try:
            for concept_key, concept_value in load_json(topic_file).items():
                concept = create_concept(concept_key, concept_value, Topic(topic_file.stem))
                concepts.append(concept)
        except Exception as reason:  # noqa: BLE001
            argument_parser.error(f"{NAME} cannot read topic file {topic_file}: {reason}.\n")
        concept_ids = tuple(concept.concept_id for concept in concepts)
        concept_id_registry.check_concept_ids(concept_ids, topic_file)
        concept_id_registry.register_concept_ids(concept_ids, topic_file)
        all_concepts |= set(concepts)
    return all_concepts
