"""Quiz factory unit tests."""

from typing import cast

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptJSON

from ....base import LabelDict, ToistoTestCase

OLLA_PRESENT_TENSE = {
    "singular": {"first person": "minä olen", "second person": "sinä olet", "third person": "hän on"},
    "plural": {"first person": "me olemme", "second person": "te olette", "third person": "he ovat"},
}

ZIJN_PRESENT_TENSE = {
    "singular": {"first person": "ik ben", "second person": "jij bent", "third person": "zij is"},
    "plural": {"first person": "wij zijn", "second person": "jullie zijn", "third person": "zij zijn"},
}


class QuizFactoryTestCase(ToistoTestCase):
    """Base class for quiz factory unit tests."""

    def create_verb_with_person(self) -> Concept:
        """Create a verb with grammatical person."""
        return self.create_concept(
            "to eat",
            labels=[
                {
                    "label": {"first person": "I eat", "second person": "you eat", "third person": "she eats"},
                    "language": EN,
                },
                {
                    "label": {"first person": "ik eet", "second person": "jij eet", "third person": "zij eet"},
                    "language": NL,
                },
            ],
        )

    def create_verb_with_tense_and_person(self, *, include_perfect_tense: bool = False) -> Concept:
        """Create a verb with grammatical person nested within tense."""
        label_en = {
            "present tense": {"singular": "I eat", "plural": "we eat"},
            "past tense": {"singular": "I ate", "plural": "we ate"},
        }
        label_nl = {
            "present tense": {"singular": "ik eet", "plural": "wij eten"},
            "past tense": {"singular": "ik at", "plural": "wij aten"},
        }
        if include_perfect_tense:
            label_en["present perfect tense"] = {"singular": "I have eaten", "plural": "we have eaten"}
            label_nl["present perfect tense"] = {"singular": "ik heb gegeten", "plural": "wij hebben gegeten"}
            label_en["past perfect tense"] = {"singular": "I had eaten", "plural": "we had eaten"}
            label_nl["past perfect tense"] = {"singular": "ik had gegeten", "plural": "wij hadden gegeten"}
        return self.create_concept(
            "to eat", labels=[{"label": label_en, "language": EN}, {"label": label_nl, "language": NL}]
        )

    def create_verb_with_infinitive_and_person(self) -> Concept:
        """Create a verb with infinitive and grammatical person."""
        return self.create_concept(
            "to sleep",
            labels=[
                {"label": {"infinitive": "to sleep", "singular": "I sleep", "plural": "we sleep"}, "language": EN},
                {"label": {"infinitive": "slapen", "singular": "ik slaap", "plural": "wij slapen"}, "language": NL},
            ],
        )

    def create_verb_with_infinitive_and_number_and_person(self) -> Concept:
        """Create a verb with infinitive and grammatical number nested with person."""
        return self.create_concept(
            "to be",
            labels=[
                cast(
                    "LabelDict",
                    {
                        "label": {"infinitive": "olla"} | OLLA_PRESENT_TENSE,
                        "language": FI,
                    },
                ),
                cast(
                    "LabelDict",
                    {
                        "label": {"infinitive": "zijn"} | ZIJN_PRESENT_TENSE,
                        "language": NL,
                    },
                ),
            ],
        )

    def create_adjective_with_degrees_of_comparison(self, antonym: str = "") -> Concept:
        """Create an adjective with degrees of comparison."""
        labels: list[LabelDict] = [
            {
                "label": {"positive degree": "big", "comparative degree": "bigger", "superlative degree": "biggest"},
                "language": EN,
            },
            {
                "label": {"positive degree": "groot", "comparative degree": "groter", "superlative degree": "grootst"},
                "language": NL,
            },
        ]
        big: ConceptJSON = {"antonym": ConceptId(antonym)} if antonym else {}
        return self.create_concept("big", big, labels=labels)

    def create_noun(self) -> Concept:
        """Create a simple noun."""
        return self.create_concept(
            "mall", labels=[{"label": "kauppakeskus", "language": FI}, {"label": "het winkelcentrum", "language": NL}]
        )

    def create_noun_with_grammatical_number(self) -> Concept:
        """Create a noun with grammatical number."""
        return self.create_concept(
            "morning",
            labels=[
                {"label": {"singular": "aamu", "plural": "aamut"}, "language": FI},
                {"label": {"singular": "de ochtend", "plural": "de ochtenden"}, "language": NL},
            ],
        )

    def create_noun_with_grammatical_gender(self) -> Concept:
        """Create a noun with grammatical gender."""
        return self.create_concept(
            "cat",
            labels=[
                {"label": {"feminine": "her cat", "masculine": "his cat"}, "language": EN},
                {"label": {"feminine": "haar kat", "masculine": "zijn kat"}, "language": NL},
            ],
        )

    def create_noun_with_grammatical_gender_including_neuter(self) -> Concept:
        """Create a noun with grammatical gender, including neuter."""
        return self.create_concept(
            "bone",
            labels=[
                {"label": {"feminine": "her bone", "masculine": "his bone", "neuter": "its bone"}, "language": EN},
                {"label": {"feminine": "haar bot", "masculine": "zijn bot", "neuter": "zijn bot"}, "language": NL},
            ],
        )

    def create_noun_with_grammatical_number_and_gender(self) -> Concept:
        """Create a noun with grammatical number and grammatical gender."""
        return self.create_concept(
            "cat",
            labels=[
                {
                    "label": {
                        "singular": {"feminine": "her cat", "masculine": "his cat"},
                        "plural": {"feminine": "her cats", "masculine": "his cats"},
                    },
                    "language": EN,
                },
                {
                    "label": {
                        "singular": {"feminine": "haar kat", "masculine": "zijn kat"},
                        "plural": {"feminine": "haar katten", "masculine": "zijn katten"},
                    },
                    "language": NL,
                },
            ],
        )
