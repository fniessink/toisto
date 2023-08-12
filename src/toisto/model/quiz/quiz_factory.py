"""Quiz factory."""

from dataclasses import dataclass
from itertools import permutations, zip_longest

from ..language import Language
from ..language.concept import Concept, Concepts
from .quiz import GRAMMATICAL_QUIZ_TYPES, Quiz, QuizType, Quizzes


@dataclass(frozen=True)
class QuizFactory:
    """Create quizzes for concepts."""

    target_language: Language
    source_language: Language

    def create_quizzes(self, *concepts: Concept) -> Quizzes:
        """Create quizzes for the concepts."""
        return Quizzes(Quizzes().union(*(self.concept_quizzes(concept, Quizzes()) for concept in concepts)))

    def concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a concept."""
        if concept.answer_only:
            return Quizzes()
        return Quizzes(
            self.composite_concept_quizzes(concept, previous_quizzes)
            | self.leaf_concept_quizzes(concept, previous_quizzes),
        )

    def composite_concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a composite concept."""
        quizzes = Quizzes()
        for constituent_concept in concept.constituents:
            quizzes |= self.concept_quizzes(constituent_concept, Quizzes(quizzes | previous_quizzes))
        quizzes |= self.grammatical_quizzes(concept, Quizzes(quizzes | previous_quizzes))
        return quizzes

    def leaf_concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a leaf concept."""
        translation_quizzes = self.translation_quizzes(concept, previous_quizzes)
        listening_quizzes = self.listening_quizzes(concept, Quizzes(translation_quizzes | previous_quizzes))
        semantic_quizzes = self.semantic_quizzes(
            concept,
            Quizzes(translation_quizzes | listening_quizzes | previous_quizzes),
        )
        return Quizzes(translation_quizzes | listening_quizzes | semantic_quizzes)

    def translation_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create translation quizzes for the concept."""
        target_language, source_language = self.target_language, self.source_language
        if concept.is_composite(target_language):
            return Quizzes()
        target_labels, source_labels = concept.labels(target_language), concept.labels(source_language)
        if not target_labels or not source_labels:
            return Quizzes()
        blocked_by = tuple(previous_quizzes) if previous_quizzes else ()
        target_to_source = Quizzes(
            Quiz(concept, target_language, source_language, target_label, source_labels, ("read",), blocked_by, ())
            for target_label in target_labels
        )
        source_to_target = Quizzes(
            Quiz(concept, source_language, target_language, source_label, target_labels, ("write",), blocked_by, ())
            for source_label in source_labels
        )
        return Quizzes(target_to_source | source_to_target)

    def listening_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create listening quizzes for the concept."""
        target_language, source_language = self.target_language, self.source_language
        labels = concept.labels(target_language)
        blocked_by = tuple(previous_quizzes) if previous_quizzes else ()
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
        for concept1, concept2 in permutations(concept.leaf_concepts(target_language), r=2):
            quiz_types = grammatical_quiz_types(concept1, concept2)
            if not quiz_types:
                continue
            labels1, labels2 = concept1.labels(target_language), concept2.labels(target_language)
            meanings = concept1.meanings(source_language) + concept2.meanings(source_language)
            quizzes |= Quizzes(
                Quiz(concept, target_language, target_language, label1, (label2,), quiz_types, blocked_by, meanings)
                for label1, label2 in zip(labels1, labels2, strict=False)
                if label1 != label2
            )
        return quizzes

    def semantic_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create semantic quizzes for the concept."""
        answer_quizzes = self.related_concept_quizzes(concept, previous_quizzes, "answer", concept.answers)
        antonym_quizzes = self.related_concept_quizzes(
            concept,
            Quizzes(answer_quizzes | previous_quizzes),
            "antonym",
            concept.antonyms,
        )
        return Quizzes(answer_quizzes | antonym_quizzes)

    def related_concept_quizzes(
        self,
        concept: Concept,
        previous_quizzes: Quizzes,
        quiz_type: QuizType,
        related_concepts: Concepts,
    ) -> Quizzes:
        """Create quizzes for the related concepts."""
        if not related_concepts:
            return Quizzes()
        target_language, source_language = self.target_language, self.source_language
        labels = concept.labels(target_language)
        meanings = list(concept.meanings(source_language))
        related_concept_labels = []
        for related_concept in related_concepts:
            meanings.extend(related_concept.meanings(source_language))
            related_concept_labels.extend(list(related_concept.labels(target_language)))
            previous_quizzes |= self.translation_quizzes(related_concept) | self.listening_quizzes(related_concept)
        return Quizzes(
            Quiz(
                concept,
                target_language,
                target_language,
                label,
                tuple(related_concept_labels),
                (quiz_type,),
                tuple(previous_quizzes),
                tuple(meanings),
            )
            for label in labels
        )


def grammatical_quiz_types(concept1: Concept, concept2: Concept) -> tuple[QuizType, ...]:
    """Return the quiz types to change the grammatical category of concept1 into that of concept2.

    For example, to change "I am" into "they are" would mean changing the grammatical number from singular to plural
    and changing the grammatical person from first person to third person. To prevent the quiz from becoming too
    complex ("Give the affirmative past tense plural third person...") we limit the number of quiz types.
    """
    quiz_types = []
    for category1, category2 in zip_longest(concept1.grammatical_categories(), concept2.grammatical_categories()):
        if category1 != category2 and category2 in GRAMMATICAL_QUIZ_TYPES:
            quiz_types.append(GRAMMATICAL_QUIZ_TYPES[category2])
    if "infinitive" in concept1.grammatical_categories():
        return tuple(quiz_types)
    if set(quiz_types) <= {"feminize", "masculinize", "neuterize", "give third person"}:
        return tuple(quiz_types)
    if len(quiz_types) == 1:
        return tuple(quiz_types)
    return tuple()


def create_quizzes(target_language: Language, source_language: Language, *concepts: Concept) -> Quizzes:
    """Create quizzes for the concepts, using the target and source language."""
    return QuizFactory(target_language, source_language).create_quizzes(*concepts)
