"""Filter concepts by concepts, topics, and levels."""

from argparse import ArgumentParser
from typing import NoReturn

from .language.concept import Concept, ConceptId
from .topic.topic import Topic


def filter_concepts(
    concepts: set[Concept],
    topics: set[Topic],
    selected_concepts: list[ConceptId],
    selected_topics: list[str],
    argument_parser: ArgumentParser,
) -> set[Concept] | NoReturn:
    """Filter the concepts by selected concepts, levels, and topics."""
    if selected_concepts:
        concepts = {concept for concept in concepts if concept.concept_id in selected_concepts}
    if selected_topics:
        concept_ids: set[ConceptId] = set()
        for topic in topics:
            if topic.name in selected_topics:
                concept_ids |= topic.concepts
        concepts = {concept for concept in concepts if concept.concept_id in concept_ids}
    if (selected_concepts or selected_topics) and not concepts:
        argument_parser.error("No concepts found that match your selection criteria\n")
    return concepts
