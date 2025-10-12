"""Tips."""

from collections.abc import Sequence

from toisto.model.language.concept import Concept
from toisto.model.language.label import Label


def homonym_tips(concept: Concept, question: Label, *homonym_labels: Label) -> Sequence[str]:
    """Return the tip(s) to be shown as part of the question, if the question has one or more homonyms."""
    if differences := question.grammatical_differences(*homonym_labels):
        return [str(category) for category in sorted(differences)]
    language = question.language
    if hypernyms := concept.get_related_concepts("hypernym"):
        return [str(hypernym.labels(language)[0]) for hypernym in hypernyms[:1]]
    if holonyms := concept.get_related_concepts("holonym"):
        return [f"part of '{holonym.labels(language)[0]}'" for holonym in holonyms]
    if involved_concepts := concept.get_related_concepts("involves"):
        return [f"involves '{concept.labels(language)[0]}'" for concept in involved_concepts]
    return []
