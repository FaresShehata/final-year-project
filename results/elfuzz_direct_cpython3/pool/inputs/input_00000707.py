"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""
from typing import Any

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int = 1
    y: float | None = None
    z: bool = False
    a_float: float = 3.456

    @property
    def coords(self) -> tuple[int, float]:
        return self.x, self.y or self.a_float

    @classmethod
    def from_dict(cls, dct: dict[str, Any]) -> "Point":
        """Create an instance of Point by using dictionary."""
        return cls(**dct)


def main() -> None:

    print("Structural Pattern Matching")
    match (True):
        case True:
            pass
        case _:
            pass

    point = Point()
    print(point.coords)

    print("\nWalrus Operator")
    if (
        name := input("Enter your name: ")
    ):  # the walrus operator is used to assign something in conditionals.
        print(f"Hello {name}")

    print("\nProtocols")
    class MyProtocol:
        ...

    class MyClass:
        protocol: MyProtocol

    my_class = MyClass()
    my_class.protocol = MyProtocol()

    print("\ndataclasses")
    Point.from_dict({"x": 1, "y": 2})
    Point.from_dict({"x": 1})  # will raise error because y has no default value.

    print("\ndataclass slots")
    Point.__slots__ = ("x", "a_float")

    try:
        Point(a_float=9)  # this will raise TypeError since "a_float" cannot be set outside constructor.
    except TypeError as e:
        print(e)

    print("\nasyncio await and coroutines")
    async def say_hello():  # this is a coroutine function
        print("hi")
        await asyncio.sleep(1)  # this is an awaitable object which can be awaited.
        print("bye")

    loop = asyncio.get_event_loop()  # get a reference to event loop.
    future = asyncio.ensure_future(say_hello())  # create a Future object with said coroutine.
    loop.run_until_complete(future)  # run until we receive the result.
    loop.close()


if __name__ == "__main__":
    main()