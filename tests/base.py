"""Base class for unit tests."""

import unittest
from collections.abc import Sequence
from io import StringIO
from typing import Final, cast

from green.output import GreenStream
from xmlrunner.result import _DuplicateWriter as DuplicateWriter

from toisto.model.language import EN, FI, NL, Language, LanguagePair
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import INTERPRET, READ, WRITE, QuizType

# The DramaticTextIOWrapper of the dramatic package expects the stdout stream to have a buffer attribute,
# but the GreenStream created by green and the DuplicateWriter created by xmlrunner do not have one, causing an
# AttributeError: 'GreenStream' object has no attribute 'buffer'. Adding a StringIO buffer attribute to the
# GreenStream class and DuplicateWriter class works around this:
GreenStream.buffer = StringIO()
DuplicateWriter.buffer = StringIO()

# Language pairs (target, source) used in the unit tests
EN_FI: Final[LanguagePair] = LanguagePair(EN, FI)
EN_NL: Final[LanguagePair] = LanguagePair(EN, NL)
FI_EN: Final[LanguagePair] = LanguagePair(FI, EN)
FI_NL: Final[LanguagePair] = LanguagePair(FI, NL)
NL_EN: Final[LanguagePair] = LanguagePair(NL, EN)
NL_FI: Final[LanguagePair] = LanguagePair(NL, FI)


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    def setUp(self) -> None:
        """Set up a default language pair."""
        self.language_pair = EN_FI

    def tearDown(self) -> None:
        """Clear the registries."""
        Concept.instances.clear()
        Concept.capitonyms.clear()
        Concept.homographs.clear()

    @staticmethod
    def create_concept(concept_id: str, concept_dict: dict[str, object]) -> Concept:
        """Create a concept."""
        return create_concept(cast(ConceptId, concept_id), cast(ConceptDict, concept_dict))

    def create_quiz(  # noqa: PLR0913
        self,
        concept: Concept,
        question: str,
        answers: Sequence[str],
        quiz_type: QuizType = READ,
        blocked_by: tuple[Quiz, ...] = (),
        question_meanings: tuple[str, ...] = (),
        answer_meanings: tuple[str, ...] = (),
        language_pair: LanguagePair | None = None,
    ) -> Quiz:
        """Create a quiz."""
        language_pair = self.language_pair if language_pair is None else language_pair
        question_language = self.question_language(language_pair, quiz_type)
        answer_language = self.answer_language(language_pair, quiz_type)
        return Quiz(
            concept,
            Label(question_language, question),
            Labels(Label(answer_language, answer) for answer in answers),
            quiz_type,
            blocked_by,
            Labels(Label(question_language, meaning) for meaning in question_meanings),
            Labels(Label(answer_language, meaning) for meaning in answer_meanings),
        )

    def copy_quiz(
        self,
        quiz: Quiz,
        question: str = "",
        answers: list[str] | None = None,
        quiz_type: QuizType | None = None,
    ) -> Quiz:
        """Copy the quiz, overriding some of its parameters."""
        return self.create_quiz(
            quiz.concept,
            question=question or str(quiz.question),
            answers=answers or quiz.answers.as_strings,
            blocked_by=quiz.blocked_by,
            question_meanings=quiz.question_meanings.as_strings,
            answer_meanings=quiz.answer_meanings.as_strings,
            quiz_type=quiz_type or quiz.quiz_type,
        )

    @staticmethod
    def question_language(language_pair: LanguagePair, quiz_type: QuizType) -> Language:
        """Return the question language for the quiz types, given the target and source languages."""
        return language_pair.source if quiz_type == WRITE else language_pair.target

    @staticmethod
    def answer_language(language_pair: LanguagePair, quiz_type: QuizType) -> Language:
        """Return the answer language for the quiz types, given the target and source languages."""
        return language_pair.source if quiz_type in (INTERPRET, READ) else language_pair.target

    def create_noun_invariant_in_english(self) -> Concept:
        """Return a concept that is composite in Dutch and not composite in English."""
        return self.create_concept(
            "means of transportation",
            dict(
                en="means of transportation",
                singular=dict(nl="het vervoersmiddel"),
                plural=dict(nl="de vervoersmiddelen"),
            ),
        )

    def create_verb_with_grammatical_number_and_person(self) -> Concept:
        """Create a verb with grammatical number nested with grammatical person."""
        return self.create_concept(
            "to have",
            dict(
                singular={
                    "first person": dict(en="I have", fi="minulla on", nl="ik heb"),
                    "second person": dict(en="you have", fi="sinulla on", nl="jij hebt"),
                    "third person": dict(en="she has", fi="hänellä on", nl="zij heeft"),
                },
                plural={
                    "first person": dict(en="we have", fi="meillä on", nl="wij hebben"),
                    "second person": dict(en="you have", fi="teillä on", nl="jullie hebben"),
                    "third person": dict(en="they have", fi="heillä on", nl="zij hebben"),
                },
            ),
        )
