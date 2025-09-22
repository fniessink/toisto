"""Degree of comparison quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import ConceptId
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import (
    ANTONYM,
    COMPARATIVE_DEGREE,
    DICTATE,
    INTERPRET,
    POSITIVE_DEGREE,
    READ,
    SUPERLATIVE_DEGREE,
    WRITE,
)

from .....base import FI_EN, NL_EN
from .quiz_factory_test_case import QuizFactoryTestCase


class DegreesOfComparisonQuizzesTest(QuizFactoryTestCase):
    """Unit tests for degrees of comparison quizzes."""

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = self.create_adjective_with_degrees_of_comparison()
        groot, groter, grootst = concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(concept, NL, EN)
            | {
                self.create_quiz(concept, groot, [groter], COMPARATIVE_DEGREE),
                self.create_quiz(concept, groot, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, groter, [groot], POSITIVE_DEGREE),
                self.create_quiz(concept, groter, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, grootst, [groot], POSITIVE_DEGREE),
                self.create_quiz(concept, grootst, [groter], COMPARATIVE_DEGREE),
            },
            create_quizzes(NL_EN, (), concept),
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        concept = self.create_concept(
            "big",
            labels=[
                {
                    "concept": "big",
                    "label": {
                        "positive degree": "big",
                        "comparative degree": "bigger",
                        "superlative degree": "biggest",
                    },
                    "language": EN,
                },
                {
                    "concept": "big",
                    "label": {"positive degree": "iso", "comparative degree": "isompi", "superlative degree": "isoin"},
                    "language": FI,
                },
                {
                    "concept": "big",
                    "label": {
                        "positive degree": "suuri",
                        "comparative degree": "suurempi",
                        "superlative degree": "suurin",
                    },
                    "language": FI,
                },
            ],
        )
        big, bigger, biggest = concept.labels(EN)
        iso, isompi, isoin, suuri, suurempi, suurin = concept.labels(FI)
        self.assertSetEqual(
            {
                self.create_quiz(concept, iso, [big], READ),
                self.create_quiz(concept, suuri, [big], READ),
                self.create_quiz(concept, iso, [iso], DICTATE),
                self.create_quiz(concept, iso, [big], INTERPRET),
                self.create_quiz(concept, suuri, [suuri], DICTATE),
                self.create_quiz(concept, suuri, [big], INTERPRET),
                self.create_quiz(concept, big, [iso, suuri], WRITE),
                self.create_quiz(concept, isompi, [bigger], READ),
                self.create_quiz(concept, suurempi, [bigger], READ),
                self.create_quiz(concept, isompi, [isompi], DICTATE),
                self.create_quiz(concept, isompi, [bigger], INTERPRET),
                self.create_quiz(concept, suurempi, [suurempi], DICTATE),
                self.create_quiz(concept, suurempi, [bigger], INTERPRET),
                self.create_quiz(concept, bigger, [isompi, suurempi], WRITE),
                self.create_quiz(concept, isoin, [biggest], READ),
                self.create_quiz(concept, suurin, [biggest], READ),
                self.create_quiz(concept, isoin, [isoin], DICTATE),
                self.create_quiz(concept, isoin, [biggest], INTERPRET),
                self.create_quiz(concept, suurin, [suurin], DICTATE),
                self.create_quiz(concept, suurin, [biggest], INTERPRET),
                self.create_quiz(concept, biggest, [isoin, suurin], WRITE),
                self.create_quiz(concept, iso, [isompi], COMPARATIVE_DEGREE),
                self.create_quiz(concept, suuri, [suurempi], COMPARATIVE_DEGREE),
                self.create_quiz(concept, iso, [isoin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, suuri, [suurin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, isompi, [iso], POSITIVE_DEGREE),
                self.create_quiz(concept, suurempi, [suuri], POSITIVE_DEGREE),
                self.create_quiz(concept, isompi, [isoin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, suurempi, [suurin], SUPERLATIVE_DEGREE),
                self.create_quiz(concept, isoin, [iso], POSITIVE_DEGREE),
                self.create_quiz(concept, suurin, [suuri], POSITIVE_DEGREE),
                self.create_quiz(concept, isoin, [isompi], COMPARATIVE_DEGREE),
                self.create_quiz(concept, suurin, [suurempi], COMPARATIVE_DEGREE),
            },
            create_quizzes(FI_EN, (), concept),
        )

    def test_degrees_of_comparison_with_antonym(self):
        """Test that quizzes can be generated for degrees of comparison with antonym."""
        big_concept = self.create_adjective_with_degrees_of_comparison(antonym="small")
        small_concept = self.create_concept(
            "small",
            {"antonym": ConceptId("big")},
            labels=[
                {
                    "label": {
                        "positive degree": "small",
                        "comparative degree": "smaller",
                        "superlative degree": "smallest",
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "positive degree": "klein",
                        "comparative degree": "kleiner",
                        "superlative degree": "kleinst",
                    },
                    "language": NL,
                },
            ],
        )
        groot, groter, grootst = big_concept.labels(NL)
        klein, kleiner, kleinst = small_concept.labels(NL)
        self.assertSetEqual(
            self.translation_quizzes(big_concept, NL, EN)
            | {
                self.create_quiz(big_concept, groot, [groter], COMPARATIVE_DEGREE),
                self.create_quiz(big_concept, groot, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(big_concept, groot, [klein], ANTONYM),
                self.create_quiz(big_concept, groter, [groot], POSITIVE_DEGREE),
                self.create_quiz(big_concept, groter, [grootst], SUPERLATIVE_DEGREE),
                self.create_quiz(big_concept, groter, [kleiner], ANTONYM),
                self.create_quiz(big_concept, grootst, [groot], POSITIVE_DEGREE),
                self.create_quiz(big_concept, grootst, [groter], COMPARATIVE_DEGREE),
                self.create_quiz(big_concept, grootst, [kleinst], ANTONYM),
            },
            create_quizzes(NL_EN, (), big_concept),
        )
