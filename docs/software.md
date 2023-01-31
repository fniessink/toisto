# Software documentation

## Topics

Builtin topics are located in `src/topics` in the form of JSON files. Users can also create their own topic files as long as it complies with the description below and pass them to Toisto using the `-t/--topic-file` command-line option.

## Concepts and labels

Each topic is a collection of *concepts*. Each concept has *labels* in different languages. A concept can be anything that can be expressed in language. The labels are words, phrases, or sentences that express the concept in a specific language.

The contents of a JSON topic file looks as follows:

```json
{
    "today": {
        "en": "Today",
        "fi": "Tänään",
        "nl": "Vandaag"
    },
    "yesterday": {
        "en": "Yesterday",
        "fi": "Eilen",
        "nl": "Gisteren"
    },
    "tomorrow": {
        "en": "Tomorrow",
        "fi": "Huomenna",
        "nl": "Morgen"
    }
}
```

Concepts are represented in the topic files as JSON-objects. The key is an identifier for the concept. It should be unique across all topic files. The value is a mapping with language identifiers as keys and labels as values. Currently supported language identifiers are `en` for English, `fi` for Finnish, and `nl` for Dutch.

When using more than two languages is not essential to explain how things work, examples below may contain just two languages.

### Spelling variants

When there are multiple ways to spell a label, use the pipe symbol to separate the alternatives. Toisto will only use the first of the alternatives to quiz the user, but will accept the other alternatives as answer.

```json
{
    "tomorrow it is tuesday": {
        "en": "Tomorrow it is Tuesday|Tomorrow it's Tuesday",
        "fi": "Huomenna on tiistai"
    }
}
```

### Concepts with multiple labels

Labels consist of either one string or a list of strings. A list of strings is used when there are multiple equivalent ways to express the concept in a language, as with "Mikä päivä tänään on?" and "Mikä päivä on tänään?" below. Toisto will quiz the user with each synonym, so in the example below users practicing Finnish will be asked to translate both Finnish sentences.

```json
{
    "what day is it today": {
        "en": "What day is it today?",
        "fi": [
            "Mikä päivä tänään on?",
            "Mikä päivä on tänään?"
        ]
    }
}
```

### Multiple concepts with the same label

Sometimes a concept in one language can be two different concepts in another language. For example, both in English and Dutch there are separate greetings for the afternoon and the whole day: "Good afternoon" and "Good day" in English and "Goedemiddag" and "Goedendag" in Dutch. In Finnish "Hyvää päivää", or just "Päivää", is used for both. As an aside, "Hyvää iltapäivää", although grammatically correct, is not used.

If we would include all these labels in one concept, Toisto would consider "Goedemiddag" a correct translation of "Good day", which is undesirable. The solution is to have two concepts, one for "good afternoon" and one for "good day". Both concepts get the Finnish labels "Hyvää päivää" and "Päivää". The Finnish labels for the "good afternoon" concept get a hint that Toisto shows when asking for the Dutch or English translation of "Hyvää päivää" or "Päivää" so that the user knows the context. The hint is the part after the `;`.

In the topic file this looks as follows:

```json
{
    "good afternoon": {
        "en": "Good afternoon",
        "fi": [
            "Hyvää päivää;afternoon",
            "Päivää;afternoon"
        ],
        "nl": "Goedemiddag"
    },
    "good day": {
        "en": "Good day",
        "fi": [
            "Hyvää päivää",
            "Päivää"
        ],
        "nl": "Goedendag"
    }
}
```

### Grammatical number

When concepts can have both singular and plural forms, such as with most nouns, these are represented in the JSON as mappings with `singular` and `plural` as keys and concepts as values.

The format of the JSON files is as follows:

```json
{
    "day": {
        "singular": {
            "en": "Day",
            "fi": "Päivä",
            "nl": "De dag"
        },
        "plural": {
            "en": "Days",
            "fi": "Päivät",
            "nl": "De dagen"
        }
    }
}
```

### Grammatical gender

When concepts have multiple genders, these can be specified as follows:

```json
{
    "parent": {
        "female": {
            "en": "Mother",
            "nl": "De moeder"
        },
        "male": {
            "en": "Father",
            "nl": "De vader"
        }
    }
}
```

