"""Quiz factory unit tests."""

from toisto.model.language import EN, FI
from toisto.model.language.concept import Concept, ConceptId
from toisto.model.language.concept_factory import ConceptJSON
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import CLOZE_TEST

from .....base import EN_FI, FI_NL, ToistoTestCase


class QuizClozeTestTest(ToistoTestCase):
    """Unit tests for cloze tests."""

    def create_concept_with_cloze(self) -> Concept:
        """Create a concept."""
        return self.create_concept(
            "to speak",
            labels=[
                {"label": "he speaks", "language": EN, "cloze": "he (speak)"},
                {"label": "hän puhuu", "language": FI},
            ],
        )

    def test_cloze_test(self):
        """Test that cloze test quizzes are created."""
        concept = self.create_concept_with_cloze()
        (he_speaks,) = concept.labels(EN)
        self.assertSetEqual(
            {self.create_quiz(EN_FI, concept, he_speaks.cloze_tests[0], [he_speaks], CLOZE_TEST)},
            create_quizzes(EN_FI, (CLOZE_TEST,), concept),
        )

    def test_meaning(self):
        """Test that cloze test quizzes have meaning."""
        concept = self.create_concept_with_cloze()
        for quiz in create_quizzes(EN_FI, (CLOZE_TEST,), concept):
            self.assertEqual(("hän puhuu",), quiz.question_meanings.as_strings)

    def test_one_language(self):
        """Test that cloze test quizzes are generated when the label has one language."""
        concept = self.create_concept(
            "I like ice cream",
            labels=[{"label": "Minä pidän jäätelöstä.", "language": FI, "cloze": "Minä pidän (jäätelö)."}],
        )
        for quiz in create_quizzes(FI_NL, (CLOZE_TEST,), concept):
            self.assertEqual("cloze", quiz.action)
            self.assertEqual("Minä pidän (jäätelö).", str(quiz.question))

    def test_one_language_multiple_answers(self):
        """Test that cloze tests have no other answers."""
        concept = self.create_concept(
            "I like ice cream",
            labels=[
                {"label": "Minä pidän jäätelöstä.", "language": FI, "cloze": "Minä pidän (jäätelö)."},
                {"label": "Minä tykkään jäätelöstä.", "language": FI},
            ],
        )
        for quiz in create_quizzes(FI_NL, (CLOZE_TEST,), concept):
            self.assertEqual((), quiz.other_answers("Minä pidän jäätelöstä."))

    def test_one_grammatical_form_with_one_without(self):
        """Test one grammatical form with cloze test, the other without."""
        concept = self.create_concept(
            "I like ice cream",
            labels=[
                {
                    "cloze": {"singular": "Minä pidän (jäätelö)."},
                    "label": {"singular": "Minä pidän jäätelöstä.", "plural": "Me pidämme jäätelöstä."},
                    "language": FI,
                },
            ],
        )
        (minä, _me) = concept.labels(FI)
        self.assertSetEqual(
            {self.create_quiz(FI_NL, concept, minä.cloze_tests[0], [minä], CLOZE_TEST)},
            create_quizzes(FI_NL, (CLOZE_TEST,), concept),
        )

    def test_multiple_close_tests_for_one_label(self):
        """Test multiple cloze tests for one label."""
        concept = self.create_concept(
            "I like ice cream",
            labels=[
                {
                    "cloze": ["Minä pidän (jäätelö).", "Minä (pitää) jäätelöstä."],
                    "label": "Minä pidän jäätelöstä.",
                    "language": FI,
                },
            ],
        )
        (minä,) = concept.labels(FI)
        self.assertSetEqual(
            {self.create_quiz(FI_NL, concept, cloze, [minä], CLOZE_TEST) for cloze in minä.cloze_tests},
            create_quizzes(FI_NL, (CLOZE_TEST,), concept),
        )

    def test_instruction_does_not_contain_tip_when_quizzed_multiple_times(self):
        """Test the quiz instruction does not contain a tip when the quiz is given multiple times."""
        self.create_concept("store", labels=[{"concept": "store", "label": "kauppa", "language": FI}])
        concept = self.create_concept(
            "works in a store",
            ConceptJSON({"involves": ConceptId("store")}),
            labels=[{"label": "Alice on töissä kauppassa.", "cloze": "Alice on töissä (kauppa).", "language": FI}],
        )
        (label,) = concept.labels(FI)
        for _ in range(2):
            quiz = self.create_quiz(FI_NL, concept, label.cloze_tests[0], [label], CLOZE_TEST)
            self.assertEqual(
                "Repeat with the [underline]bracketed words in the correct form[/underline], in Finnish",
                quiz.instruction,
            )
