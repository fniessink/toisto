"""Quiz factory."""

from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import permutations
from typing import ClassVar

from ..language import LanguagePair
from ..language.concept import Concept, ConceptRelation
from ..language.label import Label, Labels
from .quiz import Quiz, Quizzes
from .quiz_type import (
    ANSWER,
    ANTONYM,
    CLOZE_TEST,
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
        if self.quiz_type is None or self.skip_quiz_type(concept) or self.skip_concept(concept):
            return Quizzes()
        questions = self.questions(concept)
        answers = self.answers(concept)
        blocked_by = self.blocked_by(concept, previous_quizzes)
        return Quizzes(
            Quiz(
                concept,
                question,
                self.answers_for_question(question, answer, answers),
                self.quiz_type,
                blocked_by,
                self.question_meanings(question, concept),
                self.answer_meanings(answer, concept),
            )
            for question, answer in self.zip_questions_and_answers(questions, answers)
            if self.include_question(question, answer) and self.answers_for_question(question, answer, answers)
        )

    def skip_quiz_type(self, concept: Concept) -> bool:
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
        """Return the answers. Subclasses may use the concept to derive the answers."""
        return Labels()

    def question_meanings(self, question: Label, concept: Concept) -> Labels:
        """Return the question meanings. Subclasses may use question and concept to derive the question meanings."""
        return Labels()

    def answer_meanings(self, answer: Label, concept: Concept) -> Labels:
        """Return the answer meanings. Subclasses may use answer and concept to derive the answer meanings."""
        return Labels()

    def blocked_by(self, concept: Concept, previous_quizzes: Quizzes) -> tuple[Quiz, ...]:
        """Return the quizzes that block the created quizzes.

        Subclasses may use the concept to derive the blocking quizzes.
        """
        return tuple(previous_quizzes) if previous_quizzes else ()

    @abstractmethod
    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""

    def zip_questions_and_answers(self, questions: Labels, answers: Labels) -> Iterable[tuple[Label, Label]]:
        """Zip the questions and answers. Subclasses may use the answers to zip."""
        return zip(questions, questions, strict=True)

    def include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return question.grammatical_form == answer.grammatical_form


@dataclass
class TranslationQuizFactory(BaseQuizFactory):
    """Create translation quizzes for a concept."""

    @abstractmethod
    def questions(self, concept: Concept) -> Labels:
        """Return the question."""

    def skip_concept(self, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return super().skip_concept(concept) or not self.answers(concept)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        question_grammatical_categories = question.grammatical_form.grammatical_categories
        return Labels(
            [
                answer
                for answer in answers
                if not answer.grammatical_form.grammatical_categories
                or question_grammatical_categories <= answer.grammatical_form.grammatical_categories
                or question_grammatical_categories >= answer.grammatical_form.grammatical_categories
            ]
        )


@dataclass
class ReadQuizFactory(TranslationQuizFactory):
    """Create read quizzes for a concept."""

    quiz_type: QuizType | None = READ

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target).non_colloquial

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
    """Create dictate quizzes for a concept."""

    quiz_type: QuizType | None = DICTATE

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target)

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.target).non_colloquial

    def question_meanings(self, question: Label, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(self.language_pair.source).with_same_grammatical_categories_as(question)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers.with_same_grammatical_categories_as(question) if question.colloquial else Labels((question,))


@dataclass
class InterpretQuizFactory(TranslationQuizFactory):
    """Create interpretion quizzes for a concept."""

    quiz_type: QuizType | None = INTERPRET

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target)

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.source).non_colloquial

    def question_meanings(self, question: Label, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(self.language_pair.target).with_same_grammatical_categories_as(question)


@dataclass
class GrammaticalQuizFactory(BaseQuizFactory):
    """Create grammatical quizzes for a concept."""

    def create_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes."""
        quizzes = Quizzes()
        for question_label, answer_label in permutations(concept.labels(self.language_pair.target).non_colloquial, r=2):
            self.quiz_type = self.grammatical_quiz_type(question_label, answer_label)
            self._question = question_label
            self._answer = answer_label
            quizzes |= super().create_quizzes(concept, Quizzes(previous_quizzes | quizzes))
        return quizzes

    @staticmethod
    def grammatical_quiz_type(label1: Label, label2: Label) -> QuizType | None:
        """Return the quiz type to change the grammatical category of label1 into that of label2.

        For example, to change "I am" into "they are" would mean changing the grammatical number from singular to plural
        and changing the grammatical person from first person to third person. To prevent the quiz from becoming too
        complex ("Give the affirmative past tense plural third person...") we limit the number of quiz types.
        """
        quiz_types: list[GrammaticalQuizType] = []
        for grammatical_category in label2.grammatical_differences(label1):
            quiz_types.extend(GrammaticalQuizType.instances.get_values(grammatical_category))
        if set(quiz_types) <= {FEMININE, MASCULINE, NEUTER, THIRD_PERSON} and len(quiz_types) > 1:
            return GrammaticalQuizType(quiz_types=frozenset(quiz_types))
        return quiz_types[0] if len(quiz_types) == 1 else None

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return Labels((self._question,))

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return Labels((self._answer,))

    def question_meanings(self, question: Label, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(self.language_pair.source).with_same_grammatical_categories_as(question)

    def answer_meanings(self, answer: Label, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        return concept.meanings(self.language_pair.source).with_same_grammatical_categories_as(answer)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return Labels((answer,))

    def zip_questions_and_answers(self, questions: Labels, answers: Labels) -> Iterable[tuple[Label, Label]]:
        """Zip the questions and answers."""
        return zip(questions, answers, strict=False)

    def include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return (
            question.grammatical_form.grammatical_base == answer.grammatical_form.grammatical_base
            and not question.is_homograph(answer)
        )


@dataclass
class OrderQuizFactory(BaseQuizFactory):
    """Create order quizzes for a concept."""

    MIN_WORD_COUNT: ClassVar[int] = 5
    quiz_type: QuizType | None = ORDER

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target).non_colloquial

    def answer_meanings(self, answer: Label, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        return concept.meanings(self.language_pair.source)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return Labels((question,))  # Question and answer are equal, the question is shuffled when the quiz is presented

    def include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return question.word_count >= self.MIN_WORD_COUNT


@dataclass
class ClozeTestQuizFactory(BaseQuizFactory):
    """Create cloze test quizzes for a concept."""

    quiz_type: QuizType | None = CLOZE_TEST

    def questions(self, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.language_pair.target).cloze_tests

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(self.language_pair.target)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers

    def question_meanings(self, question: Label, concept: Concept) -> Labels:
        """Return the question meanings."""
        return concept.labels(self.language_pair.source)

    def skip_quiz_type(self, concept: Concept) -> bool:
        """Return whether to create quizzes for the quiz type."""
        return not self.questions(concept)


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
        return concept.labels(self.language_pair.target).non_colloquial

    def question_meanings(self, question: Label, concept: Concept) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(self.language_pair.source)

    def answers(self, concept: Concept) -> Labels:
        """Return the answers."""
        labels = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            labels.extend(list(related_concept.labels(self.language_pair.target)))
        return Labels(labels)

    def answer_meanings(self, answer: Label, concept: Concept) -> Labels:
        """Return the answer meanings of the concept."""
        meanings: list[Label] = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            meanings.extend(related_concept.meanings(self.language_pair.source))
        return Labels(meanings)

    def answers_for_question(self, question: Label, answer: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers.with_same_grammatical_categories_as(question)

    def blocked_by(self, concept: Concept, previous_quizzes: Quizzes) -> tuple[Quiz, ...]:
        """Return the quizzes that block the created quizzes."""
        for related_concept in concept.get_related_concepts(self.concept_relation):
            previous_quizzes |= QuizFactory(self.language_pair, ()).translation_quizzes(related_concept)
        return super().blocked_by(concept, previous_quizzes)


@dataclass(frozen=True)
class QuizFactory:
    """Create quizzes for multiple concepts."""

    language_pair: LanguagePair
    quiz_types: tuple[QuizType, ...]
    factories: dict[type[BaseQuizFactory], BaseQuizFactory] = field(default_factory=dict)

    def create_quizzes(self, *concepts: Concept) -> Quizzes:
        """Create quizzes for the concepts."""
        return Quizzes(Quizzes().union(*(self.concept_quizzes(concept, Quizzes()) for concept in concepts)))

    def concept_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create the quizzes for a concept."""
        previous_quizzes = previous_quizzes or Quizzes()
        translation_quizzes = self.translation_quizzes(concept, previous_quizzes)
        previous_quizzes |= translation_quizzes
        semantic_quizzes = self.semantic_quizzes(concept, Quizzes(translation_quizzes | previous_quizzes))
        previous_quizzes |= semantic_quizzes
        grammatical_quizzes = self._quizzes(concept, previous_quizzes, GrammaticalQuizFactory)
        return Quizzes(translation_quizzes | semantic_quizzes | grammatical_quizzes)

    def translation_quizzes(self, concept: Concept, previous_quizzes: Quizzes | None = None) -> Quizzes:
        """Create the translation quizzes for a concept."""
        previous_quizzes = previous_quizzes or Quizzes()
        read_quizzes = self._quizzes(concept, previous_quizzes, ReadQuizFactory)
        previous_quizzes |= read_quizzes
        dictate_quizzes = self._quizzes(concept, previous_quizzes, DictateQuizFactory)
        previous_quizzes |= dictate_quizzes
        write_quizzes = self._quizzes(concept, previous_quizzes, WriteQuizFactory)
        previous_quizzes |= write_quizzes
        interpret_quizzes = self._quizzes(concept, previous_quizzes, InterpretQuizFactory)
        return Quizzes(read_quizzes | write_quizzes | dictate_quizzes | interpret_quizzes)

    def semantic_quizzes(self, concept: Concept, previous_quizzes: Quizzes) -> Quizzes:
        """Create semantic quizzes for the concept."""
        semantic_quizzes = self._quizzes(concept, previous_quizzes, SemanticQuizFactory)
        semantic_quizzes |= self._quizzes(concept, previous_quizzes, OrderQuizFactory)
        semantic_quizzes |= self._quizzes(concept, previous_quizzes, ClozeTestQuizFactory)
        return semantic_quizzes

    def _quizzes(self, concept: Concept, previous_quizzes: Quizzes, factory_class: type[BaseQuizFactory]) -> Quizzes:
        """Create the quizzes for a concept using the quiz factory."""
        return self._factory(factory_class).create_quizzes(concept, previous_quizzes)

    def _factory(self, factory_class: type[BaseQuizFactory]) -> BaseQuizFactory:
        """Create and cache the factory."""
        if factory := self.factories.get(factory_class):
            return factory
        return self.factories.setdefault(factory_class, factory_class(self.language_pair, self.quiz_types))


def create_quizzes(language_pair: LanguagePair, quiz_types: tuple[QuizType, ...], *concepts: Concept) -> Quizzes:
    """Create quizzes for the concepts, using the target and source language."""
    return QuizFactory(language_pair, quiz_types).create_quizzes(*concepts)
