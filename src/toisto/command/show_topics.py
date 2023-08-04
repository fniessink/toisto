"""Command to show concepts."""

from itertools import chain

from rich.table import Table

from toisto.model.language import Language
from toisto.model.language.concept import Concept, Topic, topics
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Labels
from toisto.ui.text import console


def enumerate_labels(labels: Labels) -> str:
    """Enumerate the labels."""
    return "\n".join(chain.from_iterable(label.spelling_alternatives for label in labels))


def topic_table(target_language: Language, source_language: Language, topic: Topic, concepts: set[Concept]) -> Table:
    """Show the concepts of the topic."""
    table = Table(title=f"Topic {topic}")
    target_language_name, source_language_name = ALL_LANGUAGES[target_language], ALL_LANGUAGES[source_language]
    for column in (
        target_language_name,
        source_language_name,
        "Grammatical categories",
        "Language level",
        "Other topics",
    ):
        table.add_column(column)
    for concept in concepts:
        for leaf_concept in concept.leaf_concepts(target_language):
            target_labels = leaf_concept.labels(target_language)
            source_labels = leaf_concept.labels(source_language)
            table.add_row(
                enumerate_labels(target_labels),
                enumerate_labels(source_labels),
                "/".join(leaf_concept.grammatical_categories()),
                leaf_concept.level,
                ", ".join(sorted(other_topic for other_topic in leaf_concept.topics if other_topic != topic)),
            )
        table.add_section()
    return table


def show_topics(target_language: Language, source_language: Language, concepts: set[Concept]) -> None:
    """Show the concepts by topic."""
    with console.pager():
        for topic in topics(concepts):
            topic_concepts = {concept for concept in concepts if topic in concept.topics}
            console.print(topic_table(target_language, source_language, topic, topic_concepts))
