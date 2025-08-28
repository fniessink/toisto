# Software documentation

## Concepts and labels

Built-in concepts are located in `src/concepts` in the form of JSON files.

Users can also create their own files as long as they comply with the description below and pass them to Toisto using the `-f/--file` command-line option.

Each JSON file contains zero or more *concepts* and zero or more *labels* in different languages.

A concept can be anything that can be expressed in language. The labels are words, phrases, or sentences that express a concept in a specific language. The language identifiers are two or three letter strings as listed in the [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry).

The contents of a JSON file looks as follows:

```json
{
    "concepts": {
        "today": {},
        "yesterday": {},
        "tomorrow": {},
    },
    "labels": {
        "en": [
            {
                "concept": "today",
                "label": "today"
            },
            {
                "concept": "yesterday",
                "label": "yesterday"
            },
            {
                "concept": "tomorrow",
                "label": "tomorrow"
            }
        ],
        "fi": [
            {
                "concept": "today",
                "label": "tänään"
            },
            {
                "concept": "yesterday",
                "label": "eilen"
            },
            {
                "concept": "tomorrow",
                "label": "huomenna"
            }
        ],
        "nl": [
            {
                "concept": "today",
                "label": "vandaag"
            },
            {
                "concept": "yesterday",
                "label": "gisteren"
            },
            {
                "concept": "tomorrow",
                "label": "morgen"
            }
        ]
    ]
}
```

Concepts are represented in the JSON files as JSON objects. The key is an identifier for the concept. It should be unique across all JSON files. In the simplest case, concepts don't have any attributes, see below for possible concept attributes.

Labels are a objects with language identifiers as keys and list of labels as values. Currently, the built-in JSON files contain English with identifier `en`, Finnish with identifier `fi`, and Dutch with identifier `nl`.

Each label always has at least two keys: `concept` and `label`:
- The `concept` contains either one identifier of the concept that the label describes or a list of concept identifiers.
- The `label` contains the label itself. It is either a string or an object containing different grammatical forms of the label.

