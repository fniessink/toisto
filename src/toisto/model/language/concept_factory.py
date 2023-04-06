"""Concept factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union, cast, get_args

from . import Language
from .cefr import CommonReferenceLevel, CommonReferenceLevelSource
from .concept import Concept, ConceptId, ConceptIds, RelatedConcepts, Topic
from .grammar import GrammaticalCategory
from .iana_language_subtag_registry import ALL_LANGUAGES
from .label import Labels, label_factory, meaning_factory

CommonReferenceLevelDict = dict[CommonReferenceLevel, CommonReferenceLevelSource | list[CommonReferenceLevelSource]]
ConceptIdListOrString = ConceptId | list[ConceptId]
ConceptIdDictOrListOrString = dict[Language, ConceptIdListOrString] | ConceptIdListOrString
TopicList = list[Topic]
MetaData = Literal["level", "antonym", "answer", "answer-only", "roots", "topics"]
LeafConceptDict = dict[
    Language | MetaData,
    ConceptId | list[ConceptId] | ConceptIdDictOrListOrString | CommonReferenceLevelDict | TopicList | bool,
]
CompositeConceptDict = dict[
    GrammaticalCategory | MetaData,
    Union["CompositeConceptDict", LeafConceptDict, CommonReferenceLevelDict, TopicList, bool],
]
ConceptDict = LeafConceptDict | CompositeConceptDict


@dataclass(frozen=True)
class ConceptFactory:
    """Create concepts from the concept dict."""

    concept_id: ConceptId
    concept_dict: ConceptDict
    topic: Topic

    def create_concept(self, parent: ConceptId | None = None) -> Concept:
        """Create a concept from the concept_dict."""
        return Concept(
            self.concept_id,
            self._labels(),
            self._meanings(),
            self._level(),
            self._related_concepts(parent),
            self._topics(),
            self._answer_only(),
        )

    def _labels(self) -> dict[Language, Labels]:
        """Return the concept labels."""
        return {
            cast(Language, key): label_factory(cast(str | list[str], value))
            for key, value in self.concept_dict.items()
            if key in ALL_LANGUAGES
        }

    def _meanings(self) -> dict[Language, Labels]:
        """Return the concept meanings."""
        return {
            cast(Language, key): meaning_factory(cast(str | list[str], value))
            for key, value in self.concept_dict.items()
            if key in ALL_LANGUAGES
        }

    def _level(self) -> CommonReferenceLevel | None:
        """Determine the Common Reference Level for this concept.

        At the moment, just use the highest language level specified by the available sources.
        """
        concept_levels = [level for level in self._get_levels() if level in get_args(CommonReferenceLevel)]
        return max(concept_levels, default=None)

    def _related_concepts(self, parent: ConceptId | None) -> RelatedConcepts:
        """Create the related concepts."""
        return RelatedConcepts(
            parent,
            self._constituent_concepts(),
            self._root_concepts(),
            self._related_concept_ids("antonym"),
            self._related_concept_ids("answer"),
        )

    def _topics(self) -> set[Topic]:
        """Return the concept topics."""
        return self._get_topics() | {self.topic}

    def _answer_only(self) -> bool:
        """Return whether the concept is answer-only."""
        return bool(self.concept_dict.get("answer-only"))

    def _constituent_concepts(self) -> ConceptIds:
        """Create a constituent concept for each grammatical category."""
        return tuple(self._constituent_concept(category) for category in self._grammatical_categories())

    def _constituent_concept(self, category: GrammaticalCategory) -> ConceptId:
        """Create a constituent concept for the specified grammatical category."""
        constituent_concept_id = ConceptId(f"{self.concept_id}/{category}")
        concept_factory = self.__class__(constituent_concept_id, self._constituent_concept_dict(category), self.topic)
        concept_factory.create_concept(self.concept_id)
        return constituent_concept_id

    def _constituent_concept_dict(self, category: GrammaticalCategory) -> ConceptDict:
        """Create a constituent concept dict that can be used to create a constituent concept."""
        antonym_concept_ids = self._related_concept_ids("antonym")
        antonyms_dict = dict(antonym=[ConceptId(f"{antonym}/{category}") for antonym in antonym_concept_ids])
        answer_concept_ids = self._related_concept_ids("answer")
        answers_dict = dict(answer=[ConceptId(f"{answer}/{category}") for answer in answer_concept_ids])
        roots_dict = cast(CompositeConceptDict, dict(roots=self._get_roots()))
        topics_dict = cast(CompositeConceptDict, dict(topics=list(self._get_topics())))
        constituent_concept_dict = (
            cast(ConceptDict, cast(CompositeConceptDict, self.concept_dict)[category])
            | roots_dict
            | antonyms_dict
            | answers_dict
            | topics_dict
        )
        constituent_concept_dict.setdefault("level", self._get_levels())
        return cast(ConceptDict, constituent_concept_dict)

    def _grammatical_categories(self) -> tuple[GrammaticalCategory, ...]:
        """Retrieve the grammatical categories from the concept dict."""
        keys = self.concept_dict.keys()
        return tuple(cast(GrammaticalCategory, key) for key in keys if key in get_args(GrammaticalCategory))

    def _root_concepts(self) -> dict[Language, ConceptIds] | ConceptIds:
        """Retrieve the roots from the concept dict."""
        roots = self._get_roots()
        if isinstance(roots, dict):  # Roots are not the same for all languages
            return {
                language: tuple(concept_ids) if isinstance(concept_ids, list) else (concept_ids,)
                for language, concept_ids in roots.items()
            }
        return tuple(roots) if isinstance(roots, list) else (roots,)

    def _get_roots(self) -> ConceptIdDictOrListOrString:
        """Get the roots from the concept dict."""
        return cast(ConceptIdDictOrListOrString, self.concept_dict.get("roots", {}))

    def _related_concept_ids(self, relation: MetaData) -> ConceptIds:
        """Return the ids of the related concept(s)."""
        related = cast(ConceptIdListOrString, self.concept_dict.get(relation, []))
        return tuple(related) if isinstance(related, list) else (related,)

    def _get_levels(self) -> CommonReferenceLevelDict:
        """Get the Common Reference Levels from the concept dict."""
        return cast(CommonReferenceLevelDict, self.concept_dict.get("level", {}))

    def _get_topics(self) -> set[Topic]:
        """Get the topics from the concept dict."""
        topics = cast(Topic | list[Topic], self.concept_dict.get("topics", []))
        return set(topics) if isinstance(topics, list) else {topics}


def create_concept(
    concept_id: ConceptId,
    concept_dict: ConceptDict,
    topic: Topic | None = None,
) -> Concept:
    """Create a concept from the concept dict."""
    topic = topic or Topic("<unknown topic>")
    return ConceptFactory(concept_id, concept_dict or cast(ConceptDict, {}), topic).create_concept()
