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
        self.progress = Progress({}, Topics(set()))

    def create_topics(self, quizzes: Quizzes) -> Topics:
        """Create a test topics collection."""
        return Topics({Topic("topic", (), quizzes)})

    def create_progress(self, *topic_quizzes: Quizzes) -> Progress:
        """Create progress for the quizzes."""
        topics = Topics({Topic(f"topic{index}", (), quizzes) for index, quizzes in enumerate(topic_quizzes)})
        return Progress({}, topics)

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
        progress = self.create_progress({self.quiz, self.another_quiz})
        progress.update(self.quiz, correct=True)
        self.assertEqual(self.another_quiz, progress.next_quiz())

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        progress = self.create_progress([self.quiz])
        progress.update(self.quiz, correct=True)
        self.assertIsNone(progress.next_quiz())

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        progress = self.create_progress({self.quiz, self.another_quiz})
        self.assertNotEqual(progress.next_quiz(), progress.next_quiz())

    def test_next_quiz_is_not_blocked(self):
        """Test that the next quiz is a translation quiz and not a listening quiz if both are eligible."""
        listen = self.create_quiz("english", "fi", "fi", "Englanti", ["Englanti"], "listen", blocked_by=(self.quiz,))
        progress = self.create_progress({listen, self.quiz})
        self.assertEqual(self.quiz, progress.next_quiz())

    def test_concept_of_next_quiz_does_not_use_other_concepts_with_eligible_quizzes(self):
        """Test that the concept of the next quiz does not use other concepts with eligible quizzes."""
        quiz1 = self.create_quiz("good day", "nl", "en", "Goedendag", ["Good day"], uses=("good",))
        quiz2 = self.create_quiz("good", "nl", "en", "Goed", ["Good"])
        progress = self.create_progress([quiz1, quiz2])
        self.assertEqual(quiz2, progress.next_quiz())

    def test_concept_of_next_quiz_does_not_use_other_concepts_with_eligible_quizzes_even_across_topics(self):
        """Test that the concept of the next quiz does not use other concepts with eligible quizzes, even when the
        concepts belong to different topics."""
        quiz1 = self.create_quiz("good day", "nl", "en", "Goedendag", ["Good day"], uses=("good",))
        quiz2 = self.create_quiz("good", "nl", "en", "Goed", ["Good"])
        progress = self.create_progress([quiz1], [quiz2])
        self.assertEqual(quiz2, progress.next_quiz())

    def test_quiz_order(self):
        """Test that the first quizzes test the singular concept."""
        concept = self.create_concept(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        quizzes = self.create_quizzes(concept, "fi", "nl")
        progress = self.create_progress(quizzes)
        for _ in range(3):
            quiz = progress.next_quiz()
            self.assertEqual("morning/singular", quiz.concept_id)
            progress.update(quiz, correct=True)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        quizzes = [
            self.create_quiz(f"id{index}", "nl", "fi", f"Dutch label {index}", [f"Finnish label {index}"])
            for index in range(5)
        ]
        progress = self.create_progress(quizzes)
        for index in range(3):
            progress.update(quizzes[index], correct=True)
            progress.get_retention(quizzes[index]).skip_until = None
        self.assertIn(progress.next_quiz(), quizzes[:3])

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
