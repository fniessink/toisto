"""Progress unit tests."""

import unittest

from toisto.model import Label, Progress, Quiz


class ProgressTest(unittest.TestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = Quiz("fi", "nl", Label("Englanti"), [Label("Engels")])
        self.another_quiz = Quiz("nl", "fi", Label("Engels"), [Label("Englanti")])
        self.progress = Progress({})

    def test_progress_new_quiz(self):
        """Test that a new quiz has no progress."""
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
        """Test that the next quiz is not silenced."""
        self.progress.update(self.quiz, correct=True)
        self.progress.update(self.quiz, correct=True)
        another_quiz = Quiz("fi", "en", "Englanti", "English")
        self.assertEqual(another_quiz, self.progress.next_quiz([self.quiz, another_quiz]))

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        self.progress.update(self.quiz, correct=True)
        self.progress.update(self.quiz, correct=True)
        self.assertEqual(None, self.progress.next_quiz([self.quiz]))

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        quizzes = [self.quiz, self.another_quiz]
        self.assertNotEqual(self.progress.next_quiz(quizzes), self.progress.next_quiz(quizzes))

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        quizzes = [Quiz("nl", "fi", f"Dutch label {index}", f"Finnish label {index}") for index in range(5)]
        for index in range(3):
            self.progress.update(quizzes[index], correct=True)
        self.assertIn(self.progress.next_quiz(quizzes), quizzes[:3])

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
