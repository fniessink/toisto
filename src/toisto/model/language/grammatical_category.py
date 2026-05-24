"""Grammatical categories."""

from __future__ import annotations

from typing import Literal, cast

GrammaticalAspect = Literal["imperfective", "perfective"]
GrammaticalCase = Literal["nominative", "partitive"]
GrammaticalGender = Literal["feminine", "masculine", "neuter"]
GrammaticalNumber = Literal["infinitive", "verbal noun", "singular", "plural"]
GrammaticalNumberPronoun = Literal["singular pronoun", "plural pronoun"]
GrammaticalPerson = Literal["first person", "second person", "third person"]
DegreeOfComparison = Literal["positive degree", "comparative degree", "superlative degree"]
Diminutive = Literal["root", "diminutive"]
Tense = Literal["present tense", "past tense"]
GrammaticalMood = Literal["declarative", "interrogative", "imperative"]
GrammaticalPolarity = Literal["affirmative", "negative"]
Number = Literal["cardinal", "ordinal"]
Abbreviation = Literal["abbreviation", "full form"]
GrammaticalCategory = Literal[
    GrammaticalAspect,
    GrammaticalCase,
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

DEFAULT_CATEGORIES: frozenset[GrammaticalCategory] = cast(
    "frozenset[GrammaticalCategory]", frozenset({"root", "full form", "nominative"})
)

# Categories whose presence on one label but not the other signals that the two labels are NOT cross-language
# translations of each other. Unlike agreement features (e.g., gender, person), these categories encode a meaning
# distinction (e.g., partitive marks a partial-object reading) that the unmarked form in another language does not
# carry. The default value of such a category (e.g., nominative for case) belongs in DEFAULT_CATEGORIES instead.
SEMANTIC_NON_DEFAULT_CATEGORIES: frozenset[GrammaticalCategory] = cast(
    "frozenset[GrammaticalCategory]", frozenset({"partitive"})
)
