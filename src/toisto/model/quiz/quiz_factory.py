"""Quiz factory."""

from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import permutations, zip_longest
from typing import ClassVar

from ..language import LanguagePair
from ..language.concept import Concept, ConceptRelation
from ..language.label import Label, Labels
from .quiz import Quiz, Quizzes
from .quiz_type import (
    ANSWER,
    ANTONYM,
    DICTATE,
    FEMININE,
    INTERPRET,
    MASCULINE,
    NEUTER,
    ORDER,
    READ,
    THIRD_PERSON,
    WRITE,
    GrammaticalQuizType,
    QuizType,
)


@dataclass
class BaseQuizFactory:
    """Base class for quiz factories that create quizzes for one concept."""

    language_pair: LanguagePair
    quiz_types: tuple[QuizType, ...]  # Quiz types to create
    quiz_type: QuizType | None = None

    def create_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes."""
        if self.quiz_type is None or self.skip_quiz_type() or self.skip_concept(concept):
            return Quizzes()
        questions = self.questions(concept)
        answers = self.answers(concept)
        question_meanings = self.question_meanings(concept)
        answer_meanings = self.answer_meanings(concept)
        blocked_by = self.blocked_by(concept, previous_quizzes)
        return Quizzes(
            Quiz(
                concept,
                question,
                self.answers_for_question(question, answer, answers),
                self.quiz_type,
                blocked_by,
                question_meanings,
                answer_meanings,
            )
            for question, answer in self.zip_questions_and_answers(questions, answers)
            if self.include_question(question, answer)
        )

    def skip_quiz_type(self) -> bool:
        """Return whether to create quizzes for the quiz type."""
        if self.quiz_type and self.quiz_types:
            return all(not self.quiz_type.is_quiz_type(quiz_type) for quiz_type in self.quiz_types)
        return False

    def skip_concept(self, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return concept.answer_only

    @abstractmethod
    def questions(self, concept: Concept) -> Labels:
        """Return the question."""

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return Labels()

    def question_meanings(self, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return Labels()

    def answer_meanings(self, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        return Labels()

    def blocked_by(self, concept: Concept, previous_quizzes: Quizzes) -> tuple[Quiz, ...]:
        """Return the quizzes that block the created quizzes."""
        return tuple(previous_quizzes) if previous_quizzes else ()

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers

    def zip_questions_and_answers(self, questions: Labels, answers: Labels) -> Iterable[tuple[Label, Label]]:
        """Zip the questions and answers."""
        return zip(questions, questions, strict=True)

    def include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return True


@dataclass
class TranslationQuizFactory(BaseQuizFactory):
    """Create translation quizzes for a concept."""

    def skip_concept(self, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        language = self.language_pair.target
        return super().skip_concept(concept) or concept.is_composite(language) or not self.answers(concept)


@dataclass
class ReadQuizFactory(TranslationQuizFactory):
    """Create read quizzes for a concept."""

    quiz_type: QuizType | None = READ

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.own_labels(self.language_pair.target).non_colloquial

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.source).non_colloquial


@dataclass
class WriteQuizFactory(TranslationQuizFactory):
    """Create write quizzes for a concept."""

    quiz_type: QuizType | None = WRITE

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.source).non_colloquial

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.target).non_colloquial


@dataclass
class DictateQuizFactory(TranslationQuizFactory):
    """Create dicate quizzes for a concept."""

    quiz_type: QuizType | None = DICTATE

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target)

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.target).non_colloquial

    def question_meanings(self, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(self.language_pair.source)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers if question.colloquial else Labels((question,))


@dataclass
class InterpretQuizFactory(TranslationQuizFactory):
    """Create interpretion quizzes for a concept."""

    quiz_type: QuizType | None = INTERPRET

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.own_labels(self.language_pair.target)

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.source).non_colloquial

    def question_meanings(self, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(self.language_pair.target)


@dataclass
class GrammaticalQuizFactory(BaseQuizFactory):
    """Create grammatical quizzes for a concept."""

    def create_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes."""
        quizzes = Quizzes()
        for question_concept, answer_concept in permutations(concept.leaf_concepts(self.language_pair.target), r=2):
            self.question_concept, self.answer_concept = question_concept, answer_concept
            self.quiz_type = self.grammatical_quiz_type(question_concept, answer_concept)
            quizzes |= super().create_quizzes(concept, previous_quizzes)
        return quizzes

    @staticmethod
    def grammatical_quiz_type(concept1: Concept, concept2: Concept) -> QuizType | None:
        """Return the quiz type to change the grammatical category of concept1 into that of concept2.

        For example, to change "I am" into "they are" would mean changing the grammatical number from singular to plural
        and changing the grammatical person from first person to third person. To prevent the quiz from becoming too
        complex ("Give the affirmative past tense plural third person...") we limit the number of quiz types.
        """
        quiz_types: list[GrammaticalQuizType] = []
        for category1, category2 in zip_longest(concept1.grammatical_categories, concept2.grammatical_categories):
            if category1 != category2:
                quiz_types.extend(GrammaticalQuizType.instances.get_values(category2))
        if set(quiz_types) <= {FEMININE, MASCULINE, NEUTER, THIRD_PERSON} and len(quiz_types) > 1:
            return GrammaticalQuizType(quiz_types=tuple(quiz_types))
        return quiz_types[0] if len(quiz_types) == 1 else None

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return self.question_concept.labels(self.language_pair.target).non_colloquial

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return self.answer_concept.labels(self.language_pair.target).non_colloquial

    def question_meanings(self, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return self.question_concept.meanings(self.language_pair.source)

    def answer_meanings(self, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        return self.answer_concept.meanings(self.language_pair.source)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return Labels((answer,))

    def zip_questions_and_answers(self, questions: Labels, answers: Labels) -> Iterable[tuple[Label, Label]]:
        """Zip the questions and answers."""
        return zip(questions, answers, strict=False)

    def include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return question != answer


@dataclass
class OrderQuizFactory(BaseQuizFactory):
    """Create order quizzes for a concept."""

    MIN_WORD_COUNT: ClassVar[int] = 5
    quiz_type: QuizType | None = ORDER

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target).non_colloquial

    def answer_meanings(self, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        return concept.meanings(self.language_pair.source)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return Labels((question,))  # Question and answer are equal, the question is shuffled when the quiz is presented

    def include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return question.word_count >= self.MIN_WORD_COUNT


@dataclass
class SemanticQuizFactory(BaseQuizFactory):
    """Create semantic quizzes for a concept."""

    def create_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes."""
        quizzes = Quizzes()
        for semantic_quiz_type in (ANSWER, ANTONYM):
            self.quiz_type = semantic_quiz_type
            self.concept_relation: ConceptRelation = semantic_quiz_type.concept_relation
            quizzes |= super().create_quizzes(concept, previous_quizzes)
        return quizzes

    def skip_concept(self, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return super().skip_concept(concept) or not concept.get_related_concepts(self.concept_relation)

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.own_labels(self.language_pair.target).non_colloquial

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        labels = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            labels.extend(list(related_concept.labels(self.language_pair.target)))
        return Labels(labels)

    def answer_meanings(self, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        meanings = list(concept.meanings(self.language_pair.source))
        for related_concept in concept.get_related_concepts(self.concept_relation):
            meanings.extend(related_concept.meanings(self.language_pair.source))
        return Labels(meanings)

    def blocked_by(self, concept: Concept, previous_quizzes: Quizzes) -> tuple[Quiz, ...]:
        """Return the quizzes that block the created quizzes."""
        for related_concept in concept.get_related_concepts(self.concept_relation):
            previous_quizzes |= QuizFactory(self.language_pair, ()).translation_quizzes(related_concept)
        return super().blocked_by(concept, previous_quizzes)


class QuizFactory:
    """Create quizzes for multiple concepts."""

    def __init__(self, language_pair: LanguagePair, quiz_types: tuple[QuizType, ...]) -> None:
        self.language_pair = language_pair
        self.read_quiz_factory = ReadQuizFactory(self.language_pair, quiz_types)
        self.write_quiz_factory = WriteQuizFactory(self.language_pair, quiz_types)
        self.dictate_quiz_factory = DictateQuizFactory(self.language_pair, quiz_types)
        self.interpret_quiz_factory = InterpretQuizFactory(self.language_pair, quiz_types)
        self.grammatical_quiz_factory = GrammaticalQuizFactory(self.language_pair, quiz_types)
        self.semantic_quiz_factory = SemanticQuizFactory(self.language_pair, quiz_types)
        self.order_quiz_factory = OrderQuizFactory(self.language_pair, quiz_types)

    def create_quizzes(self, *concepts: Concept) -> Quizzes:
        """Create quizzes for the concepts."""
        return Quizzes(Quizzes().union(*(self.concept_quizzes(concept, Quizzes()) for concept in concepts)))

    def concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a concept."""
        return Quizzes(
            self.composite_concept_quizzes(concept, previous_quizzes)
            | self.leaf_concept_quizzes(concept, previous_quizzes),
        )

    def composite_concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a composite concept."""
        quizzes = Quizzes()
        for constituent_concept in concept.constituents:
            quizzes |= self.concept_quizzes(constituent_concept, Quizzes(quizzes | previous_quizzes))
        quizzes |= self.grammatical_quiz_factory.create_quizzes(concept, Quizzes(quizzes | previous_quizzes))
        return quizzes

    def leaf_concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a leaf concept."""
        translation_quizzes = self.translation_quizzes(concept, previous_quizzes)
        semantic_quizzes = self.semantic_quizzes(concept, Quizzes(translation_quizzes | previous_quizzes))
        return Quizzes(translation_quizzes | semantic_quizzes)

    def translation_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create the translation quizzes for a concept."""
        previous_quizzes = previous_quizzes or Quizzes()
        read_quizzes = self.read_quiz_factory.create_quizzes(concept, previous_quizzes)
        previous_quizzes |= read_quizzes
        dictate_quizzes = self.dictate_quiz_factory.create_quizzes(concept, previous_quizzes)
        previous_quizzes |= dictate_quizzes
        write_quizzes = self.write_quiz_factory.create_quizzes(concept, previous_quizzes)
        previous_quizzes |= write_quizzes
        interpret_quizzes = self.interpret_quiz_factory.create_quizzes(concept, previous_quizzes)
        return Quizzes(read_quizzes | write_quizzes | dictate_quizzes | interpret_quizzes)

    def semantic_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create semantic quizzes for the concept."""
        semantic_quizzes = self.semantic_quiz_factory.create_quizzes(concept, previous_quizzes)
        semantic_quizzes |= self.order_quiz_factory.create_quizzes(concept, previous_quizzes)
        return semantic_quizzes


def create_quizzes(language_pair: LanguagePair, quiz_types: tuple[QuizType, ...], *concepts: Concept) -> Quizzes:
    """Create quizzes for the concepts, using the target and source language."""
    return QuizFactory(language_pair, quiz_types).create_quizzes(*concepts)
