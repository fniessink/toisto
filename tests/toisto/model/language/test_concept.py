"""Unit tests for concepts."""

import unittest
from argparse import ArgumentParser
from typing import cast
from unittest.mock import Mock, patch

from toisto.model.filter import filter_concepts
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.language.label import Label
from toisto.model.topic.topic import Topic, TopicId

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertEqual((), concept.labels("fi"))
        self.assertEqual((), concept.meanings("fi"))
        self.assertEqual((), concept.answers)
        self.assertFalse(concept.answer_only)
        self.assertEqual((), concept.roots("fi"))
        self.assertIsNone(concept.parent)
        self.assertEqual((), concept.constituents)
        self.assertEqual((), concept.antonyms)

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = create_concept("thirty", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances["thirty"])

    def test_meaning_leaf_concept(self):
        """Test the meaning of a leaf concept."""
        concept = create_concept("one", dict(fi="yksi", nl="een"))
        self.assertEqual((Label("fi", "yksi"),), concept.meanings("fi"))
        self.assertEqual((Label("nl", "een"),), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("en"))

    def test_meaning_composite_concept(self):
        """Test the meaning of a composite concept."""
        concept = create_concept(
            "table",
            dict(singular=dict(en="table", nl="de tafel"), plural=dict(en="tables", nl="de tafels")),
        )
        self.assertEqual((Label("en", "table"), Label("en", "tables")), concept.meanings("en"))
        self.assertEqual((Label("nl", "de tafel"), Label("nl", "de tafels")), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("fi"))

    def test_meaning_mixed_concept(self):
        """Test the meaning of a concept that is leaf in one language and composite in another."""
        concept = create_concept(
            "to eat/third person",
            dict(fi="hän syö", female=dict(nl="zij eet"), male=dict(nl="hij eet")),
        )
        self.assertEqual((Label("fi", "hän syö"),), concept.meanings("fi"))
        self.assertEqual((Label("nl", "zij eet"), Label("nl", "hij eet")), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("en"))


class ConceptFilterTest(unittest.TestCase):
    """Unit tests for the concept filter function."""

    def setUp(self) -> None:
        """Override to set up concepts."""
        self.two = create_concept(ConceptId("two"), cast(ConceptDict, dict(fi="kaksi", nl="twee")))
        self.three = create_concept(ConceptId("three"), cast(ConceptDict, dict(fi="kolme", nl="drie")))
        self.concepts = {self.two, self.three}
        small = Topic(TopicId("small"), frozenset([ConceptId("two")]))
        big = Topic(TopicId("big"), frozenset([ConceptId("three")]))
        self.topics = {small, big}

    def test_no_filter(self):
        """Test that all concepts are returned when there is no filter specified."""
        self.assertEqual({self.two}, filter_concepts({self.two}, self.topics, [], [], ArgumentParser()))

    def test_filter_by_selected_concepts(self):
        """Test that concepts can be filtered by selected concepts."""
        self.assertEqual({self.two}, filter_concepts(self.concepts, self.topics, ["two"], [], ArgumentParser()))

    def test_filter_by_topic(self):
        """Test that concepts can be filtered by topic."""
        self.assertEqual({self.two}, filter_concepts(self.concepts, self.topics, [], ["small"], ArgumentParser()))

    @patch("sys.stderr.write")
    def test_no_match(self, sys_stderr_write: Mock):
        """Test that an error message is given when no concepts match the filter criteria."""
        self.assertRaises(
            SystemExit,
            filter_concepts,
            self.concepts,
            self.topics,
            [],
            ["missing"],
            ArgumentParser(),
        )
        self.assertIn("Topic 'missing' not found", sys_stderr_write.call_args_list[1][0][0])
