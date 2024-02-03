"""Concept relations unit tests."""

from toisto.model.language import EN, FI
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
        mall = self.create_concept("mall", dict(roots=["shop", "centre"], fi="kauppakeskus", nl="het winkelcentrum"))
        shop = self.create_concept("shop", dict(fi="kauppa"))
        centre = self.create_concept("centre", dict(fi="keskusta"))
        self.assertEqual((shop, centre), create_quizzes(FI_NL, (), mall).pop().concept.roots(FI))

    def test_concept_relationship_composite_concept(self):
        """Test that composite concepts can declare to have roots."""
        mall = self.create_concept(
            "mall",
            dict(
                roots=["shop", "centre"],
                fi=dict(singular="kauppakeskus", plural="kauppakeskukset"),
                nl=dict(singular="het winkelcentrum", plural="de winkelcentra"),
            ),
        )
        shop = self.create_concept("shop", dict(fi="kauppa"))
        centre = self.create_concept("centre", dict(fi="keskusta"))
        for quiz in create_quizzes(FI_NL, (), mall):
            self.assertIn(shop, quiz.concept.roots(FI))
            self.assertIn(centre, quiz.concept.roots(FI))

    def test_concept_relationship_leaf_concept_one_root(self):
        """Test that leaf concepts can declare to have one root."""
        capital = self.create_concept("capital", dict(roots="city", fi="pääkaupunki", en="capital"))
        city = self.create_concept("city", dict(fi="kaupunki"))
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
        self.language_pair = EN_NL
        self.big = self.create_concept("big", dict(antonym="small", en="big"))
        self.small = self.create_concept("small", dict(antonym="big", en="small"))
        self.quizzes = create_quizzes(self.language_pair, (), self.big, self.small)

    def test_antonym_leaf_concepts(self):
        """Test that quizzes are generated for concepts with antonym concepts."""
        for concept, question, answer in [(self.big, "big", "small"), (self.small, "small", "big")]:
            antonym = self.create_quiz(concept, question, [answer], ANTONYM)
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
        self.language_pair = EN_NL
        question = self.create_concept("question", dict(answer="answer", en="How are you?"))
        answer = self.create_concept("answer", dict(en="I'm fine, thank you."))
        quizzes = create_quizzes(EN_NL, (), question, answer)
        answer_quiz = self.create_quiz(question, "How are you?", ["I'm fine, thank you."], ANSWER)
        self.assertIn(answer_quiz, quizzes)

    def test_answer_composite_concepts(self):
        """Test that quizzes are generated for composite concepts with answer concepts."""
        self.language_pair = EN_NL
        question = self.create_concept(
            "question",
            dict(answer="answer", en=dict(singular="How are you?;singular", plural="How are you?;plural")),
        )
        answer = self.create_concept(
            "answer",
            dict(en=dict(singular="I'm fine, thank you.", plural="We're fine, thank you.")),
        )
        quizzes = create_quizzes(EN_NL, (), question, answer)
        singular_answer_quiz = self.create_quiz(question, "How are you?;singular", ["I'm fine, thank you."], ANSWER)
        plural_answer_quiz = self.create_quiz(question, "How are you?;plural", ["We're fine, thank you."], ANSWER)
        self.assertIn(singular_answer_quiz, quizzes)
        self.assertIn(plural_answer_quiz, quizzes)

    def test_multiple_answers(self):
        """Test that quizzes can have multiple answers."""
        question = self.create_concept("question", dict(answer=["fine", "good"], en="How are you?"))
        fine = self.create_concept("fine", dict(en="I'm fine, thank you."))
        good = self.create_concept("good", dict(en="I'm doing good, thank you."))
        quiz = first(create_quizzes(EN_NL, (ANSWER,), question, fine, good))
        self.assertEqual((fine.labels(EN)[0], good.labels(EN)[0]), quiz.answers)

    def test_answer_quiz_order(self):
        """Test that before quizzing for an answer to a question, the answer itself has been quizzed."""
        question = self.create_concept("question", dict(answer="answer", en="How are you?"))
        answer = self.create_concept("answer", dict(en="I'm fine, thank you."))
        quizzes = create_quizzes(EN_NL, (), question, answer)
        answer_quizzes = Quizzes(quiz for quiz in quizzes if quiz.has_quiz_type(ANSWER))
        other_quizzes = quizzes - answer_quizzes
        for answer_quiz in answer_quizzes:
            for other_quiz in other_quizzes:
                message = f"{answer_quiz.key} should be blocked by {other_quiz.key}, but isn't"
                self.assertTrue(answer_quiz.is_blocked_by(Quizzes({other_quiz})), message)
