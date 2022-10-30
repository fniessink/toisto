"""Concept classes."""

from __future__ import annotations

from itertools import permutations
from typing import Iterable, cast, Sequence

from toisto.metadata import Language

from .label import Labels
from .quiz import Quiz, QuizType, quiz_factory


ConceptDict = dict[Language, str | list[str]]


class Concept:
    """Class representing a concept from a topic."""

    def __init__(self, labels: dict[Language, Labels]) -> None:
        self._labels = labels

    def quizzes(self, language: Language, source_language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the concept and its labels."""
        return (
            quiz_factory(language, source_language, self.labels(language), self.labels(source_language))
        ) if self.has_labels(language, source_language) else []

    def has_labels(self, *languages: Language) -> bool:
        """Return whether the concept has labels for all the specified languages."""
        return all(language in self._labels for language in languages)

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        return self._labels[language]

    def leaf_concepts(self) -> Iterable[Concept]:
        """Return self as a list of leaf concepts."""
        return [self]

    @classmethod
    def from_dict(cls, concept_dict: ConceptDict) -> Concept:
        """Instantiate a concept from a dict."""
        return cls(
            {
                language: cast(Labels, (label if isinstance(label, list) else [label]))
                for language, label in concept_dict.items()
            }
        )


ConceptPair = tuple[Concept, Concept]


class CompositeConcept:
    """A concept that consists of multiple other (sub)concepts. Currently assumes precisely two subconcepts."""

    def __init__(self, concepts: Sequence[Concept | CompositeConcept], quiz_types: Sequence[QuizType]) -> None:
        self._concepts = concepts
        self._quiz_types = quiz_types

    def quizzes(self, language: Language, source_language: Language) -> list[Quiz]:
        """Generate the possible quizzes from the concept."""
        result = []
        for concept in self._concepts:
            result.extend(concept.quizzes(language, source_language))
        if self.has_labels(language):
            for (concept1, concept2), quiz_type in self.paired_concepts():
                labels1, labels2 = concept1.labels(language), concept2.labels(language)
                result.extend([Quiz(language, language, label, labels2, quiz_type) for label in labels1])
        return result

    def has_labels(self, *languages: Language) -> bool:
        """Return whether the concept has labels for all the specified languages."""
        return all(concept.has_labels(*languages) for concept in self._concepts)

    def leaf_concepts(self) -> Iterable[Concept]:
        """Return a list of leaf concepts."""
        for concept in self._concepts:
            for leaf_concept in concept.leaf_concepts():
                yield leaf_concept

    def paired_concepts(self) -> Iterable[tuple[ConceptPair, QuizType]]:
        """Pair the leaf concepts from the composite concepts."""
        leaf_concepts = [concept.leaf_concepts() for concept in self._concepts]
        for concept_group in zip(*leaf_concepts):
            for permutation, quiz_type in zip(permutations(concept_group, r=2), self._quiz_types):
                yield cast(ConceptPair, permutation), quiz_type

    @classmethod
    def from_dict(cls, concept_dict, keys: Sequence[str], quiz_types: Sequence[QuizType]) -> CompositeConcept:
        """Instantiate a concept from a dict."""
        return cls(tuple(concept_factory(concept_dict[key]) for key in keys), quiz_types)


def concept_factory(concept_dict) -> Concept | CompositeConcept:
    """Create a concept from the concept dict."""
    if {"singular", "plural"} <= set(concept_dict):
        return CompositeConcept.from_dict(concept_dict, ("singular", "plural"), ("pluralize", "singularize"))
    if {"female", "male"} <= set(concept_dict):
        return CompositeConcept.from_dict(concept_dict, ("female", "male"), ("masculinize", "feminize"))
    if {"positive_degree", "comparitive_degree", "superlative_degree"} <= set(concept_dict):
        return CompositeConcept.from_dict(
            concept_dict,
            ("positive_degree", "comparitive_degree", "superlative_degree"),
            (
                "give comparitive degree", "give superlative degree", "give positive degree",
                "give superlative degree", "give positive degree", "give comparitive degree"
            )
        )
    if {"first_person", "second_person", "third_person"} <= set(concept_dict):
        return CompositeConcept.from_dict(
            concept_dict,
            ("first_person", "second_person", "third_person"),
            (
                "give second person", "give third person", "give first person",
                "give third person", "give first person", "give second person"
            )
        )
    return Concept.from_dict(cast(ConceptDict, concept_dict))
