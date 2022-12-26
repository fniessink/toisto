# Software documentation

## Topics

Builtin topics are located in `src/topics` in the form of JSON files. Users can also create their own topic files as long as it complies with the description below and pass them to Toisto using the `-t/--topic-file` command-line option.

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

Concepts are represented in the topic files as objects. The key is an identifier for the concept. The value is a mapping with language identifiers as keys and labels as values. Currently supported language identifiers are `en` for English, `fi` for Finnish, and `nl` for Dutch.

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

If we would include all these labels in one concept, Toisto would consider "Goedemiddag" a correct translation of "Good day", which is undesirable. The solution is to have two concepts, one for "good afternoon" and one for "good day". Both concepts get the Finnish labels "Hyvää päivää" and "Päivää". The Finnish labels for the "good afternoon" concept get a hint that Toisto shows when asking for the Dutch or English translation of "Hyvää päivää" or "Päivää" so that the user knows the context.

In the topic file this looks as follows:

```json
{
    "good afternoon": {
        "uses": "day",
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

The singular and plural forms are considered *subconcepts* of the main concept. Both implicitly get their own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the singular form gets `day/singular` as key and the plural form `day/plural`.

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

The gendered forms are considered *subconcepts* of the main concept. Each subconcept gets its own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the female form gets `parent/female` as key, the male form `parent/male`, and the neuter form `parent/neuter`.

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

The different persons are considered *subconcepts* of the main concept. Each subconcept gets its own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the first person singular gets `to have/singular/first person` as key, the second person singular `to have/singular/second person`, etc.

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

Infinitives, like the different persons, are considered *subconcepts* of the main concept. Each subconcept gets its own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the infinitive gets `to have/infinitive` as key.

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

Tenses, like the infinitive, are considered *subconcepts* of the main concept. Each subconcept gets its own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the present tense gets `to be/present tense` as key and the past tense `to be/past tense`.

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
            "fi": ["Iso", "Suuri"],
            "nl": "Groot"
        },
        "comparitive degree": {
            "en": "Bigger",
            "fi": ["Isompi", "Suurempi"],
            "nl": "Groter"
        },
        "superlative degree": {
            "en": "Biggest",
            "fi": ["Isoin", "Suurin"],
            "nl": "Grootst"
        }
    }
}
```

The diffent degrees of comparison are considered *subconcepts* of the main concept. Each subconcept gets its own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the positive degree gets `big/positive degree` as key, the comparitive degree `big/comparitive degree`, and the superlative degree `big/superlative degree`.

### Sentence types

When the topic file contains both the declarative and the interrogative type of a sentence, Toisto can generate quizzes to change one into the other. Sentence types are specified as follows:

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

The sentence types are considered *subconcepts* of the main concept. Each subconcept gets its own key that can be used to refer to the subconcept, see the section on [concept relationships](#concept-relationships) below. In the example above, the declarative sentence type gets `the car is black/declarative` as key and the interrogative type gets `the car is black/interrogative`.

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

If a concept uses exactly one other concept, the `uses` value can be a string instead of a list of concept identifiers.

As mentioned in the previous sections, subconcepts automatically get a more specific key. This means the uses relationsips in the example above could be made more specific be referring to the singular of week and the plural of day:

```json
{
    "days of the week": {
        "uses": ["day/plural", "week/singular"],
        "en": "Days of the week",
        "nl": "De dagen van de week"
    }
}
```

## Quizzes

Toisto uses the concepts to generate quizzes. Currently, the following types of quizzes are generated:

1. Quizzes to translate a concept from one language to another and vice versa. Toisto quizzes the user in both directions. If there are multiple labels, Toisto uses all labels as question and as answer. So both "Mikä päivä tänään on?" and "Mikä päivä on tänään?" are asked as question and both are accepted as correct answer for the quiz "What day is it today?".
2. Quizzes to listen to a concept in the practice language and then type in what was said.
3. Quizzes to singularize a plural concept or pluralize a singular concept.
4. Quizzes to change the person of a concept.
5. Quizzes to change the gender of a concept.
6. Quizzes to provide the positive, comparitive, or superlative degree of comparison, given an adjective in another degree.

Except for the translation type quizzes, quizzes only use the user's practice language.

## Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of the retention of quizzes, i.e. how long the user has been correctly answering a quiz. Retention is defined as the time between the most recent correct answer and the oldest correct answer, where there have been no incorrect answers in between.

For example, if a user answers a quiz correctly on March 1, incorrectly on March 3, correctly on March 6, correctly on March 8, and correctly on March 15, that quiz has a retention of nine days (March 6 to March 15).

Each time a quiz is answered correctly, the quiz is silenced for a while. The longer the quiz's current retention, the longer the quiz is silenced. Whenever the user makes a mistake the retention is reset to zero.

If a user knows the correct answer the first time a quiz is presented, the quiz is silenced for a longer duration (24 hours).
