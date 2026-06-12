"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

# import asyncio
import sys

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Person:
    name: str = 'John Doe'
    age: int = 30


def main() -> None:

    # Async Await
    print("\n\nAsync/Await")
    async def print_hello():
        await asyncio.sleep(1)
        return "Hello"

    async def run_tasks(tasks):
        for task in tasks:
            result = await task
            print(result)

    # To run an async function we need to use the event loop
    loop = asyncio.get_event_loop()
    tasks = [print_hello(), print_hello()]
    loop.run_until_complete(run_tasks(tasks))

    # Protocol
    print("\n\nProtocol")
    class IStringConvertible:
        def to_string(self):
            raise NotImplementedError()

    @dataclass(slots=True)
    class String(IStringConvertible):
        value: str

        def to_string(self):
            return self.value.upper()

    @dataclass(slots=True)
    class ImmutableString(String):
        pass

    strings = [String("hello"), ImmutableString("world")]
    for string in strings:
        print(string.to_string())

    # Dataclasses
    print("\n\nDataclasses")
    new_person = Person(name="Jane Smith", age=45)
    print(new_person)

    # Slots
    print("\n\nSlots")
    person = Person()
    setattr(person, "age", 67)
    print(person.age)

    # Structural Pattern Matching
    print("\n\nStructural Pattern Matching")
    match_value = {"name": "Alice", "age": 30}
    match match_value:
        case {"name": name, "age": age} if isinstance(age, int):
            print(f"Name: {name}, Age: {age}")
        case _:
            print("Invalid data")

    # Walrus Operator
    print("\n\nWalrus Operator")
    x = (y := 10)
    print(x)

    y += 5
    print(y)

    # Generics
    print("\n\nGenerics")
    from typing import TypeVar
    T = TypeVar('T')

    class Queue:
        """FIFO queue implementation using a Python list as underlying storage."""
        DEFAULT_CAPACITY = 10
        
        def __init__(self) -> None:
            """Create an empty queue."""