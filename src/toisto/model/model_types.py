"""Model types."""

from typing import NewType


ConceptId = NewType("ConceptId", str)


def equal_or_prefix(concept_id1: ConceptId, concept_id2: ConceptId) -> bool:
    """Return True when one tuple is a prefix of the other or they are equal."""
    for element1, element2 in zip(concept_id1.split("/"), concept_id2.split("/")):
        if element1 != element2:
            return False
    return True
