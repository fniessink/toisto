"""Unit tests for the persistence module."""

from itertools import permutations
from unittest.mock import patch, Mock

from toisto.model.model_types import ConceptId
from toisto.persistence import load_topics

from ..base import ToistoTestCase


class LoadTopicsTest(ToistoTestCase):
    """Unit tests for loading the topics."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.quiz = self.create_quiz(ConceptId("welcome"), "fi", "nl", "Tervetuloa", ["Welkom"])

    def test_load_topics(self):
        """Test that the topics can be loaded."""
        self.assertIn(self.quiz, load_topics("fi", "nl", [], []).quizzes)

    def test_instructions(self):
        """Test that an instruction can be created for all quizzes."""
        for language1, language2 in permutations(["en", "fi", "nl"], r=2):
            for quiz in load_topics(language1, language2, [], []).quizzes:
                quiz.instruction()  # This raises KeyError if types of the quiz are not present in the instructions

    def test_load_topic_by_name(self):
        """Test that a subset of the builtin topics can be loaded by name."""
        self.assertNotIn(self.quiz, load_topics("fi", "nl", ["family"], []).quizzes)

    @patch("pathlib.Path.exists", Mock(return_value=False))
    @patch("sys.stderr.write")
    def test_load_topic_by_filename(self, stderr_write):
        """Test that an error message is given when the topic file does not exist."""
        self.assertRaises(SystemExit, load_topics, "fi",  "nl", [], ["file-does-not-exist"])
        stderr_write.assert_called_with(
            "Toisto cannot read topic file-does-not-exist: [Errno 2] No such file or directory: "
            "'file-does-not-exist'.\n"
        )
