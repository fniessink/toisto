"""Quiz types."""

from __future__ import annotations

import random
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import chain, permutations
from typing import ClassVar, TypeAlias, cast, final

from toisto.model.language import LanguagePair
from toisto.model.language.concept import Concept, ConceptRelation
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Label, Labels
from toisto.tools import first
from toisto.ui.dictionary import linkified
from toisto.ui.format import quoted

from .tips import homonym_tips

QuizAction: TypeAlias = str


@dataclass(frozen=True)
class QuizType:
    """Base quiz type."""

    action: QuizAction = ""  # Default action for the quiz type
    _instruction: str = ""  # Instruction telling the user what action(s) they need to perform to answer the quiz

    def _skip_concept(self, language_pair: LanguagePair, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return concept.answer_only or not self.questions(language_pair, concept)

    def instruction(self, question: Label, action: QuizAction) -> str:
        """Return the quiz type instruction. Subclasses may use the question to generate the instruction."""
        return self._instruction if self._instruction else f"Give the [underline]{action}[/underline] in"

    def questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(language_pair.target).non_colloquial

    def question(self, question: Label) -> Label:
        """Return the question for the quiz type. Can be overridden for quiz types that transform questions."""
        return question

    def _include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return question.grammatical_form == answer.grammatical_form

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings. Subclasses may use question and concept to derive the question meanings."""
        return Labels()

    def answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the answers. Subclasses may use the concept to derive the answers."""
        return concept.labels(language_pair.source).non_colloquial

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Return the answer meanings. Subclasses may use answer and concept to derive the answer meanings."""
        return Labels()

    def tips(self, concept: Concept, question: Label, answers: Labels) -> Sequence[str]:
        """Return the tips to be shown before the quiz has been answered."""
        tips = list(question.tips) if question.tips and self._tips_applicable(question, first(answers)) else []
        tips.extend(self._homonym_tips(concept, question))
        return tips

    def _homonym_tips(self, concept: Concept, question: Label) -> Sequence[str]:
        """Return the extra tip for homonyms."""
        if homographs := question.homographs:
            return homonym_tips(concept, question, *homographs)
        return []

    def _tips_applicable(self, question: Label, answer: Label) -> bool:
        """Return whether the quiz should get tips."""
        return question.language != answer.language

    def notes(self, question: Label, answers: Labels) -> Sequence[str]:
        """Return the notes to be shown after the quiz has been answered.

        Subclasses may use the answers to generate the notes.
        """
        notes = [re.sub("'([^']+)'", lambda match: linkified(str(match[0])), note) for note in question.notes]
        if self._include_grammatical_notes() and question.grammatical_form.other_grammatical_categories:
            other_category = random.choice(list(question.grammatical_form.other_grammatical_categories.keys()))  # noqa: S311 # nosec
            other_label = question.grammatical_form.other_grammatical_categories[other_category]
            also = " also" if str(question) == str(other_label) else ""
            question_str = quoted(linkified(str(question)))
            other_label_str = quoted(linkified(str(other_label)))
            notes.append(f"The {other_category} of {question_str} is{also} {other_label_str}.")
        return tuple(notes)

    def _include_grammatical_notes(self) -> bool:
        """Return whether to include the grammatical notes for the grammatical categories."""
        return True

    def other_answers(self, guess: str, answers: Labels) -> Labels:
        """Return the answers not equal to the guess."""
        return Labels(
            answer for answer in answers if not answer.spelling_alternatives.matching(guess, case_sensitive=False)
        )

    def is_quiz_type(self, quiz_type: QuizType | type[QuizType]) -> bool:
        """Return whether this quiz type matches the given quiz type."""
        return quiz_type == self if isinstance(quiz_type, QuizType) else isinstance(self, quiz_type)

    def questions_and_answers(
        self, language_pair: LanguagePair, concept: Concept
    ) -> Iterable[tuple[Label, Labels, QuizAction]]:
        """Generate the questions and answers for each question."""
        if self._skip_concept(language_pair, concept):
            return []
        questions = self.questions(language_pair, concept)
        answers = self.answers(language_pair, concept)
        return [
            (question, answers_for_question, self.action)
            for question, answer in zip(questions, questions, strict=True)
            if self._include_question(question, answer)
            and (answers_for_question := self._answers_for_question(question, answers))
        ]

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:  # noqa: ARG004
        """Return the answers for the question."""
        return answers

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return False


@dataclass(frozen=True)
class ListenOnlyQuizType(QuizType):
    """Listen-only quiz type."""

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return True if isinstance(quiz_type, TranslationQuizType) else super().blocked_by(quiz_type)

    def instruction(self, question: Label, action: QuizAction) -> str:
        """Override to return the quiz type instruction for listen-only quizzes."""
        colloquial_note = f"to the colloquial {ALL_LANGUAGES[question.language]} "
        return f"Listen {colloquial_note if question.colloquial else ''}and write in"

    def other_answers(self, guess: str, answers: Labels) -> Labels:
        """Override because returning other answers doesn't make sense if the user has to type what is spoken."""
        return Labels()

    def _homonym_tips(self, concept: Concept, question: Label) -> Sequence[str]:
        """Return the extra tip for homonyms."""
        if tips := super()._homonym_tips(concept, question):
            return tips
        if capitonyms := question.capitonyms:
            return homonym_tips(concept, question, *capitonyms)
        return []


@dataclass(frozen=True)
class TranslationQuizType(QuizType):
    """Translation quiz type."""

    _instruction: str = "Translate into"

    def _skip_concept(self, language_pair: LanguagePair, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return super()._skip_concept(language_pair, concept) or not self.answers(language_pair, concept)

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:
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


@dataclass(frozen=True)
class SemanticQuizType(QuizType):
    """Semantic quiz type."""

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return True if not isinstance(quiz_type, self.__class__) else super().blocked_by(quiz_type)

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(language_pair.source)

    def answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the answers."""
        labels = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            labels.extend(list(related_concept.labels(language_pair.target)))
        return Labels(labels)

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Return the answer meanings of the concept."""
        meanings: list[Label] = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            meanings.extend(related_concept.meanings(language_pair.source))
        return Labels(meanings)

    def _tips_applicable(self, question: Label, answer: Label) -> bool:
        """Override to return True because semantic quizzes should always get a tip."""
        return True

    @property
    def concept_relation(self) -> ConceptRelation:
        """Return the concept relation that the quiz type is quizzing."""
        return cast("ConceptRelation", self.action)

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers.with_same_grammatical_categories_as(question)


@dataclass(frozen=True)
class GrammaticalQuizType(QuizType):
    """Grammatical quiz type."""

    def questions_and_answers(
        self, language_pair: LanguagePair, concept: Concept
    ) -> Iterable[tuple[Label, Labels, QuizAction]]:
        """Generate the questions and answers for each question."""
        results = []
        for question, answer in permutations(concept.labels(language_pair.target).non_colloquial, r=2):
            if self._include_question(question, answer) and (action := self.grammatical_quiz_action(question, answer)):
                results.append((question, Labels((answer,)), action))
        return results

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return super().blocked_by(quiz_type) if isinstance(quiz_type, self.__class__) else True

    def _include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return (
            question.grammatical_form.grammatical_base == answer.grammatical_form.grammatical_base
            and not question.is_homograph(answer)
        )

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(language_pair.source).with_same_grammatical_categories_as(question)

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Return the answer meanings of the concept."""
        return concept.meanings(language_pair.source).with_same_grammatical_categories_as(answer)

    def _include_grammatical_notes(self) -> bool:
        """Return whether to include the grammatical notes for the grammatical categories."""
        return False

    @classmethod
    def grammatical_quiz_action(cls, label1: Label, label2: Label) -> QuizAction | None:
        """Return the quiz action to change the grammatical category of label1 into that of label2.

        For example, to change "I am" into "they are" would mean changing the grammatical number from singular to plural
        and changing the grammatical person from first person to third person. To prevent the quiz from becoming too
        complex ("Give the affirmative past tense plural third person...") we limit the number of quiz actions.
        """
        quiz_actions = {
            quiz_type.action
            for quiz_type in GRAMMATICAL_QUIZ_TYPES
            if quiz_type.action in label2.grammatical_differences(label1)
        }
        if quiz_actions <= {"feminine", "masculine", "neuter", "third person"} and len(quiz_actions) > 1:
            return " ".join(sorted(quiz_actions))
        return first(quiz_actions) if len(quiz_actions) == 1 else None


@final
@dataclass(frozen=True)
class ReadQuizType(TranslationQuizType):
    """Read a translation quiz type."""

    action: QuizAction = "read"


@final
@dataclass(frozen=True)
class WriteQuizType(TranslationQuizType):
    """Write a translation quiz type."""

    action: QuizAction = "write"

    def questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(language_pair.source).non_colloquial

    def answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(language_pair.target).non_colloquial

    def notes(self, question: Label, answers: Labels) -> Sequence[str]:
        """Return the notes to be shown after the quiz has been answered."""
        return tuple(chain.from_iterable(answer.notes for answer in answers))


@final
@dataclass(frozen=True)
class OrderQuizType(SemanticQuizType):
    """Order quiz type."""

    MIN_WORD_COUNT: ClassVar[int] = 5

    action: QuizAction = "order"
    _instruction: str = "Give the [underline]right order[/underline] of the words in"

    def _include_question(self, question: Label, answer: Label) -> bool:
        """Return whether to include the question."""
        return question.word_count >= self.MIN_WORD_COUNT

    def question(self, question: Label) -> Label:
        """Override to randomize the word order."""
        return question.random_order

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Return the answer meanings of the concept."""
        return concept.meanings(language_pair.source)

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:  # noqa: ARG004
        """Return the answers for the question."""
        return Labels((question,))  # Question and answer are equal, the question is shuffled when the quiz is presented


@dataclass(frozen=True)
class RelationshipQuizType(SemanticQuizType):
    """Quiz type based on concept relationship."""

    def _skip_concept(self, language_pair: LanguagePair, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return super()._skip_concept(language_pair, concept) or not concept.get_related_concepts(self.concept_relation)


@final
@dataclass(frozen=True)
class ClozeTestQuizType(QuizType):
    """Cloze test quiz type."""

    action: QuizAction = "cloze"
    _instruction: str = "Repeat with the [underline]bracketed words in the correct form[/underline], in"

    def questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(language_pair.target).cloze_tests

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings."""
        return concept.labels(language_pair.source)

    def answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(language_pair.target)

    def other_answers(self, guess: str, answers: Labels) -> Labels:
        """Override because returning other answers doesn't make sense if the user has to repeat the question."""
        return Labels()


@final
@dataclass(frozen=True)
class DictateQuizType(ListenOnlyQuizType):
    """Dictate quiz type."""

    action: QuizAction = "dictate"

    def questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(language_pair.target)

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(language_pair.source).with_same_grammatical_categories_as(question)

    def answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the answers."""
        return concept.labels(language_pair.target).non_colloquial

    def instruction(self, question: Label, action: QuizAction) -> str:
        """Extend to add "standard" for dictate quizzes."""
        instruction = super().instruction(question, action)
        return instruction + " standard" if question.colloquial else instruction

    def _tips_applicable(self, question: Label, answer: Label) -> bool:
        """Override to return True because dictate quizzes should always get a tip."""
        return True

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers.with_same_grammatical_categories_as(question) if question.colloquial else Labels((question,))


@final
@dataclass(frozen=True)
class InterpretQuizType(ListenOnlyQuizType):
    """Interpret quiz type."""

    action: QuizAction = "interpret"

    def questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(language_pair.target)

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings of the concept."""
        return concept.meanings(language_pair.target).with_same_grammatical_categories_as(question)

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:
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


# Translate quiz types
READ = ReadQuizType()
WRITE = WriteQuizType()

# Listen-only quiz types
DICTATE = DictateQuizType()
INTERPRET = InterpretQuizType()

# Semantic quiz types
ANSWER = RelationshipQuizType("answer")
ANTONYM = RelationshipQuizType("antonym")
ORDER = OrderQuizType()

# Cloze test
CLOZE_TEST = ClozeTestQuizType()

# Non-grammatical quiz types
NON_GRAMMATICAL_QUIZ_TYPES = (READ, DICTATE, WRITE, INTERPRET, CLOZE_TEST, ANSWER, ANTONYM, ORDER)

# Grammatical quiz types
PLURAL = GrammaticalQuizType("plural")
SINGULAR = GrammaticalQuizType("singular")
PLURAL_PRONOUN = GrammaticalQuizType("plural pronoun")
SINGULAR_PRONOUN = GrammaticalQuizType("singular pronoun")
FIRST_PERSON = GrammaticalQuizType("first person")
SECOND_PERSON = GrammaticalQuizType("second person")
THIRD_PERSON = GrammaticalQuizType("third person")
MASCULINE = GrammaticalQuizType("masculine")
FEMININE = GrammaticalQuizType("feminine")
NEUTER = GrammaticalQuizType("neuter")
PRESENT_TENSE = GrammaticalQuizType("present tense")
PAST_TENSE = GrammaticalQuizType("past tense")
PERFECTIVE = GrammaticalQuizType("perfective")
IMPERFECTIVE = GrammaticalQuizType("imperfective")
INFINITIVE = GrammaticalQuizType("infinitive")
VERBAL_NOUN = GrammaticalQuizType("verbal noun")
POSITIVE_DEGREE = GrammaticalQuizType("positive degree")
COMPARATIVE_DEGREE = GrammaticalQuizType("comparative degree")
SUPERLATIVE_DEGREE = GrammaticalQuizType("superlative degree")
INTERROGATIVE = GrammaticalQuizType("interrogative")
DECLARATIVE = GrammaticalQuizType("declarative")
IMPERATIVE = GrammaticalQuizType("imperative")
AFFIRMATIVE = GrammaticalQuizType("affirmative")
NEGATIVE = GrammaticalQuizType("negative")
DIMINUTIVE = GrammaticalQuizType("diminutive")
CARDINAL = GrammaticalQuizType("cardinal")
ORDINAL = GrammaticalQuizType("ordinal")
ABBREVIATION = GrammaticalQuizType("abbreviation")
FULL_FORM = GrammaticalQuizType("full form")

GRAMMATICAL_QUIZ_TYPES = (
    PLURAL,
    SINGULAR,
    PLURAL_PRONOUN,
    SINGULAR_PRONOUN,
    FIRST_PERSON,
    SECOND_PERSON,
    THIRD_PERSON,
    MASCULINE,
    FEMININE,
    NEUTER,
    PRESENT_TENSE,
    PAST_TENSE,
    PERFECTIVE,
    IMPERFECTIVE,
    INFINITIVE,
    VERBAL_NOUN,
    POSITIVE_DEGREE,
    COMPARATIVE_DEGREE,
    SUPERLATIVE_DEGREE,
    INTERROGATIVE,
    DECLARATIVE,
    IMPERATIVE,
    AFFIRMATIVE,
    NEGATIVE,
    DIMINUTIVE,
    CARDINAL,
    ORDINAL,
    ABBREVIATION,
    FULL_FORM,
)

QUIZ_TYPES = NON_GRAMMATICAL_QUIZ_TYPES + GRAMMATICAL_QUIZ_TYPES
