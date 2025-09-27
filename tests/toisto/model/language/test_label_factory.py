"""Unit tests for the label factory."""

from typing import cast

from toisto.model.language import EN, NL
from toisto.model.language.concept import ConceptId
from toisto.model.language.grammatical_form import GrammaticalForm
from toisto.model.language.label import Label
from toisto.model.language.label_factory import JSONGrammar, LabelFactory, LabelJSON
from toisto.tools import first

from ....base import ToistoTestCase


class LabelFactoryTestCase(ToistoTestCase):
    """Base class for label factory unit tests."""

    def setUp(self) -> None:
        """Extend to setup test fixtures."""
        super().setUp()
        self.factory = LabelFactory()

    def with_extra(
        self, label_json: LabelJSON, tip: JSONGrammar = "", note: JSONGrammar = "", cloze: JSONGrammar = ""
    ) -> LabelJSON:
        """Add the extra elements to the label JSON."""
        if tip:
            label_json["tip"] = tip
        if note:
            label_json["note"] = note
        if cloze:
            label_json["cloze"] = cloze
        return label_json

    def label(self, label: str, concept_id: str = "", **kwargs: JSONGrammar) -> LabelJSON:
        """Create a simple label."""
        label_json: LabelJSON = {"concept": ConceptId(concept_id or label), "label": label, "language": EN}
        return self.with_extra(label_json, **kwargs)

    def label_with_grammatical_number(
        self, singular: str = "chair", plural: str = "chairs", **kwargs: JSONGrammar
    ) -> LabelJSON:
        """Create a label with grammatical number forms."""
        label_json: LabelJSON = {
            "concept": ConceptId(singular),
            "label": cast("JSONGrammar", {"singular": singular, "plural": plural}),
            "language": EN,
        }
        return self.with_extra(label_json, **kwargs)

    def label_with_grammatical_number_and_diminutive(self, **kwargs: JSONGrammar) -> LabelJSON:
        """Create a label with grammatical number and diminutive forms."""
        label_json: LabelJSON = {
            "concept": ConceptId("chair"),
            "label": cast(
                "JSONGrammar",
                {
                    "root": {"singular": "de stoel", "plural": "de stoelen"},
                    "diminutive": {"singular": "het stoeltje", "plural": "de stoeltjes"},
                },
            ),
            "language": NL,
        }
        return self.with_extra(label_json, **kwargs)

    def label_with_nested_grammatical_number(self, **kwargs: JSONGrammar) -> LabelJSON:
        """Create a label with nested grammatical number."""
        label_json: LabelJSON = {
            "concept": ConceptId("chair"),
            "label": cast(
                "JSONGrammar",
                {
                    "singular": {"singular pronoun": "my chair", "plural pronoun": "our chair"},
                    "plural": {"singular pronoun": "my chairs", "plural pronoun": "our chairs"},
                },
            ),
            "language": EN,
        }
        return self.with_extra(label_json, **kwargs)


