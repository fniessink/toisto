"""Command to show concepts."""

from itertools import chain

from rich.table import Table

from toisto.model.language import Language
from toisto.model.language.concept import Concept
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Labels
from toisto.model.topic.topic import Topic
from toisto.ui.text import console


def enumerate_labels(labels: Labels) -> str:
    """Enumerate the labels."""
    return "\n".join(chain.from_iterable(label.spelling_alternatives for label in labels))


def topic_table(
    target_language: Language,
    source_language: Language,
    topic: Topic,
    topics: set[Topic],
    concepts: set[Concept],
) -> Table:
    """Show the concepts of the topic."""
    table = Table(title=f"Topic {topic.name}")
    target_language_name, source_language_name = ALL_LANGUAGES[target_language], ALL_LANGUAGES[source_language]
    for column in (
        target_language_name,
        source_language_name,
        "Grammatical categories",
        "Other topics",
    ):
        table.add_column(column)
    for concept in concepts:
        other_topics = ", ".join(
            sorted(t.name for t in topics if t.name != topic.name and concept.concept_id in t.concepts),
        )
        for leaf_concept in concept.leaf_concepts(target_language):
            target_labels = leaf_concept.labels(target_language)
            source_labels = leaf_concept.labels(source_language)
            table.add_row(
                enumerate_labels(target_labels),
                enumerate_labels(source_labels),
                "/".join(leaf_concept.grammatical_categories()),
                other_topics,
            )
        table.add_section()
    return table


def show_topics(
    target_language: Language,
    source_language: Language,
    topics: set[Topic],
    concepts: set[Concept],
) -> None:
    """Show the concepts by topic."""
    with console.pager():
        for topic in sorted(topics, key=lambda topic: topic.name):
            topic_concepts = {concept for concept in concepts if concept.concept_id in topic.concepts}
            if topic_concepts:
                console.print(topic_table(target_language, source_language, topic, topics, topic_concepts))
