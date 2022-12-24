"""Grammar types."""

from typing import Literal


GrammaticalGender = Literal["female", "male", "neuter"]
GrammaticalNumber = Literal["infinitive", "singular", "plural"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparitive degree", "superlative degree"]
Tense = Literal["present tense", "past tense"]
GrammaticalCategory = Literal[GrammaticalGender, GrammaticalNumber, GrammaticalPerson, DegreeOfComparison, Tense]

# A plural concept automatically uses the singular form and past tense automatically uses the present tense
AUTO_USES = {"plural": "singular", "past tense": "present tense"}