class LabelFactoryTest(LabelFactoryTestCase):
    """Label factory unit tests."""

    def label_with_spelling_alternatives(self) -> LabelJSON:
        """Create a label with multiple spelling alternatives."""
        return {"concept": ConceptId("color"), "label": ["color", "colour"], "language": EN}

    def test_create_label(self):
        """Test creating a single label."""
        json = self.label("chair")
        self.assertEqual((Label(EN, "chair"),), self.factory.create_labels([json]))

    def test_create_labels(self):
        """Test creating multiple labels."""
        json = self.label("chair")
        table_json = self.label("table")
        self.assertEqual((Label(EN, "chair"), Label(EN, "table")), self.factory.create_labels([json, table_json]))

    def test_create_label_with_spelling_alternatives(self):
        """Test creating a label with spelling alternatives."""
        color_json = self.label_with_spelling_alternatives()
        self.assertEqual((Label(EN, ["color", "colour"]),), self.factory.create_labels([color_json]))

    def test_create_synonym_labels(self):
        """Test creating synonym labels."""
        begin_json = self.label("begin")
        start_json = self.label("start", concept_id="begin")
        self.assertEqual((Label(EN, "begin"), Label(EN, "start")), self.factory.create_labels([begin_json, start_json]))

    def test_create_label_with_grammatical_forms(self):
        """Test creating labels with grammatical forms."""
        json = self.label_with_grammatical_number()
        self.assertEqual(
            (
                Label(EN, "chair", GrammaticalForm("chair", "singular")),
                Label(EN, "chairs", GrammaticalForm("chair", "plural")),
            ),
            self.factory.create_labels([json]),
        )

    def test_create_label_with_nested_grammatical_forms(self):
        """Test creating labels with nested grammatical forms."""
        json = self.label_with_grammatical_number_and_diminutive()
        base = "de stoel"
        self.assertEqual(
            (
                Label(NL, "de stoel", GrammaticalForm(base, "root", "singular")),
                Label(NL, "de stoelen", GrammaticalForm(base, "root", "plural")),
                Label(NL, "het stoeltje", GrammaticalForm(base, "diminutive", "singular")),
                Label(NL, "de stoeltjes", GrammaticalForm(base, "diminutive", "plural")),
            ),
            self.factory.create_labels([json]),
        )

    def test_create_label_with_nested_grammatical_number(self):
        """Test creating labels with nested grammatical number."""
        json = self.label_with_nested_grammatical_number()
        base = "my chair"
        self.assertEqual(
            (
                Label(EN, "my chair", GrammaticalForm(base, "singular", "singular pronoun")),
                Label(EN, "our chair", GrammaticalForm(base, "singular", "plural pronoun")),
                Label(EN, "my chairs", GrammaticalForm(base, "plural", "singular pronoun")),
                Label(EN, "our chairs", GrammaticalForm(base, "plural", "plural pronoun")),
            ),
            self.factory.create_labels([json]),
        )

    def test_grammatical_base(self):
        """Test the grammatical base of a simple label."""
        json = self.label("chair")
        self.assertEqual("chair", LabelFactory.grammatical_base_for(json))

    def test_grammatical_base_with_spelling_alternatives(self):
        """Test the grammatical base of a label with spelling alternatives."""
        color_json = self.label_with_spelling_alternatives()
        self.assertEqual("color", LabelFactory.grammatical_base_for(color_json))

    def test_grammatical_base_with_grammatical_forms(self):
        """Test the grammatical base of a label with different grammatical forms."""
        json = self.label_with_grammatical_number()
        self.assertEqual("chair", LabelFactory.grammatical_base_for(json))

    def test_grammatical_base_with_nested_grammatical_forms(self):
        """Test the grammatical base of a label with nested grammatical forms."""
        json = self.label_with_grammatical_number_and_diminutive()
        self.assertEqual("de stoel", LabelFactory.grammatical_base_for(json))


class LabelFactoryTipTest(LabelFactoryTestCase):
    """Test creating labels with tips."""

    TIP = "furniture"

    def test_label_without_tip(self):
        """Test creating a label without tip."""
        json = self.label("chair")
        chair = first(self.factory.create_labels([json]))
        self.assertEqual((), chair.tips)

    def test_label_with_tip(self):
        """Test creating a label with tip."""
        json = self.label("chair", tip=self.TIP)
        chair = first(self.factory.create_labels([json]))
        self.assertEqual((self.TIP,), chair.tips)

    def test_label_with_tips(self):
        """Test creating a label with multiple tips."""
        json = self.label("chair", tip=[self.TIP, "has legs"])
        chair = first(self.factory.create_labels([json]))
        self.assertEqual((self.TIP, "has legs"), chair.tips)

    def test_label_with_grammatical_number_and_one_tip_for_all_grammatical_forms(self):
        """Test creating a label with singular and plural and one tip for both forms."""
        json = self.label_with_grammatical_number(tip=self.TIP)
        for label in self.factory.create_labels([json]):
            self.assertEqual((self.TIP,), label.tips)

    def test_label_with_grammatical_number_and_a_tip_for_one_grammatical_form(self):
        """Test creating a label with singular and plural forms and a tip for one form."""
        json = self.label_with_grammatical_number(tip={"singular": self.TIP})
        singular, plural = self.factory.create_labels([json])
        self.assertEqual((self.TIP,), singular.tips)
        self.assertEqual((), plural.tips)

    def test_label_with_grammatical_number_and_diminutive_and_a_tip_for_one_grammatical_form(self):
        """Test creating a label with nested grammatical forms and a tip for one form."""
        tip: JSONGrammar = {"root": {"plural": self.TIP}}
        json = self.label_with_grammatical_number_and_diminutive(tip=tip)
        root_singular, root_plural, diminutive_singular, diminutive_plural = self.factory.create_labels([json])
        self.assertEqual((), root_singular.tips)
        self.assertEqual((self.TIP,), root_plural.tips)
        self.assertEqual((), diminutive_singular.tips)
        self.assertEqual((), diminutive_plural.tips)


