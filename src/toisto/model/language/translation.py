"""Translating labels."""

from toisto.tools import unique

from . import Language
from .concept import Concept
from .label import Labels


def meanings(source_text: str, source_language: Language, target_language: Language) -> Labels:
    """Return the meanings of the source text in the target language."""
    return Labels(
        unique(
            meaning
            for concept in Concept.instances.get_all_values()
            for label in concept.labels(source_language).matching(source_text)
            for meaning in concept.meanings(target_language).with_same_grammatical_categories_as(label)
        )
    )
