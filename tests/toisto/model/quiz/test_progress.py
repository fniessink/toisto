"""Progress unit tests."""

from toisto.model import Progress, Topic, Topics

from ...base import ToistoTestCase


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz("fi", "nl", "Englanti", ["Engels"])
        self.another_quiz = self.create_quiz("nl", "fi", "Engels", ["Englanti"])
        self.progress = Progress({})

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
        self.progress.update(self.quiz, correct=True)
        another_quiz = self.create_quiz("fi", "en", "Englanti", ["English"])
        topics = Topics(set([Topic("topic", set([self.quiz, another_quiz]))]))
        self.assertEqual(another_quiz, self.progress.next_quiz(topics))

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        self.progress.update(self.quiz, correct=True)
        self.progress.update(self.quiz, correct=True)
        topics = Topics(set([Topic("topic", set([self.quiz]))]))
        self.assertEqual(None, self.progress.next_quiz(topics))

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        quizzes = [self.quiz, self.another_quiz]
        topics = Topics(set([Topic("topic", set(quizzes))]))
        self.assertNotEqual(self.progress.next_quiz(topics), self.progress.next_quiz(topics))

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        quizzes = [
            self.create_quiz("nl", "fi", f"Dutch label {index}", [f"Finnish label {index}"]) for index in range(5)
        ]
        for index in range(3):
            self.progress.update(quizzes[index], correct=True)
        topics = Topics(set([Topic("topic", set(quizzes))]))
        self.assertIn(self.progress.next_quiz(topics), quizzes[:3])

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