If you add new languages to the built-in files, or create your own JSON files, be sure to check that the language identifiers used are listed in the [IANA language subtag registry](https://www.iana.org/assignments/language-subtag-registry).

> [!NOTE]
> When using multiple languages is not essential to explain how things work, examples below may contain just one or two languages.

### Letter case and punctuation in labels

Labels can use both uppercase and lowercase letters, and any mix of them. Toisto will check the answers to quizzes in a case sensitive manner.

Labels that contain complete sentences or utterances (for example, "Hello!") are written with an initial capital letter and with punctuation. Labels that contain individual words or phrases (for example, "days of the week") are not written with an initial capital, unless the first word is always written with a capital (for example, "I am"), and don't have punctuation.

### Labels with spelling variants

When there are multiple ways to spell a label, use a list to specify the alternatives. Toisto will only use the first of the alternatives to quiz the user, but will accept the other alternatives as answer.

```json
{
    "concepts": {
        "hotdog": {}
    },
    "labels": {
        "en": [
            {
                "concept": "hotdog",
                "label": [
                    "hotdog",
                    "hot dog"
                ]
            }
        ]
    }
}
```

To prevent having to spell out that "it's" is an alternative for "it is" in every label that contains "it is", Toisto has [builtin spelling variants](../src/languages/spelling_alternatives.json).

The builtin spelling alternatives are specified as a mapping from regular expressions to replacements, organized per language:

```json
{
    "en": {
        "\\bI am\\b": "I'm",
        "\\byou are\\b": "you're",
        "^You are\\b": "You're",
        "...": "..."
    },
    "fi": {
        "^[ms]inä ": "",
        " [ms]inä ": " ",
        "...": "..."
    },
    "nl": {
        "\\bjij\\b": "je",
        "^Jij\\b": "Je",
        "...": "..."
    }
}
```

> [!NOTE]
> Backslashes need to be escaped in the JSON file, hence the double backslashes.

Some spelling alternatives should only be applied if the language is the user's source language and not when the language is the user's target language. For example, users with Dutch as target language should learn nouns together with their article ("de" or "het"), but users with Dutch as source language should be allowed to omit them.

These spelling alternatives can be specified under the `<language identifier>-if-source-language` key:

```json
{
    "nl-if-source-language": {
        "^de ": "",
        "^het ": ""
    }
}
```

### Labels with spoken language

To indicate that a label is only used in spoken language, add the colloquial flag to the label. Toisto will only quiz the label using speech.

```json
{
    "concepts": {
        "7": {},
    },
    "labels": {
        "en": [
            {
                "concept": "7",
                "label": "seven"
            }
        ],
        "fi": [
            {
                "concept": "7",
                "label": "seitsemän"
            },
            {
                "concept": "7",
                "label": "seittemän",
                "colloquial": true
            }
        ]
    }
}
```

### Labels with tips

Sometimes labels are ambiguous. For example, "hän" in Finnish can mean both he or she. To help the user understand which meaning is intended, a tip can be added to the label:

```json
{
    "concepts": {
        "she wants ice cream": {}
    },
    "labels": {
        "en": [
            {
                "concept": "she wants ice cream",
                "label": "She wants ice cream."
            }
        ],
        "fi": [
            {
                "concept": "she wants ice cream",
                "label": "Hän haluaa jäätelöä.",
                "tip": "feminine"
            }
        ]
    }
}
```

In the above example, Toisto will show the tip 'feminine' to the user when asking for the English translation of "Hän haluaa jäätelöä".

If the label has multiple grammatical forms and the tip should only be shown for some of the forms, the grammatical forms can be specified as follows:

```json
{
    "concepts": {
        "to have": {}
    },
    "labels": {
        "fi": [
            {
                "concept": "to have",
                "label": {
                    "infinitive": "olla",
                    "present tense": {
                        "singular": {
                            "first person": "minulla on",
                            "second person": "..."
                        },
                        "plural": {
                            "first person": "meillä on",
                            "second person": "..."
                        }
                    }
                },
                "tip": {
                    "infinitive": "omistaa"
                }
            }
        ]
    }
}
```

Tips can be either a single string or a list of strings.

### Labels with notes

It's also possible to add notes. The notes will be shown after the user has answered. This can be used to point out extra information, for example:

```json
{
    "concepts": {
        "I want ice cream": {}
    },
    "labels": {
        "fi": [
            {
                "concept": "I want ice cream",
                "label": "Minä haluan jäätelöä.",
                "note": "'jäätelöä' is the partitive case of 'jäätelö'"
            }
        ]
    }
}
```

If the label has multiple grammatical forms and the note should only be shown for some of the forms, the grammatical forms can be specified as follows:

```json
{
    "concepts": {
        "I want a cookie": {}
    },
    "labels": {
        "fi": [
            {
                "concept": "I want a cookie",
                "label": {
                    "singular": "Minä haluan keksin.",
                    "plural": "Me haluamme keksejä."
                },
                "note": {
                    "plural": "'keksejä' is the plural partitive case of 'keksi'"
                }
            }
        ]
    }
}
```

Notes can be either a single string or a list of strings.

### Compound labels

When a label is a compound of one or more other labels, this can be specified with the `roots` relation. Toisto will only quiz a concept with *compound* labels when all concepts with the *root* labels (including roots of roots) have been quizzed. The `roots` relationship can be specified by adding a `roots` key to the label with a list of concept identifiers as value:

```json
{
    "concepts": {
        "day": {},
        "week": {},
        "days of the week": {}
    },
    "labels": [
        "en": [
            {
                "concept": "day",
                "label": {
                    "singular": "day",
                    "plural": "days"
                }
            },
            {
                "concept": "week",
                "label": {
                    "singular": "week",
                    "plural": "weeks"
                }
            },
            {
                "concept": "days of the week",
                "label": "days of the week"
                "roots": [
                    "days",
                    "week"
                ],
            }
        ],
        "nl": [
            {
                "concept": "day",
                "label": {
                    "singular": "de dag",
                    "plural": "de dagen"
                }
            },
            {
                "concept": "week",
                "label": {
                    "singular": "de week",
                    "plural": "de weken"
                }
            },
            {
                "concept": "days of the week",
                "label": "de dagen van de week"
                "roots": [
                    "de dagen"
                    "de week"
                ],
            }
        ]
    ]
}
```

The roots can be any grammatical form of the root label, but should be the first spelling alternative of a label if there are multiple. Also, the roots should be labels of different concepts.

If a concept has exactly one root, for example because not all roots have been included in the JSON files yet, the `roots` value can be a string instead of a list of concept identifiers.

### Concepts with multiple labels

Add multiple labels if there are multiple ways to express the concept in a language, as with "Mikä päivä tänään on?" and "Mikä päivä on tänään?" below. Toisto will quiz the user with each synonym, so in the example below users practicing Finnish will be quizzed about both Finnish sentences.

```json
{
    "concepts": {
        "what day is it today": {}
    },
    "labels": {
        "fi": [
            {
                "concept": "what day is it today",
                "label": "Mikä päivä tänään on?"
            },
            {
                "concept": "what day is it today",
                "label": "Mikä päivä on tänään?"
            }
        ]
    }
}
```

### Concepts without label in some languages

Some concepts have a label in one language, but not in other languages. Mämmi, for example, is a traditional Finnish dessert, eaten around Eastern. There's no label in English or Dutch for mämmi. To allow Toisto to explain the meaning of mämmi when quizzing the user, indicate that the label is to be used to explain meaning only and is not to be quizzed:

```json
{
    "concepts": {
        "mämmi": {}
    },
    "labels": {
        "en": [
            {
                "concept": "mämmi",
                "label": "Traditional Finnish Easter dessert",
                "meaning-only": true
            }
        ],
        "fi": [
            {
                "concept": "mämmi",
                "label": "mämmi"
            }
        ]
    }
}
```

### Concepts with identical labels (homographs)

If different concepts have identical labels (meaning they are homographs) and Toisto presents the label in a quiz, it's impossible for the user to know which concept Toisto is looking for. For example, the Dutch word "bank" can mean both "couch" and "bank". A quiz asking the user to translate the Dutch word "bank" to English could be looking for either "bank" or "couch". English verbs have the same problem, as the second person singular and the second person plural are indistinguishable without context.

Toisto recognizes homographs and automatically provides a hint when quizzing a label that has homographs. It does so by looking at the relation between the different concepts that share the same label.

#### Hints based on grammar

If the homographs share a common base concept, such as with verbs, Toisto will base the hint on the grammar of the concepts. For example:

```json
{
    "concepts": {
        "to have": {}
    },
    "labels": {
        "en": [
            {
                "concept": "to have",
                "label": {
                    "singular": {
                        "first person": "...",
                        "second person": "you have",
                        "third person": "..."
                    },
                    "plural":{
                        "first person": "...",
                        "second person": "you have",
                        "third person": "..."
                    }
                }
            }
        ],
        "nl": [
            {
                "concept": "to have",
                "label": {
                    "singular": {
                        "first person": "...",
                        "second person": "jij hebt",
                        "third person": "..."
                    },
                    "plural":{
                        "first person": "...",
                        "second person": "jullie hebben",
                        "third person": "..."
                    }
                }
            }
        ]
    }
}
```

When quizzing the translation of "you have", Toisto will provide a hint based on the grammar, for example: "Listen and write in Dutch (singular)".

#### Hints based on hypernyms

If the homographs have different hypernyms, Toisto will provide a hint based on the hypernym. For example, in the case of the Dutch word "bank", there are two concepts that share that label: "bank" with hypernym "financial institution" and "bank" with hypernym "furniture":

```json
{
    "concepts": {
        "bank": {
            "hypernym": "financial institution",
        },
        "couch": {
            "hypernym": "furniture",
        }
    },
    "labels": {
        "en": [
            {
                "concept": "bank",
                "label": "bank"
            },
            {
                "concept": "couch",
                "label": "couch"
            }
        ],
        "nl": [
            {
                "concept": [
                    "bank",
                    "couch",
                ],
                "label": "de bank"
            }
        ]
    }
}
```

When quizzing the translation of "bank", Toisto provides the hypernym as hint, for example: "Listen and write in Dutch (furniture)".

#### Hints based on invoved concepts

If the homographs involve other concepts, Toisto will provide a hint based on the involved concepts. For example, in the case of the English verb "to play", there are two different verbs in Finnish: "pelata" for playing a sport and "soittaa" for playing a musical instrument:

```json
{
    "concepts": {
        "sport": {},
        "to play a sport": {
            "involves": "sport"
        },
        "musical instrument": {},
        "to play a musical instrument": {
            "involves": "musical instrument"
        },
    },
    "labels": [
        "en": [
            {
                "concept": "sport",
                "label": "sport"
            },
            {
                "concept": "musical instrument",
                "label": "musical instrument"
            },
            {
                "concept": [
                    "to play a musical instrument",
                    "to play a sport"
                ],
                "label": "to play"
            }
        ],
        "fi": [
            {
                "concept": "sport",
                "label": "urheilu"
            },
            {
                "concept": "musical instrument",
                "label": "soitin"
            },
            {
                "concept": "to play a sport",
                "label": "pelata"
            },
            {
                "concept": "to play a musical instrument",
                "label": "soittaa"
            }
        ]
    }
}
```

When quizzing the translation of "to play", Toisto provides the involved concept as hint, for example: "Translate into Finnish (involves 'sport')".

### Concepts with labels that only differ in capitalization (capitonyms)

If different concepts have labels that only differ in capitalization (meaning they are capitonyms) and Toisto presents the label in a listen quiz, it's impossible for the user to hear which concept Toisto is looking for. For example, the Finnish word "Kreikka" means "Greece" (the country) but the word "kreikka" means "Greek" (the language). A quiz asking the user to write the Finnish word "Kreikka" in Finnish could be looking for either "Kreikka" or "kreikka".

Toisto recognizes capitonyms and automatically provides a hint when quizzing a label that has capitonyms. It does so by looking at the relation between the different concepts that share the same label except for capitalization.

#### Hints based on grammar

If the capitonyms share a common base concept, such as with verbs, Toisto will base the hint on the grammar of the concepts. For example, when the second person singular includes the polite form of "you are" that is the same as the second person plural, except for capitalization:

```json
{
    "concepts": {
        "to be": {}
    },
    "labels": {
        "fi": [
            {
                "label": {
                    "singular": {
                        "first person": "..."
                        "second person": [
                            "sinä olet",
                            "Te olette"
                        ],
                        "third person": "..."
                    },
                    "plural": {
                        "first person": "..."
                        "second person": "te olette",
                        "third person": "..."
                    }
                }
            }
        ],
        "nl": [
            {
                "label": {
                    "singular": {
                        "first person": "..."
                        "second person": [
                            "jij bent",
                            "u bent"
                        ],
                        "third person": "..."
                    },
                    "plural": {
                        "first person": "..."
                        "second person": "jullie zijn",
                        "third person": "..."
                    }
                }
            }
        ]
    }
}
```

When quizzing the translation of "te olette", Toisto will provide a hint based on the grammar, for example: "Listen and write in Finnish (plural)".

#### Hints based on hypernyms

If the capitonyms have different hypernyms, Toisto will provide a hint based on the hypernym. For example, in the case of the Finnish words "Kreikka" and "kreikka", "Kreikka" has hypernym "country" and "kreikka" has hypernym "language":

```json
{
    "concepts": {
        "greece": {
            "hypernym": "country",
        },
        "greek": {
            "hypernym": "language",
        },
    },
    "labels": {
        "en": [
            {
                "concept": "greece",
                "label":"Greece"
            },
            {
                "concept": "greek",
                "label":"Greek",
            }
        ],
        "fi": [
            {
                "concept": "greece",
                "label":"Kreikka"
            },
            {
                "concept": "greek",
                "label":"kreikka"
            }
        ]
    }
}
```

When quizzing the spoken version of "Kreikka", Toisto provides the hypernym as hint: "Listen and write in Finnish (country)".

### Concepts with different meanings per language

Sometimes a concept in one language can be two different concepts in another language. For example, both in English and Dutch there are separate greetings for the afternoon and the whole day: "Good afternoon" and "Good day" in English and "Goedemiddag" and "Goedendag" in Dutch. In Finnish "Hyvää päivää" is used for both and "Hyvää iltapäivää", although grammatically correct, is not used.

If we would link all these labels to one concept, Toisto would consider "Goedemiddag" a correct translation of "Good day", which is undesirable. The solution is to have two concepts, one for "good afternoon" and one for "good day". Both concepts get the Finnish labels "Hyvää päivää" and "Päivää". The Finnish labels for the "good afternoon" concept get a tip that Toisto shows when asking for the Dutch or English translation of "Hyvää päivää" or "Päivää" so that the user knows the context.

In the JSON file this looks as follows:

```json
{
    "concepts": {
        "good afternoon": {},
        "good day": {}
    },
    "labels": {
        "en": [
            {
                "concept": "good afternoon",
                "label": "Good afternoon!"
            },
            {
                "concept": "good day",
                "label": "Good day!"
            }
        ],
        "fi": [
            {
                "concept": "good afternoon",
                "label": "Hyvää päivää!",
                "tip": "afternoon"
            },
            {
                "concept": "good day",
                "label": "Hyvää päivää!"
            }
        ],
        "nl": [
            {
                "concept": "good afternoon",
                "label": "Goedemiddag!"
            },
            {
                "concept": "good day",
                "label": "Goedendag!"
            }
        ]
    }
}
```

### Grammatical number

When concepts can have both singular and plural forms, such as with most nouns, these are represented in the JSON as mappings with `singular` and `plural` as keys and labels as values.

The format of the JSON files is as follows:

```json
{
    "concepts": {
        "day": {}
    },
    "labels": {
        "en": [
            {
                "concept": "day",
                "label": {
                    "singular": "day",
                    "plural": "days"
                }
            }
        ],
        "fi": [
            {
                "concept": "day",
                "label": {
                    "singular": "päivä",
                    "plural": "päivät"
                }
            }
        ]
    }
}
```

### Diminutive

When a concept has a diminutive, the diminutive can be included in the JSON file by using `root` for the base form of the concept and `diminutive` for the diminutive form:

```json
{
    "concepts": {
        "table": {}
    },
    "labels": [
        "nl": [
            {
                "concept": "table",
                "label": {
                    "root": "de tafel",
                    "diminutive": "het tafeltje"
                }
            }
        ]
    ]
}
```

With the example above, Toisto will quiz users with Dutch as target language for the diminutive form of "de tafel".

Note that in many languages, diminutives can (only) be formed by using multi-word constructions such as "little table". Though possible, it is not recommended to add these to the JSON files. Instead, only add the root form:

```json
{
    "concepts": {
        "table": {}
    },
    "labels": {
        "en": [
            {
                "concept": "table",
                "label": "table"
            }
        ],
        "nl": [
            {
                "concept": "table",
                "label": {
                    "root": "de tafel",
                    "diminutive": "het tafeltje"
                }
            }
        ]
    }
}
```

### Grammatical gender

When concepts have multiple genders, these can be specified as follows:

```json
{
    "concepts": {
        "parent": {}
    },
    "labels": {
        "en": [
            {
                "concept": "parent",
                "label": {
                    "feminine": "mother",
                    "masculine": "father"
                }
            }
        ],
        "nl": [
            {
                "concept": "parent",
                "label": {
                    "feminine": "moeder",
                    "masculine": "vader"
                }
            }
        ]
    }
}
```

It is also possible to have a neutral gender:

```json
{
    "concepts": {
        "parent": {}
    },
    "labels": {
        "en": [
            {
                "concept": "parent",
                "label": {
                    "feminine": "mother",
                    "masculine": "father",
                    "neutral": "parent"
                }
            }
        ],
        "nl": [
            {
                "concept": "parent",
                "label": {
                    "feminine": "de moeder",
                    "masculine": "de vader",
                    "neutral": "de ouder"
                }
            }
        ]
    }
}
```

Note that Toisto uses gender only for verbs at the moment, see the next section. The examples above are not in the built-in files.

### Grammatical person

When concepts, usually verbs and pronouns, have different persons, these are represented in the JSON as mappings with `first person`, `second person`, and `third person` as keys.

The format of the JSON files is as follows:

```json
{
    "concepts": {
        "to have": {}
    },
    "labels": {
        "en": [
            {
                "concept": "to have",
                "label": {
                    "singular": {
                        "first person": "I have",
                        "second person": "you have",
                        "third person": {
                            "feminine": "she has",
                            "masculine": "he has"
                        }
                    },
                    "plural": {
                        "first person": "we have",
                        "second person": "you have",
                        "third person": "they have"
                    }
                }
            }
        ],
        "nl": [
            {
                "concept": "to have",
                "label": {
                    "singular": {
                        "first person": "ik heb",
                        "second person": "jij hebt",
                        "third person": {
                            "feminine": "zij heeft",
                            "masculine": "hij heeft"
                        }
                    },
                    "plural": {
                        "first person": "wij hebben",
                        "second person": "jullie hebben",
                        "third person": "zij hebben"
                    }
                }
            }
        ]
    }
}
```

Because Finnish does not distinguish between masculine and feminine gender, the third person singular of verbs in Finnish is included directly under the `third person` key:

```json
{
    "concepts": {
        "to have": {}
    },
    "labels": {
        "fi": [
            {
                "concept": "to have",
                "label": {
                    "singular": {
                        "first person": "minulla on",
                        "second person": "sinulla on",
                        "third person": "hänellä on"
                    },
                    "plural": "..."
                }
            }
        ]
    }
}
```

### Infinitive

When concepts are verbs, infinitives can be specified as follows:

```json
{
    "concepts": {
        "to have": {}
    },
    "labels": {
        "en": [
            {
                "concept": "to have",
                "label": {
                    "infinitive": "to have",
                    "singular": {
                        "first person": "I have",
                        "second person": "..."
                    },
                    "plural": "..."
                }
            }
        ]
        "nl": [
            {
                "concept": "to have",
                "label": {
                    "infinitive": "olla (omistaa)",
                    "singular": {
                        "first person": "minulla on",
                        "second person": "..."
                    },
                    "plural": "..."
                }
            }
        ]
    }
}
```

### Verbal nouns

When concepts are verbs, verbal nouns (fourth infinitive in Finnish) can be specified as follows:

```json
{
    "concepts": {
        "to ask": {}
    },
    "labels": {
        "en": [
            {
                "concepts": "to ask,"
                "label": {
                    "infinitive": "to ask",
                    "verbal noun": "asking"
                }
            }
        ],
        "fi": [
            {
                "concepts": "to ask,"
                "label": {
                    "infinitive": "kysyä",
                    "verbal noun": "kysyminen"
                }
            }
        ],
        "nl": [
            {
                "concepts": "to ask,"
                "label": {
                    "infinitive": "vragen",
                    "verbal noun": "het vragen"
                }
            }
        ]
    }
}
```

### Tenses

When concepts are verbs, the present tense, past tense, present perfect, and past perfect tense can be specified as follows:

```json
{
    "concepts": {
        "to be": {}
    },
    "labels": {
        "en": [
            {
                "concept": "to be",
                "label": {
                    "infinitive": "to be",
                    "present tense": {
                        "singular": {
                            "first person": "I am",
                            "second person": "..."
                        },
                        "plural": "..."
                    },
                    "past tense": {
                        "singular": {
                            "first person": "I was",
                            "second person": "..."
                        },
                        "plural": "..."
                    },
                    "present perfect tense": {
                        "singular": {
                            "first person": "I have been",
                            "second person": "..."
                        },
                        "plural": "..."
                    },
                    "past perfect tense": {
                        "singular": {
                            "first person": "I had been",
                            "second person": "..."
                        },
                        "plural": "..."
                    }
                }
            }
        ]
    }
}
```

### Degrees of comparison

Degrees of comparison are specified as follows:

```json
{
    "concepts": {
        "small": {}
    },
    "labels": {
        "en": [
            {
                "concept": "small",
                "label": {
                    "positive degree": "small",
                    "comparative degree": "smaller",
                    "superlative degree": "smallest"
                }
            }
        ],
        "nl": [
            {
                "concept": "small",
                "label": {
                    "positive degree": "klein",
                    "comparative degree": "kleiner",
                    "superlative degree": "kleinst"
                }
            }
        ]
    }
}
```

### Grammatical mood

When the concept file contains different grammatical moods, Toisto can generate quizzes to change one into another. Toisto supports the declarative, interrogative, and imperative mood.

All three moods can be combined as follows:

```json
{
    "concepts": {
        "you run": {}
    },
    "labels": {
        "en": [
            {
                "concept": "you run",
                "label": {
                    "declarative": "You run.",
                    "interrogative": "Do you run?",
                    "imperative": "Run!"
                }
            }
        ],
        "nl": [
            {
                "concept": "you run",
                "label": {
                    "declarative": "Jij rent.",
                    "interrogative": "Ren jij?",
                    "imperative": "Ren!"
                }
            }
        ]
    }
}
```

It is also possible to include just two of the three grammatical moods:

```json
{
    "concepts": {
        "the car is black": {}
    },
    "labels": {
        "en": [
            {
                "concept": "the car is black",
                "label": {
                    "declarative": "The car is black.",
                    "interrogative": "Is the car black?"
                }
            }
        ],
        "nl": [
            {
                "concept": "the car is black",
                "label": {
                    "declarative": "De auto is zwart.",
                    "interrogative": "Is de auto zwart?"
                }
            }
        ]
    }
}
```

### Grammatical polarity

Polarity (affirmative and negative sentence forms) can be specified as follows:

```json
{
    "concepts": {
        "the car is black": {}
    },
    "labels": {
        "en": [
            {
                "concept": "the car is black",
                "label": {
                    "affirmative": "The car is black.",
                    "negative": "The car is not black."
                }
            }
        ],
        "nl": [
            {
                "concept": "the car is black",
                "label": {
                    "affirmative": "De auto is zwart.",
                    "negative": "De auto is niet zwart."
                }
            }
        ]
    }
}
```

### Numbers

Cardinal and ordinal numbers can be specified as follows:

```json
{
    "concepts": {
        "1": {}
    },
    "labels": {
        "en": [
            {
                "concept": "1",
                "label": {
                    "cardinal": "one",
                    "ordinal": "first"
                }
            }
        ],
        "fi": [
            {
                "concept": "1",
                "label": {
                    "cardinal": "yksi",
                    "ordinal": "ensimmäinen"
                }
            }
        ]
    }
}
```

### Abbreviations

Abbreviations can be specified as follows:

```json
{
    "concepts":{
        "llc": {}
    },
    "labels": {
        "en": [
            {
                "concept": "llc",
                "label": {
                    "full form": "limited liability company",
                    "abbreviation": "LLC"
                }
            }
        ],
        "fi": [
            {
                "concept": "llc",
                "label": {
                    "full form": "osakeyhtiö",
                    "abbreviation": "oy"
                }
            }
        ],
        "nl": [
            {
                "concept": "llc",
                "label": {
                    "full form": "de naamloze vennootschap",
                    "abbreviation": "de NV"
                }
            }
        ]
    }
}
```

## Concept relationships

### Antonyms

When one concept is an antonym (opposite) of another concept, this can be specified with the `antonym` relation. Toisto will add quizzes to ask users for the antonym of concepts in their target language.

```json
{
    "concepts": {
        "big": {
            "antonym": "small"
        },
        "small": {
            "antonym": "big"
        },
    "labels": {
        "en": [
            {
                "concept": "big",
                "label": "big"
            },
            {
                "concept": "small",
                "label": "small"
            },
        ],
        "nl": [
            {
                "concept": "big",
                "label": "groot"
            },
            {
                "concept": "small",
                "label": "klein"
            }
        ]
    }
}
```

If a concept has more than one antonym (for example, "large" and "big" are both antonyms of "small"), the `antonym` value can be a list of concept identifiers instead of a string.

### Hypernyms

> [!NOTE]
> Concept X is a hypernym of concept Y if concept Y is a (kind of) X. For example, red is a color, so the concept "color" is a hypernym of the concept "red". The reverse relation is called hyponym, so "red" is a hyponym of "color".

When one concept is a hypernym of another concept (and conversely the other concept is a hyponym of the first concept), this can be specified with the `hypernym` relation. Toisto will derive the hyponym relations automatically. Toisto uses the hyponym relations to decide which related concepts to use when a user selects a concept to practice. This works recursively, so Toisto also includes hyponyms of hyponyms.

Given the JSON below, the command `toisto practice color`, would select both color and red to practice.

```json
{
    "concepts": {
        "color": {},
        "red": {
            "hypernym": "color"
        }
    },
    "labels": {
        "en": [
            {
                "concept": "color",
                "label": "color"
            },
            {
                "concept": "red",
                "label": "red"
            },
        ],
        "nl": [
            {
                "concept": "color",
                "label": "de kleur"
            },
            {
                "concept": "red",
                "label": "rood"
            }
        ]
    }
}
```

If a concept has more than one hypernym (for example, "pet" and "mammal" are both hypernyms of "dog"), the `hypernym` value can be a list of concept identifiers instead of a string.

### Holonyms

> [!NOTE]
> Concept X is a holonym of concept Y if concept Y is a part of X. For example, cars have wheels, so the concept "car" is a holonym of the concept "wheel". The reverse relation is called meronym, so "wheel" is a meronym of "car".

When one concept is a holonym of another concept (and conversely the other concept is a meronym of the first concept), this can be specified with the `holonym` relation. Toisto will derive the meronym relations automatically. Toisto uses the holonym and meronym relations to decide which related concepts to use when a user selects a concept to practice. This works recursively, so Toisto also includes holonyms of holonyms.

Given the JSON below, the command `toisto practice car`, would select both the concept "car" and the concept "wheel" to practice.

```json
{
    "concepts": {
        "car": {},
        "wheel": {
            "holonym": "car",
        },
    "labels": {
        "en": [
            {
                "concept": "car",
                "label": "car"
            },
            {
                "concept": "wheel",
                "label": "wheel"
            },
        ],
        "nl": [
            {
                "concept": "car",
                "label": "de auto"
            },
            {
                "concept": "wheel",
                "label": "het wiel"
            }
        ]
    }
}
```

If a concept has more than one holonym (for example, "chair" and "table" are both holonyms of "leg"), the `holonym` value can be a list of concept identifiers instead of a string.

### Concept involvement

When one concept involves another concept, this can be specified with the `involves` relation. Toisto will derive the inverse relation automatically. Toisto uses the involvement relations to decide with related concepts to use when a user selects a concept to practice. This works recursively, so Toisto also includes concepts involved by concepts involved by concepts.

Given the JSON below, the command `toisto practice "to paint"`, would select "to paint", "painter", and "painting" to practice.

```json
{
    "concepts": {
        "painter": {},
        "painting": {},
        "to paint": {
            "involves": [
                "painter",
                "painting"
            ]
        },
    "labels": {
        "en": [
            {
                "concept": "to paint",
                "label": "to paint"
            },
            {
                "concept": "painter",
                "label": "painter"
            },
            {
                "concept": "painting",
                "label": "painting"
            }
        ],
        "nl": [
            {
                "concept": "to paint",
                "label": "schilderen"
            },
            {
                "concept": "painter",
                "label": "de schilder"
            },
            {
                "concept": "painting",
                "label": "het schilderij"
            }
        ]
    }
}
```

If a concept involves just one other concept (for example, "to save" involves only "money"), the `involves` value can be a single concept identifier instead of a list of concept identifiers.

### Examples

When one concept is an example of the usage of another concept, this can be specified using the `example` relation. Toisto will show the example after the user has answered the quiz.

```json
{
    "concepts": {
        "next to": {
            "example": "the museum is next to the church"
        },
        "the museum is next to the church": {}
    },
    "labels": {
        "en": [
            {
                "concept": "next to",
                "label": "next to"
            },
            {
                "concept": "the museum is next to the church",
                "label": "The museum is next to the church."
            }
        ],
        "fi": [
            {
                "concept": "next to",
                "label": "vieressä"
            },
            {
                "concept": "the museum is next to the church",
                "label": "Museo on kirkon vieressä."
            }
        ]
    }
}
```

If a concept has multiple examples, the `example` value can be a list of concept identifiers instead of a string.

### Questions/answers

When one concept is a question and the other concept is the answer, this can be specified using the `answer` relation. Toisto will add a quiz, asking the user to answer the question in their target language.

```json
{
    "concepts": {
        "what do you like": {
            "answer": "i like ice cream"
        },
        "i like ice cream": {}
    },
    "labels": {
        "en": [
            {
                "concept": "what do you like",
                "label": "What do you like?",
                "tip": "ice cream"
            },
            {
                "concept": "i like ice cream.",
                "label": "I like ice cream."
            }
        ],
        "fi": [
            {
                "concept": "what do you like",
                "label": "Mistä sinä pidät?",
                "tip": "jäätelöä"
            },
            {
                "concept": "i like ice cream.",
                "label": "Minä pidän jäätelöstä."
            }
        ]
    }
}
```

Answers are also possible if the concept has multiple grammatical forms, like singular and plural:

```json
{
    "concepts": {
        "what do you like": {
            "answer": "i like ice cream",
        },
        "i like ice cream": {}
    },
    "labels": {
        "en": [
            {
                "concept": "what do you like",
                "label": {
                    "singular": "What do you like?",
                    "plural": "What do you all like?"
                },
                "tip": "ice cream"
            },
            {
                "concept": "i like ice cream",
                "label": {
                    "singular": "I like ice cream.",
                    "plural": "We like ice cream."
                }
            }
        ],
        "fi": [
            {
                "concept": "what do you like",
                "label": {
                    "singular": "Mistä sinä pidät?",
                    "plural": "Mistä te pidätte?"
                },
                "tip": "jäätelöä"
            },
            {
                "concept": "i like ice cream",
                "label": {
                    "singular": "Minä pidän jäätelöstä.",
                    "plural": "Me pidämme jäätelöstä."
                }
            }
        ]
    }
}
```

If a concept has multiple answers, the `answer` value can be a list of concept identifiers instead of a string:

```json
{
    "concepts": {
        "do you like ice cream": {
            "answer": [
                "yes, i like ice cream",
                "no, i don't like ice cream"
            ],
        },
        "yes, i like ice cream": {
            "answer-only": true
        },
        "no, i don't like ice cream": {
            "answer-only": true
        }
    },
    "labels": {
        "en": [
            {
                "concept": "do you like ice cream",
                "label": "Do you like ice cream?"
            },
            {
                "concept": "yes, i like ice cream",
                "label": "Yes, I do."
            },
            {
                "concept": "no, i don't like ice cream",
                "label": "No, I don't."
            }
        ],
        "fi": [
            {
                "concept": "do you like ice cream",
                "label": "Pidätko sinä jäätelöstä?"
            },
            {
                "concept": "yes, i like ice cream",
                "label": "Pidän."
            },
            {
                "concept": "no, i don't like ice cream",
                "label": "En."
            }
        ]
    }
}
```

The answer concepts in the previous example have the key `answer-only` set to `true`. This tells Toisto not to generate quizzes for these two concepts. Given how Finnish and English deal with answering yes/no questions differently, it doesn't make sense to ask users to, for example, translate "Yes, I do" into "Pidän".

## Quizzes

Toisto uses the concepts to generate quizzes. Currently, the following types of quizzes are generated:

Translation quizzes:

1. Translate a concept from the target language to the source language.
2. Listen to a concept in the target language and then type in what was said.
3. Translate a concept from the source language to the target language.
4. Listen to a concept in the target language and then translate what was said in the source language.

Grammatical quizzes:

5. Singularize a plural concept or pluralize a singular concept.
6. Diminutize a concept.
7. Change the person of a concept.
9. Change the gender of a concept.
9. Provide the positive, comparative, or superlative degree of comparison, given an adjective in another degree.
10. Change the tense of a concept between infinitive, present tense, and past tense.
11. Change the grammatical mood of a concept between declarative, interrogative, and imperative mood.
12. Change the polarity from affirmative to negative and vice versa.
13. Change cardinal numbers into ordinal numbers and vice versa.

Semantic quizzes:

14. Give the antonym.
15. Answer a question.
16. Abbreviate a concept or give the full-form of the abbreviation.
17. Put the words of a shuffled sentence in the right order.

Except when asking the user to translate from the source language to the target language, quizzes only use the user's target language.

## Spaced repetition

Toisto uses a very simple implementation of a spaced repetition algorithm. Toisto does not make assumptions about how many concepts the user wants to practice per session or per day. It only keeps track of the retention of quizzes, i.e. how long the user has been correctly answering a quiz. Retention is defined as the time between the most recent correct answer and the oldest correct answer, where there have been no incorrect answers in between.

For example, if a user answers a quiz correctly on March 1, incorrectly on March 3, correctly on March 6, correctly on March 8, and correctly on March 15, that quiz has a retention of nine days (March 6 to March 15).

Each time a quiz is answered correctly, the quiz is silenced for a while. The longer the quiz's current retention, the longer the quiz is silenced. Whenever the user makes a mistake the retention is reset to zero.

If a user knows the correct answer the first time a quiz is presented, the quiz is silenced for a longer duration (24 hours).

## Progress savefile

When the program is stopped, progress is saved in a file named `.toisto-{device specific id}-progress-{target language}.json` in the user's home folder, for example `.toisto-c5323926-33e2-1eef-a453-2922a2aed6c5-progress-fi.json`. So each target language gets its own progress file.

Each entry in the file is the progress of one specific quiz. The key denotes the quiz, the value contains information about the user's retention of the quiz. This looks as follows:

```json
{
    "nl:fi:lezen:lukea:translate": {
        "count": 2
    },
    "nl:fi:het oog:silmä:translate": {
        "start": "2023-02-25T17:34:37",
        "end": "2023-02-25T17:35:37",
        "skip_until": "2023-02-26T17:40:37",
        "count": 3
    }
}
```

The key format was changed in Toisto v0.28 to not include the concept identifier. This allows for changing the concept identifier without invalidating the user's progress on quizzes for that concept. Whenever Toisto reads a progress file with keys in the old format, it converts the keys the new format, where possible (it can only do so for concepts the user wants to practice). The old format looks as follows:

```json
{
    "to read:nl:fi:lezen:translate": {
        "count": 2
    },
    "eye:nl:fi:het oog:translate": {
        "start": "2023-02-25T17:34:37",
        "end": "2023-02-25T17:35:37",
        "skip_until": "2023-02-26T17:40:37",
        "count": 3
    }
}
```

The first entry is the quiz to translate "lezen" from Dutch to Finnish. This quiz has been presented to the user twice (`count` is 2), but they haven't answered it correctly since the last time it was presented.

The second entry is the quiz to translate "het oog" from Dutch to Finnish. This quiz has been presented to the user three times (`count` is 3) in the period between `start` and `end` and they have answered it correctly each time. Toisto will not present to quiz again until after `skip_until`.

The keys in the savefile contain the question label of quizzes. That means that when the label of a concept changes, for example to fix spelling, progress on quizzes that use the label will be lost.
