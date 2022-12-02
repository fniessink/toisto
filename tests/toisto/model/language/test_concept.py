"""Concept unit tests."""

from toisto.model import concept_factory, Label

from ...base import ToistoTestCase


class ConceptQuizzesTest(ToistoTestCase):
    """Unit tests for the concept class."""

    def test_quizzes(self):
        """Test that quizzes can be generated from a concept."""
        concept = concept_factory("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual(
            set([
                self.create_quiz("english", "nl", "en", "Engels", ["English"]),
                self.create_quiz("english", "en", "nl", "English", ["Engels"]),
                self.create_quiz("english", "nl", "nl", "Engels", ["Engels"], "listen")
            ]),
            concept.quizzes("nl", "en")
        )

    def test_multiple_labels(self):
        """Test that quizzes can be generated from a concept with a language with multiple labels."""
        concept = concept_factory("couch", dict(nl=["Bank"], en=["Couch", "Bank"]))
        self.assertEqual(
            set([
                self.create_quiz("couch", "nl", "en", "Bank", ["Couch", "Bank"]),
                self.create_quiz("couch", "en", "nl", "Couch", ["Bank"]),
                self.create_quiz("couch", "en", "nl", "Bank", ["Bank"]),
                self.create_quiz("couch", "nl", "nl", "Bank", ["Bank"], "listen")
            ]),
            concept.quizzes("nl", "en")
        )

    def test_missing_language(self):
        """Test that quizzes can be generated from a concept even if it's missing one of the languages."""
        concept = concept_factory("english", dict(en=["English"], nl=["Engels"]))
        self.assertEqual(set(), concept.quizzes("fi", "en"))

    def test_grammatical_number(self):
        """Test that quizzes can be generated for different grammatical numbers, i.e. singular and plural."""
        concept = concept_factory(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        self.assertEqual(
            set([
                self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]),
                self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]),
                self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"),
                self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]),
                self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]),
                self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"),
                self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"),
                self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize")
            ]),
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_number_without_plural(self):
        """Test that quizzes can be generated even if one language has no plural labels for the concept."""
        concept = concept_factory(
            "ketchup", dict(singular=dict(fi="Ketsuppi", nl="De ketchup"), plural=dict(fi="Ketsupit"))
        )
        self.assertEqual(
            set([
                self.create_quiz("ketchup", "fi", "nl", "Ketsuppi", ["De ketchup"]),
                self.create_quiz("ketchup", "nl", "fi", "De ketchup", ["Ketsuppi"]),
                self.create_quiz("ketchup", "fi", "fi", "Ketsuppi", ["Ketsuppi"], "listen"),
                self.create_quiz("ketchup", "fi", "fi", "Ketsupit", ["Ketsupit"], "listen"),
                self.create_quiz("ketchup", "fi", "fi", "Ketsuppi", ["Ketsupit"], "pluralize"),
                self.create_quiz("ketchup", "fi", "fi", "Ketsupit", ["Ketsuppi"], "singularize")
            ]),
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_number_with_one_language(self):
        """Test that quizzes can be generated from a concept with labels in the practice language only."""
        concept = concept_factory("mämmi", dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(
            set([
                self.create_quiz("mämmi", "fi", "fi", "Mämmi", ["Mämmi"], "listen"),
                self.create_quiz("mämmi", "fi", "fi", "Mämmit", ["Mämmit"], "listen"),
                self.create_quiz("mämmi", "fi", "fi", "Mämmi", ["Mämmit"], "pluralize"),
                self.create_quiz("mämmi", "fi", "fi", "Mämmit", ["Mämmi"], "singularize")
            ]),
            concept.quizzes("fi", "en")
        )

    def test_grammatical_number_with_one_language_reversed(self):
        """Test that no quizzes can be generated from a noun concept with labels in the native language."""
        concept = concept_factory("mämmi", dict(singular=dict(fi="Mämmi"), plural=dict(fi="Mämmit")))
        self.assertEqual(set(), concept.quizzes("en", "fi"))

    def test_grammatical_number_with_synonyms(self):
        """Test that in case of synonyms the plural of one synonym isn't the correct answer for the other synonym."""
        concept = concept_factory(
            "mall",
            dict(
                singular=dict(fi=["Kauppakeskus", "Ostoskeskus"], nl="Het winkelcentrum"),
                plural=dict(fi=["Kauppakeskukset", "Ostoskeskukset"], nl="De winkelcentra")
            )
        )
        self.assertEqual(
            set([
                self.create_quiz("mall", "fi", "nl", "Kauppakeskus", ["Het winkelcentrum"]),
                self.create_quiz("mall", "fi", "nl", "Ostoskeskus", ["Het winkelcentrum"],),
                self.create_quiz("mall", "nl", "fi", "Het winkelcentrum", ["Kauppakeskus", "Ostoskeskus"]),
                self.create_quiz("mall", "fi", "fi", "Kauppakeskus", ["Kauppakeskus"], "listen"),
                self.create_quiz("mall", "fi", "fi", "Ostoskeskus", ["Ostoskeskus"], "listen"),
                self.create_quiz("mall", "fi", "nl", "Kauppakeskukset", ["De winkelcentra"]),
                self.create_quiz("mall", "fi", "nl", "Ostoskeskukset", ["De winkelcentra"]),
                self.create_quiz("mall", "nl", "fi", "De winkelcentra", ["Kauppakeskukset", "Ostoskeskukset"]),
                self.create_quiz("mall", "fi", "fi", "Kauppakeskukset", ['Kauppakeskukset'], "listen"),
                self.create_quiz("mall", "fi", "fi", "Ostoskeskukset", ['Ostoskeskukset'], "listen"),
                self.create_quiz("mall", "fi", "fi", "Kauppakeskus", ["Kauppakeskukset"], "pluralize"),
                self.create_quiz("mall", "fi", "fi", "Ostoskeskus", ["Ostoskeskukset"], "pluralize"),
                self.create_quiz("mall", "fi", "fi", "Kauppakeskukset", ['Kauppakeskus'], "singularize"),
                self.create_quiz("mall", "fi", "fi", "Ostoskeskukset", ["Ostoskeskus"], "singularize")
            ]),
            concept.quizzes("fi", "nl")
        )

    def test_grammatical_gender(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            "cat",
            dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat"))
        )
        self.assertEqual(
            set([
                self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"),
                self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"),
                self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"),
                self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize")
            ]),
            concept.quizzes("nl", "en")
        )

    def test_grammatical_gender_with_neuter(self):
        """Test that quizzes can be generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            "bone",
            dict(
                female=dict(en="Her bone", nl="Haar bot"),
                male=dict(en="His bone", nl="Zijn bot"),
                neuter=dict(en="Its bone", nl="Zijn bot")
            )
        )
        self.assertEqual(
            set([
                self.create_quiz("bone", "nl", "en", "Haar bot", ["Her bone"], "translate"),
                self.create_quiz("bone", "en", "nl", "Her bone", ["Haar bot"], "translate"),
                self.create_quiz("bone", "nl", "nl", "Haar bot", ["Haar bot"], "listen"),
                self.create_quiz("bone", "nl", "en", "Zijn bot", ["His bone"], "translate"),
                self.create_quiz("bone", "en", "nl", "His bone", ["Zijn bot"], "translate"),
                self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"),
                self.create_quiz("bone", "nl", "en", "Zijn bot", ["Its bone"], "translate"),
                self.create_quiz("bone", "en", "nl", "Its bone", ["Zijn bot"], "translate"),
                self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"),
                self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "masculinize"),
                self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "neuterize"),
                self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"),
                self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize")
            ]),
            concept.quizzes("nl", "en")
        )

    def test_grammatical_number_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical number nested with grammatical gender."""
        concept = concept_factory(
            "cat",
            dict(
                singular=dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat")),
                plural=dict(female=dict(en="Her cats", nl="Haar katten"), male=dict(en="His cats", nl="Zijn katten"))
            )
        )
        self.assertEqual(
            set([
                self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"),
                self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"),
                self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"),
                self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                self.create_quiz("cat", "nl", "en", "Haar katten", ["Her cats"], "translate"),
                self.create_quiz("cat", "en", "nl", "Her cats", ["Haar katten"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar katten"], "listen"),
                self.create_quiz("cat", "nl", "en", "Zijn katten", ["His cats"], "translate"),
                self.create_quiz("cat", "en", "nl", "His cats", ["Zijn katten"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"),
                self.create_quiz("cat", "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Haar katten"], "feminize"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize")
            ]),
            concept.quizzes("nl", "en")
        )

    def test_degrees_of_comparison(self):
        """Test that quizzes can be generated for degrees of comparison."""
        concept = concept_factory(
            "big",
            {
                "positive degree": dict(en="Big", nl="Groot"),
                "comparitive degree": dict(en="Bigger", nl="Groter"),
                "superlative degree": dict(en="Biggest", nl="Grootst")
            }
        )
        self.assertEqual(
            set([
                self.create_quiz("big", "nl", "en", "Groot", ["Big"], "translate"),
                self.create_quiz("big", "en", "nl", "Big", ["Groot"], "translate"),
                self.create_quiz("big", "nl", "nl", "Groot", ["Groot"], "listen"),
                self.create_quiz("big", "nl", "en", "Groter", ["Bigger"], "translate"),
                self.create_quiz("big", "en", "nl", "Bigger", ["Groter"], "translate"),
                self.create_quiz("big", "nl", "nl", "Groter", ["Groter"], "listen"),
                self.create_quiz("big", "nl", "en", "Grootst", ["Biggest"], "translate"),
                self.create_quiz("big", "en", "nl", "Biggest", ["Grootst"], "translate"),
                self.create_quiz("big", "nl", "nl", "Grootst", ["Grootst"], "listen"),
                self.create_quiz("big", "nl", "nl", "Groot", ["Groter"], "give comparitive degree"),
                self.create_quiz("big", "nl", "nl", "Groot", ["Grootst"], "give superlative degree"),
                self.create_quiz("big", "nl", "nl", "Groter", ["Groot"], "give positive degree"),
                self.create_quiz("big", "nl", "nl", "Groter", ["Grootst"], "give superlative degree"),
                self.create_quiz("big", "nl", "nl", "Grootst", ["Groot"], "give positive degree"),
                self.create_quiz("big", "nl", "nl", "Grootst", ["Groter"], "give comparitive degree"),
            ]),
            concept.quizzes("nl", "en")
        )

    def test_degrees_of_comparison_with_synonyms(self):
        """Test that quizzes can be generated for degrees of comparison with synonyms."""
        concept = concept_factory(
            "big",
            {
                "positive degree": dict(en="Big", fi=["Iso", "Suuri"]),
                "comparitive degree": dict(en="Bigger", fi=["Isompi", "Suurempi"]),
                "superlative degree": dict(en="Biggest", fi=["Isoin", "Suurin"])
            }
        )
        self.assertEqual(
            set([
                self.create_quiz("big", "fi", "en", "Iso", ["Big"], "translate"),
                self.create_quiz("big", "fi", "en", "Suuri", ["Big"], "translate"),
                self.create_quiz("big", "en", "fi", "Big", ["Iso", "Suuri"], "translate"),
                self.create_quiz("big", "fi", "fi", "Iso", ["Iso"], "listen"),
                self.create_quiz("big", "fi", "fi", "Suuri", ["Suuri"], "listen"),
                self.create_quiz("big", "fi", "en", "Isompi", ["Bigger"], "translate"),
                self.create_quiz("big", "fi", "en", "Suurempi", ["Bigger"], "translate"),
                self.create_quiz("big", "en", "fi", "Bigger", ["Isompi", "Suurempi"], "translate"),
                self.create_quiz("big", "fi", "fi", "Isompi", ["Isompi"], "listen"),
                self.create_quiz("big", "fi", "fi", "Suurempi", ["Suurempi"], "listen"),
                self.create_quiz("big", "fi", "en", "Isoin", ["Biggest"], "translate"),
                self.create_quiz("big", "fi", "en", "Suurin", ["Biggest"], "translate"),
                self.create_quiz("big", "en", "fi", "Biggest", ["Isoin", "Suurin"], "translate"),
                self.create_quiz("big", "fi", "fi", "Isoin", ["Isoin"], "listen"),
                self.create_quiz("big", "fi", "fi", "Suurin", ["Suurin"], "listen"),
                self.create_quiz("big", "fi", "fi", "Iso", ["Isompi"], "give comparitive degree"),
                self.create_quiz("big", "fi", "fi", "Suuri", ["Suurempi"], "give comparitive degree"),
                self.create_quiz("big", "fi", "fi", "Iso", ["Isoin"], "give superlative degree"),
                self.create_quiz("big", "fi", "fi", "Suuri", ["Suurin"], "give superlative degree"),
                self.create_quiz("big", "fi", "fi", "Isompi", ["Iso"], "give positive degree"),
                self.create_quiz("big", "fi", "fi", "Suurempi", ["Suuri"], "give positive degree"),
                self.create_quiz("big", "fi", "fi", "Isompi", ["Isoin"], "give superlative degree"),
                self.create_quiz("big", "fi", "fi", "Suurempi", ["Suurin"], "give superlative degree"),
                self.create_quiz("big", "fi", "fi", "Isoin", ["Iso"], "give positive degree"),
                self.create_quiz("big", "fi", "fi", "Suurin", ["Suuri"], "give positive degree"),
                self.create_quiz("big", "fi", "fi", "Isoin", ["Isompi"], "give comparitive degree"),
                self.create_quiz("big", "fi", "fi", "Suurin", ["Suurempi"], "give comparitive degree"),
            ]),
            concept.quizzes("fi", "en")
        )

    def test_grammatical_person(self):
        """Test that quizzes can be generated for grammatical person."""
        concept = concept_factory(
            "to eat",
            {
                "first person": dict(en="I eat", nl="Ik eet"),
                "second person": dict(en="You eat", nl="Jij eet"),
                "third person": dict(en="She eats", nl="Zij eet")
            }
        )
        self.assertEqual(
            set([
                self.create_quiz("to eat", "nl", "en", "Ik eet", ["I eat"], "translate"),
                self.create_quiz("to eat", "en", "nl", "I eat", ["Ik eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Ik eet"], "listen"),
                self.create_quiz("to eat", "nl", "en", "Jij eet", ["You eat"], "translate"),
                self.create_quiz("to eat", "en", "nl", "You eat", ["Jij eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Jij eet", ["Jij eet"], "listen"),
                self.create_quiz("to eat", "nl", "en", "Zij eet", ["She eats"], "translate"),
                self.create_quiz("to eat", "en", "nl", "She eats", ["Zij eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Zij eet"], "listen"),
                self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                self.create_quiz("to eat", "nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                self.create_quiz("to eat", "nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            ]),
            concept.quizzes("nl", "en")
        )

    def test_grammatical_person_nested_with_grammatical_gender(self):
        """Test that quizzes can be generated for grammatical person, nested with grammatical gender."""
        concept = concept_factory(
            "to eat",
            {
                "first person": dict(en="I eat", nl="Ik eet"),
                "second person": dict(en="You eat", nl="Jij eet"),
                "third person": dict(female=dict(en="She eats", nl="Zij eet"), male=dict(en="He eats", nl="Hij eet"))
            }
        )
        self.assertEqual(
            set([
                self.create_quiz("to eat", "nl", "en", "Ik eet", ["I eat"], "translate"),
                self.create_quiz("to eat", "en", "nl", "I eat", ["Ik eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Ik eet"], "listen"),
                self.create_quiz("to eat", "nl", "en", "Jij eet", ["You eat"], "translate"),
                self.create_quiz("to eat", "en", "nl", "You eat", ["Jij eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Jij eet", ["Jij eet"], "listen"),
                self.create_quiz("to eat", "nl", "en", "Zij eet", ["She eats"], "translate"),
                self.create_quiz("to eat", "en", "nl", "She eats", ["Zij eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Zij eet"], "listen"),
                self.create_quiz("to eat", "nl", "en", "Hij eet", ["He eats"], "translate"),
                self.create_quiz("to eat", "en", "nl", "He eats", ["Hij eet"], "translate"),
                self.create_quiz("to eat", "nl", "nl", "Hij eet", ["Hij eet"], "listen"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Hij eet"], "masculinize"),
                self.create_quiz("to eat", "nl", "nl", "Hij eet", ["Zij eet"], "feminize"),
                self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Jij eet"], "give second person"),
                self.create_quiz("to eat", "nl", "nl", "Ik eet", ["Zij eet"], "give third person"),
                self.create_quiz("to eat", "nl", "nl", "Jij eet", ["Ik eet"], "give first person"),
                self.create_quiz("to eat", "nl", "nl", "Jij eet", ["Zij eet"], "give third person"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Ik eet"], "give first person"),
                self.create_quiz("to eat", "nl", "nl", "Zij eet", ["Jij eet"], "give second person"),
            ]),
            concept.quizzes("nl", "en")
        )

    def test_grammatical_number_nested_with_grammatical_person(self):
        """Test that quizzes can be generated for grammatical number, nested with grammatical person."""
        concept = concept_factory(
            "to have",
            dict(
                singular={
                    "first person": dict(fi="Minulla on", nl="Ik heb"),
                    "second person": dict(fi="Sinulla on", nl="Jij hebt"),
                    "third person": dict(fi="Hänellä on", nl="Zij heeft"),
                },
                plural={
                    "first person": dict(fi="Meillä on", nl="Wij hebben"),
                    "second person": dict(fi="Teillä on", nl="Jullie hebben"),
                    "third person": dict(fi="Heillä on", nl="Zij hebben"),
                }
            )
        )
        self.assertEqual(
            set([
                self.create_quiz("to have", "nl", "fi", "Ik heb", ["Minulla on"], "translate"),
                self.create_quiz("to have", "fi", "nl", "Minulla on", ["Ik heb"], "translate"),
                self.create_quiz("to have", "nl", "nl", "Ik heb", ["Ik heb"], "listen"),
                self.create_quiz("to have", "nl", "fi", "Jij hebt", ["Sinulla on"], "translate"),
                self.create_quiz("to have", "fi", "nl", "Sinulla on", ["Jij hebt"], "translate"),
                self.create_quiz("to have", "nl", "nl", "Jij hebt", ["Jij hebt"], "listen"),
                self.create_quiz("to have", "nl", "fi", "Zij heeft", ["Hänellä on"], "translate"),
                self.create_quiz("to have", "fi", "nl", "Hänellä on", ["Zij heeft"], "translate"),
                self.create_quiz("to have", "nl", "nl", "Zij heeft", ["Zij heeft"], "listen"),
                self.create_quiz("to have", "nl", "nl", "Ik heb", ["Jij hebt"], "give second person"),
                self.create_quiz("to have", "nl", "nl", "Ik heb", ["Zij heeft"], "give third person"),
                self.create_quiz("to have", "nl", "nl", "Jij hebt", ["Ik heb"], "give first person"),
                self.create_quiz("to have", "nl", "nl", "Jij hebt", ["Zij heeft"], "give third person"),
                self.create_quiz("to have", "nl", "nl", "Zij heeft", ["Ik heb"], "give first person"),
                self.create_quiz("to have", "nl", "nl", "Zij heeft", ["Jij hebt"], "give second person"),
                self.create_quiz("to have", "nl", "fi", "Wij hebben", ["Meillä on"], "translate"),
                self.create_quiz("to have", "fi", "nl", "Meillä on", ["Wij hebben"], "translate"),
                self.create_quiz("to have", "nl", "nl", "Wij hebben", ["Wij hebben"], "listen"),
                self.create_quiz("to have", "nl", "fi", "Jullie hebben", ["Teillä on"], "translate"),
                self.create_quiz("to have", "fi", "nl", "Teillä on", ["Jullie hebben"], "translate"),
                self.create_quiz("to have", "nl", "nl", "Jullie hebben", ["Jullie hebben"], "listen"),
                self.create_quiz("to have", "nl", "fi", "Zij hebben", ["Heillä on"], "translate"),
                self.create_quiz("to have", "fi", "nl", "Heillä on", ["Zij hebben"], "translate"),
                self.create_quiz("to have", "nl", "nl", "Zij hebben", ["Zij hebben"], "listen"),
                self.create_quiz("to have", "nl", "nl", "Wij hebben", ["Jullie hebben"], "give second person"),
                self.create_quiz("to have", "nl", "nl", "Wij hebben", ["Zij hebben"], "give third person"),
                self.create_quiz("to have", "nl", "nl", "Jullie hebben", ["Wij hebben"], "give first person"),
                self.create_quiz("to have", "nl", "nl", "Jullie hebben", ["Zij hebben"], "give third person"),
                self.create_quiz("to have", "nl", "nl", "Zij hebben", ["Wij hebben"], "give first person"),
                self.create_quiz("to have", "nl", "nl", "Zij hebben", ["Jullie hebben"], "give second person"),
                self.create_quiz("to have", "nl", "nl", "Ik heb", ["Wij hebben"], "pluralize"),
                self.create_quiz("to have", "nl", "nl", "Wij hebben", ["Ik heb"], "singularize"),
                self.create_quiz("to have", "nl", "nl", "Jij hebt", ["Jullie hebben"], "pluralize"),
                self.create_quiz("to have", "nl", "nl", "Jullie hebben", ["Jij hebt"], "singularize"),
                self.create_quiz("to have", "nl", "nl", "Zij heeft", ["Zij hebben"], "pluralize"),
                self.create_quiz("to have", "nl", "nl", "Zij hebben", ["Zij heeft"], "singularize"),
            ]),
            concept.quizzes("nl", "fi")
        )

    def test_grammatical_gender_nested_with_grammatical_number(self):
        """Test that quizzes can be generated for nested concepts."""
        concept = concept_factory(
            "cat",
            dict(
                female=dict(singular=dict(en="Her cat", nl="Haar kat"), plural=dict(en="Her cats", nl="Haar katten")),
                male=dict(singular=dict(en="His cat", nl="Zijn kat"), plural=dict(en="His cats", nl="Zijn katten"))
            )
        )
        self.assertEqual(
            set([
                self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"),
                self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"),
                self.create_quiz("cat", "nl", "en", "Haar katten", ["Her cats"], "translate"),
                self.create_quiz("cat", "en", "nl", "Her cats", ["Haar katten"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar katten"], "listen"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"),
                self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar kat"], "singularize"),
                self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"),
                self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"),
                self.create_quiz("cat", "nl", "en", "Zijn katten", ["His cats"], "translate"),
                self.create_quiz("cat", "en", "nl", "His cats", ["Zijn katten"], "translate"),
                self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"),
                self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"),
                self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"),
                self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"),
                self.create_quiz("cat", "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"),
                self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Haar katten"], "feminize")
            ]),
            concept.quizzes("nl", "en")
        )

    def test_same_label_in_different_composite_concepts(self):
        """Test that the same label in different leaf concepts is ignored."""
        concept = concept_factory(
            "to be",
            dict(
                female=dict(en="She is|She's", fi="Hän on|On;female"),
                male=dict(en="He is|He's", fi="Hän on|On;male")
            )
        )
        self.assertEqual(
            set([
                self.create_quiz("to be", "fi", "en", Label("Hän on|On;female"), ("She is|She's",)),
                self.create_quiz("to be", "en", "fi", "She is|She's", ("Hän on|On;female",)),
                self.create_quiz("to be", "fi", "fi", "Hän on|On;female", ("Hän on|On;female",), "listen"),
                self.create_quiz("to be", "fi", "en", "Hän on|On;male", ("He is|He's",)),
                self.create_quiz("to be", "en", "fi", "He is|He's", ("Hän on|On;male",))
            ]),
            concept.quizzes("fi", "en")
        )


class ConceptRelationshipsTest(ToistoTestCase):
    """Unit tests for relationships between concepts."""

    def test_concept_relationship_leaf_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = concept_factory(
            "mall",
            dict(uses=["shop", "centre"], fi="Kauppakeskus", nl="Het winkelcentrum"),
        )
        self.assertEqual(("shop", "centre"), concept.quizzes("fi", "nl").pop().uses)

    def test_concept_relationship_composite_concept(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = concept_factory(
            "mall",
            dict(
                uses=["shop", "centre"],
                singular=dict(fi="Kauppakeskus", nl="Het winkelcentrum"),
                plural=dict(fi="Kauppakeskukset", nl="De winkelcentra")
            )
        )
        for quiz in concept.quizzes("fi", "nl"):
            self.assertIn("shop", quiz.uses)
            self.assertIn("centre", quiz.uses)

    def test_concept_relationship_leaf_concept_one_uses(self):
        """Test that concepts can declare to use, i.e. depend on, other concepts."""
        concept = concept_factory("capital", dict(uses="city", fi="Pääkaupunki", en="Capital"))
        self.assertEqual(("city",), concept.quizzes("fi", "en").pop().uses)

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = concept_factory(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        expected_concept_ids = {
            self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]): "morning/singular",
            self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]): "morning/singular",
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"): "morning/singular",
            self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]): "morning/plural",
            self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]): "morning/plural",
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"): "morning/plural",
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"): "morning",
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize"): "morning"
        }
        for quiz in concept.quizzes("fi", "nl"):
            self.assertEqual(expected_concept_ids[quiz], quiz.concept_id)

    def test_generated_uses_for_grammatical_number(self):
        """Test that constituent concepts get a generated uses list."""
        concept = concept_factory(
            "morning", dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden"))
        )
        expected_uses = {
            self.create_quiz("morning", "fi", "nl", "Aamu", ["De ochtend"]): (),
            self.create_quiz("morning", "nl", "fi", "De ochtend", ["Aamu"]): (),
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamu"], "listen"): (),
            self.create_quiz("morning", "fi", "nl", "Aamut", ["De ochtenden"]): ("morning/singular",),
            self.create_quiz("morning", "nl", "fi", "De ochtenden", ["Aamut"]): ("morning/singular",),
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamut"], "listen"): ("morning/singular",),
            self.create_quiz("morning", "fi", "fi", "Aamu", ["Aamut"], "pluralize"): ("morning/plural",),
            self.create_quiz("morning", "fi", "fi", "Aamut", ["Aamu"], "singularize"): ("morning/singular",)
        }
        for quiz in concept.quizzes("fi", "nl"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_grammatical_gender(self):
        """Test that use relations are generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            "cat",
            dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat"))
        )
        expected_uses = {
            self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"): (),
            self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"): ("cat/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"): ("cat/female",)
        }
        for quiz in concept.quizzes("nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_grammatical_gender_with_neuter(self):
        """Test that use relations are generated for different grammatical genders, i.e. female and male."""
        concept = concept_factory(
            "bone",
            dict(
                female=dict(en="Her bone", nl="Haar bot"),
                male=dict(en="His bone", nl="Zijn bot"),
                neuter=dict(en="Its bone", nl="Zijn bot")
            )
        )
        expected_uses = {
            self.create_quiz("bone", "nl", "en", "Haar bot", ["Her bone"], "translate"): (),
            self.create_quiz("bone", "en", "nl", "Her bone", ["Haar bot"], "translate"): (),
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Haar bot"], "listen"): (),
            self.create_quiz("bone", "nl", "en", "Zijn bot", ["His bone"], "translate"): (),
            self.create_quiz("bone", "en", "nl", "His bone", ["Zijn bot"], "translate"): (),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"): (),
            self.create_quiz("bone", "nl", "en", "Zijn bot", ["Its bone"], "translate"): (),
            self.create_quiz("bone", "en", "nl", "Its bone", ["Zijn bot"], "translate"): (),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Zijn bot"], "listen"): (),
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "masculinize"): ("bone/male",),
            self.create_quiz("bone", "nl", "nl", "Haar bot", ["Zijn bot"], "neuterize"): ("bone/neuter",),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"): ("bone/female",),
            self.create_quiz("bone", "nl", "nl", "Zijn bot", ["Haar bot"], "feminize"): ("bone/female",)
        }
        for quiz in concept.quizzes("nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_grammatical_number_with_grammatical_gender(self):
        """Test that use relations are generated for grammatical number nested with grammatical gender."""
        concept = concept_factory(
            "cat",
            dict(
                singular=dict(female=dict(en="Her cat", nl="Haar kat"), male=dict(en="His cat", nl="Zijn kat")),
                plural=dict(female=dict(en="Her cats", nl="Haar katten"), male=dict(en="His cats", nl="Zijn katten"))
            )
        )
        expected_uses = {
            self.create_quiz("cat", "nl", "en", "Haar kat", ["Her cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "Her cat", ["Haar kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar kat"], "listen"): (),
            self.create_quiz("cat", "nl", "en", "Zijn kat", ["His cat"], "translate"): (),
            self.create_quiz("cat", "en", "nl", "His cat", ["Zijn kat"], "translate"): (),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn kat"], "listen"): (),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Zijn kat"], "masculinize"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Haar kat"], "feminize"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "en", "Haar katten", ["Her cats"], "translate"): ("cat/singular/female",),
            self.create_quiz("cat", "en", "nl", "Her cats", ["Haar katten"], "translate"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar katten"], "listen"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "en", "Zijn katten", ["His cats"], "translate"): ("cat/singular/male",),
            self.create_quiz("cat", "en", "nl", "His cats", ["Zijn katten"], "translate"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn katten"], "listen"): ("cat/singular/male",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Zijn katten"], "masculinize"): ("cat/plural/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Haar katten"], "feminize"): ("cat/plural/female",),
            self.create_quiz("cat", "nl", "nl", "Haar kat", ["Haar katten"], "pluralize"): ("cat/plural/female",),
            self.create_quiz("cat", "nl", "nl", "Haar katten", ["Haar kat"], "singularize"): ("cat/singular/female",),
            self.create_quiz("cat", "nl", "nl", "Zijn kat", ["Zijn katten"], "pluralize"): ("cat/plural/male",),
            self.create_quiz("cat", "nl", "nl", "Zijn katten", ["Zijn kat"], "singularize"): ("cat/singular/male",)
        }
        for quiz in concept.quizzes("nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)

    def test_generated_uses_for_degrees_of_comparison(self):
        """Test that use relations are generated for degrees of comparison."""
        concept = concept_factory(
            "big",
            {
                "positive degree": dict(en="Big", nl="Groot"),
                "comparitive degree": dict(en="Bigger", nl="Groter"),
                "superlative degree": dict(en="Biggest", nl="Grootst")
            }
        )
        expected_uses = {
            self.create_quiz("big", "nl", "en", "Groot", ["Big"], "translate"): (),
            self.create_quiz("big", "en", "nl", "Big", ["Groot"], "translate"): (),
            self.create_quiz("big", "nl", "nl", "Groot", ["Groot"], "listen"): (),
            self.create_quiz("big", "nl", "en", "Groter", ["Bigger"], "translate"): (),
            self.create_quiz("big", "en", "nl", "Bigger", ["Groter"], "translate"): (),
            self.create_quiz("big", "nl", "nl", "Groter", ["Groter"], "listen"): (),
            self.create_quiz("big", "nl", "en", "Grootst", ["Biggest"], "translate"): (),
            self.create_quiz("big", "en", "nl", "Biggest", ["Grootst"], "translate"): (),
            self.create_quiz("big", "nl", "nl", "Grootst", ["Grootst"], "listen"): (),
            self.create_quiz(
                "big", "nl", "nl", "Groot", ["Groter"], "give comparitive degree"): ("big/comparitive degree",),
            self.create_quiz(
                "big", "nl", "nl", "Groot", ["Grootst"], "give superlative degree"): ("big/superlative degree",),
            self.create_quiz("big", "nl", "nl", "Groter", ["Groot"], "give positive degree"): ("big/positive degree",),
            self.create_quiz(
                "big", "nl", "nl", "Groter", ["Grootst"], "give superlative degree"): ("big/superlative degree",),
            self.create_quiz("big", "nl", "nl", "Grootst", ["Groot"], "give positive degree"): ("big/positive degree",),
            self.create_quiz(
                "big", "nl", "nl", "Grootst", ["Groter"], "give comparitive degree"): ("big/comparitive degree",)
        }
        for quiz in concept.quizzes("nl", "en"):
            self.assertEqual(expected_uses[quiz], quiz.uses)
