"""Concept classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import permutations, zip_longest
from typing import cast, get_args, Iterable, Literal, Union

from toisto.metadata import Language
from toisto.tools import zip_and_cycle

from ..model_types import ConceptId
from ..quiz import Quizzes, QuizType, quiz_factory, GRAMMATICAL_QUIZ_TYPES
from .grammar import GrammaticalCategory
from .label import Labels, Label, label_factory

ConceptRelation = Literal["uses"]
LeafConceptDict = dict[Language | ConceptRelation, str | ConceptId | list[str] | list[ConceptId]]
CompositeConceptDict = dict[GrammaticalCategory | ConceptRelation, Union["CompositeConceptDict", LeafConceptDict]]
ConceptDict = LeafConceptDict | CompositeConceptDict


class Concept(ABC):
    """Abstract base class for concepts."""

    def __init__(self, concept_id: ConceptId, uses: tuple[ConceptId, ...]) -> None:
        self.concept_id = concept_id
        self._uses = uses

    @abstractmethod
    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""

    @abstractmethod
    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return self as a list of leaf concepts."""

    def grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Return the grammatical categories of this concept."""
        grammatical_categories = get_args(GrammaticalCategory)
        id_parts = self.concept_id.split("/")
        return tuple(cast(GrammaticalCategory, id_part) for id_part in id_parts if id_part in grammatical_categories)

    @staticmethod
    def get_uses_from_concept_dict(concept_dict: ConceptDict) -> list[ConceptId]:
        """Retrieve the uses relationship from the concept dict."""
        uses = cast(list[ConceptId] | ConceptId, concept_dict.get("uses") or [])
        return uses if isinstance(uses, list) else [uses]


class LeafConcept(Concept):
    """Class representing an atomic concept from a topic."""

    def __init__(self, concept_id: ConceptId, labels: dict[Language, Labels], uses: tuple[ConceptId, ...]) -> None:
        extra_uses = (concept_id.replace("plural", "singular"),) if "plural" in concept_id else ()
        super().__init__(concept_id, uses + cast(tuple[ConceptId], extra_uses))
        self._labels = labels

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept and its labels."""
        labels, source_labels = self.labels(language), self.labels(source_language)
        meanings = self.meanings(source_language)
        translate = quiz_factory(self.concept_id, language, source_language, labels, source_labels, uses=self._uses)
        listen = quiz_factory(self.concept_id, language, language, labels, labels, ("listen",), self._uses, meanings)
        return translate | listen

    def labels(self, language: Language) -> Labels:
        """Return the labels for the language."""
        return self._labels.get(language, Labels())

    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return self as a list of leaf concepts."""
        return [self]

    def meanings(self, language: Language) -> Labels:
        """Return the meaning of the concept in the specified language."""
        meaning = Label(self._labels.get(language, [""])[0])
        return (meaning,) if meaning else ()

    @classmethod
    def from_dict(cls, concept_id: ConceptId, concept_dict: LeafConceptDict) -> LeafConcept:
        """Instantiate a concept from a dict."""
        languages = cast(list[Language], [key for key in concept_dict if key in get_args(Language)])
        labels = {language: label_factory(cast(str | list[str], concept_dict[language])) for language in languages}
        uses = tuple(cls.get_uses_from_concept_dict(concept_dict))
        return cls(concept_id, labels, uses)


LeafConceptPair = tuple[LeafConcept, LeafConcept]


class CompositeConcept(Concept):
    """A concept that consists of multiple constituent concepts."""

    def __init__(
        self,
        concept_id: ConceptId,
        constituent_concepts: dict[GrammaticalCategory, Concept],
        uses: tuple[ConceptId, ...]
    ) -> None:
        super().__init__(concept_id, uses)
        self._constituent_concepts = constituent_concepts

    def quizzes(self, language: Language, source_language: Language) -> Quizzes:
        """Generate the possible quizzes from the concept."""
        result = set()
        for concept in self._constituent_concepts.values():
            result.update(concept.quizzes(language, source_language))
        concept_id = self.concept_id
        for concept1, concept2 in self.paired_concepts():
            quiz_types = self.grammatical_quiz_types(concept1, concept2)
            labels1, labels2 = concept1.labels(language), concept2.labels(language)
            uses = self._uses + (concept2.concept_id,)
            meanings = concept1.meanings(source_language) + concept2.meanings(source_language)
            result.update(quiz_factory(concept_id, language, language, labels1, labels2, quiz_types, uses, meanings))
        return result

    def grammatical_quiz_types(self, concept1: Concept, concept2: Concept) -> tuple[QuizType, ...]:
        """Return the quiz types to change the grammatical category of concept1 into that of concept2."""
        quiz_types = []
        for category1, category2 in zip_longest(concept1.grammatical_categories(), concept2.grammatical_categories()):
            if category1 != category2 and category2 is not None:
                quiz_types.append (GRAMMATICAL_QUIZ_TYPES[category2])
        return tuple(quiz_types)

    def leaf_concepts(self) -> Iterable[LeafConcept]:
        """Return a list of leaf concepts."""
        for concept in self._constituent_concepts.values():
            yield from concept.leaf_concepts()

    def paired_concepts(self) -> Iterable[LeafConceptPair]:
        """Pair the leaf concepts from the composite concepts."""
        leaf_concepts = [list(concept.leaf_concepts()) for concept in self._constituent_concepts.values()]
        for concept_group in zip_and_cycle(*leaf_concepts):
            for permutation in permutations(concept_group, r=2):
                yield cast(LeafConceptPair, permutation)

    @classmethod
    def from_dict(cls, concept_id: ConceptId, concept_dict: CompositeConceptDict) -> CompositeConcept:
        """Instantiate a concept from a dict."""
        grammatical_categories = cast(
            list[GrammaticalCategory], [key for key in concept_dict.keys() if key in get_args(GrammaticalCategory)]
        )
        uses = cls.get_uses_from_concept_dict(concept_dict)
        constituent_concepts = {
            key: concept_factory(
                ConceptId(f"{concept_id}/{key}"), cast(ConceptDict, concept_dict[key] | dict(uses=uses))
            ) for key in grammatical_categories
        }
        return cls(concept_id, constituent_concepts, tuple(uses))


def concept_factory(concept_id: ConceptId, concept_dict: ConceptDict) -> Concept:
    """Create a concept from the concept dict."""
    if set(get_args(GrammaticalCategory)) & set(concept_dict):
        return CompositeConcept.from_dict(concept_id, cast(CompositeConceptDict, concept_dict))
    return LeafConcept.from_dict(concept_id, cast(LeafConceptDict, concept_dict))
