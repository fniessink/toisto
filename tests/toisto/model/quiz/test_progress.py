"""Progress unit tests."""

from toisto.model import Progress, Quizzes, Topic, Topics
from toisto.model.model_types import ConceptId

from ...base import ToistoTestCase


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz(ConceptId("english"), "fi", "nl", "Englanti", ["Engels"])
        self.another_quiz = self.create_quiz(ConceptId("english"), "nl", "fi", "Engels", ["Englanti"])
        self.progress = Progress({})

    def create_topics(self, quizzes: Quizzes) -> Topics:
        """Create a test topics collection."""
        return Topics({Topic("topic", (), quizzes)})

    def test_progress_new_quiz(self):
        """Test that a new quiz has no progress."""
        self.assertIsNone(self.progress.get_retention(self.quiz).start)
        self.assertIsNone(self.progress.get_retention(self.quiz).end)
        self.assertIsNone(self.progress.get_retention(self.quiz).skip_until)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.update(self.quiz, correct=True)
        self.assertIsNotNone(self.progress.get_retention(self.quiz).start)
        self.assertIsNotNone(self.progress.get_retention(self.quiz).end)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.update(self.quiz, correct=False)
        self.assertIsNone(self.progress.get_retention(self.quiz).start)
        self.assertIsNone(self.progress.get_retention(self.quiz).end)
        self.assertIsNone(self.progress.get_retention(self.quiz).skip_until)

    def test_next_quiz(self):
        """Test that the next quiz is not silenced."""
        self.progress.update(self.quiz, correct=True)
        another_quiz = self.create_quiz("english", "fi", "en", "Englanti", ["English"])
        topics = self.create_topics({self.quiz, another_quiz})
        self.assertEqual(another_quiz, self.progress.next_quiz(topics))

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        self.progress.update(self.quiz, correct=True)
        topics = self.create_topics({self.quiz})
        self.assertIsNone(self.progress.next_quiz(topics))

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        topics = self.create_topics({self.quiz, self.another_quiz})
        self.assertNotEqual(self.progress.next_quiz(topics), self.progress.next_quiz(topics))

    def test_concept_of_next_quiz_does_not_use_other_concepts_with_eligible_quizzes(self):
        """Test that the concept of the next quiz does not use other concepts with eligible quizzes."""
        quiz1 = self.create_quiz("good day", "nl", "en", "Goedendag", ["Good day"], uses=("good",))
        quiz2 = self.create_quiz("good", "nl", "en", "Goed", ["Good"])
        topics = self.create_topics({quiz1, quiz2})
        self.assertEqual(quiz2, self.progress.next_quiz(topics))

    def test_concept_of_next_quiz_does_not_use_other_concepts_with_eligible_quizzes_even_across_topics(self):
        """Test that the concept of the next quiz does not use other concepts with eligible quizzes, even when the
        concepts belong to different topics."""
        quiz1 = self.create_quiz("good day", "nl", "en", "Goedendag", ["Good day"], uses=("good",))
        quiz2 = self.create_quiz("good", "nl", "en", "Goed", ["Good"])
        topics = Topics({Topic("topic1", (), {quiz1}), Topic("topic2",  (), {quiz2})})
        self.assertEqual(quiz2, self.progress.next_quiz(topics))

    def test_quiz_order(self):
        """Test that the first quizzes test the singular concept."""
        concept = self.create_concept(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        quizzes = self.create_quizzes(concept, "fi", "nl")
        topics = self.create_topics(quizzes)
        for _ in range(3):
            quiz = self.progress.next_quiz(topics)
            self.assertEqual("morning/singular", quiz.concept_id)
            self.progress.update(quiz, correct=True)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        quizzes = [
            self.create_quiz(
                f"id{index}", "nl", "fi", f"Dutch label {index}", [f"Finnish label {index}"]
            ) for index in range(5)
        ]
        for index in range(3):
            self.progress.update(quizzes[index], correct=True)
            self.progress.get_retention(quizzes[index]).skip_until = None
        topics = self.create_topics(set(quizzes))
        self.assertIn(self.progress.next_quiz(topics), quizzes[:3])

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
