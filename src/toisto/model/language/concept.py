"""Concept classes."""

from __future__ import annotations

from itertools import permutations
from typing import cast, get_args, Iterable, Sequence, Union

from toisto.metadata import Language

from .grammar import GrammaticalCategory
from .label import Labels, label_factory
from ..quiz.quiz import Quizzes, QuizType, quiz_factory, quiz_type_factory


ConceptDict = dict[Language, str | list[str]]
CompositeConceptDict = dict[GrammaticalCategory, Union["CompositeConceptDict", ConceptDict]]


class Concept:
    """Class representing a concept from a topic."""

    def __init__(self, labels: dict[Language, Labels]) -> None:
        self._labels = labels

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept and its labels."""
        result = set()
        if self.has_labels(language, source_language):
            result.update(quiz_factory(language, source_language, self.labels(language), self.labels(source_language)))
        if self.has_labels(language):
            result.update(quiz_factory(language, language, self.labels(language), self.labels(language), "listen"))
        return result

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
        return cls({language: label_factory(label) for language, label in concept_dict.items()})


ConceptPair = tuple[Concept, Concept]


class CompositeConcept:
    """A concept that consists of multiple other (sub)concepts."""

    def __init__(self, concepts: Sequence[Concept | CompositeConcept], quiz_types: Sequence[QuizType]) -> None:
        self._concepts = concepts
        self._quiz_types = quiz_types

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""
        result = set()
        for concept in self._concepts:
            result.update(concept.quizzes(language, source_language))
        if not self.has_labels(language):
            return result
        for (concept1, concept2), quiz_type in self.paired_concepts():
            labels1, labels2 = concept1.labels(language), concept2.labels(language)
            result.update(quiz_factory(language, language, labels1, labels2, quiz_type))
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
    def from_dict(cls, concept_dict: CompositeConceptDict) -> CompositeConcept:
        """Instantiate a concept from a dict."""
        keys = concept_dict.keys()
        return cls(tuple(concept_factory(concept_dict[key]) for key in keys), quiz_type_factory(tuple(keys)))


def concept_factory(concept_dict: CompositeConceptDict | ConceptDict) -> CompositeConcept | Concept:
    """Create a concept from the concept dict."""
    if set(get_args(GrammaticalCategory)) & set(concept_dict):
        return CompositeConcept.from_dict(cast(CompositeConceptDict, concept_dict))
    return Concept.from_dict(cast(ConceptDict, concept_dict))
