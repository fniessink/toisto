"""Filter concepts."""

from argparse import ArgumentParser
from typing import NoReturn

from .language import Language
from .language.concept import Concept, ConceptId


def filter_concepts(
    concepts: set[Concept],
    selected_concepts: list[ConceptId],
    language: Language,
    argument_parser: ArgumentParser,
) -> set[Concept] | NoReturn:
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
        all_selected_concepts |= set(concept.hyponyms + concept.meronyms)
    for concept in all_selected_concepts.copy():
        all_selected_concepts |= set(
            concept.antonyms
            + concept.hyponyms
            + concept.meronyms
            + concept.involves
            + concept.involved_by
            + concept.compounds(language)
        )
    return all_selected_concepts
