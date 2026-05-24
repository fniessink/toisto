"""Quiz types."""

from __future__ import annotations

import random
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain, permutations
from typing import ClassVar, final

from toisto.model.language import Language, LanguagePair
from toisto.model.language.concept import Concept, ConceptRelation
from toisto.model.language.iana_language_subtag_registry import ALL_LANGUAGES
from toisto.model.language.label import Label, Labels
from toisto.tools import first
from toisto.ui.dictionary import linkified
from toisto.ui.format import quoted

from .tips import homonym_tips

type QuizAction = str


class QuizDirection(Enum):
    """The language relationship between a quiz's question and its answer.

    SOURCE_TO_SOURCE is intentionally omitted: no use quizzing the user in a language they already speak.
    """

    TARGET_TO_SOURCE = auto()
    SOURCE_TO_TARGET = auto()
    TARGET_TO_TARGET = auto()

    def question_language(self, language_pair: LanguagePair) -> Language:
        """Return the language the question is presented in."""
        return language_pair.source if self is QuizDirection.SOURCE_TO_TARGET else language_pair.target

    def answer_language(self, language_pair: LanguagePair) -> Language:
        """Return the language the answer is expected in."""
        return language_pair.source if self is QuizDirection.TARGET_TO_SOURCE else language_pair.target

    def meaning_language(self, language_pair: LanguagePair) -> Language:
        """Return the language the meaning is to be given in."""
        source, target = language_pair.source, language_pair.target
        return source if self.answer_language(language_pair) is target else target


