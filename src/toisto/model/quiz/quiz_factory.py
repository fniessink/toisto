"""Quiz factory."""

from dataclasses import dataclass
from itertools import permutations, zip_longest

from ..language import LanguagePair
from ..language.concept import Concept, Concepts
from .quiz import GRAMMATICAL_QUIZ_TYPES, Quiz, QuizType, Quizzes


@dataclass(frozen=True)
class QuizFactory:
    """Create quizzes for concepts."""

    language_pair: LanguagePair

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
        semantic_quizzes = self.semantic_quizzes(concept, Quizzes(translation_quizzes | previous_quizzes))
        return Quizzes(translation_quizzes | semantic_quizzes)

    def translation_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create the translation quizzes for a concept."""
        previous_quizzes = previous_quizzes or Quizzes()
        read_quizzes = self.read_quizzes(concept, previous_quizzes)
        dictate_quizzes = self.dictate_quizzes(concept, Quizzes(read_quizzes | previous_quizzes))
        write_quizzes = self.write_quizzes(concept, Quizzes(read_quizzes | dictate_quizzes | previous_quizzes))
        interpret_quizzes = self.interpret_quizzes(
            concept,
            Quizzes(read_quizzes | write_quizzes | dictate_quizzes | previous_quizzes),
        )
        return Quizzes(read_quizzes | write_quizzes | dictate_quizzes | interpret_quizzes)

    def read_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create read quizzes for the concept."""
        target_language, source_language = self.language_pair.target, self.language_pair.source
        if concept.is_composite(target_language):
            return Quizzes()
        target_labels = concept.non_colloquial_labels(target_language)
        source_labels = concept.non_colloquial_labels(source_language)
        if not target_labels or not source_labels:
            return Quizzes()
        blocked_by = tuple(previous_quizzes) if previous_quizzes else ()
        return Quizzes(
            Quiz(concept, target_label, source_labels, ("read",), blocked_by) for target_label in target_labels
        )

    def write_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create write quizzes for the concept."""
        target_language, source_language = self.language_pair.target, self.language_pair.source
        if concept.is_composite(target_language):
            return Quizzes()
        target_labels = concept.non_colloquial_labels(target_language)
        source_labels = concept.non_colloquial_labels(source_language)
        if not target_labels or not source_labels:
            return Quizzes()
        blocked_by = tuple(previous_quizzes) if previous_quizzes else ()
        return Quizzes(
            Quiz(concept, source_label, target_labels, ("write",), blocked_by) for source_label in source_labels
        )

    def dictate_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create dictation quizzes for the concept."""
        target_language, source_language = self.language_pair.target, self.language_pair.source
        target_labels = concept.non_colloquial_labels(target_language)
        blocked_by = tuple(previous_quizzes) if previous_quizzes else ()
        meanings = concept.meanings(source_language)
        non_colloquial_quizzes = Quizzes(
            Quiz(concept, label, (label,), ("dictate",), blocked_by, meanings) for label in target_labels
        )
        colloquial_quizzes = Quizzes(
            Quiz(concept, label, target_labels, ("dictate",), blocked_by, meanings)
            for label in concept.colloquial_labels(target_language)
        )
        return Quizzes(non_colloquial_quizzes | colloquial_quizzes)

    def interpret_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create interpret (listen and translate) quizzes for the concept."""
        target_language, source_language = self.language_pair.target, self.language_pair.source
        source_labels = concept.non_colloquial_labels(source_language)
        if not source_labels or concept.is_composite(target_language):
            return Quizzes()
        blocked_by = tuple(previous_quizzes) if previous_quizzes else ()
        meanings = concept.meanings(target_language)
        return Quizzes(
            Quiz(concept, label, source_labels, ("interpret",), blocked_by, meanings)
            for label in concept.labels(target_language)
        )

    def grammatical_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create grammatical quizzes for the concept."""
        target_language, source_language = self.language_pair.target, self.language_pair.source
        blocked_by = tuple(previous_quizzes)
        quizzes = Quizzes()
        for question_concept, answer_concept in permutations(concept.leaf_concepts(target_language), r=2):
            quiz_types = grammatical_quiz_types(question_concept, answer_concept)
            if not quiz_types:
                continue
            question_labels = question_concept.non_colloquial_labels(target_language)
            answer_labels = answer_concept.non_colloquial_labels(target_language)
            question_meanings = question_concept.meanings(source_language)
            answer_meanings = answer_concept.meanings(source_language)
            quizzes |= Quizzes(
                Quiz(
                    concept,
                    question_label,
                    (answer_label,),
                    quiz_types,
                    blocked_by,
                    question_meanings,
                    answer_meanings,
                )
                for question_label, answer_label in zip(question_labels, answer_labels, strict=False)
                if question_label != answer_label
            )
        return quizzes

    def semantic_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create semantic quizzes for the concept."""
        answer_quizzes = self.related_concept_quizzes(
            concept, previous_quizzes, "answer", concept.get_related_concepts("answer")
        )
        antonym_quizzes = self.related_concept_quizzes(
            concept,
            Quizzes(answer_quizzes | previous_quizzes),
            "antonym",
            concept.get_related_concepts("antonym"),
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
        target_language, source_language = self.language_pair.target, self.language_pair.source
        meanings = list(concept.meanings(source_language))
        related_concept_labels = []
        for related_concept in related_concepts:
            meanings.extend(related_concept.meanings(source_language))
            related_concept_labels.extend(list(related_concept.labels(target_language)))
            previous_quizzes |= self.translation_quizzes(related_concept)
        return Quizzes(
            Quiz(
                concept,
                label,
                tuple(related_concept_labels),
                (quiz_type,),
                tuple(previous_quizzes),
                (),
                tuple(meanings),
            )
            for label in concept.non_colloquial_labels(target_language)
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
    if set(quiz_types) <= {"feminize", "masculinize", "neuterize", "give third person"}:
        return tuple(quiz_types)
    return tuple(quiz_types) if len(quiz_types) == 1 else ()


def create_quizzes(language_pair: LanguagePair, *concepts: Concept) -> Quizzes:
    """Create quizzes for the concepts, using the target and source language."""
    return QuizFactory(language_pair).create_quizzes(*concepts)
