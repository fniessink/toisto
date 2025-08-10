"""Unit tests for the model filter."""

from argparse import ArgumentParser
from unittest.mock import Mock, patch

from toisto.model.filter import filter_concepts
from toisto.model.language import EN
from toisto.model.language.concept import Concept

from ...base import ToistoTestCase


class FilterTest(ToistoTestCase):
    """Unit tests for the filter method."""

    def setUp(self) -> None:
        """Set up the unit test fixtures."""
        super().setUp()
        self.argument_parser = ArgumentParser()
        self.matter = self.create_concept("matter", labels=[{"label": "matter", "language": EN}])
        self.thing = self.create_concept("thing", labels=[{"label": "thing", "language": EN}])
        self.thing_id = self.thing.concept_id
        self.concepts = {self.matter, self.thing}

    def filter_concepts(
        self,
        *,
        concepts: set[Concept] | None = None,
        selected_concepts: list[str] | None = None,
    ) -> set[Concept]:
        """Filter the concepts."""
        return filter_concepts(
            self.concepts if concepts is None else concepts,
            selected_concepts or [],
            EN,
            self.argument_parser,
        )

    def test_no_concepts_and_no_filter(self):
        """Test no concepts and no filters."""
        self.assertEqual(set(), self.filter_concepts(concepts=set()))

    def test_concepts_but_no_filters(self):
        """Test that all concepts are returned."""
        self.assertEqual(self.concepts, self.filter_concepts())

    def test_selected_concepts(self):
        """Test that the selected concepts are returned."""
        self.assertEqual({self.thing}, self.filter_concepts(selected_concepts=["thing"]))

    @patch("sys.stderr.write")
    def test_selected_concepts_without_concepts(self, sys_stderr_write: Mock) -> None:
        """Test that an empty selection results in an error message."""
        self.assertRaises(SystemExit, self.filter_concepts, selected_concepts=["baz"])
        self.assertIn("'baz' not found", sys_stderr_write.call_args_list[1][0][0])

    def test_add_hyponyms_of_selected_concepts_recursively(self):
        """Test that the hyponyms of selected concepts are added, recursively."""
        little_thing = self.create_concept("little thing", {"hypernym": self.thing_id})
        small_little_thing = self.create_concept("small little thing", {"hypernym": little_thing.concept_id})
        self.assertEqual(
            {self.thing, little_thing, small_little_thing},
            self.filter_concepts(
                concepts=self.concepts | {little_thing, small_little_thing}, selected_concepts=["thing"]
            ),
        )

    def test_do_not_add_hypernyms_of_selected_concepts(self):
        """Test that the hypernyms of selected concepts are not added."""
        little_thing = self.create_concept("little thing", {"hypernym": self.thing_id})
        small_little_thing = self.create_concept(
            "small little thing",
            {"hypernym": little_thing.concept_id},
            labels=[{"label": "small little thing", "language": EN}],
        )
        self.assertEqual(
            {small_little_thing},
            self.filter_concepts(
                concepts=self.concepts | {little_thing, small_little_thing}, selected_concepts=["small little thing"]
            ),
        )

    def test_add_meronyms_of_selected_concepts_recursively(self):
        """Test that the holonyms and meronyms of selected concepts are added, recursively."""
        thing_part = self.create_concept("thing part", {"holonym": self.thing_id})
        thing_part_part = self.create_concept("thing part part", {"holonym": thing_part.concept_id})
        self.assertEqual(
            {self.thing, thing_part, thing_part_part},
            self.filter_concepts(concepts=self.concepts | {thing_part, thing_part_part}, selected_concepts=["thing"]),
        )

    def test_do_not_add_holonyms_of_selected_concepts(self):
        """Test that the holonyms of selected concepts are not added."""
        thing_part = self.create_concept("thing part", {"holonym": self.thing_id})
        thing_part_part = self.create_concept(
            "thing part part", {"holonym": thing_part.concept_id}, labels=[{"label": "thing part part", "language": EN}]
        )
        self.assertEqual(
            {thing_part_part},
            self.filter_concepts(
                concepts=self.concepts | {thing_part, thing_part_part}, selected_concepts=["thing part part"]
            ),
        )

    def test_add_hyponyms_of_meronyms_of_selected_concepts(self):
        """Test that hyponyms of meronyms of selected concepts are added."""
        thing_part = self.create_concept("thing part", {"holonym": self.thing_id})
        little_thing_part = self.create_concept("little thing part", {"hypernym": thing_part.concept_id})
        self.assertEqual(
            {self.thing, thing_part, little_thing_part},
            self.filter_concepts(concepts=self.concepts | {thing_part, little_thing_part}, selected_concepts=["thing"]),
        )

    def test_add_meronyms_of_hyponyms_of_selected_concepts(self):
        """Test that meronyms of hyponyms of selected concepts are added."""
        little_thing = self.create_concept("little thing", {"hypernym": self.thing_id})
        little_thing_part = self.create_concept("little thing part", {"holonym": little_thing.concept_id})
        self.assertEqual(
            {self.thing, little_thing, little_thing_part},
            self.filter_concepts(
                concepts=self.concepts | {little_thing, little_thing_part}, selected_concepts=["thing"]
            ),
        )

    def test_add_antonyms_of_selected_concepts(self):
        """Test that antonyms of selected concepts are added."""
        anti_matter = self.create_concept(
            "anti matter", {"antonym": self.matter.concept_id}, labels=[{"label": "anti matter", "language": EN}]
        )
        self.assertEqual(
            {self.matter, anti_matter},
            self.filter_concepts(concepts=self.concepts | {anti_matter}, selected_concepts=["anti matter"]),
        )

    def test_add_concepts_that_have_selected_concepts_as_root(self):
        """Test that the concepts that have a selected concept as root are added."""
        little_thing = self.create_concept(
            "little thing", labels=[{"label": "little thing", "language": EN, "roots": "thing"}]
        )
        self.assertEqual(
            {self.thing, little_thing},
            self.filter_concepts(concepts=self.concepts | {little_thing}, selected_concepts=["thing"]),
        )

    def test_add_concepts_involved_by_selected_concepts_recursively(self):
        """Test that concepts involved by selected concepts are added, recursively."""
        location = self.create_concept("location", {"involves": self.thing_id})
        coordinate = self.create_concept(
            "coordinate", {"involves": location.concept_id}, labels=[{"label": "coordinate", "language": EN}]
        )
        self.assertEqual(
            {self.thing, coordinate, location},
            self.filter_concepts(concepts=self.concepts | {coordinate, location}, selected_concepts=["thing"]),
        )
