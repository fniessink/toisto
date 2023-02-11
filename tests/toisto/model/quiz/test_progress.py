"""Progress unit tests."""

from toisto.model.model_types import ConceptId
from toisto.model.quiz.progress import Progress
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.topic import Topic, Topics

from ....base import ToistoTestCase


class ProgressTest(ToistoTestCase):
    """Unit tests for the progress class."""

    def setUp(self) -> None:
        """Override to set up test fixtures."""
        self.concept = self.create_concept(ConceptId("english"))
        self.quiz = self.create_quiz(self.concept, "fi", "nl", "Englanti", ["Engels"])
        self.another_quiz = self.create_quiz(self.concept, "nl", "fi", "Engels", ["Englanti"])
        self.progress = Progress({}, Topics(set()))

    def create_topics(self, quizzes: Quizzes) -> Topics:
        """Create a test topics collection."""
        return Topics({Topic("topic", (), quizzes)})

    def create_progress(self, *topic_quizzes: Quizzes) -> Progress:
        """Create progress for the quizzes."""
        topics = Topics({Topic(f"topic{index}", (), quizzes) for index, quizzes in enumerate(topic_quizzes)})
        return Progress({}, topics)

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
        listen = self.create_quiz(self.concept, "fi", "fi", "Englanti", ["Englanti"], "listen", blocked_by=(self.quiz,))
        progress = self.create_progress({listen, self.quiz})
        self.assertEqual(self.quiz, progress.next_quiz())

    def test_roots_block_quizzes(self):
        """Test that quizzes are blocked if roots have eligible quizzes."""
        concept1 = self.create_concept("good day", dict(roots="good"))
        quiz1 = self.create_quiz(concept1, "nl", "en", "Goedendag", ["Good day"])
        concept2 = self.create_concept("good")
        quiz2 = self.create_quiz(concept2, "nl", "en", "Goed", ["Good"])
        progress = self.create_progress([quiz1, quiz2])
        self.assertEqual(quiz2, progress.next_quiz())

    def test_roots_block_quizzes_even_across_topics(self):
        """Test that quizzes are blocked if roots have eligible quizzes, even when they belong to different topics."""
        concept1 = self.create_concept("good day", dict(roots="good"))
        quiz1 = self.create_quiz(concept1, "nl", "en", "Goedendag", ["Good day"])
        concept2 = self.create_concept("good")
        quiz2 = self.create_quiz(concept2, "nl", "en", "Goed", ["Good"])
        progress = self.create_progress([quiz1], [quiz2])
        self.assertEqual(quiz2, progress.next_quiz())

    def test_quiz_order(self):
        """Test that the first quizzes test the singular concept."""
        morning = self.create_concept(
            "morning",
            dict(singular=dict(fi="Aamu", nl="De ochtend"), plural=dict(fi="Aamut", nl="De ochtenden")),
        )
        afternoon = self.create_concept(
            "afternoon",
            dict(
                roots="morning",
                singular=dict(fi="Iltapäivä", nl="De middag"),
                plural=dict(fi="Iltapäivät", nl="De middagen"),
            ),
        )
        evening = self.create_concept(
            "evening",
            dict(roots="afternoon", singular=dict(fi="Ilta", nl="De avond"), plural=dict(fi="Illat", nl="De avonden")),
        )
        quizzes = (
            self.create_quizzes(morning, "fi", "nl")
            | self.create_quizzes(afternoon, "fi", "nl")
            | self.create_quizzes(evening, "fi", "nl")
        )
        progress = self.create_progress(quizzes)
        for _ in range(9):
            quiz = progress.next_quiz()
            self.assertTrue("singular" in quiz.concept.concept_id)
            progress.increase_retention(quiz)

    def test_next_quiz_is_quiz_with_progress(self):
        """Test that the next quiz is one the user has seen before if possible."""
        concepts = [self.create_concept(f"id{index}") for index in range(5)]
        quizzes = [
            self.create_quiz(concept, "nl", "fi", f"Dutch label {index}", [f"Finnish label {index}"])
            for index, concept in enumerate(concepts)
        ]
        progress = self.create_progress(quizzes)
        for index in range(3):
            progress.increase_retention(quizzes[index])
            progress.get_retention(quizzes[index]).skip_until = None
        self.assertIn(progress.next_quiz(), quizzes[:3])

    def test_next_quiz_has_lower_language_level(self):
        """Test that the next quiz has the lowest language level of the eligible quizzes."""
        morning = self.create_concept("morning", dict(level=dict(A1="EP"), fi="Aamu", nl="De ochtend"))
        noon = self.create_concept("noon", dict(level=dict(A2="EP"), fi="Keskipäivä", nl="De middag"))
        quizzes = self.create_quizzes(morning, "fi", "nl") | self.create_quizzes(noon, "fi", "nl")
        self.assertEqual("morning", self.create_progress(quizzes).next_quiz().concept.concept_id)

    def test_as_dict(self):
        """Test that the progress can be retrieved as dict."""
        self.assertEqual({}, self.progress.as_dict())