@dataclass(frozen=True)
class QuizType:
    """Base quiz type."""

    action: QuizAction = ""  # Default action for the quiz type
    _instruction: str = ""  # Instruction telling the user what action(s) they need to perform to answer the quiz
    direction: QuizDirection = QuizDirection.TARGET_TO_SOURCE  # Languages of question and answer

    def _skip_concept(self, language_pair: LanguagePair, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return concept.answer_only or not self._questions(language_pair, concept)

    def instruction(self, question: Label, action: QuizAction) -> str:
        """Return the quiz type instruction. Subclasses may use the question to generate the instruction."""
        return self._instruction or f"Give the [underline]{action}[/underline] in"

    def _questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the questions."""
        return concept.labels(self.direction.question_language(language_pair)).non_colloquial

    def question(self, question: Label) -> Label:
        """Return the question for the quiz type. Can be overridden for quiz types that transform questions."""
        return question

    def _include_question(self, question: Label) -> bool:
        """Return whether to include the question."""
        return True

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Return the question meanings. Subclasses may use question and concept to derive the question meanings."""
        if self.direction.meaning_language(language_pair) == self.direction.question_language(language_pair):
            return Labels()  # Meaning would duplicate the question text
        return self._concept_meanings(language_pair, concept, question)

    def _answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Return the answers. Subclasses may use the concept to derive the answers."""
        return concept.labels(self.direction.answer_language(language_pair)).non_colloquial

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Return the answer meanings. Subclasses may use answer and concept to derive the answer meanings."""
        if self.direction.meaning_language(language_pair) == self.direction.question_language(language_pair):
            return Labels()  # Meaning would duplicate the answer text
        return self._concept_meanings(language_pair, concept, answer)

    def _concept_meanings(self, language_pair: LanguagePair, concept: Concept, label: Label) -> Labels:
        """Return the meanings of the concept, in the language not used for the answer."""
        meaning_language = self.direction.meaning_language(language_pair)
        return concept.meanings(meaning_language).with_same_grammatical_categories_as(label)

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
        if self._include_grammatical_notes() and question.other_grammatical_categories:
            other_category, other_label = random.choice(list(question.other_grammatical_categories.items()))  # noqa: S311 # nosec
            also = " also" if str(question) == str(other_label) else ""
            question_str = quoted(linkified(str(question)))
            other_label_str = quoted(linkified(str(other_label)))
            notes.append(f"The {other_category} of {question_str} is{also} {other_label_str}.")
        return tuple(notes)

    def _include_grammatical_notes(self) -> bool:
        """Return whether to include the grammatical notes for the grammatical categories."""
        return True

    def other_answers(self, guess: str, answers: Labels) -> Labels:
        """Return the alternate valid answers not equal to the guess."""
        return answers.not_matching(guess, case_sensitive=False)

    def is_quiz_type(self, quiz_type: QuizType | type[QuizType]) -> bool:
        """Return whether this quiz type matches the given quiz type."""
        return quiz_type == self if isinstance(quiz_type, QuizType) else isinstance(self, quiz_type)

    def questions_and_answers(
        self, language_pair: LanguagePair, concept: Concept
    ) -> Iterable[tuple[Label, Labels, QuizAction]]:
        """Generate the questions and answers for each question."""
        if self._skip_concept(language_pair, concept):
            return []
        questions = self._questions(language_pair, concept)
        answers = self._answers(language_pair, concept)
        return [
            (question, answers_for_question, self.action)
            for question in questions
            if self._include_question(question)
            and (answers_for_question := self._answers_for_question(question, answers))
        ]

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:
        """Return the answers grammatically compatible with the question (no-op when labels have no categories)."""
        return answers.with_compatible_grammatical_categories_as(question)

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return False


@dataclass(frozen=True)
class ListenOnlyQuizType(QuizType):
    """Listen-only quiz type."""

    def _questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Override to include colloquial labels: the user listens to colloquial forms and writes the standard form."""
        return concept.labels(self.direction.question_language(language_pair))

    def question_meanings(self, language_pair: LanguagePair, concept: Concept, question: Label) -> Labels:
        """Override to bypass the base's redundancy check: writing out the audio is always informative."""
        return self._concept_meanings(language_pair, concept, question)

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return True if isinstance(quiz_type, TranslationQuizType) else super().blocked_by(quiz_type)

    def instruction(self, question: Label, action: QuizAction) -> str:
        """Override to return the quiz type instruction for listen-only quizzes."""
        colloquial_note = f"to the colloquial {ALL_LANGUAGES[question.language]} " if question.colloquial else ""
        write_part = "write a complete sentence" if question.is_complete_sentence else "write"
        return f"Listen {colloquial_note}and {write_part} in"

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
        return super()._skip_concept(language_pair, concept) or not self._answers(language_pair, concept)


@dataclass(frozen=True)
class SemanticQuizType(QuizType):
    """Semantic quiz type."""

    direction: QuizDirection = QuizDirection.TARGET_TO_TARGET

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return True if not isinstance(quiz_type, self.__class__) else super().blocked_by(quiz_type)

    def _tips_applicable(self, question: Label, answer: Label) -> bool:
        """Override to return True because semantic quizzes should always get a tip."""
        return True

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:
        """Return the answers for the question."""
        return answers.with_same_grammatical_categories_as(question)


@dataclass(frozen=True)
class GrammaticalQuizType(QuizType):
    """Grammatical quiz type."""

    direction: QuizDirection = QuizDirection.TARGET_TO_TARGET

    # Gender (feminine/masculine/neuter) is only marked on the third person, so these categories combine as a single
    # compound action like "feminine third person" without becoming opaque. Other combinations would produce confusing
    # prompts ("Give the affirmative past tense plural third person..."), so they are reduced to a single action.
    COMBINABLE_ACTIONS: ClassVar[frozenset[QuizAction]] = frozenset({"feminine", "masculine", "neuter", "third person"})

    def questions_and_answers(
        self, language_pair: LanguagePair, concept: Concept
    ) -> Iterable[tuple[Label, Labels, QuizAction]]:
        """Generate the questions and answers for each question."""
        results = []
        question_language = self.direction.question_language(language_pair)
        for question, answer in permutations(concept.labels(question_language).non_colloquial, r=2):
            if self._include_pair(question, answer) and (action := self.grammatical_quiz_action(question, answer)):
                results.append((question, Labels((answer,)), action))
        return results

    def blocked_by(self, quiz_type: QuizType) -> bool:
        """Return whether this quiz type is blocked by the given quiz type."""
        return super().blocked_by(quiz_type) if isinstance(quiz_type, self.__class__) else True

    @staticmethod
    def _include_pair(question: Label, answer: Label) -> bool:
        """Return whether to include a (question, answer) pair as a grammatical quiz."""
        return question.has_same_grammatical_base(answer) and not question.is_homograph(answer)

    def _include_grammatical_notes(self) -> bool:
        """Return whether to include the grammatical notes for the grammatical categories."""
        return False

    @classmethod
    def grammatical_quiz_action(cls, label1: Label, label2: Label) -> QuizAction | None:
        """Return the quiz action to change the grammatical category of label1 into that of label2.

        For example, to change "I am" into "they are" would mean changing the grammatical number from singular to plural
        and changing the grammatical person from first person to third person. To prevent the quiz from becoming too
        complex ("Give the affirmative past tense plural third person...") we only combine actions when all of them
        come from COMBINABLE_ACTIONS; otherwise the quiz requires a single action.
        """
        quiz_actions = {
            quiz_type.action
            for quiz_type in GRAMMATICAL_QUIZ_TYPES
            if quiz_type.action in label2.grammatical_differences(label1)
        }
        if quiz_actions <= cls.COMBINABLE_ACTIONS and len(quiz_actions) > 1:
            return " ".join(sorted(quiz_actions))
        return first(quiz_actions) if len(quiz_actions) == 1 else None


@dataclass(frozen=True)
class ReproductionQuizType(QuizType):
    """Quiz type where the user reproduces a single specific form.

    Because there is only one expected answer, no alternate valid answers are shown after a correct response.
    """

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Override to return no meanings.

        User reproduces the question, so answer and question meanings are the same.
        """
        return Labels()

    def other_answers(self, guess: str, answers: Labels) -> Labels:
        """Override to return no alternates.

        This quiz type expects a specific reproduction, not one of many translations.
        """
        return Labels()


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
    direction: QuizDirection = QuizDirection.SOURCE_TO_TARGET

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

    def _include_question(self, question: Label) -> bool:
        """Return whether to include the question."""
        return question.word_count >= self.MIN_WORD_COUNT

    def question(self, question: Label) -> Label:
        """Override to randomize the word order."""
        return question.random_order

    @staticmethod
    def _answers_for_question(question: Label, answers: Labels) -> Labels:  # noqa: ARG004
        """Return the answers for the question."""
        return Labels((question,))  # Question and answer are equal, the question is shuffled when the quiz is presented


@dataclass(frozen=True)
class RelationshipQuizType(SemanticQuizType):
    """Quiz type based on a concept relationship (e.g., antonym, answer)."""

    concept_relation: ConceptRelation = "answer"

    def _skip_concept(self, language_pair: LanguagePair, concept: Concept) -> bool:
        """Return whether to create quizzes for the concept."""
        return super()._skip_concept(language_pair, concept) or not concept.get_related_concepts(self.concept_relation)

    def _answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Override to take answers from concepts related to this one via concept_relation."""
        labels = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            labels.extend(list(related_concept.labels(self.direction.answer_language(language_pair))))
        return Labels(labels)

    def answer_meanings(self, language_pair: LanguagePair, concept: Concept, answer: Label) -> Labels:
        """Override to take answer meanings from concepts related to this one via concept_relation."""
        meaning_language = self.direction.meaning_language(language_pair)
        meanings: list[Label] = []
        for related_concept in concept.get_related_concepts(self.concept_relation):
            meanings.extend(related_concept.meanings(meaning_language))
        return Labels(meanings)


@final
@dataclass(frozen=True)
class ClozeTestQuizType(ReproductionQuizType):
    """Cloze test quiz type."""

    action: QuizAction = "cloze"
    _instruction: str = "Repeat with the [underline]bracketed words in the correct form[/underline], in"
    direction: QuizDirection = QuizDirection.TARGET_TO_TARGET

    def _questions(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Override to return cloze-test labels instead of regular labels."""
        return concept.labels(self.direction.question_language(language_pair)).cloze_tests

    def _answers(self, language_pair: LanguagePair, concept: Concept) -> Labels:
        """Override because cloze answers include colloquial labels (no .non_colloquial filter)."""
        return concept.labels(self.direction.answer_language(language_pair))


@final
@dataclass(frozen=True)
class DictateQuizType(ListenOnlyQuizType, ReproductionQuizType):
    """Dictate quiz type."""

    action: QuizAction = "dictate"
    direction: QuizDirection = QuizDirection.TARGET_TO_TARGET

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


# Translate quiz types
READ = ReadQuizType()
WRITE = WriteQuizType()

# Listen-only quiz types
DICTATE = DictateQuizType()
INTERPRET = InterpretQuizType()

# Semantic quiz types
ANSWER = RelationshipQuizType(action="answer", concept_relation="answer")
ANTONYM = RelationshipQuizType(action="antonym", concept_relation="antonym")
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
