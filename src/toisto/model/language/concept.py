"""Concept classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import permutations
from typing import cast, get_args, Iterable, Literal, Sequence, Union

from toisto.metadata import Language

from ..types import ConceptId
from ..quiz import Quizzes, QuizType, quiz_factory, quiz_type_factory
from .grammar import GrammaticalCategory
from .label import Labels, label_factory

ConceptRelation = Literal["uses"]
LeafConceptDict = dict[Language | ConceptRelation, str | ConceptId | list[str] | list[ConceptId]]
CompositeConceptDict = dict[GrammaticalCategory | ConceptRelation, Union["CompositeConceptDict", LeafConceptDict]]
ConceptDict = LeafConceptDict | CompositeConceptDict


class Concept(ABC):
    """Abstract base class for concepts."""

    def __init__(self, concept_id: ConceptId, uses: tuple[ConceptId, ...]) -> None:
        self._id = concept_id
        self._uses = uses

    @abstractmethod
    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""

    @abstractmethod
    def has_labels(self, *languages: Language) -> bool:
        """Return whether the concept has labels for all the specified languages."""

    @abstractmethod
    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return self as a list of leaf concepts."""

    @staticmethod
    def get_uses_from_concept_dict(concept_dict: ConceptDict) -> list[ConceptId]:
        """Retrieve the uses relationship from the concept dict."""
        uses = cast(list[ConceptId] | ConceptId, concept_dict.get("uses") or [])
        return uses if isinstance(uses, list) else [uses]


class LeafConcept(Concept):
    """Class representing an atomic concept from a topic."""

    def __init__(self, concept_id: ConceptId, labels: dict[Language, Labels], uses: tuple[ConceptId, ...]) -> None:
        super().__init__(concept_id, uses)
        self._labels = labels

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept and its labels."""
        result = set()
        if self.has_labels(language, source_language):
            labels, source_labels = self.labels(language), self.labels(source_language)
            result.update(quiz_factory(self._id, language, source_language, labels, source_labels, uses=self._uses))
        if self.has_labels(language):
            labels = self.labels(language)
            result.update(quiz_factory(self._id, language, language, labels, labels, "listen", self._uses))
        return result

    def has_labels(self, *languages: Language) -> bool:
        """Return whether the concept has labels for all the specified languages."""
        return all(language in self._labels for language in languages)

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        return self._labels[language]

    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return self as a list of leaf concepts."""
        return [self]

    @classmethod
    def from_dict(cls, concept_id: ConceptId, concept_dict: LeafConceptDict) -> LeafConcept:
        """Instantiate a concept from a dict."""
        languages = cast(list[Language], [key for key in concept_dict if key in get_args(Language)])
        labels = {language: label_factory(cast(str | list[str], concept_dict[language])) for language in languages}
        uses = tuple(cls.get_uses_from_concept_dict(concept_dict))
        return cls(concept_id, labels, uses)


LeafConceptPair = tuple[LeafConcept, LeafConcept]


class CompositeConcept(Concept):
    """A concept that consists of multiple other (sub)concepts."""

    def __init__(
        self,
        concept_id: ConceptId,
        concepts: Sequence[Concept],
        quiz_types: Sequence[QuizType],
        uses: tuple[ConceptId, ...]
    ) -> None:
        super().__init__(concept_id, uses)
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
            result.update(quiz_factory(self._id, language, language, labels1, labels2, quiz_type, self._uses))
        return result

    def has_labels(self, *languages: Language) -> bool:
        """Return whether the concept has labels for all the specified languages."""
        return all(concept.has_labels(*languages) for concept in self._concepts)

    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return a list of leaf concepts."""
        for concept in self._concepts:
            for leaf_concept in concept.leaf_concepts():
                yield leaf_concept

    def paired_concepts(self) -> Iterable[tuple[LeafConceptPair, QuizType]]:
        """Pair the leaf concepts from the composite concepts."""
        leaf_concepts = [concept.leaf_concepts() for concept in self._concepts]
        for concept_group in zip(*leaf_concepts):
            for permutation, quiz_type in zip(permutations(concept_group, r=2), self._quiz_types):
                yield cast(LeafConceptPair, permutation), quiz_type

    @classmethod
    def from_dict(cls, concept_id: ConceptId, concept_dict: CompositeConceptDict) -> CompositeConcept:
        """Instantiate a concept from a dict."""
        grammatical_categories = cast(
            list[GrammaticalCategory], [key for key in concept_dict.keys() if key in get_args(GrammaticalCategory)]
        )
        uses = cls.get_uses_from_concept_dict(concept_dict)
        constituent_concepts = tuple(
            concept_factory(concept_id, cast(ConceptDict, concept_dict[key] | dict(uses=uses)))
            for key in grammatical_categories
        )
        return cls(concept_id, constituent_concepts, quiz_type_factory(tuple(grammatical_categories)), tuple(uses))


def concept_factory(concept_id: ConceptId, concept_dict: ConceptDict) -> Concept:
    """Create a concept from the concept dict."""
    if set(get_args(GrammaticalCategory)) & set(concept_dict):
        return CompositeConcept.from_dict(concept_id, cast(CompositeConceptDict, concept_dict))
    return LeafConcept.from_dict(concept_id, cast(LeafConceptDict, concept_dict))
