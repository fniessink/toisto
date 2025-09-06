"""Grammatical categories."""

from __future__ import annotations

from typing import Literal

GrammaticalGender = Literal["feminine", "masculine", "neuter"]
GrammaticalNumber = Literal["infinitive", "verbal noun", "singular", "plural"]
GrammaticalNumberPronoun = Literal["singular pronoun", "plural pronoun"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparative degree", "superlative degree"]
Diminutive = Literal["root", "diminutive"]
Tense = Literal["present tense", "past tense", "present perfect tense", "past perfect tense"]
GrammaticalMood = Literal["declarative", "interrogative", "imperative"]
GrammaticalPolarity = Literal["affirmative", "negative"]
Number = Literal["cardinal", "ordinal"]
Abbreviation = Literal["abbreviation", "full form"]
GrammaticalCategory = Literal[
    GrammaticalGender,
    GrammaticalNumber,
    GrammaticalNumberPronoun,
    GrammaticalPerson,
    DegreeOfComparison,
    Diminutive,
    Tense,
    GrammaticalMood,
    GrammaticalPolarity,
    Number,
    Abbreviation,
]
