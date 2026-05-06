# The Meta Language (TML)

## Overview

The Meta Language (TML) is a flexible metalanguage system designed to allow users to define and interpret their own custom programming and domain-specific languages.

This project demonstrates how a single system can support multiple languages, each with its own syntax and behavior, by using configurable grammar and interpreter logic.

---

## Purpose & Philosophy

TML was created to explore how programming languages can be abstracted and generated from a higher-level system.

**Goals:**

* Allow rapid creation of new languages
* Keep syntax simple and readable
* Support multiple domains (configuration, scripting, game logic)
* Demonstrate how interpreters and parsers work

---

## Language Style

TML-based languages are:

* Text-based
* Rule-driven
* Interpreted (not compiled)
* Designed for readability and flexibility

Each language is defined using `.tml` configuration files and executed through Python interpreters.

---

## Interpreters

This project includes multiple interpreters:

* `main.py` → Core TML interpreter for `.mtml` programs
* `questlang_interpreter.py` → Interpreter for QuestLang (game scripting language)
* `minitml_interpreter.py` → Lightweight interpreter for simplified TML programs

---

## Programs Included

### Simple Programs

1. `hello_world.mtml`

   * Prints a basic message

2. `simple_program.mtml`

   * Demonstrates basic syntax and execution

3. `basic_logic.mtml`

   * Shows simple logic or control flow

---

### Complex Programs

4. `complex.mtml`

   * Demonstrates advanced language features

5. `cryptwalker.quest`

   * A QuestLang game script demonstrating domain-specific language design

---

### Required Program

6. `fizzbuzz.mtml`

   * Classic FizzBuzz implementation using TML

---

## How to Run

Make sure you have **Python 3 installed**.

### Run TML Programs

```bash
python main.py hello_world.mtml
python main.py fizzbuzz.mtml
python main.py complex.mtml
```

### Run Quest Language Program

```bash
python questlang_interpreter.py cryptwalker.quest
```

### Run MiniTML Programs

```bash
python minitml_interpreter.py example.mtml
```

---

## Example Output

### Hello World

```
Hello, World!
```

### FizzBuzz

```
1
2
Fizz
4
Buzz
...
```

---

## Demonstration

All programs have been tested locally and run successfully using the provided interpreters.

---

## Website & Source Code

**Live Website:**
(coming soon)

**GitHub Repository:**
https://github.com/VictorPartain/TheMetaLanguage

---

## Presentation Summary

This project includes:

* A custom metalanguage (TML)
* Multiple interpreters
* Six working programs (including FizzBuzz)
* A simple website (in progress)
* A presentation explaining design and functionality

---

## Bonus Features

* Multiple language support within one system
* Domain-specific language (QuestLang)
* Modular interpreter design
* Expandable architecture for future languages

---

## Author

Victor Partain, Matthew Aquino
