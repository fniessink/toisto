"""Translating labels."""

from . import Language
from .concept import Concept
from .label import Label, Labels


def meanings(source_label: Label, target_language: Language) -> Labels:
    """Return the meanings of the source label in the target language."""
    source_language = source_label.language
    return Labels(
        [
            meaning
            for concept in Concept.instances.get_all_values()
            for label in concept.labels(source_language).matching(source_label)
            for meaning in concept.meanings(target_language).with_same_grammatical_categories_as(label)
        ]
    )
