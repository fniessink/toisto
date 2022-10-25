"""Concept classes."""

from dataclasses import dataclass
from typing import cast, Literal

from toisto.metadata import Language

from .label import Labels
from .quiz import Quiz


ConceptDict = dict[Language, str | list[str]]
NounType = Literal["plural", "singular"]
NounConceptDict = dict[NounType, ConceptDict]


@dataclass
class Concept:
    """Class representing a concept from a topic."""

    _labels: dict[Language, Labels]

    def quizzes(self, language: Language, source_language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the concept and its labels."""
        return (
            [Quiz(language, source_language, label, self.labels(source_language)) for label in self.labels(language)] +
            [Quiz(source_language, language, label, self.labels(language)) for label in self.labels(source_language)]
        ) if self.has_labels(language, source_language) else []

    def has_labels(self, *languages: Language) -> bool:
        """Return whether the concept has labels for all the specified languages."""
        return all(language in self._labels for language in languages)

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        return self._labels[language]

    @classmethod
    def from_dict(cls, concept_dict: ConceptDict) -> "Concept":
        """Instantiate a concept from a dict."""
        return cls(
            {
                language: cast(Labels, (label if isinstance(label, list) else [label]))
                for language, label in concept_dict.items()
            }
        )


@dataclass
class NounConcept:
    """A concept that is a noun with a singular and plural grammatical number.

    See https://en.wikipedia.org/wiki/Grammatical_number.
    """

    singular: Concept
    plural: Concept

    def quizzes(self, language: Language, source_language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the concept."""
        result = []
        for concept in self.singular, self.plural:
            if concept.has_labels(language, source_language):
                result.extend(concept.quizzes(language, source_language))
        if self.singular.has_labels(language) and self.plural.has_labels(language):
            singular_labels, plural_labels = self.singular.labels(language), self.plural.labels(language)
            result.extend([Quiz(language, language, label, plural_labels, "pluralize") for label in singular_labels])
            result.extend([Quiz(language, language, label, singular_labels, "singularize") for label in plural_labels])
        return result

    @classmethod
    def from_dict(cls, concept_dict: NounConceptDict) -> "NounConcept":
        """Instantiate a concept from a dict."""
        singular = Concept.from_dict(concept_dict["singular"])
        plural = Concept.from_dict(concept_dict["plural"])
        return cls(singular, plural)


def concept_factory(concept_dict: ConceptDict | NounConceptDict) -> Concept | NounConcept:
    """Create a concept from the concept dict."""
    if "singular" in concept_dict and "plural" in concept_dict:
        return NounConcept.from_dict(cast(NounConceptDict, concept_dict))
    return Concept.from_dict(cast(ConceptDict, concept_dict))
