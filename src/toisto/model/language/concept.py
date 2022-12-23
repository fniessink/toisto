"""Concept classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import chain, permutations, zip_longest
from typing import cast, get_args, Iterable

from toisto.metadata import Language
from toisto.tools import zip_and_cycle

from ..model_types import ConceptId
from ..quiz import Quizzes, QuizType, quiz_factory, GRAMMATICAL_QUIZ_TYPES
from .grammar import GrammaticalCategory
from .label import Labels, Label


class Concept(ABC):
    """Abstract base class for concepts."""

    def __init__(self,
        concept_id: ConceptId,
        uses: tuple[ConceptId, ...],
        constituent_concepts: tuple[Concept, ...] = ()
    ) -> None:
        self.concept_id = concept_id
        self._uses = uses
        self._constituent_concepts = constituent_concepts

    @abstractmethod
    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""

    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return self as a list of leaf concepts."""
        for concept in self._constituent_concepts:
            yield from concept.leaf_concepts()

    def grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Return the grammatical categories of this concept."""
        keys = self.concept_id.split("/")
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))


class LeafConcept(Concept):
    """Class representing an atomic concept from a topic."""

    def __init__(self, concept_id: ConceptId, uses: tuple[ConceptId, ...], labels: dict[Language, Labels]) -> None:
        super().__init__(concept_id, uses)
        self._labels = labels

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept and its labels."""
        labels, source_labels = self.labels(language), self.labels(source_language)
        meanings = self.meanings(source_language)
        translate = quiz_factory(self.concept_id, language, source_language, labels, source_labels, uses=self._uses)
        listen = quiz_factory(self.concept_id, language, language, labels, labels, ("listen",), self._uses, meanings)
        return translate | listen

    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return self as a list of leaf concepts."""
        yield self

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        return self._labels.get(language, Labels())

    def meanings(self, language: Language) -> Labels:
        """Return the meaning of the concept in the specified language."""
        meaning = Label(self._labels.get(language, [""])[0])
        return (meaning,) if meaning else ()


class LeafConceptPair(Concept):
    """A pair of leaf concepts."""

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""
        labels1, labels2 = [concept.labels(language) for concept in self.leaf_concepts()]
        meanings = tuple(chain.from_iterable(concept.meanings(source_language) for concept in self.leaf_concepts()))
        quiz_types = self.grammatical_quiz_types()
        return quiz_factory(self.concept_id, language, language, labels1, labels2, quiz_types, self._uses, meanings)

    def grammatical_quiz_types(self) -> tuple[QuizType, ...]:
        """Return the quiz types to change the grammatical category of concept1 into that of concept2."""
        quiz_types = []
        grammatical_categories = [concept.grammatical_categories() for concept in self.leaf_concepts()]
        for category1, category2 in zip_longest(*grammatical_categories):
            if category1 != category2 and category2 is not None:
                quiz_types.append(GRAMMATICAL_QUIZ_TYPES[category2])
        return tuple(quiz_types)


class CompositeConcept(Concept):
    """A concept that consists of multiple constituent concepts."""

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""
        concepts = list(self._constituent_concepts) + list(self.paired_leaf_concepts())
        return set(chain.from_iterable(concept.quizzes(language, source_language) for concept in concepts))

    def paired_leaf_concepts(self) -> Iterable[LeafConceptPair]:
        """Pair the leaf concepts from the composite concepts."""
        leaf_concepts = [list(concept.leaf_concepts()) for concept in self._constituent_concepts]
        for concept_group in zip_and_cycle(*leaf_concepts):
            for permutation in permutations(concept_group, r=2):
                uses = self._uses + (permutation[1].concept_id,)
                yield LeafConceptPair(self.concept_id, uses, cast(tuple[LeafConcept, LeafConcept], permutation))
