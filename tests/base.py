"""Base class for unit tests."""

import unittest
from collections.abc import Collection, Sequence
from io import StringIO
from typing import Final, Required, TypedDict, cast

from green.output import GreenStream
from xmlrunner.result import _DuplicateWriter as DuplicateWriter

from toisto.model.language import EN, FI, NL, Language, LanguagePair
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptJSON, LabelJSON, create_concept
from toisto.model.language.label import Label, Labels
from toisto.model.quiz.quiz import Quiz
from toisto.model.quiz.quiz_type import READ, QuizType

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

ConceptIdListOrString = str | list[str]
ConceptIdDictOrListOrString = dict[str, ConceptIdListOrString] | ConceptIdListOrString

ConceptDict = TypedDict(
    "ConceptDict",
    {
        "antonym": ConceptIdListOrString,
        "answer": ConceptIdListOrString,
        "answer-only": bool,
        "example": ConceptIdListOrString,
        "holonym": ConceptIdListOrString,
        "hypernym": ConceptIdListOrString,
        "involves": ConceptIdListOrString,
        "roots": ConceptIdDictOrListOrString,
    },
    total=False,
)

LabelDict = TypedDict(
    "LabelDict",
    {
        "colloquial": bool,
        "concept": ConceptIdListOrString,
        "label": (
            Required[
                str
                | list[str]
                | dict[str, Collection[str]]
                | dict[str, list[str]]
                | dict[str, str]
                | dict[str, dict[str, str]]
                | dict[str, str | dict[str, str]]
                | dict[str, dict[str, dict[str, str]]]
            ]
        ),
        "language": Required[Language],
        "meaning-only": bool,
        "note": str | list[str],
        "roots": str | list[str],
        "tip": str,
    },
    total=False,
)


class ToistoTestCase(unittest.TestCase):
    """Base class for Toisto unit tests."""

    def tearDown(self) -> None:
        """Clear the registries."""
        Concept.instances.clear()
        Concept.capitonyms.clear()
        Concept.homographs.clear()

    @staticmethod
    def create_concept(
        concept_id: str, concept_dict: ConceptDict | None = None, labels: list[LabelDict] | None = None
    ) -> Concept:
        """Create a concept."""
        concept_dict = concept_dict or {}
        labels = labels or []
        for label in labels:
            if "concept" not in label:
                label["concept"] = concept_id
        return create_concept(
            cast("ConceptId", concept_id), cast("ConceptJSON", concept_dict), cast("list[LabelJSON]", labels)
        )

    def create_quiz(
        self,
        concept: Concept,
        question: Label,
        answers: Sequence[Label],
        quiz_type: QuizType = READ,
        blocked_by: tuple[Quiz, ...] = (),
    ) -> Quiz:
        """Create a quiz."""
        return Quiz(concept, question, Labels(answers), quiz_type, blocked_by)

    def copy_quiz(
        self,
        quiz: Quiz,
        question: Label | None = None,
        answers: Sequence[Label] | None = None,
        quiz_type: QuizType | None = None,
    ) -> Quiz:
        """Copy the quiz, overriding some of its parameters."""
        return self.create_quiz(
            quiz.concept,
            question=question or quiz.question,
            answers=answers or list(quiz.answers),
            quiz_type=quiz_type or quiz.quiz_type,
            blocked_by=quiz.blocked_by,
        )

    def create_noun_invariant_in_english(self) -> Concept:
        """Return a concept that is composite in Dutch and not composite in English."""
        return self.create_concept(
            "means of transportation",
            labels=[
                {"label": "means of transportation", "language": EN},
                {"label": {"singular": "het vervoersmiddel", "plural": "de vervoersmiddelen"}, "language": NL},
            ],
        )

    def create_verb_with_grammatical_number_and_person(self) -> Concept:
        """Create a verb with grammatical number nested with grammatical person."""
        return self.create_concept(
            "to have",
            labels=[
                {
                    "label": {
                        "singular": {"first person": "I have", "second person": "you have", "third person": "she has"},
                        "plural": {"first person": "we have", "second person": "you have", "third person": "they have"},
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "singular": {
                            "first person": "minulla on",
                            "second person": "sinulla on",
                            "third person": "hänellä on",
                        },
                        "plural": {
                            "first person": "meillä on",
                            "second person": "teillä on",
                            "third person": "heillä on",
                        },
                    },
                    "language": FI,
                },
                {
                    "label": {
                        "singular": {
                            "first person": "ik heb",
                            "second person": "jij hebt",
                            "third person": "zij heeft",
                        },
                        "plural": {
                            "first person": "wij hebben",
                            "second person": "jullie hebben",
                            "third person": "zij hebben",
                        },
                    },
                    "language": NL,
                },
            ],
        )
