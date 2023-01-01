"""Grammar types."""

from typing import Literal


GrammaticalGender = Literal["female", "male", "neuter"]
GrammaticalNumber = Literal["infinitive", "singular", "plural"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparitive degree", "superlative degree"]
Tense = Literal["present tense", "past tense"]
SentenceForm = Literal["declarative", "interrogative"]
GrammaticalPolarity = Literal["affirmative", "negative"]
GrammaticalCategory = Literal[
    GrammaticalGender,
    GrammaticalNumber,
    GrammaticalPerson,
    DegreeOfComparison,
    Tense,
    SentenceForm,
    GrammaticalPolarity,
]

# Mapping of grammatical categories to grammatical categories they automatically use. For example, a plural concept
# automatically uses the singular form. This forces Toisto to present quizzes of the used category before presenting
# quizzes for the using category.
AUTO_USES = {
    "plural": "singular",
    "past tense": "present tense",
    "negative": "affirmative",
    "interrogative": "declarative",
}
