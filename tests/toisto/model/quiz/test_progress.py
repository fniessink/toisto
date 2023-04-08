"""Progress unit tests."""

from typing import get_args

from toisto.model.language import Language
from toisto.model.language.concept import ConceptId
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes, TranslationQuizType
from toisto.model.quiz.quiz_factory import QuizFactory

from ....base import ToistoTestCase


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = self.create_concept(ConceptId("english"))
        self.quiz = self.create_quiz(self.concept, "fi", "nl", "Englanti", ["Engels"])
        self.another_quiz = self.create_quiz(self.concept, "nl", "fi", "Engels", ["Englanti"])
        self.progress = Progress({}, Quizzes(), Language("fi"))

    def create_progress(self, quizzes: Quizzes) -> Progress:
        """Create progress for the quizzes."""
        return Progress({}, quizzes, Language("fi"), skip_concepts=2)

    def test_progress_new_quiz(self):
        """Test that a new quiz has no progress."""
        self.assertIsNone(self.progress.get_retention(self.quiz).start)
        self.assertIsNone(self.progress.get_retention(self.quiz).end)
        self.assertIsNone(self.progress.get_retention(self.quiz).skip_until)

    def test_update_progress_correct(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.increase_retention(self.quiz)
        self.assertIsNotNone(self.progress.get_retention(self.quiz).start)
        self.assertIsNotNone(self.progress.get_retention(self.quiz).end)

    def test_update_progress_incorrect(self):
        """Test that the progress of a quiz can be updated."""
        self.progress.reset_retention(self.quiz)
        self.assertIsNone(self.progress.get_retention(self.quiz).start)
        self.assertIsNone(self.progress.get_retention(self.quiz).end)
        self.assertIsNone(self.progress.get_retention(self.quiz).skip_until)

    def test_update_progress_when_case_changed(self):
        """Test that changing the case of labels does impact the progress."""
        self.progress.increase_retention(self.quiz)
        quiz_with_case_changed = self.copy_quiz(self.quiz, question=self.quiz.question.lower())
        self.assertNotEqual(self.progress.get_retention(self.quiz), self.progress.get_retention(quiz_with_case_changed))

    def test_next_quiz(self):
        """Test that the next quiz is not silenced."""
        progress = self.create_progress({self.quiz, self.another_quiz})
        progress.increase_retention(self.quiz)
        self.assertEqual(self.another_quiz, progress.next_quiz())

    def test_no_next_quiz(self):
        """Test that there are no next quizzes when they are all silenced."""
        progress = self.create_progress([self.quiz])
        progress.increase_retention(self.quiz)
        self.assertIsNone(progress.next_quiz())

    def test_next_quiz_is_different_from_previous(self):
        """Test that the next quiz is different from the previous one."""
        progress = self.create_progress({self.quiz, self.another_quiz})
        self.assertNotEqual(progress.next_quiz(), progress.next_quiz())

    def test_next_quiz_is_not_blocked(self):
        """Test that the next quiz is a translation quiz and not a listening quiz if both are eligible."""
        concept = self.create_concept("good", dict(en="good", nl="goed"))
        quizzes = QuizFactory("nl", "en").create_quizzes(concept)
        progress = self.create_progress(quizzes)
        self.assertTrue(progress.next_quiz().quiz_types[0] in get_args(TranslationQuizType))

    def test_roots_block_quizzes(self):
        """Test that quizzes are blocked if roots have eligible quizzes."""
        concept1 = self.create_concept("good day", dict(roots="good", en="good day", nl="goedendag"))
        concept2 = self.create_concept("good", dict(en="good", nl="goed"))
        quizzes = QuizFactory("nl", "en").create_quizzes(concept1, concept2)
        progress = self.create_progress(quizzes)
        self.assertEqual("good", progress.next_quiz().concept.concept_id)

    def test_roots_block_quizzes_even_if_roots_only_apply_to_target_language(self):
        """Test that quizzes are blocked, even if the roots only apply to the target language."""
        concept1 = self.create_concept("good day", dict(roots=dict(nl="good"), en="good day", nl="goedendag"))
        concept2 = self.create_concept("good", dict(en="good", nl="goed"))
        quizzes = QuizFactory("nl", "en").create_quizzes(concept1, concept2)
        progress = self.create_progress(quizzes)
        self.assertEqual("good", progress.next_quiz().concept.concept_id)

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
        quizzes = QuizFactory("fi", "nl").create_quizzes(morning, afternoon, evening)
        progress = self.create_progress(quizzes)
        for _ in range(9):
            quiz = progress.next_quiz()
            self.assertTrue("singular" in quiz.concept.concept_id)
            progress.increase_retention(quiz)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        concepts = [self.create_concept(f"id{index}", dict(fi=f"fi{index}", nl=f"nl{index}")) for index in range(5)]
        quizzes = [quiz for quiz in QuizFactory("fi", "nl").create_quizzes(*concepts) if quiz.quiz_types == ("listen",)]
        progress = self.create_progress(quizzes)
        progress.increase_retention(quizzes[0])
        progress.get_retention(quizzes[0]).skip_until = None
        self.assertEqual(progress.next_quiz(), quizzes[0])

    def test_next_quiz_has_lower_language_level(self):
        """Test that the next quiz has the lowest language level of the eligible quizzes."""
        morning = self.create_concept("morning", dict(level=dict(A1="EP"), fi="aamu", nl="de ochtend"))
        noon = self.create_concept("noon", dict(level=dict(A2="EP"), fi="keskipäivä", nl="de middag"))
        quizzes = QuizFactory("fi", "nl").create_quizzes(morning, noon)
        self.assertEqual("morning", self.create_progress(quizzes).next_quiz().concept.concept_id)

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
