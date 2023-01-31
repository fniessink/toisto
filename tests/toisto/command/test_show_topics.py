"""Unit tests for the show topics command."""

from unittest.mock import patch

from toisto.command.show_topics import show_topics
from toisto.model.quiz.topic import Topic, Topics

from ..base import ToistoTestCase


class ShowTopicsTest(ToistoTestCase):
    """Test the show topics command."""

    def setUp(self):
        """Set up test fixtures."""
        concept = self.create_concept("hello")
        self.quiz = self.create_quiz(concept, "fi", "nl", "Terve", ["Hoi"])
        self.topics = Topics({Topic("topic", (), {self.quiz})})

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("fi", "nl", self.topics)
        self.assertEqual("Topic topic", console_print.call_args[0][0].title)
