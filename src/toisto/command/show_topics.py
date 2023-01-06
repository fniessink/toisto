"""Command to show concepts."""

from itertools import chain

from rich.table import Table

from toisto.metadata import Language, SUPPORTED_LANGUAGES
from toisto.model import Labels, Topic, Topics
from toisto.ui.text import console


def enumerate_labels(labels: Labels) -> str:
    """Enumerate the labels."""
    return "\n".join(chain.from_iterable(label.spelling_alternatives for label in labels))


def topic_table(language: Language, source_language: Language, topic: Topic) -> Table:
    """Show the concepts of the topic."""
    table = Table(title=f"Topic {topic.name}")
    table.add_column(SUPPORTED_LANGUAGES[language])
    table.add_column(SUPPORTED_LANGUAGES[source_language])
    table.add_column("Grammatical categories")
    for concept in topic.concepts:
        for leaf_concept in concept.leaf_concepts():
            table.add_row(
                enumerate_labels(leaf_concept.labels(language)),
                enumerate_labels(leaf_concept.labels(source_language)),
                "/".join(leaf_concept.grammatical_categories()),
            )
        table.add_section()
    return table


def show_topics(language: Language, source_language: Language, topics: Topics) -> None:
    """Show the concepts of the topics."""
    with console.pager():
        for topic in topics:
            console.print(topic_table(language, source_language, topic))
