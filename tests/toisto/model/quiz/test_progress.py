"""Progress unit tests."""

from typing import cast, get_args

from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quiz, Quizzes, TranslationQuizType
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.tools import first

from ....base import ToistoTestCase


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        concept = self.create_concept("english", dict(fi="englanti", nl="Engels"))
        self.quizzes = create_quizzes(self.fi, self.nl, concept)
        self.progress = Progress({}, self.fi, Quizzes(self.quizzes))

    def test_progress_new_quiz(self):
        """Test that a new quiz has no progress."""
        quiz = self.quizzes.pop()
        self.assertIsNone(self.progress.get_retention(quiz).start)
        self.assertIsNone(self.progress.get_retention(quiz).end)
        self.assertIsNone(self.progress.get_retention(quiz).skip_until)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        quiz = self.quizzes.pop()
        self.progress.mark_correct_answer(quiz)
        self.assertIsNotNone(self.progress.get_retention(quiz).start)
        self.assertIsNotNone(self.progress.get_retention(quiz).end)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        quiz = self.quizzes.pop()
        self.progress.mark_incorrect_answer(quiz)
        self.assertIsNone(self.progress.get_retention(quiz).start)
        self.assertIsNone(self.progress.get_retention(quiz).end)
        self.assertIsNone(self.progress.get_retention(quiz).skip_until)

    def test_next_quiz(self):
        """Test that the next quiz is not silenced."""
        quiz = first(self.quizzes)
        self.progress.mark_correct_answer(quiz)
        self.assertNotEqual(quiz, self.progress.next_quiz())

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        for quiz in self.quizzes:
            self.progress.mark_correct_answer(quiz)
        self.assertIsNone(self.progress.next_quiz())

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        self.assertNotEqual(self.progress.next_quiz(), self.progress.next_quiz())

    def test_next_quiz_is_not_blocked(self):
        """Test that the next quiz is a translation quiz and not a listening quiz if both are eligible."""
        next_quiz = cast(Quiz, self.progress.next_quiz())
        self.assertIn(next_quiz.quiz_types[0], get_args(TranslationQuizType))

    def test_roots_block_quizzes(self):
        """Test that quizzes are blocked if roots have eligible quizzes."""
        concept1 = self.create_concept("good day", dict(roots="good", en="good day", nl="goedendag"))
        concept2 = self.create_concept("good", dict(en="good", nl="goed"))
        quizzes = create_quizzes(self.nl, self.en, concept1, concept2)
        progress = Progress({}, self.nl, quizzes)
        next_quiz = cast(Quiz, progress.next_quiz())
        self.assertEqual("good", next_quiz.concept.concept_id)

    def test_roots_block_quizzes_even_if_roots_only_apply_to_target_language(self):
        """Test that quizzes are blocked, even if the roots only apply to the target language."""
        concept1 = self.create_concept("good day", dict(roots=dict(nl="good"), en="good day", nl="goedendag"))
        concept2 = self.create_concept("good", dict(en="good", nl="goed"))
        quizzes = create_quizzes(self.nl, self.en, concept1, concept2)
        progress = Progress({}, self.nl, quizzes)
        next_quiz = cast(Quiz, progress.next_quiz())
        self.assertEqual("good", next_quiz.concept.concept_id)

    def test_quiz_order(self):
        """Test that the first quizzes test the singular concept."""
        morning = self.create_concept(
            "morning",
            dict(singular=dict(fi="Aamu", nl="de ochtend"), plural=dict(fi="aamut", nl="de ochtenden")),
        )
        afternoon = self.create_concept(
            "afternoon",
            dict(
                roots="morning",
                singular=dict(fi="iltapäivä", nl="de middag"),
                plural=dict(fi="iltapäivät", nl="de middagen"),
            ),
        )
        evening = self.create_concept(
            "evening",
            dict(roots="afternoon", singular=dict(fi="ilta", nl="de avond"), plural=dict(fi="illat", nl="de avonden")),
        )
        quizzes = create_quizzes(self.fi, self.nl, morning, afternoon, evening)
        progress = Progress({}, self.fi, quizzes, skip_concepts=2)
        while quiz := progress.next_quiz():
            self.assertIn("singular", quiz.concept.concept_id)
            progress.mark_correct_answer(quiz)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        concepts = [self.create_concept(f"id{index}", dict(fi=f"fi{index}", nl=f"nl{index}")) for index in range(5)]
        quizzes = Quizzes(
            quiz for quiz in create_quizzes(self.fi, self.nl, *concepts) if quiz.quiz_types == ("dictate",)
        )
        progress = Progress({}, self.fi, quizzes)
        random_quiz = next(iter(quizzes))
        progress.mark_correct_answer(random_quiz)
        progress.get_retention(random_quiz).skip_until = None
        self.assertEqual(progress.next_quiz(), random_quiz)

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())


class ProgressOfRelatedQuizzesTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        super().setUp()
        example = self.create_concept("example", dict(fi="Puhun englantia"))
        example_quizzes = create_quizzes(self.fi, self.nl, example)
        concept = self.create_concept("english", dict(example="example", fi="englanti", nl="Engels"))
        self.concept_quizzes = create_quizzes(self.fi, self.nl, concept)
        self.quizzes = Quizzes(example_quizzes | self.concept_quizzes)
        self.progress = Progress({}, self.fi, self.quizzes)

    def test_update_progress_correct(self):
        """Test that related quizzes are paused, including quizzes for examples."""
        self.progress.mark_correct_answer(next(iter(self.concept_quizzes)))
        for quiz in self.quizzes:
            self.assertIsNotNone(self.progress.get_retention(quiz).skip_until, quiz)
