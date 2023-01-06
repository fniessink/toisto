"""Model types."""

from typing import NewType


ConceptId = NewType("ConceptId", str)


def parent_ids(concept_id: ConceptId) -> tuple[ConceptId, ...]:
    """return the parent ids of the concept id including the concept id itself."""
    all_concept_ids = []
    partial_id = ""
    for part in concept_id.split("/"):
        if partial_id:
            partial_id += "/"
        partial_id += part
        all_concept_ids.append(ConceptId(partial_id))
    return tuple(all_concept_ids)
