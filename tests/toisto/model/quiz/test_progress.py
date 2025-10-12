"""Progress unit tests."""

from typing import TYPE_CHECKING, cast

from toisto.model.language import EN, FI, NL
from toisto.model.language.concept import ConceptId
from toisto.model.quiz.evaluation import Evaluation
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import DICTATE, TranslationQuizType
from toisto.tools import first

from ....base import FI_NL, NL_EN, ToistoTestCase

if TYPE_CHECKING:
    from toisto.model.quiz.quiz import Quiz


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        concept = self.create_concept(
            "english", labels=[{"label": "englanti", "language": FI}, {"label": "Engels", "language": NL}]
        )
        self.quizzes = create_quizzes(FI_NL, (), concept)
        self.progress = Progress(FI, Quizzes(self.quizzes), {})

    def test_progress_new_quiz(self):
        """Test that a new quiz has no progress."""
        quiz = first(self.quizzes)
        retention = self.progress.get_retention(quiz)
        self.assertIsNone(retention.start)
        self.assertIsNone(retention.end)
        self.assertIsNone(retention.skip_until)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        quiz = first(self.quizzes)
        retention = self.progress.mark_evaluation(quiz, Evaluation.CORRECT)
        self.assertIsNotNone(retention.start)
        self.assertIsNotNone(retention.end)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        quiz = first(self.quizzes)
        retention = self.progress.mark_evaluation(quiz, Evaluation.INCORRECT)
        self.assertIsNone(retention.start)
        self.assertIsNone(retention.end)
        self.assertIsNone(retention.skip_until)

    def test_next_quiz(self):
        """Test that the next quiz is not silenced."""
        quiz = first(self.quizzes)
        self.progress.mark_evaluation(quiz, Evaluation.CORRECT)
        self.assertNotEqual(quiz, self.progress.next_quiz())

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        for quiz in self.quizzes:
            self.progress.mark_evaluation(quiz, Evaluation.CORRECT)
        self.assertIsNone(self.progress.next_quiz())

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        self.assertNotEqual(self.progress.next_quiz(), self.progress.next_quiz())

    def test_next_quiz_is_not_blocked(self):
        """Test that the next quiz is a translation quiz and not a listening quiz if both are eligible."""
        next_quiz = cast("Quiz", self.progress.next_quiz())
        self.assertTrue(next_quiz.has_quiz_type(TranslationQuizType))

    def test_roots_block_quizzes(self):
        """Test that quizzes are blocked if roots have eligible quizzes."""
        concept1 = self.create_concept(
            "good day",
            labels=[
                {"label": "good day", "language": EN, "roots": "good"},
                {"label": "goedendag", "language": NL, "roots": "goed"},
            ],
        )
        concept2 = self.create_concept(
            "good", labels=[{"label": "good", "language": EN}, {"label": "goed", "language": NL}]
        )
        quizzes = create_quizzes(NL_EN, (), concept1, concept2)
        progress = Progress(NL, quizzes, {})
        next_quiz = cast("Quiz", progress.next_quiz())
        self.assertEqual("good", next_quiz.concept.concept_id)

    def test_roots_block_quizzes_even_if_roots_only_apply_to_target_language(self):
        """Test that quizzes are blocked, even if the roots only apply to the target language."""
        concept1 = self.create_concept(
            "good day",
            labels=[{"label": "good day", "language": EN}, {"label": "goedendag", "language": NL, "roots": ["goed"]}],
        )
        concept2 = self.create_concept(
            "good", labels=[{"label": "good", "language": EN}, {"label": "goed", "language": NL}]
        )
        quizzes = create_quizzes(NL_EN, (), concept1, concept2)
        progress = Progress(NL, quizzes, {})
        next_quiz = cast("Quiz", progress.next_quiz())
        self.assertEqual("good", next_quiz.concept.concept_id)

    def test_quiz_order(self):
        """Test that the first quizzes test the singular concept."""
        morning = self.create_concept(
            "morning",
            labels=[
                {"label": {"singular": "aamu", "plural": "aamut"}, "language": FI},
                {"label": {"singular": "de ochtend", "plural": "de ochtenden"}, "language": NL},
            ],
        )
        afternoon = self.create_concept(
            "afternoon",
            labels=[
                {"label": {"singular": "iltapäivä", "plural": "iltapäivät"}, "language": FI, "roots": ["ilta"]},
                {"label": {"singular": "de middag", "plural": "de middagen"}, "language": NL},
            ],
        )
        evening = self.create_concept(
            "evening",
            labels=[
                {"label": {"singular": "ilta", "plural": "illat"}, "language": FI},
                {"label": {"singular": "de avond", "plural": "de avonden"}, "language": NL},
            ],
        )
        quizzes = create_quizzes(FI_NL, (), morning, afternoon, evening)
        progress = Progress(FI, quizzes, {}, skip_concepts=2)
        while quiz := progress.next_quiz():
            self.assertIn("singular", quiz.concept.labels(FI)[0].grammatical_form.grammatical_categories)
            progress.mark_evaluation(quiz, Evaluation.CORRECT)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has see before if possible."""
        concepts = [
            self.create_concept(
                f"id{index}", labels=[{"label": f"fi{index}", "language": FI}, {"label": f"nl{index}", "language": NL}]
            )
            for index in range(5)
        ]
        quizzes = create_quizzes(FI_NL, (DICTATE,), *concepts)
        progress = Progress(FI, quizzes, {})
        random_quiz = next(iter(quizzes))
        retention = progress.mark_evaluation(random_quiz, Evaluation.CORRECT)
        retention.skip_until = None
        self.assertEqual(progress.next_quiz(), random_quiz)

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())


class ProgressOfRelatedQuizzesTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        example = self.create_concept("example", labels=[{"label": "Puhun englantia", "language": FI}])
        example_quizzes = create_quizzes(FI_NL, (), example)
        concept = self.create_concept(
            "english",
            {"example": ConceptId("example")},
            labels=[{"label": "englanti", "language": FI}, {"label": "Engels", "language": NL}],
        )
        self.concept_quizzes = create_quizzes(FI_NL, (), concept)
        self.quizzes = Quizzes(example_quizzes | self.concept_quizzes)
        self.progress = Progress(FI, self.quizzes, {})

    def test_update_progress_correct(self):
        """Test that related quizzes are paused, including quizzes for examples."""
        self.progress.mark_evaluation(next(iter(self.concept_quizzes)), Evaluation.CORRECT)
        for quiz in self.quizzes:
            self.assertIsNotNone(self.progress.get_retention(quiz).skip_until, quiz)
