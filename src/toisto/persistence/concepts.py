"""Load concepts from topic files and generate quizzes."""

import pathlib
from argparse import ArgumentParser
from typing import NoReturn

from ..metadata import NAME, TOPIC_JSON_FILES
from ..model.language.cefr import CommonReferenceLevel
from ..model.language.concept import Concept, ConceptId, ConceptIds, Topic
from ..model.language.concept_factory import create_concept
from .json_file import load_json


def load_concepts(
    levels: list[CommonReferenceLevel],
    builtin_topics_to_load: list[Topic],
    topic_files_to_load: list[str],
    argument_parser: ArgumentParser,
) -> set[Concept] | NoReturn:
    """Load the concepts from the specified topics and with the specified levels."""
    all_concepts = set()
    topic_files: list[pathlib.Path] = []
    if builtin_topics_to_load or topic_files_to_load:
        topic_files.extend(topic for topic in TOPIC_JSON_FILES if topic.stem in builtin_topics_to_load)
        topic_files.extend(pathlib.Path(topic) for topic in topic_files_to_load)
    else:
        topic_files.extend(TOPIC_JSON_FILES)
    registry = ConceptIdRegistry(argument_parser)
    for topic_file in topic_files:
        concepts = []
        try:
            for concept_key, concept_value in load_json(topic_file).items():
                concept = create_concept(concept_key, concept_value, topics={Topic(topic_file.stem)})
                if levels and concept.level not in levels:
                    continue
                concepts.append(concept)
        except Exception as reason:  # noqa: BLE001
            argument_parser.error(f"{NAME} cannot read topic {topic_file}: {reason}.\n")
        concept_ids = tuple(concept.concept_id for concept in concepts)
        registry.check_concept_ids(concept_ids, topic_file)
        registry.register_concept_ids(concept_ids, topic_file)
        all_concepts |= set(concepts)
    return all_concepts


class ConceptIdRegistry:
    """Registry to check the uniqueness of concept identifiers across topic files."""

    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.topic_files_by_concept_id: dict[ConceptId, pathlib.Path] = {}

    def check_concept_ids(self, concept_ids: ConceptIds, topic_file: pathlib.Path) -> None:
        """Check that the concept ids are unique."""
        for concept_id in concept_ids:
            self._check_concept_id(concept_id, topic_file)

    def _check_concept_id(self, concept_id: ConceptId, topic_file: pathlib.Path) -> None:
        """Check that the concept id is unique."""
        if concept_id in self.topic_files_by_concept_id:
            other_topic_file = self.topic_files_by_concept_id[concept_id]
            self.argument_parser.error(
                f"{NAME} cannot read topic {topic_file}: concept identifier '{concept_id}' also occurs in topic "
                f"'{other_topic_file}'.\nConcept identifiers must be unique across topic files.\n",
            )

    def register_concept_ids(self, concept_ids: ConceptIds, topic_file: pathlib.Path) -> None:
        """Register the concept ids."""
        for concept_id in concept_ids:
            self.topic_files_by_concept_id[concept_id] = topic_file
