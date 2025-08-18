"""Quiz factory unit tests."""

from toisto.model.language import FI, NL
from toisto.model.quiz.quiz_factory import create_quizzes

from .....base import FI_NL, ToistoTestCase


class QuizNoteTest(ToistoTestCase):
    """Unit tests for the quiz notes."""

    def test_note(self):
        """Test that the quizzes use the notes of the target language."""
        concept = self.create_concept(
            "finnish",
            labels=[
                {"label": "suomi", "language": FI, "note": "In Finnish, the names of languages are not capitalized"},
                {"label": "Fins", "language": NL, "note": "In Dutch, the names of languages are capitalized"},
            ],
        )
        for quiz in create_quizzes(FI_NL, (), concept):
            self.assertEqual("In Finnish, the names of languages are not capitalized", quiz.notes[0])
