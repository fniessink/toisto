"""Filter concepts."""

from argparse import ArgumentParser

from .language import Language
from .language.concept import Concept, ConceptId


def filter_concepts(
    concepts: set[Concept],
    selected_concepts: list[ConceptId],
    language: Language,
    argument_parser: ArgumentParser,
) -> set[Concept]:
    """Filter the concepts by selected concepts."""
    if not selected_concepts:
        return concepts
    all_selected_concepts: set[Concept] = set()
    concepts_by_concept_id = {concept.concept_id: concept for concept in concepts}
    for concept_id in selected_concepts:
        if concept_id not in concepts_by_concept_id:
            argument_parser.error(f"Concept '{concept_id}' not found\n")
        all_selected_concepts.add(concepts_by_concept_id[concept_id])
    for concept in all_selected_concepts.copy():
        all_selected_concepts |= set(concept.get_related_concepts("hyponym") + concept.get_related_concepts("meronym"))
    for concept in all_selected_concepts.copy():
        all_selected_concepts |= set(
            concept.get_related_concepts("antonym")
            + concept.get_related_concepts("hyponym")
            + concept.get_related_concepts("meronym")
            + concept.get_related_concepts("involves")
            + concept.get_related_concepts("involved_by")
            + concept.compounds(language)
        )
    return all_selected_concepts
