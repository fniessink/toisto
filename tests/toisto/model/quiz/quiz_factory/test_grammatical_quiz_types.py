"""Quiz factory unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.quiz.quiz_factory import GrammaticalQuizFactory
from toisto.model.quiz.quiz_type import (
    COMPARATIVE_DEGREE,
    FEMININE,
    FIRST_PERSON,
    INFINITIVE,
    MASCULINE,
    NEUTER,
    PAST_TENSE,
    PLURAL,
    POSITIVE_DEGREE,
    PRESENT_TENSE,
    SECOND_PERSON,
    SINGULAR,
    SUPERLATIVE_DEGREE,
    THIRD_PERSON,
)

from .quiz_factory_test_case import QuizFactoryTestCase


class GrammaticalQuizTypesTest(QuizFactoryTestCase):
    """Test the grammatical quiz types generator."""

    def test_adjective_with_degrees_of_comparison(self):
        """Test the grammatical quiz types for an adjective with degrees of comparison."""
        positive, comparative, superlative = self.create_adjective_with_degrees_of_comparison().labels(EN)
        for label in (positive, comparative):
            self.assertEqual(SUPERLATIVE_DEGREE, GrammaticalQuizFactory.grammatical_quiz_type(label, superlative))
        for label in (positive, superlative):
            self.assertEqual(COMPARATIVE_DEGREE, GrammaticalQuizFactory.grammatical_quiz_type(label, comparative))
        for label in (comparative, superlative):
            self.assertEqual(POSITIVE_DEGREE, GrammaticalQuizFactory.grammatical_quiz_type(label, positive))

    def test_noun_with_grammatical_number(self):
        """Test the grammatical quiz types for a noun with singular and plural form."""
        singular, plural = self.create_noun_with_grammatical_number().labels(FI)
        self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
        self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))

    def test_noun_with_grammatical_gender(self):
        """Test the grammatical quiz types for a noun with grammatical gender."""
        feminine, masculine = self.create_noun_with_grammatical_gender().labels(EN)
        self.assertEqual(MASCULINE, GrammaticalQuizFactory.grammatical_quiz_type(feminine, masculine))
        self.assertEqual(FEMININE, GrammaticalQuizFactory.grammatical_quiz_type(masculine, feminine))

    def test_noun_with_grammatical_gender_including_neuter(self):
        """Test the grammatical quiz types for a noun with grammatical gender including neuter."""
        feminine, masculine, neuter = self.create_noun_with_grammatical_gender_including_neuter().labels(NL)
        for concept in (feminine, neuter):
            self.assertEqual(MASCULINE, GrammaticalQuizFactory.grammatical_quiz_type(concept, masculine))
        for concept in (feminine, masculine):
            self.assertEqual(NEUTER, GrammaticalQuizFactory.grammatical_quiz_type(concept, neuter))
        for concept in (masculine, neuter):
            self.assertEqual(FEMININE, GrammaticalQuizFactory.grammatical_quiz_type(concept, feminine))

    def test_noun_with_grammatical_number_and_gender(self):
        """Test the grammatical quiz types for a noun with grammatical number and gender."""
        noun = self.create_noun_with_grammatical_number_and_gender()
        singular_feminine, singular_masculine, plural_feminine, plural_masculine = noun.labels(EN)
        for feminine, masculine in ((singular_feminine, singular_masculine), (plural_feminine, plural_masculine)):
            self.assertEqual(MASCULINE, GrammaticalQuizFactory.grammatical_quiz_type(feminine, masculine))
            self.assertEqual(FEMININE, GrammaticalQuizFactory.grammatical_quiz_type(masculine, feminine))
        for singular, plural in ((singular_feminine, plural_feminine), (singular_masculine, plural_masculine)):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))

    def test_verb_with_person(self):
        """Test the grammatical quiz types for a verb with grammatical person."""
        first_person, second_person, third_person = self.create_verb_with_person().labels(EN)
        for concept in (first_person, second_person):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(concept, third_person))
        for concept in (first_person, third_person):
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(concept, second_person))
        for concept in (second_person, third_person):
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(concept, first_person))

    def test_verb_with_tense_and_person(self):
        """Test the grammatical quiz types for a verb with tense and grammatical person."""
        verb = self.create_verb_with_tense_and_person()
        present_singular, present_plural, past_singular, past_plural = verb.labels(NL)
        for singular, plural in ((present_singular, present_plural), (past_singular, past_plural)):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))
        for present, past in ((present_singular, past_singular), (present_plural, past_plural)):
            self.assertEqual(PAST_TENSE, GrammaticalQuizFactory.grammatical_quiz_type(present, past))
            self.assertEqual(PRESENT_TENSE, GrammaticalQuizFactory.grammatical_quiz_type(past, present))

    def test_verb_with_infinitive_and_person(self):
        """Test the grammatical quiz types for a verb with infinitive and grammatical person."""
        infinitive, singular, plural = self.create_verb_with_infinitive_and_person().labels(EN)
        for concept in (infinitive, singular):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(concept, plural))
        for concept in (infinitive, plural):
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(concept, singular))
        for concept in (singular, plural):
            self.assertEqual(INFINITIVE, GrammaticalQuizFactory.grammatical_quiz_type(concept, infinitive))

    def test_verb_with_person_and_number(self):
        """Test the grammatical quiz types for a verb with grammatical person and number."""
        verb = self.create_verb_with_grammatical_number_and_person()
        (
            first_singular,
            second_singular,
            third_singular,
            first_plural,
            second_plural,
            third_plural,
        ) = verb.labels(NL)
        for singular, plural in (
            (first_singular, first_plural),
            (second_singular, second_plural),
            (third_singular, third_plural),
        ):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))
        for first_person, second_person in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, second_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, first_person))
        for first_person, third_person in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, third_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, first_person))
        for second_person, third_person in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, third_person))
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, second_person))

    def test_verb_with_infinitive_and_person_and_number(self):
        """Test the grammatical quiz types for a verb with infinitive, grammatical person and number."""
        verb = self.create_verb_with_infinitive_and_number_and_person()
        (
            infinitive,
            first_singular,
            second_singular,
            third_singular,
            first_plural,
            second_plural,
            third_plural,
        ) = verb.labels(NL)
        for singular, plural in (
            (first_singular, first_plural),
            (second_singular, second_plural),
            (third_singular, third_plural),
        ):
            self.assertEqual(PLURAL, GrammaticalQuizFactory.grammatical_quiz_type(singular, plural))
            self.assertEqual(SINGULAR, GrammaticalQuizFactory.grammatical_quiz_type(plural, singular))
            self.assertIsNone(GrammaticalQuizFactory.grammatical_quiz_type(infinitive, singular))
            self.assertIsNone(GrammaticalQuizFactory.grammatical_quiz_type(infinitive, plural))
        for first_person, second_person in ((first_singular, second_singular), (first_plural, second_plural)):
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, second_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, first_person))
        for first_person, third_person in ((first_singular, third_singular), (first_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(first_person, third_person))
            self.assertEqual(FIRST_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, first_person))
        for second_person, third_person in ((second_singular, third_singular), (second_plural, third_plural)):
            self.assertEqual(THIRD_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(second_person, third_person))
            self.assertEqual(SECOND_PERSON, GrammaticalQuizFactory.grammatical_quiz_type(third_person, second_person))
