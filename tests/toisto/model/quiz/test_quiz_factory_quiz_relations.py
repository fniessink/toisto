"""Unit tests for quiz relations that thw quiz factory creates."""

from .test_quiz_factory import QuizFactoryTestCase


class QuizRelationsTest(QuizFactoryTestCase):
    """Unit tests for the quiz relations that the quiz factory creates."""

    def test_translation_quizzes_block_listening_quizzes(self):
        """Test that translation quizzes block listening quizzes."""
        quizzes = self.create_quizzes(self.create_noun(), "fi", "nl")
        translation_quizzes = {quiz for quiz in quizzes if quiz.quiz_types == ("translate",)}
        listening_quizzes = {quiz for quiz in quizzes if quiz.quiz_types == ("listen",)}
        for quiz in listening_quizzes:
            self.assertEqual(translation_quizzes, set(quiz.blocked_by), msg=quiz)

    def test_non_grammatical_quizzes_block_grammatical_quizzes(self):
        """Test that listening and translation quizzes block grammatical quizzes."""
        quizzes = self.create_quizzes(self.create_noun_with_grammatical_number(), "fi", "nl")
        non_grammatical_quizzes = {quiz for quiz in quizzes if quiz.quiz_types in [("translate",), ("listen",)]}
        grammatical_quizzes = {quiz for quiz in quizzes if quiz not in non_grammatical_quizzes}
        for quiz in grammatical_quizzes:
            self.assertEqual(non_grammatical_quizzes, set(quiz.blocked_by), msg=quiz)

    def test_earlier_grammatical_quizzes_block_later_grammatical_quizzes(self):
        """Test that e.g. quizzes for singular forms block quizzes for plural forms."""
        quizzes = self.create_quizzes(self.create_noun_with_grammatical_number(), "fi", "nl")
        singular_quizzes = {quiz for quiz in quizzes if "singular" in quiz.concept_id}
        plural_quizzes = {quiz for quiz in quizzes if "plural" in quiz.concept_id}
        for quiz in plural_quizzes:
            self.assertTrue(singular_quizzes.issubset(set(quiz.blocked_by)), msg=quiz)

    def test_constituent_concept_quizzes_block_composite_concept_quizzes(self):
        """Test that quizzes for constituent quizzes block quizzes for their composite concepts."""
        quizzes = self.create_quizzes(self.create_noun_with_grammatical_number(), "fi", "nl")
        composite_quizzes = {quiz for quiz in quizzes if "/" not in quiz.concept_id}
        constituent_quizzes = {quiz for quiz in quizzes if "/" in quiz.concept_id}
        for quiz in composite_quizzes:
            self.assertEqual(constituent_quizzes, set(quiz.blocked_by), msg=quiz)

    def test_nested_constituent_concept_quizzes_block_composite_concept_quizzes(self):
        """Test that nested quizzes for constituent quizzes block quizzes for their composite concepts."""
        quizzes = self.create_quizzes(self.create_noun_with_grammatical_number_and_gender(), "en", "nl")
        female_quizzes = {quiz for quiz in quizzes if "female" in quiz.concept_id}
        male_quizzes = {quiz for quiz in quizzes if "cat/plural/male" in quiz.concept_id}
        for quiz in male_quizzes:
            self.assertTrue(female_quizzes.issubset(set(quiz.blocked_by)), msg=quiz)
