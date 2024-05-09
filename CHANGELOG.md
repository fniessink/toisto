# Changelog

All notable changes to Toisto will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Accept an initial capital letter when both the question and the answer of a quiz are in lower case. Fixes [#671](https://github.com/fniessink/toisto/issues/671).
- Use single quotes when referring to questions and answers in user feedback. When feedback ends with a quoted question or answer, only add a period if the quoted question or answer does not already end with punctuation. Fixes [#675](https://github.com/fniessink/toisto/issues/675).
- Allow for omitting the article when the source language is Dutch and the answer has a capital. For example, when the correct answer was "het Engels", answering "Engels" would be marked as incorrect. Fixes [#680](https://github.com/fniessink/toisto/issues/680).
- When concepts have roots that also have roots, not only quiz the direct root concepts before the compound concept but also the roots of the roots. For example, one of the roots of "last weekend" would be "weekend", which in turn has "week" and "end" as roots. Fixes [#683](https://github.com/fniessink/toisto/issues/683).

### Added

- Add support for the present perfect tense. Closes [#632](https://github.com/fniessink/toisto/issues/632).
- When showing examples, also show the meaning of the examples. Closes [#638](https://github.com/fniessink/toisto/issues/638).
- Clarify in the documentation which concept relations are recursive. Closes [#683](https://github.com/fniessink/toisto/issues/683).
- Add several concepts.

## 0.18.1 - 2024-04-09

### Fixed

- When showing examples, show only one spelling alternative. Fixes [#639](https://github.com/fniessink/toisto/issues/639).
- When quizzing colloquial language (which is quizzed spoken only), show the colloquial language after the quiz. Fixes [#640](https://github.com/fniessink/toisto/issues/640).
- Split the "head" concept into two different concepts: head as in part of a human or animal body and head as in the main part of something. Fixes [#643](https://github.com/fniessink/toisto/issues/643).
- When quizzing a colloquial sentence, mention that the user is expected to enter a complete sentence. Fixes [#645](https://github.com/fniessink/toisto/issues/645).
- When quizzing a translation from source language to target language, show any examples in the target language. Fixes [#649](https://github.com/fniessink/toisto/issues/649).

## 0.18.0 - 2024-04-06

### Changed

- On the command line, accept concepts as positional arguments, so users don't have to type `--concept` or `-c` before each concept. Closes [#631](https://github.com/fniessink/toisto/issues/631).

### Added

- Show tip about the config file when users have not configured their language preferences. Closes [#633](https://github.com/fniessink/toisto/issues/633).
- Add several concepts related to the human body.

## 0.17.0 - 2024-04-01

### Fixed

- Don't show builtin spelling alternatives as other correct answers. For example, Toisto would show "de pijn" as another correct answer when a user with Dutch as source language had entered "pijn" as answer. Fixes [#623](https://github.com/fniessink/toisto/issues/623).
- The progress command would not sort the quizzes correctly when sorting by retention. Fixes [#625](https://github.com/fniessink/toisto/issues/625).
- When practicing Dutch, Toisto would crash on certain concepts because they would refer to non-existing root concepts. Fixes [#626](https://github.com/fniessink/toisto/issues/626).

### Added

- Add support for the imperative grammatical mood. Closes [#618](https://github.com/fniessink/toisto/issues/618).

## 0.16.0 - 2024-03-30

### Fixed

- Toisto would crash when trying to give the standard Finnish version of two colloquial phrases because they were missing.

### Added

- Add several concepts.

## 0.15.0 - 2024-02-08

### Fixed

- Give an error message when a selected concept does not exist. Closes [#516](https://github.com/fniessink/toisto/issues/516).
- Remove dashes from labels before sending them to the speech synthesizer for better pronunciation. Closes [#546](https://github.com/fniessink/toisto/issues/546).

### Added

- Support abbreviations. Closes [#498](https://github.com/fniessink/toisto/issues/498).
- Support generating alternative answers (like accepting "it's" when the label is "it is"). Closes [#520](https://github.com/fniessink/toisto/issues/520).
- Specifying a concept to practice with `-c/--concept` also loads related concepts.
- Allow for specifying examples in the concept files and show those examples after quizzes.

### Removed

- Topics and topic files no longer exist. The command line parameter for loading extra files has been renamed to `-f/--file`.

## 0.14.1 - 2023-12-09

### Fixed

- Version 0.14.0 did not include the built-in concept files. Fixes [#512](https://github.com/fniessink/toisto/issues/512).

## 0.14.0 - 2023-12-09

### Fixed

- Toisto wouldn't warn the user when answering in the wrong language in the case of dictation quizzes. Fixes [#453](https://github.com/fniessink/toisto/issues/453).
- Toisto would incorrectly warn the user about answering in the wrong language in the case of grammatical quizzes if the user would answer with the question. Fixes [#509](https://github.com/fniessink/toisto/issues/509).

### Changed

- Make the warning for answering in the wrong language more prominent. Changes [#453](https://github.com/fniessink/toisto/issues/453).
- Distinguish between the meanings of questions and answers by inserting  "respectively" between them. Changes [#442](https://github.com/fniessink/toisto/issues/442).
- On Macos, when there is no internet connection, use the "enhanced" voices of the `say` command for Finnish and English.

### Added

- Added several topics and concepts.

## 0.13.0 - 2023-11-12

### Fixed

- Give an error message when the user's filters (by level, by topic, by concept identifier) don't match any concepts. Fixes [#437](https://github.com/fniessink/toisto/issues/437).
- Give an error message when the target and source language are the same. Fixes [#453](https://github.com/fniessink/toisto/issues/453).
- When using the topics command with filters, hide empty topic tables. Fixes [#477](https://github.com/fniessink/toisto/issues/477).

### Added

- Distinguish between the meanings of questions and answers by inserting a ">" between them. Closes [#442](https://github.com/fniessink/toisto/issues/442).
- Warn the user if they are answering in their target language when the source language is asked, or vice versa. Closes [#459](https://github.com/fniessink/toisto/issues/459).
- Added quizzes for changing cardinal numbers into ordinals numbers and vice versa.
- Added several topics and concepts.

### Changed

- Concepts and topics are now stored in different files. This allows users to create their own topic files consisting of a list of existing topics.

### Removed

- Toisto no longer includes CEFR-levels in concept files not uses them sort quizzes. Most if not all sources for CEFR-levels prohibit redistribution of their material. Closes [#482](https://github.com/fniessink/toisto/issues/482).

## 0.12.0 - 2023-09-20

### Fixed

- Don't consider answers with spaces inside correct. Fixes [#403](https://github.com/fniessink/toisto/issues/403).
- After asking the user to listen to and translate a concept with synonyms, show all synonyms as meanings. Fixes [#408](https://github.com/fniessink/toisto/issues/408).

### Added

- Add a 'translate' quiz type where Toisto speaks the label in the target language and the user has to enter the translation in the source language.
- Allow for specifying that labels are colloquial, i.e. spoken language, only.
- When expecting the user to enter a complete sentence, add "write a complete sentence" to the quiz instruction.

## 0.11.0 - 2023-08-16

### Fixed

- Fixed a few typo's.
- Show notes for listening quizzes. Fixes [#351](https://github.com/fniessink/toisto/issues/351).
- Don't generate complicated grammatical quizzes like "Give the affirmative past tense plural third person...". Fixes [#372](https://github.com/fniessink/toisto/issues/372).

### Added

- Add question/answer concepts. Closes [#233](https://github.com/fniessink/toisto/issues/233).
- Concepts can belong to multiple topics. Closes [#234](https://github.com/fniessink/toisto/issues/234).
- Allow for adding notes that are shown after a quiz has been answered. Closes [#321](https://github.com/fniessink/toisto/issues/321).
- Allow for specifying one or more concepts to practice via de command-line interface.
- Added several topics and concepts.

### Changed

- The context information that can be added to labels and that is shown as part of quiz instructions is no longer called a "hint" but a "note". This prepares for supporting notes that are shown after the quiz.

## 0.10.0 - 2023-04-01

### Added

- Make `practice` the default command. Closes [#278](https://github.com/fniessink/toisto/issues/278).
- Add some more concepts.

### Removed

- Remove plurals of compound nouns if the plural of the compound is simply the plural of the last root.

## 0.9.0 - 2023-03-21

### Note

Unfortunately, this version is backwards incompatible and progress information from previous versions is lost.

### Fixed

- In the topic files, only have words with capitals when they start a sentence or are always written with an initial capital. Use proper punctuation for sentences. Compare answers case sensitive. Fixes [#242](https://github.com/fniessink/toisto/issues/242) and [#242](https://github.com/fniessink/toisto/issues/242).
- Don't ask the user what the antonym of a concept is before the antonym itself has been quizzed. Fixes [#256](https://github.com/fniessink/toisto/issues/256).

### Added

- Allow for specifying the meaning of concepts that have no label in a language. Closes [#138](https://github.com/fniessink/toisto/issues/138).
- Allow for adding diminutives to concepts. Closes [#240](https://github.com/fniessink/toisto/issues/240).

### Changed

- Save progress for different target languages in different files. The progress files are saved in the user's home directory as before, but now include the target language in the filename, for example `/home/user/.toisto-progress-fi.json`. Closes [#271](https://github.com/fniessink/toisto/issues/271).

## 0.8.2 - 2023-02-18

### Fixed

- Allow users to specify languages besides the built-in languages so they can use their own topic files with other languages. Fixes [#225](https://github.com/fniessink/toisto/issues/225).
- Ignore timeouts when checking the latest Toisto version with GitHub. Fixes [#226](https://github.com/fniessink/toisto/issues/226).

## 0.8.1 - 2023-02-18

### Fixed

- Provide better error messages when the configuration file is not valid. Fixes [#221](https://github.com/fniessink/toisto/issues/221).
- Make the instruction about clicking underlined words platform independent. Fixes [#222](https://github.com/fniessink/toisto/issues/222).

## 0.8.0 - 2023-02-12

### Fixed

- Fix spelling error (comparative, not comparitive). Unfortunately, this means that progress on quizzes that ask to give the comparative degree is reset.
- Remove the unnecessary word 'form' from the instructions. Fixes [#193](https://github.com/fniessink/toisto/issues/193).
- Don't assume that the readline module is installed on Windows.

### Added

- Allow for specifying the target and source language in the configuration file. Note: because this change makes the target and source language parameters optional, this changes the command-line interface. You need to use: `toisto practice --target fi --source en` instead of `toisto practice fi en` when specifying the languages on the command-line.
- Allow for practicing a specific language level with `--level {level}`. Also allow for specifying the language level in the configuration file. Closes [#186](https://github.com/fniessink/toisto/issues/186).
- Add quizzes for antonyms (opposites). Closes [#7](https://github.com/fniessink/toisto/issues/7).
- Show the language level in the output of the topics command.
- More colorful help information.
- Health topic.

## 0.7.0 - 2023-01-28

### Fixed

- Also link labels to https://en.wiktionary.org/ when the user answered incorrectly. Closes [#169](https://github.com/fniessink/toisto/issues/169).

### Added

- Allow for specifying different concept usage relations per language. Closes [#163](https://github.com/fniessink/toisto/issues/163).
- If a newer version of Toisto is available, show it on startup. Closes [#171](https://github.com/fniessink/toisto/issues/171).
- Add support for Linux and Windows. Closes [#176](https://github.com/fniessink/toisto/issues/176).
- Add [Common European Framework of Reference for Languages (CEFR)](https://www.coe.int/en/web/common-european-framework-reference-languages) levels to concepts and use them as one of the factors to determine the order in which to quiz the user.
- Added "to dress" to the clothes topic.
- Add example sentences to the colors topic.

## v0.6.1 - 2023-01-14

### Fixed

- Fix the order of quizzes so that singulars are quizzed before plurals, present tense before past tense, etc.

## v0.6.0 - 2023-01-07

### Added

- Add affirmative and negative sentence types (polarity) and quizzes to change affirmative sentence into negative sentences and vice versa. Closes [#82](https://github.com/fniessink/toisto/issues/82).
- Add topics for transport, languages, and adverbs.

## v0.5.0 - 2022-12-27

### Fixed

- Also show alternative answers if the user answers incorrectly.

### Added

- Add past tense of verbs and quizzes to change past tense into present tense and vice versa.
- Add declarative and interrogative sentence types and quizzes to change declarative sentences into interrogative sentences and vice versa. Closes [#140](https://github.com/fniessink/toisto/issues/140).
- Add a topic with interrogative pronouns (who, what, where, ...).
- Add links to https://en.wiktionary.org/ for alternative meanings as well.
- Add a command to show the contents of topics. Run `toisto topics -h` for more information.

### Changed

- Changed the command-line interface to use subcommands, to prepare for more subcommands. Type `toisto -h` for more information.

## v0.4.0 - 2022-12-14

### Fixed

- When showing the correct answer, replace removed spaces with an underscore so it is more clear what the user would have needed to type differently to enter the correct answer. Fixes [#96](https://github.com/fniessink/toisto/issues/96).
- Apostrophes were ignored when checking answers. Fixes [#97](https://github.com/fniessink/toisto/issues/97).
- Toisto would show empty strings as meaning if the quizzed concept has no label in the user's language. Fixes [#101](https://github.com/fniessink/toisto/issues/101).

### Added

- Reply with "?" to a quiz to skip to the answer immediately. Closes [#112](https://github.com/fniessink/toisto/issues/112).
- Add command line option to sort progress information by either quiz retention length or number of attempts.
- Allow for infinitive forms of verbs in topic files. Add infinitives to current verbs. Closes [#85](https://github.com/fniessink/toisto/issues/85).
- Add new concepts to the food, time, and verbs topics.
- Add body, clothes, and weather topics.

## v0.3.0 - 2022-12-04

### Added

- When languages of both question and answer are the same, give the meaning of both the question and the answer. Closes [#73](https://github.com/fniessink/toisto/issues/73).
- Also show the meaning when the answer is incorrect. Closes [#90](https://github.com/fniessink/toisto/issues/90).
- Add links to https://en.wiktionary.org/ for each word.
- Add some regular and auxiliary verbs.
- Add some colors.
- Add holiday topic.

## v0.2.1 - 2022-12-01

### Fixed

- When the quiz type is "listen and type what you hear", don't show alternative answers as that doesn't make sense for this quiz type. Fixes [#74](https://github.com/fniessink/toisto/issues/74).
- Relations between concepts were only taken into account when both concepts belonged to the same topic. Fixes [#76](https://github.com/fniessink/toisto/issues/76).

## v0.2.0 - 2022-12-01

### Removed

- Don't show how long a quiz is silenced after each correctly answered quiz. The information is not relevant while practicing and can be easily viewed using the progress command.

### Fixed

- Show hints only when translating. Fixes [#51](https://github.com/fniessink/toisto/issues/51).
- When showing the meaning of a concept, only show the first spelling variant. Fixes [#63](https://github.com/fniessink/toisto/issues/63).

### Changed

- When the user makes a mistake and the question is repeated, say the question slightly slower. Closes [#48](https://github.com/fniessink/toisto/issues/48).

### Added

- It is possible to specify usage relations between concepts in topic files. For example, the concept "days of the week" uses the concepts "day" and "week". Toisto will first quiz the user on "day" and "week" before quizzing "days of the week". Plural concepts automatically "use" singular concepts so that plural forms of concepts are quizzed before their singular form.
- When the quiz type is not "translate", as a reminder, show the meaning of the quizzed concept in the user's language after the quiz is finished. Closes [#31](https://github.com/fniessink/toisto/issues/31).
- When the user enters an empty answer, repeat the spoken question. Closes [#47](https://github.com/fniessink/toisto/issues/47).
- Add more concepts to the house and nature topics and add an animals topic.
- Use Google Translate for text-to-speech, but fall back to the MacOS say command if getting the audio from Google Translate fails.

## v0.1.0 - 2022-11-20

### Changed

- Determine the time to silence a quiz using the retention so far, instead of the streak. Unfortunately, this is a backwards incompatible change and progress information is lost.
- Silence quizzes that the user knows on the first attempt for 24 hours.

### Added

- Add more concepts to the city, family, furniture, house, nature, and time topics.

## v0.0.16 - 2022-11-14

### Fixed

- For some streak lengths, Toisto would not give the correct duration for which the quiz will be silenced.

### Added

- Show until when a quiz is silenced in the progress table.
- Add listening-only quizzes. Closes [#43](https://github.com/fniessink/toisto/issues/43).

## v0.0.15 - 2022-11-08

### Fixed

- Fix the Dutch label for "shortest" in the degrees of comparison topic.

### Added

- When selecting new quizzes for the user to answer, do so in the order of topics and order of concepts in the topic files. This makes sure the user will be quizzed on concepts and topics concepts they have already been working on, before being introduced to new concepts and topics. Closes [#32](https://github.com/fniessink/toisto/issues/32).

## v0.0.14 - 2022-11-06

### Fixed

- Answers shown in "Another correct answer is..." would include the hint.

## v0.0.13 - 2022-11-06

### Fixed

- On MacOS Ventura, the say command that Toisto uses for speech does not print the spoken text, even when told to. Work-around the issue by having Toisto print the question itself.
- The plural of one synonym should not be accepted as the plural of another synonym and vice versa. For example, kauppakeskus and ostoskeskus both mean shopping centre, but the plural of kauppakeskus, kauppakeskukset, should still not be accepted as plural for ostoskeskus and vice versa. Fixes [#13](https://github.com/fniessink/toisto/issues/13).

### Added

- Added more words and sentences to the days, time, family, and greetings topics.
- Allow for specifying hints, for example to tell users to interpret "You are" as either singular or plural.

### Changed

- To not overwhelm the user with new quizzes, give preference to quizzes the user has seen before when selecting the next quiz.

## v0.0.12 - 2022-10-30

### Added

- Added a nature topic.
- Added shopping center to the city topic.
- Added quizzes for degrees of comparison and a topic with degrees of comparison.
- Added quizzes for grammatical person (first, second, and third person) and a topic with the verbs "to be" and "to have".

## v0.0.11 - 2022-10-27

### Added

- When concepts have female and male versions add quizzes for changing the words into the opposite gender (daughter-son, father-mother, etc.).

## v0.0.10 - 2022-10-25

### Added

- Added a possessive adjectives topic (my cat, your house, their cats, etc.).

## v0.0.9 - 2022-10-25

### Fixed

- Fixed typo in bibliotheken (city topic).

## v0.0.8 - 2022-10-23

- Added more phrases to the greetings topic.
- Added a city topic.

## v0.0.7 - 2022-10-21

### Fixed

- The food topic wouldn't work with languages other than Finnish.

## v0.0.6 - 2022-10-21

### Changed

- Renamed decks to topics. This also means the command line interface option `-d/--deck` was renamed to `-t/--topic`.

### Added

- Added a food topic.
- In addition to using built-in topic files, allow the user to load their own local topic files, using the command line interface option `--topic-file`.

## v0.0.5 - 2022-10-18

### Added

- Add English as supported language.

## v0.0.4 - 2022-10-17

### Fixed

- Toisto did not start because the rich library was not bundled.

## v0.0.3 - 2022-10-17

### Added

- Added decks with words related to furniture and houses.
- Add command to show progress (`toisto {language} progress`).
- When the user translates a word correctly and there are multiple correct translations, also show the other translations.
- When words have a singular and plural version add quizzes for pluralizing and singularizing the words.
- When the user answers incorrectly, give them a chance to correct typo's.

## v0.0.2 - 2022-10-10

### Added

- Added a deck with colors and a deck with family related words.
- Added command line options for help, version, and specifying decks to use. Run `toisto -h` to see the help information.
- Entries in decks can have multiple answers.
- When the user translates words correctly multiple times in a row, silence the word for a while. The more often a word is correctly translated, the longer it is silenced.

### Fixed

- Some words in the decks included invisible white space, causing Toisto to never see the user's input as correct.

## v0.0.1 - 2022-10-05

- Initial version.
