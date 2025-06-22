"""Concept relations unit tests."""

from toisto.model.language import EN, FI, NL
from toisto.model.language.label import Label
from toisto.model.quiz.quiz import Quizzes
from toisto.model.quiz.quiz_factory import create_quizzes
from toisto.model.quiz.quiz_type import ANSWER, ANTONYM
from toisto.tools import first

from ....base import EN_NL, FI_NL
from .test_quiz_factory import QuizFactoryTestCase


class ConceptRootsTest(QuizFactoryTestCase):
    """Unit tests for roots."""

    def test_concept_relationship_leaf_concept(self):
        """Test that leaf concepts can declare to have roots."""
        mall = self.create_concept(
            "mall",
            {"roots": ["shop", "centre"]},
            labels=[{"label": "kauppakeskus", "language": FI}, {"label": "het winkelcentrum", "language": NL}],
        )
        shop = self.create_concept("shop", labels=[{"label": "kauppa", "language": FI}])
        centre = self.create_concept("centre", labels=[{"label": "keskusta", "language": FI}])
        self.assertEqual((shop, centre), create_quizzes(FI_NL, (), mall).pop().concept.roots(FI))

    def test_concept_relationship_composite_concept(self):
        """Test that composite concepts can declare to have roots."""
        mall = self.create_concept(
            "mall",
            {"roots": ["shop", "centre"]},
            labels=[
                {"label": {"singular": "kauppakeskus", "plural": "kauppakeskukset"}, "language": FI},
                {"label": {"singular": "het winkelcentrum", "plural": "de winkelcentra"}, "language": NL},
            ],
        )
        shop = self.create_concept("shop", labels=[{"label": "kauppa", "language": FI}])
        centre = self.create_concept("centre", labels=[{"label": "keskusta", "language": FI}])
        for quiz in create_quizzes(FI_NL, (), mall):
            self.assertIn(shop, quiz.concept.roots(FI))
            self.assertIn(centre, quiz.concept.roots(FI))

    def test_concept_relationship_leaf_concept_one_root(self):
        """Test that leaf concepts can declare to have one root."""
        capital = self.create_concept(
            "capital",
            {"roots": "city"},
            labels=[{"label": "pääkaupunki", "language": FI}, {"label": "capital", "language": EN}],
        )
        city = self.create_concept("city", labels=[{"label": "kaupunki", "language": FI}])
        self.assertEqual((city,), create_quizzes(FI_NL, (), capital).pop().concept.roots(FI))

    def test_generated_concept_ids_for_constituent_concepts(self):
        """Test that constituent concepts get a generated concept id."""
        concept = self.create_noun_with_grammatical_number()
        expected_concept_ids: dict[tuple[str, str], str] = {
            ("aamu", "de ochtend"): "morning/singular",
            ("aamu", "aamu"): "morning/singular",
            ("de ochtend", "aamu"): "morning/singular",
            ("aamut", "de ochtenden"): "morning/plural",
            ("aamut", "aamut"): "morning/plural",
            ("de ochtenden", "aamut"): "morning/plural",
            ("aamu", "aamut"): "morning",
            ("aamut", "aamu"): "morning",
        }
        for quiz in create_quizzes(FI_NL, (), concept):
            self.assertEqual(expected_concept_ids[(str(quiz.question), str(quiz.answers[0]))], quiz.concept.concept_id)


class AntonymConceptsTest(QuizFactoryTestCase):
    """Unit tests for antonym concepts."""

    def setUp(self) -> None:
        """Extend to set up text fixtures."""
        super().setUp()
        self.big = self.create_concept("big", {"antonym": "small"}, labels=[{"label": "big", "language": EN}])
        self.small = self.create_concept("small", {"antonym": "big"}, labels=[{"label": "small", "language": EN}])
        self.quizzes = create_quizzes(EN_NL, (), self.big, self.small)

    def test_antonym_leaf_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        for concept, answer in [(self.big, "small"), (self.small, "big")]:
            antonym = self.create_quiz(concept, concept.labels(EN)[0], [Label(EN, answer)], ANTONYM)
            self.assertIn(antonym, self.quizzes)

    def test_antonym_quiz_order(self):
        """Test that before quizzing for an antonym, the anytonym itself has been quizzed."""
        antonym_quizzes = Quizzes(quiz for quiz in self.quizzes if quiz.has_quiz_type(ANTONYM))
        other_quizzes = self.quizzes - antonym_quizzes
        for antonym_quiz in antonym_quizzes:
            for other_quiz in other_quizzes:
                message = f"{antonym_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(antonym_quiz.is_blocked_by(Quizzes({other_quiz})), message)


class AnswerConceptsTest(QuizFactoryTestCase):
    """Unit tests for answer concepts."""

    def test_answer_leaf_concepts(self):
        """Test that quizzes are generated for concepts with answer concepts."""
        question = self.create_concept(
            "question", {"answer": "answer"}, labels=[{"label": "How are you?", "language": EN}]
        )
        answer = self.create_concept("answer", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        quizzes = create_quizzes(EN_NL, (), question, answer)
        (answer_label,) = answer.labels(EN)
        answer_quiz = self.create_quiz(question, question.labels(EN)[0], [answer_label], ANSWER)
        self.assertIn(answer_quiz, quizzes)

    def test_answer_composite_concepts(self):
        """Test that quizzes are generated for composite concepts with answer concepts."""
        question = self.create_concept(
            "question",
            {"answer": "answer"},
            labels=[{"label": {"singular": "How are you?", "plural": "How are you all?"}, "language": EN}],
        )
        answer = self.create_concept(
            "answer",
            labels=[
                {"label": {"singular": "I'm fine, thank you.", "plural": "We're fine, thank you."}, "language": EN}
            ],
        )
        quizzes = create_quizzes(EN_NL, (), question, answer)
        how_are_you, how_are_you_all = question.labels(EN)
        i_am_fine, we_are_fine = answer.labels(EN)
        singular_answer_quiz = self.create_quiz(question, how_are_you, [i_am_fine], ANSWER)
        plural_answer_quiz = self.create_quiz(question, how_are_you_all, [we_are_fine], ANSWER)
        self.assertIn(singular_answer_quiz, quizzes)
        self.assertIn(plural_answer_quiz, quizzes)

    def test_multiple_answers(self):
        """Test that quizzes can have multiple answers."""
        question = self.create_concept(
            "question", {"answer": ["fine", "good"]}, labels=[{"label": "How are you?", "language": EN}]
        )
        fine = self.create_concept("fine", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        good = self.create_concept("good", labels=[{"label": "I'm doing good, thank you.", "language": EN}])
        quiz = first(create_quizzes(EN_NL, (ANSWER,), question, fine, good))
        self.assertEqual((fine.labels(EN)[0], good.labels(EN)[0]), quiz.answers)

    def test_answer_quiz_order(self):
        """Test that before quizzing for an answer to a question, the answer itself has been quizzed."""
        question = self.create_concept(
            "question", {"answer": "answer"}, labels=[{"label": "How are you?", "language": EN}]
        )
        answer = self.create_concept("answer", labels=[{"label": "I'm fine, thank you.", "language": EN}])
        quizzes = create_quizzes(EN_NL, (), question, answer)
        answer_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(ANSWER))
        other_quizzes = quizzes - answer_quizzes
        for answer_quiz in answer_quizzes:
            for other_quiz in other_quizzes:
                message = f"{answer_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(answer_quiz.is_blocked_by(Quizzes({other_quiz})), message)
