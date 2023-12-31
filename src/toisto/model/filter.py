"""Filter concepts by concepts, topics, and levels."""

from argparse import ArgumentParser
from typing import NoReturn

from .language.concept import Concept, ConceptId
from .topic.topic import Topic, TopicId


def filter_concepts(
    concepts: set[Concept],
    topics: set[Topic],
    selected_concepts: list[ConceptId],
    selected_topics: list[TopicId],
    argument_parser: ArgumentParser,
) -> set[Concept] | NoReturn:
    """Filter the concepts by selected concepts or selected topics."""
    all_selected_concepts: set[Concept] = set()
    if selected_concepts:
        concepts_by_concept_id = {concept.concept_id: concept for concept in concepts}
        for concept_id in selected_concepts:
            if concept_id not in concepts_by_concept_id:
                argument_parser.error(f"Concept '{concept_id}' not found\n")
            all_selected_concepts.add(concepts_by_concept_id[concept_id])
        return all_selected_concepts
    if selected_topics:
        topics_by_name = {topic.name: topic for topic in topics}
        for topic_name in selected_topics:
            if topic_name not in topics_by_name:
                argument_parser.error(f"Topic '{topic_name}' not found\n")
            topic_concepts = {
                concept for concept in concepts if concept.concept_id in topics_by_name[topic_name].concepts
            }
            if not topic_concepts:
                argument_parser.error(f"No concepts with topic '{topic_name}' found\n")
            all_selected_concepts |= topic_concepts
        return all_selected_concepts
    return concepts
