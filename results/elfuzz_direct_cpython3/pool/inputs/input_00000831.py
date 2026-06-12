"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining, etc.
"""

import asyncio
from contextlib import asynccontextmanager
import re
import sys
from typing import List, Literal, NamedTuple, Optional, Tuple, TypeAlias, Union, get_args

sys.setrecursionlimit(500)

re.match(r"^(.+)(\d+)$", "hello")


@asynccontextmanager
async def context_manager():
    try:
        yield
    finally:
        print("Done!")


# https://docs.python.org/3/howto/functional.html?highlight=closure#closures
def func_closure():
    x = [1]
    def inner():
        x.append(2)
        return x[0]
    return inner


class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data) # kwargs unpacking
    
    
person_1 = Person('John', 28)
print(person_1.__dict__)

person_data = {"name": "Jane", "age": 45}
person_2 = Person.from_dict(person_data)
print(person_2.__dict__)


# @staticmethod vs. @classmethod
# Static methods don't receive instance as the first argument that's why they are useful when you want to
# you can access class attributes but not instance attributes.

class MyClass:

    @staticmethod
    def static_method(x):
        return x + 1

    @classmethod
    def class_method(cls, y):
        return cls.static_method(y)


MyClass().static_method(1)   # returns 2
MyClass().class_method(1)    # returns 2


# docstring
def my_function(param: int) -> None:
    """
    This is a function description.
    :param param: some integer parameter
    :type param: int
    """
    pass
help(my_function)


# type hinting
my_list: list[int] = []
my_tuple: tuple[str, ...] = ('Hello', 'World')
my_set: set[int] = {1}
my_dictionary: dict[str, int] = {'a': 1}


# assert
assert isinstance(1, int)
assert isinstance([1], list)


# unbound method
def foo(self=None, arg=None):
    if self is not None:
        # do something with `self`
        ...
    else:
        # use the default value of `arg` here
        ...

foo()
foo(arg=2)


if True:
    print("True")
else:
    print("False")

x = 1 if True else 0
y = 0 if False else 1

#