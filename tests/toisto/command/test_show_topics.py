"""Unit tests for the show topics command."""

from unittest.mock import patch

from toisto.command.show_topics import show_topics
from toisto.model.language.concept_factory import create_concept
from toisto.model.quiz.quiz_factory import create_quizzes

from ...base import ToistoTestCase


class ShowTopicsTest(ToistoTestCase):
    """Test the show topics command."""

    def setUp(self):
        """Set up test fixtures."""
        concept = create_concept("hello", dict(fi="Terve", nl="Hoi"), topics={"topic"})
        self.quiz = create_quizzes("fi", "nl", concept).by_quiz_type("read").pop()
        self.concepts = {concept}

    def test_title(self):
        """Test the table title."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("fi", "nl", self.concepts)
        self.assertEqual("Topic topic", console_print.call_args[0][0].title)
        self.assertEqual(1, console_print.call_args_list[0][0][0].row_count)

    def test_contents(self):
        """Test that the table contains the concept."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("fi", "nl", self.concepts)
        self.assertEqual(1, console_print.call_args_list[0][0][0].row_count)

    def test_skip_concepts_without_labels_in_the_selected_languages(self):
        """Test that concepts without labels in the target or source language are not shown."""
        with patch("rich.console.Console.print") as console_print:
            show_topics("en", "fr", self.concepts)
        self.assertEqual(0, console_print.call_args_list[0][0][0].row_count)
