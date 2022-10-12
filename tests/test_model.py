"""Model unit tests."""

import unittest

from toisto.model import Entry, Progress, Quiz


class QuizTest(unittest.TestCase):
    """Unit tests for the quiz class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("en", "nl", "English", ["Engels"])

    def test_is_correct(self):
        """Test a correct guess."""
        self.assertTrue(self.quiz.is_correct("engels"))

    def test_is_not_correct(self):
        """Test an incorrect guess."""
        self.assertFalse(self.quiz.is_correct("engles"))

    def test_get_answer(self):
        """Test that the answer is returned."""
        self.assertEqual("Engels", self.quiz.get_answer())

    def test_get_first_answer(self):
        """Test that the first answer is returned when there are multiple."""
        quiz = Quiz("en", "nl", "One", ["Een", "Eén"])
        self.assertEqual("Een", quiz.get_answer())


class EntryTest(unittest.TestCase):
    """Unit tests for the entry class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from an entry."""
        entry = Entry("en", "nl", ["English"], ["Engels"])
        self.assertEqual(
            [Quiz("en", "nl", "English", ["Engels"]), Quiz("nl", "en", "Engels", ["English"])], entry.quizzes()
        )

    def test_multiple_answers(self):
        """Test that quizzes can be generated from an entry."""
        entry = Entry("nl", "en", ["Bank"], ["Couch", "Bank"])
        self.assertEqual(
            [
                Quiz("nl", "en", "Bank", ["Couch", "Bank"]),
                Quiz("en", "nl", "Couch", ["Bank"]),
                Quiz("en", "nl", "Bank", ["Bank"])
            ],
            entry.quizzes()
        )


class ProgressTest(unittest.TestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("en", "nl", "English", "Engels")
        self.progress = Progress({})

    def test_progress_new_entry(self):
        """Test that the progress of a quiz without progress."""
        self.assertEqual(0, self.progress.get_progress(self.quiz).count)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.update(self.quiz, correct=True)
        self.assertEqual(1, self.progress.get_progress(self.quiz).count)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.update(self.quiz, correct=False)
        self.assertEqual(0, self.progress.get_progress(self.quiz).count)

    def test_next_quiz(self):
        """Test that the next quiz has the lowest score."""
        self.progress.update(self.quiz, correct=True)
        another_quiz = Quiz("nl", "en", "Engels", "English")
        self.progress.update(another_quiz, correct=False)
        self.assertEqual(another_quiz, self.progress.next_quiz([self.quiz, another_quiz]))

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        self.progress.update(self.quiz, correct=True)
        self.progress.update(self.quiz, correct=True)
        self.assertEqual(None, self.progress.next_quiz([self.quiz]))

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
