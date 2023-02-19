"""Unit tests for the show topics command."""

from unittest.mock import patch

from toisto.command.show_topics import show_topics
from toisto.model.quiz.topic import Topic, Topics

from ...base import ToistoTestCase


class ShowTopicsTest(ToistoTestCase):
    """Test the show topics command."""

    def setUp(self):
        """Set up test fixtures."""
        concept = self.create_concept("hello", dict(fi="Terve", nl="Hoi"))
        self.quiz = self.create_quiz(concept, "fi", "nl", "Terve", ["Hoi"])
        self.topics = Topics({Topic("topic", (concept,), {self.quiz})})

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("fi", "nl", self.topics)
        self.assertEqual("Topic topic", console_print.call_args[0][0].title)
        self.assertEqual(1, console_print.call_args_list[0][0][0].row_count)

    def test_contents(self):
        """Test that the table contains the concept."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("fi", "nl", self.topics)
        self.assertEqual(1, console_print.call_args_list[0][0][0].row_count)

    def test_skip_concepts_without_labels_in_the_selected_languages(self):
        """Test that concepts without labels in the target or source language are not shown."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("en", "fr", self.topics)
        self.assertEqual(0, console_print.call_args_list[0][0][0].row_count)
