"""Grammar types."""

from typing import Literal


GrammaticalGender = Literal["female", "male", "neuter"]
GrammaticalNumber = Literal["infinitive", "singular", "plural"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparitive degree", "superlative degree"]
GrammaticalCategory = Literal[GrammaticalGender, GrammaticalNumber, GrammaticalPerson, DegreeOfComparison]
