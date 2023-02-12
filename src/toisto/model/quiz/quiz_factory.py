"""Quiz factory."""

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import permutations, zip_longest
from typing import cast

from toisto.metadata import Language
from toisto.tools import zip_and_cycle

from ..language.concept import Concept
from .quiz import GRAMMATICAL_QUIZ_TYPES, Quiz, QuizType, Quizzes


@dataclass
class QuizFactory:
    """Create quizzes for concepts."""

    target_language: Language
    source_language: Language

    def create_quizzes(self, *concepts: Concept) -> Quizzes:
        """Create quizzes for the concepts."""
        return Quizzes().union(*(self.concept_quizzes(concept, Quizzes()) for concept in concepts))

    def concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a concept."""
        if concept.constituents:
            return self.composite_concept_quizzes(concept, previous_quizzes)
        return self.leaf_concept_quizzes(concept, previous_quizzes)

    def composite_concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a composite concept."""
        quizzes = Quizzes()
        for constituent_concept in concept.constituents:
            quizzes |= self.concept_quizzes(constituent_concept, quizzes.copy() | previous_quizzes)
        quizzes |= self.grammatical_quizzes(concept, quizzes.copy() | previous_quizzes)
        return quizzes

    def leaf_concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a leaf concept."""
        translation_quizzes = self.translation_quizzes(concept, previous_quizzes)
        listening_quizzes = self.listening_quizzes(concept, translation_quizzes.copy() | previous_quizzes)
        antonym_quizzes = self.antonym_quizzes(
            concept,
            translation_quizzes.copy() | listening_quizzes.copy() | previous_quizzes,
        )
        return translation_quizzes | listening_quizzes | antonym_quizzes

    def translation_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create translation quizzes for the concept."""
        target_language, source_language = self.target_language, self.source_language
        target_labels, source_labels = concept.labels(target_language), concept.labels(source_language)
        if not target_labels or not source_labels:
            return Quizzes()
        blocked_by = tuple(previous_quizzes)
        target_to_source = Quizzes(
            Quiz(concept, target_language, source_language, target_label, source_labels, blocked_by=blocked_by)
            for target_label in target_labels
        )
        source_to_target = Quizzes(
            Quiz(concept, source_language, target_language, source_label, target_labels, blocked_by=blocked_by)
            for source_label in source_labels
        )
        return target_to_source | source_to_target

    def listening_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create listening quizzes for the concept."""
        target_language, source_language = self.target_language, self.source_language
        labels = concept.labels(target_language)
        blocked_by = tuple(previous_quizzes)
        meanings = concept.meanings(source_language)
        return Quizzes(
            Quiz(concept, target_language, target_language, label, (label,), ("listen",), blocked_by, meanings)
            for label in labels
        )

    def grammatical_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create grammatical quizzes for the concept."""
        target_language, source_language = self.target_language, self.source_language
        blocked_by = tuple(previous_quizzes)
        quizzes = Quizzes()
        for concept1, concept2 in paired_leaf_concepts(concept):
            labels1, labels2 = concept1.labels(target_language), concept2.labels(target_language)
            meanings = concept1.meanings(source_language) + concept2.meanings(source_language)
            quiz_types = grammatical_quiz_types(concept1, concept2)
            quizzes |= Quizzes(
                Quiz(concept, target_language, target_language, label1, (label2,), quiz_types, blocked_by, meanings)
                for label1, label2 in zip(labels1, labels2, strict=False)
                if label1 != label2
            )
        return quizzes

    def antonym_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create antonym quizzes for the concept."""
        target_language, source_language = self.target_language, self.source_language
        labels = concept.labels(target_language)
        blocked_by = tuple(previous_quizzes)
        quizzes = Quizzes()
        for antonym in concept.antonyms:
            antonym_labels = antonym.labels(target_language)
            meanings = concept.meanings(source_language) + antonym.meanings(source_language)
            quizzes |= Quizzes(
                Quiz(
                    concept,
                    target_language,
                    target_language,
                    label,
                    antonym_labels,
                    ("antonym",),
                    blocked_by,
                    meanings,
                )
                for label in labels
            )
        return quizzes


def grammatical_quiz_types(concept1: Concept, concept2: Concept) -> tuple[QuizType, ...]:
    """Return the quiz types to change the grammatical category of concept1 into that of concept2."""
    quiz_types = []
    for category1, category2 in zip_longest(concept1.grammatical_categories(), concept2.grammatical_categories()):
        if category1 != category2 and category2 is not None:
            quiz_types.append(GRAMMATICAL_QUIZ_TYPES[category2])
    return tuple(quiz_types)


def paired_leaf_concepts(concept: Concept) -> Iterable[tuple[Concept, Concept]]:
    """Pair the leaf concepts from the constituent concepts."""
    for concept_group in zip_and_cycle(*[list(constituent.leaf_concepts()) for constituent in concept.constituents]):
        for permutation in permutations(concept_group, r=2):
            yield cast(tuple[Concept, Concept], permutation)