It is also possible to have a neutral gender:

```json
{
    "parent": {
        "female": {
            "en": "Mother",
            "nl": "De moeder"
        },
        "male": {
            "en": "Father",
            "nl": "De vader"
        },
        "neuter": {
            "en": "Parent",
            "nl": "De ouder"
        }
    }
}
```

Note that Toisto uses gender only for verbs at the moment, see the next section. The examples above are not in the builtin topic files.

### Grammatical person

When concepts, usually verbs and pronouns, have different persons, these are represented in the JSON as mappings with `first person`, `second person`, and `third person`.

The format of the JSON files is as follows:

```json
{
    "to have": {
        "singular": {
            "first person": {
                "en": "I have|I've",
                "fi": "Minulla on"
            },
            "second person": {
                "en": "You have|You've;singular",
                "fi": "Sinulla on"
            },
            "third person": {
                "female": {
                    "en": "She has|She's",
                    "fi": "Hänellä on;female"
                },
                "male": {
                    "en": "He has|He's",
                    "fi": "Hänellä on;male"
                }
            }
        },
        "plural": {
            "first person": {
                "en": "We have|We've",
                "fi": "Meillä on"
            },
            "second person": {
                "en": "You have|You've;plural",
                "fi": "Teillä on"
            },
            "third person": {
                "en": "They have|They've",
                "fi": "Heillä on"
            }
        }
    }
}
```

Note that because the second person singular and plural are the same in English, Toisto needs to tell the user whether it is asking for a translation of the singular version or the plural version of "You are". The hint is the part after the `;`.

The same goes for the third person Finnish. Because Finnish does not distinguish between male and female gender, Toisto needs to tell the user whether it is asking for the female or the male translation of "Hänellä on".

### Infinitive

When concepts are verbs, infinitives can be specified as follows:

```json
{
    "to have": {
        "infinitive": {
            "en": "To have",
            "fi": "Olla (omistaa)"
        },
        "singular": {
            "first person": {
                "en": "I have|I've",
                "fi": "Minulla on"
            },
            "second person": "..."
        },
        "plural": "..."
    }
}
```

### Tenses

When concepts are verbs, the present tense and the past tense can be specified as follows:

```json
{
    "to be": {
        "infinitive": "...",
        "present tense": {
            "singular": {
                "first person": {
                    "en": "I am|I'm",
                    "fi": "Minä olen|Olen",
                },
                "second person": "..."
            },
            "plural": "..."
        },
        "past tense": {
            "singular": {
                "first person": {
                    "en": "I was",
                    "fi": "Minä olin|Olin",
                },
                "second person": "..."
            },
            "plural": "..."
        }
    }
}
```

### Degrees of comparison

Degrees of comparison are specified as follows:

```json
{
    "small": {
        "positive degree": {
            "en": "Small",
            "nl": "Klein"
        },
        "comparitive degree": {
            "en": "Smaller",
            "nl": "Kleiner"
        },
        "superlative degree": {
            "en": "Smallest",
            "nl": "Kleinst"
        }
    }
}
```

When there are synonyms, they need to be in the same order in every degree. This makes sure Toisto does not consider "Suurin" a superlative of "Iso".

```json
{
    "big": {
        "positive degree": {
            "en": "Big",
            "fi": ["Iso", "Suuri"]
        },
        "comparitive degree": {
            "en": "Bigger",
            "fi": ["Isompi", "Suurempi"]
        },
        "superlative degree": {
            "en": "Biggest",
            "fi": ["Isoin", "Suurin"]
        }
    }
}
```

### Sentence forms

When the topic file contains both the declarative and the interrogative form of a sentence, Toisto can generate quizzes to change one into the other. Sentence forms are specified as follows:

```json
{
    "the car is black": {
        "declarative": {
            "en": "The car is black",
            "nl": "De auto is zwart"
        },
        "interrogative": {
            "en": "Is the car black?",
            "nl": "Is de auto zwart?"
        }
    }
}
```

### Grammatical polarity

Polarity (affirmative and negative sentence forms) can be specified as follows:

