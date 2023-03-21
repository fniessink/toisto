"""Grammar types."""

from typing import Literal

GrammaticalGender = Literal["female", "male", "neuter"]
GrammaticalNumber = Literal["infinitive", "singular", "plural"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparative degree", "superlative degree"]
Diminutive = Literal["root", "diminutive"]
Tense = Literal["present tense", "past tense"]
SentenceForm = Literal["declarative", "interrogative"]
GrammaticalPolarity = Literal["affirmative", "negative"]
GrammaticalCategory = Literal[
    GrammaticalGender,
    GrammaticalNumber,
    GrammaticalPerson,
    DegreeOfComparison,
    Diminutive,
    Tense,
    SentenceForm,
    GrammaticalPolarity,
]
