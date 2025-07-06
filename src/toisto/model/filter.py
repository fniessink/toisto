"""Filter concepts."""

from argparse import ArgumentParser

from .language import Language
from .language.concept import Concept


def map_concepts_by_label(concepts: set[Concept], language: Language) -> dict[str, set[Concept]]:
    """Return the concepts mapped by label."""
    concepts_by_label: dict[str, set[Concept]] = {}
    for concept in concepts:
        labels = concept.labels(language) or concept.meanings(language)
        if labels:
            concepts_by_label.setdefault(str(labels[0].first_spelling_alternative), set()).add(concept)
    return concepts_by_label


def filter_concepts(
    concepts: set[Concept],
    selected_labels: list[str],
    language: Language,
    argument_parser: ArgumentParser,
) -> set[Concept]:
    """Filter the concepts by selected labels."""
    if not selected_labels:
        return concepts
    all_selected_concepts: set[Concept] = set()
    concepts_by_label = map_concepts_by_label(concepts, language)
    for selected_label in selected_labels:
        if selected_label not in concepts_by_label:
            argument_parser.error(f"'{selected_label}' not found\n")
        all_selected_concepts |= concepts_by_label[selected_label]
    for concept in all_selected_concepts.copy():
        all_selected_concepts |= set(concept.get_related_concepts("hyponym") + concept.get_related_concepts("meronym"))
    for concept in all_selected_concepts.copy():
        all_selected_concepts |= set(
            concept.get_related_concepts("antonym")
            + concept.get_related_concepts("hyponym")
            + concept.get_related_concepts("meronym")
            + concept.get_related_concepts("involves")
            + concept.get_related_concepts("involved_by")
        )
    for concept in all_selected_concepts.copy():
        for compound in concept.labels(language).compounds:
            all_selected_concepts |= concepts_by_label[str(compound)]
    return all_selected_concepts
