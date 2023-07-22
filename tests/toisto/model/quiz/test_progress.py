"""Progress unit tests."""

from typing import cast, get_args

from toisto.model.language import Language
from toisto.model.language.concept import ConceptId
from toisto.model.language.concept_factory import ConceptDict, create_concept
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes, TranslationQuizType
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.tools import first

from ....base import ToistoTestCase


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        concept = create_concept(ConceptId("english"), cast(ConceptDict, dict(fi="englanti", nl="Engels")))
        self.quizzes = create_quizzes(Language("fi"), Language("nl"), concept)
        self.progress = Progress({}, Language("fi"))

    def test_progress_new_quiz(self):
        """Test that a new quiz has no progress."""
        quiz = self.quizzes.pop()
        self.assertIsNone(self.progress.get_retention(quiz).start)
        self.assertIsNone(self.progress.get_retention(quiz).end)
        self.assertIsNone(self.progress.get_retention(quiz).skip_until)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        quiz = self.quizzes.pop()
        self.progress.increase_retention(quiz)
        self.assertIsNotNone(self.progress.get_retention(quiz).start)
        self.assertIsNotNone(self.progress.get_retention(quiz).end)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        quiz = self.quizzes.pop()
        self.progress.reset_retention(quiz)
        self.assertIsNone(self.progress.get_retention(quiz).start)
        self.assertIsNone(self.progress.get_retention(quiz).end)
        self.assertIsNone(self.progress.get_retention(quiz).skip_until)

    def test_next_quiz(self):
        """Test that the next quiz is not silenced."""
        quiz = first(self.quizzes)
        self.progress.increase_retention(quiz)
        self.assertNotEqual(quiz, self.progress.next_quiz(self.quizzes))

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        for quiz in self.quizzes:
            self.progress.increase_retention(quiz)
        self.assertIsNone(self.progress.next_quiz(self.quizzes))

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        self.assertNotEqual(self.progress.next_quiz(self.quizzes), self.progress.next_quiz(self.quizzes))

    def test_next_quiz_is_not_blocked(self):
        """Test that the next quiz is a translation quiz and not a listening quiz if both are eligible."""
        self.assertTrue(self.progress.next_quiz(self.quizzes).quiz_types[0] in get_args(TranslationQuizType))

    def test_roots_block_quizzes(self):
        """Test that quizzes are blocked if roots have eligible quizzes."""
        concept1 = create_concept("good day", dict(roots="good", en="good day", nl="goedendag"))
        concept2 = create_concept("good", dict(en="good", nl="goed"))
        quizzes = create_quizzes("nl", "en", concept1, concept2)
        self.assertEqual("good", self.progress.next_quiz(quizzes).concept.concept_id)

    def test_roots_block_quizzes_even_if_roots_only_apply_to_target_language(self):
        """Test that quizzes are blocked, even if the roots only apply to the target language."""
        concept1 = create_concept("good day", dict(roots=dict(nl="good"), en="good day", nl="goedendag"))
        concept2 = create_concept("good", dict(en="good", nl="goed"))
        quizzes = create_quizzes("nl", "en", concept1, concept2)
        self.assertEqual("good", self.progress.next_quiz(quizzes).concept.concept_id)

    def test_quiz_order(self):
        """Test that the first quizzes test the singular concept."""
        morning = create_concept(
            "morning",
            dict(singular=dict(fi="Aamu", nl="de ochtend"), plural=dict(fi="aamut", nl="de ochtenden")),
        )
        afternoon = create_concept(
            "afternoon",
            dict(
                roots="morning",
                singular=dict(fi="iltapäivä", nl="de middag"),
                plural=dict(fi="iltapäivät", nl="de middagen"),
            ),
        )
        evening = create_concept(
            "evening",
            dict(roots="afternoon", singular=dict(fi="ilta", nl="de avond"), plural=dict(fi="illat", nl="de avonden")),
        )
        quizzes = create_quizzes("fi", "nl", morning, afternoon, evening)
        progress = Progress({}, Language("fi"), skip_concepts=2)
        for _ in range(9):
            quiz = progress.next_quiz(quizzes)
            self.assertTrue("singular" in quiz.concept.concept_id)
            progress.increase_retention(quiz)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        concepts = [create_concept(f"id{index}", dict(fi=f"fi{index}", nl=f"nl{index}")) for index in range(5)]
        quizzes = Quizzes(quiz for quiz in create_quizzes("fi", "nl", *concepts) if quiz.quiz_types == ("listen",))
        random_quiz = next(iter(quizzes))
        self.progress.increase_retention(random_quiz)
        self.progress.get_retention(random_quiz).skip_until = None
        self.assertEqual(self.progress.next_quiz(quizzes), random_quiz)

    def test_next_quiz_has_lower_language_level(self):
        """Test that the next quiz has the lowest language level of the eligible quizzes."""
        morning = create_concept("morning", dict(level=dict(A1="EP"), fi="aamu", nl="de ochtend"))
        noon = create_concept("noon", dict(level=dict(A2="EP"), fi="keskipäivä", nl="de middag"))
        quizzes = create_quizzes("fi", "nl", morning, noon)
        self.assertEqual("morning", self.progress.next_quiz(quizzes).concept.concept_id)

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
