"""Quiz factory."""

from dataclasses import dataclass
from itertools import permutations, zip_longest
from typing import cast, Iterable

from toisto.metadata import Language
from toisto.tools import zip_and_cycle

from .quiz import Quiz, Quizzes, QuizType, GRAMMATICAL_QUIZ_TYPES
from ..language import Concept


@dataclass
class QuizFactory:
    """Create quizzes for concepts."""

    language: Language
    source_language: Language

    def create_quizzes(self, *concepts: Concept) -> Quizzes:
        """Create quizzes for the concept."""
        quizzes = set()
        for concept in concepts:
            quizzes |= self.create_quizzes(*concept.constituent_concepts)
            quizzes |= self.create_grammatical_quizzes(concept)
            quizzes |= self.create_translation_quizzes(concept)
            quizzes |= self.create_listen_quizzes(concept)
        return quizzes

    def create_translation_quizzes(self, concept: Concept) -> Quizzes:
        """Create translation quizzes for the concept."""
        language, source_language = self.language, self.source_language
        labels, source_labels = concept.labels(language), concept.labels(source_language)
        if not labels or not source_labels:
            return set()
        concept_id = concept.concept_id
        uses = concept.uses
        back = set(Quiz(concept_id, language, source_language, label, source_labels, uses=uses) for label in labels)
        forth = set(Quiz(concept_id, source_language, language, label, labels, uses=uses) for label in source_labels)
        return back | forth

    def create_listen_quizzes(self, concept: Concept) -> Quizzes:
        """Create listening quizzes for the concept."""
        labels = concept.labels(self.language)
        meanings = concept.meanings(self.source_language)
        return set(
            Quiz(concept.concept_id, self.language, self.language, label, (label,), ("listen",), concept.uses, meanings)
            for label in labels
        )

    def create_grammatical_quizzes(self, concept: Concept) -> Quizzes:
        """Create grammatical quizzes for the concept."""
        quizzes = set()
        for concept1, concept2 in paired_leaf_concepts(*concept.constituent_concepts):
            labels1, labels2 = concept1.labels(self.language), concept2.labels(self.language)
            meanings = concept1.meanings(self.source_language) + concept2.meanings(self.source_language)
            quiz_types = grammatical_quiz_types(concept1, concept2)
            uses = concept.uses + (concept1.concept_id, concept2.concept_id)
            quizzes |= set(
                Quiz(concept.concept_id, self.language, self.language, label1, (label2,), quiz_types, uses, meanings)
                for label1, label2 in zip(labels1, labels2)
                if label1 != label2
            )
        return quizzes


def grammatical_quiz_types(concept1: Concept, concept2: Concept) -> tuple[QuizType, ...]:
    """Return the quiz types to change the grammatical category of concept1 into that of concept2."""
    quiz_types = []
    for category1, category2 in zip_longest(concept1.grammatical_categories(), concept2.grammatical_categories()):
        if category1 != category2 and category2 is not None:
            quiz_types.append(GRAMMATICAL_QUIZ_TYPES[category2])
    return tuple(quiz_types)


def paired_leaf_concepts(*concepts: Concept) -> Iterable[tuple[Concept, Concept]]:
    """Pair the leaf concepts from the concepts."""
    for concept_group in zip_and_cycle(*[list(concept.leaf_concepts()) for concept in concepts]):
        for permutation in permutations(concept_group, r=2):
            yield cast(tuple[Concept, Concept], permutation)
