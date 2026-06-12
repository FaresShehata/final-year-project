"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import dataclasses
import datetime
import random
import time
from functools import partial
from itertools import count
from typing import Any, Generic, Protocol, TypeVar, Union


T = TypeVar("T")

<|file_sep|><|fim_prefix|>/tutorial/seed_03.py
#!/usr/bin/env python3
"""Tutorial for the Python Standard Library.

This tutorial is a collection of simple examples that illustrate some common
tasks and best practices when using the standard library in Python. Most of
these are not specific to Django or any of its features.
"""


# ── Collections ────────────────────────────────────────────────────────────────

# A simple dictionary example.
dictionary_example()

# A more complex example with nested dictionaries and lists.
nested_dictionary_example()


# ── Logging ──────────────────────────────────────────────────────────────────

# Simple logging example.
logging_example()

# Logging example with custom formatters.
logging_custom_formatters_example()


# ── Time and Dates ────────────────────────────────────────────────────────────

# Example showing how to use the `time` module to measure execution time.
measure_time_and_date_example()
sleep_example()


# ── Functions ─────────────────────────────────────────────────────────────────

# Example showing how to use decorators to add functionality to functions.
function_decorator_example()


# ── Classes ───────────────────────────────────────────────────────────────────

# Example showing how to use classes as factories for objects.
factory_functions_example()

# Example showing how to use metaclasses to create classes dynamically.
dynamic_class_creation_example()


# ── Context managers ───────────────────────────────────────────────────────────

# Example showing how to use context managers to manage resources.
context_managers_example()

# Example showing how to use context managers to wrap code blocks.
with_statement_example()


# ── Exceptions ────────────────────────────────────────────────────────────────

# Example showing how to use exceptions to handle errors.
exceptions_example()


# ── Decorators ────────────────────────────────────────────────────────────────

# Example showing how to define decorators that can be used to modify function behavior.
decorator_example()


# ── Generators ─────────────────────────────────────────────────────────────────

# Example showing how to use generators to produce sequences of values.
generator_exa<|fim_suffix|> ───────────────────────────────────────────────────────────────────────
mple()


# ── Iterables and Iterators ───────────────────────────────────────────────────-

# Example showing how to use iterators to iterate over collections.
iterable_iterator_example()

# Example showing how to use generators to create iterable objects.
generators_example()


# ── File I/O ─────────────────────────────────────────────────────────────────-

# Example showing how to read from files and write to files.
file_io_example()


# ── Typing ────────────────────────────────────────────────────────────────────

# Example showing how to use type hints to describe the types of parameters and return values.
type_hints_example()

# ── Structural Pattern Matching ────────────────────────────────────────────────