class LabelFactoryNoteTest(LabelFactoryTestCase):
    """Test creating labels with notes."""

    NOTE = "chair can also be a person that leads a meeting or committee"

    def test_label_without_note(self):
        """Test creating a label without note."""
        json = self.label("chair")
        chair = first(self.factory.create_labels([json]))
        self.assertEqual((), chair.notes)

    def test_label_with_note(self):
        """Test creating a label with note."""
        json = self.label("chair", note=self.NOTE)
        chair = first(self.factory.create_labels([json]))
        self.assertEqual((self.NOTE,), chair.notes)

    def test_label_with_notes(self):
        """Test creating a label with multiple notes."""
        json = self.label("chair", note=[self.NOTE, "chair can also be a verb: to chair"])
        chair = first(self.factory.create_labels([json]))
        self.assertEqual((self.NOTE, "chair can also be a verb: to chair"), chair.notes)

    def test_label_with_grammatical_number_and_one_note_for_all_grammatical_forms(self):
        """Test creating a label with singular and plural and one note for both forms."""
        json = self.label_with_grammatical_number(note=self.NOTE)
        for label in self.factory.create_labels([json]):
            self.assertEqual((self.NOTE,), label.notes)

    def test_label_with_grammatical_number_and_a_note_for_one_grammatical_form(self):
        """Test creating a label with singular and plural forms and a note for one form."""
        json = self.label_with_grammatical_number(note={"singular": self.NOTE})
        singular, plural = self.factory.create_labels([json])
        self.assertEqual((self.NOTE,), singular.notes)
        self.assertEqual((), plural.notes)

    def test_label_with_grammatical_number_and_diminutive_and_a_note_for_one_grammatical_form(self):
        """Test creating a label with nested grammatical forms and a note for one form."""
        note: JSONGrammar = {"root": {"plural": self.NOTE}}
        json = self.label_with_grammatical_number_and_diminutive(note=note)
        root_singular, root_plural, diminutive_singular, diminutive_plural = self.factory.create_labels([json])
        self.assertEqual((), root_singular.notes)
        self.assertEqual((self.NOTE,), root_plural.notes)
        self.assertEqual((), diminutive_singular.notes)
        self.assertEqual((), diminutive_plural.notes)


class LabelFactoryClozeTestTest(LabelFactoryTestCase):
    """Test creating labels with cloze tests."""

    def test_label_without_cloze_tests(self):
        """Test creating a label without cloze tests."""
        json = self.label("Minä pidän jäätelöstä.")
        label = first(self.factory.create_labels([json]))
        self.assertEqual((), label.cloze_tests)

    def test_label_with_cloze_test(self):
        """Test creating a label with a cloze test."""
        json = self.label("Minä pidän jäätelöstä.", cloze="Minä (pitää) (jäätelö).")
        label = first(self.factory.create_labels([json]))
        self.assertEqual(("Minä (pitää) (jäätelö).",), label.cloze_tests.as_strings)

    def test_label_with_cloze_tests(self):
        """Test creating a label with multiple cloze tests."""
        json = self.label("Minä pidän jäätelöstä.", cloze=["Minä pidän (jäätelö).", "Minä (pitää) jäätelöstä."])
        label = first(self.factory.create_labels([json]))
        self.assertEqual(("Minä pidän (jäätelö).", "Minä (pitää) jäätelöstä."), label.cloze_tests.as_strings)

    def test_label_with_grammatical_number_and_one_cloze_test_for_all_grammatical_forms(self):
        """Test creating a label with singular and plural and one cloze test for both forms."""
        json = self.label_with_grammatical_number(
            singular="Minä pidän jäätelöstä.",
            plural="Me pidämme jäätelöstä.",
            cloze="(Minä/Me) (pitää) (jäätelö).",
        )
        for label in self.factory.create_labels([json]):
            self.assertEqual(("(Minä/Me) (pitää) (jäätelö).",), label.cloze_tests.as_strings)

    def test_label_with_grammatical_number_and_a_cloze_test_for_one_grammatical_form(self):
        """Test creating a label with singular and plural forms and a cloze test for one form."""
        json = self.label_with_grammatical_number(
            singular="Minä pidän jäätelöstä.",
            plural="Me pidämme jäätelöstä.",
            cloze={"singular": "Minä (pitää) (jäätelö)."},
        )
        singular, plural = self.factory.create_labels([json])
        self.assertEqual(("Minä (pitää) (jäätelö).",), singular.cloze_tests.as_strings)
        self.assertEqual((), plural.cloze_tests)

    def test_label_with_grammatical_number_and_diminutive_and_a_cloze_test_for_one_grammatical_form(self):
        """Test creating a label with nested grammatical forms and a cloze test for one form."""
        cloze_test: JSONGrammar = {"root": {"plural": "Me pidämme jäätelöstä."}}
        json = self.label_with_grammatical_number_and_diminutive(cloze=cloze_test)
        root_singular, root_plural, diminutive_singular, diminutive_plural = self.factory.create_labels([json])
        self.assertEqual((), root_singular.cloze_tests)
        self.assertEqual(("Me pidämme jäätelöstä.",), root_plural.cloze_tests.as_strings)
        self.assertEqual((), diminutive_singular.cloze_tests)
        self.assertEqual((), diminutive_plural.cloze_tests)
