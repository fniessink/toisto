"""Unit tests for the persistence module."""

from unittest.mock import patch, Mock

from toisto.persistence import load_quizzes

from ..base import ToistoTestCase


class LoadQuizzesTest(ToistoTestCase):
    """Unit tests for loading the quizzes."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz("welcome", "fi", "nl", "Tervetuloa", ["Welkom"])

    def test_load_quizzes(self):
        """Test that the quizzes can be loaded."""
        self.assertIn(self.quiz, load_quizzes("fi", "nl", [], []).quizzes)

    def test_load_quizzes_by_topic_name(self):
        """Test that a subset of the quizzes can be loaded."""
        self.assertNotIn(self.quiz, load_quizzes("fi", "nl", ["family"], []).quizzes)

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_topic_by_filename(self, stderr_write):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(SystemExit, load_quizzes, "fi",  "nl", [], ["file-does-not-exist"])
        stderr_write.assert_called_with(
            "Toisto cannot read topic file-does-not-exist: [Errno 2] No such file or directory: "
            "'file-does-not-exist'.\n"
        )
