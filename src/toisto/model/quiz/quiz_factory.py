"""Quiz factory."""

from itertools import permutations, zip_longest
from typing import cast, Iterable

from toisto.metadata import Language
from toisto.tools import zip_and_cycle

from .quiz import Quiz, Quizzes, QuizType, GRAMMATICAL_QUIZ_TYPES
from ..language import Concept


def create_quizzes(concept: Concept, language: Language, source_language: Language) -> Quizzes:
    """Create quizzes for the concept."""
    constituent_concept_quizzes = set()
    for constituent_concept in concept.constituent_concepts:
        constituent_concept_quizzes |= create_quizzes(constituent_concept, language, source_language)
    grammatical_quizzes = create_grammatical_quizzes(concept, language, source_language)
    translation_quizzes = create_translation_quizzes(concept, language, source_language)
    listen_quizzes = create_listen_quizzes(concept, language, source_language)
    return constituent_concept_quizzes | grammatical_quizzes | translation_quizzes | listen_quizzes


def create_translation_quizzes(concept: Concept, language: Language, source_language: Language) -> Quizzes:
    """Create translation quizzes for the concept."""
    labels, source_labels = concept.labels(language), concept.labels(source_language)
    if not labels or not source_labels:
        return set()
    concept_id = concept.concept_id
    uses = concept.uses
    return (
        set(Quiz(concept_id, language, source_language, label, source_labels, uses=uses) for label in labels) |
        set(Quiz(concept_id, source_language, language, label, labels, uses=uses) for label in source_labels)
    )


def create_listen_quizzes(concept: Concept, language: Language, source_language: Language) -> Quizzes:
    """Create listening quizzes for the concept."""
    labels = concept.labels(language)
    meanings = concept.meanings(source_language)
    concept_id = concept.concept_id
    uses = concept.uses
    return set(Quiz(concept_id, language, language, label, (label,), ("listen",), uses, meanings) for label in labels)


def create_grammatical_quizzes(concept: Concept, language: Language, source_language: Language) -> Quizzes:
    """Create grammatical quizzes for the concept."""
    quizzes = set()
    for concept1, concept2 in paired_leaf_concepts(concept):
        labels1, labels2 = concept1.labels(language), concept2.labels(language)
        meanings = concept1.meanings(source_language) + concept2.meanings(source_language)
        quiz_types = grammatical_quiz_types(concept1, concept2)
        uses = concept.uses + (concept2.concept_id,)
        quizzes |= set(
            Quiz(concept.concept_id, language, language, label1, (label2,), quiz_types, uses, meanings)
            for label1, label2 in zip(labels1, labels2) if label1 != label2
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
    """Pair the leaf concepts from the composite concepts."""
    leaf_concepts = [list(constituent_concept.leaf_concepts()) for constituent_concept in concept.constituent_concepts]
    for concept_group in zip_and_cycle(*leaf_concepts):
        for permutation in permutations(concept_group, r=2):
            yield cast(tuple[Concept, Concept], permutation)
