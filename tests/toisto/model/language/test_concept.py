"""Unit tests for concepts."""

import unittest
from argparse import ArgumentParser
from typing import cast
from unittest.mock import Mock, patch

from toisto.model.filter import filter_concepts
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.topic.topic import Topic

from ....base import ToistoTestCase


class ConceptTest(ToistoTestCase):
    """Unit tests for the Concept class."""

    def test_defaults(self):
        """Test the default attributes of a concept."""
        concept = create_concept("concept_id", {})
        self.assertEqual("concept_id", concept.concept_id)
        self.assertEqual((), concept.labels("fi"))
        self.assertEqual((), concept.meanings("fi"))
        self.assertIsNone(concept.level)
        self.assertEqual((), concept.answers)
        self.assertFalse(concept.answer_only)
        self.assertEqual((), concept.roots("fi"))
        self.assertIsNone(concept.parent)
        self.assertEqual((), concept.constituents)
        self.assertEqual((), concept.antonyms)

    def test_level(self):
        """Test that the level of a concept is the maximum of the available levels."""
        concept = create_concept("thirty", dict(level=dict(A1="EP", A2="OD"), fi="kolmekymmentä", nl="dertig"))
        self.assertEqual("A2", concept.level)

    def test_instance_registry(self):
        """Test that concepts register themselves with the Concept class instance registry."""
        concept = create_concept("thirty", dict(fi="kolmekymmentä", nl="dertig"))
        self.assertEqual(concept, Concept.instances["thirty"])

    def test_meaning_leaf_concept(self):
        """Test the meaning of a leaf concept."""
        concept = create_concept("one", dict(fi="yksi", nl="een"))
        self.assertEqual(("yksi",), concept.meanings("fi"))
        self.assertEqual(("een",), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("en"))

    def test_meaning_composite_concept(self):
        """Test the meaning of a composite concept."""
        concept = create_concept(
            "table",
            dict(singular=dict(en="table", nl="de tafel"), plural=dict(en="tables", nl="de tafels")),
        )
        self.assertEqual(("table", "tables"), concept.meanings("en"))
        self.assertEqual(("de tafel", "de tafels"), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("fi"))

    def test_meaning_mixed_concept(self):
        """Test the meaning of a concept that is leaf in one language and composite in another."""
        concept = create_concept(
            "to eat/third person",
            dict(fi="hän syö", female=dict(nl="zij eet"), male=dict(nl="hij eet")),
        )
        self.assertEqual(("hän syö",), concept.meanings("fi"))
        self.assertEqual(("zij eet", "hij eet"), concept.meanings("nl"))
        self.assertEqual((), concept.meanings("en"))


class ConceptFilterTest(unittest.TestCase):
    """Unit tests for the concept filter function."""

    def setUp(self) -> None:
        """Override to set up concepts."""
        self.two = create_concept(
            ConceptId("two"),
            cast(ConceptDict, dict(level={"A1": "KK"}, fi="kaksi", nl="twee")),
        )
        self.three = create_concept(
            ConceptId("three"),
            cast(ConceptDict, dict(level={"A2": "KK"}, fi="kolme", nl="drie")),
        )
        self.concepts = {self.two, self.three}
        small = Topic(name="small", concepts=(ConceptId("two"),))
        big = Topic(name="big", concepts=(ConceptId("three"),))
        self.topics = {small, big}

    def test_no_filter(self):
        """Test that all concepts are returned when there is no filter specified."""
        self.assertEqual({self.two}, filter_concepts({self.two}, self.topics, [], [], [], ArgumentParser()))

    def test_filter_by_selected_concepts(self):
        """Test that concepts can be filtered by selected concepts."""
        self.assertEqual({self.two}, filter_concepts(self.concepts, self.topics, ["two"], [], [], ArgumentParser()))

    def test_filter_by_level(self):
        """Test that concepts can be filtered by level."""
        self.assertEqual({self.two}, filter_concepts(self.concepts, self.topics, [], ["A1"], [], ArgumentParser()))

    def test_filter_by_topic(self):
        """Test that concepts can be filtered by topic."""
        self.assertEqual({self.two}, filter_concepts(self.concepts, self.topics, [], [], ["small"], ArgumentParser()))

    @patch("sys.stderr.write")
    def test_no_match(self, sys_stderr_write: Mock):
        """Test that an error message is given when no concepts match the filter criteria."""
        self.assertRaises(
            SystemExit,
            filter_concepts,
            self.concepts,
            self.topics,
            [],
            [],
            ["missing"],
            ArgumentParser(),
        )
        self.assertIn("No concepts found that match your selection criteria", sys_stderr_write.call_args_list[1][0][0])