```json
{
    "the car is black": {
        "affirmative": {
            "en": "The car is black",
            "nl": "De auto is zwart"
        },
        "negative": {
            "en": "The car is not black",
            "nl": "De auto is niet zwart"
        }
    }
}
```

### Concept relationships

When a concept uses one or more other concepts, this can be specified with the `uses` relation. Toisto will only quiz a *using* concept when all *used* concepts have been quizzed. The `uses` relationship can be specified by adding a `uses` key to the concept with a list of concept identifiers as value:

```json
{
    "day": {
        "singular": {
            "en": "Day",
            "nl": "De dag"
        },
        "plural": {
            "en": "Days",
            "nl": "De dagen"
        }
    },
    "week": {
        "singular": {
            "en": "Week",
            "nl": "De week"
        },
        "plural": {
            "en": "Weeks",
            "nl": "De weken"
        }
    },
    "days of the week": {
        "uses": ["day", "week"],
        "en": "Days of the week",
        "nl": "De dagen van de week"
    }
}
```

If a concept uses exactly one other concept, the `uses` value can be a string instead of a list of concept identifiers. If the used concepts differ per language, an object with languages as keys can be used:

```json
{
    "shirt": {
        "en": "Shirt",
        "fi": "Paita"
    },
    "sweater": {
        "uses": {
            "fi": "shirt"
        },
        "en": "Sweater",
        "fi": "Neulepaita"
    }
}
```

### Concept levels

The [Common European Framework of Reference for Languages (CEFR)](https://www.coe.int/en/web/common-european-framework-reference-languages) organises language proficiency into six levels:

1. Basic user: `A1` and `A2`
2. Independent user: `B1` and `B2`
3. Proficient user: `C1` and `C2`

Some dictionaries provide the language levels of words. Toisto uses these resources as source for the language level (and only for the language level, no other information from these source is used in Toisto):

1. The [English Vocabulary Profile Online - British English]("https://www.englishprofile.org/wordlists/evp"). Key: `EP`. Language: English.
2. The [Yle Kielikoulu Learning Profile]("https://kielikoulu.yle.fi/#/profile"). Key: `KK`. Language: Finnish.
3. The [Oxford Advanced Learner’s Dictionary online]("https://www.oxfordlearnersdictionaries.com"). Key: `OD`. Language: English.

Toisto uses the language level of words as one of the factors in determining the order in which to present concepts to the user.

Because the sources may disagree on the language level of words, we add the language level per concept, as follows:

```json
{
    "1000": {
        "level": {
            "A1": ["KK", "OD"],
            "A2": "EP"
        },
        "en": "Thousand",
        "fi": "Tuhat"
    },
    "2000": {
        "level": {
            "none": ["EP", "OD"]
        },
        "en": "Two thousand",
        "fi": "Kaksituhatta"
    }
}
```

If the source does not provide a language level for a concept, this can be indicated by adding the source to the key `none`. This makes it clear that the source has been consulted but did not provide a language level for the concept.

## Quizzes

Toisto uses the concepts to generate quizzes. Currently, the following types of quizzes are generated:

1. Quizzes to translate a concept from one language to another and vice versa. Toisto quizzes the user in both directions.
2. Quizzes to listen to a concept in the target language and then type in what was said.
3. Quizzes to singularize a plural concept or pluralize a singular concept.
4. Quizzes to change the person of a concept.
5. Quizzes to change the gender of a concept.
6. Quizzes to provide the positive, comparitive, or superlative degree of comparison, given an adjective in another degree.
7. Quizzes to change the sentence form and polarity.

Except for the translation type quizzes, quizzes only use the user's target language.

## Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of the retention of quizzes, i.e. how long the user has been correctly answering a quiz. Retention is defined as the time between the most recent correct answer and the oldest correct answer, where there have been no incorrect answers in between.

For example, if a user answers a quiz correctly on March 1, incorrectly on March 3, correctly on March 6, correctly on March 8, and correctly on March 15, that quiz has a retention of nine days (March 6 to March 15).

Each time a quiz is answered correctly, the quiz is silenced for a while. The longer the quiz's current retention, the longer the quiz is silenced. Whenever the user makes a mistake the retention is reset to zero.

If a user knows the correct answer the first time a quiz is presented, the quiz is silenced for a longer duration (24 hours).
