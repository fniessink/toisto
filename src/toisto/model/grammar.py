"""Grammar types."""

from typing import Literal


GrammaticalGender = Literal["female", "male"]
GrammaticalNumber = Literal["singular", "plural"]
GrammaticalPerson = Literal["first_person", "second_person", "third_person"]
DegreeOfComparison = Literal["positive_degree", "comparitive_degree", "superlative_degree"]
GrammaticalCategory = Literal[GrammaticalGender, GrammaticalNumber, GrammaticalPerson, DegreeOfComparison]
