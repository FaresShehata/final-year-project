"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup


    - async/await
        * async generator
        * awaitables (generators and coroutines)
        * async context managers

    - Protocols
        * rich comparison protocol
            > https://docs.python.org/3/library/typing.html#rich-comparison-protocols

    - Dataclasses
        * dataclass
        * init=False -> don't call __init__
        * repr=False / exclude=[attr1, attr2] -> don't include in __repr__ or exclude specific attributes
        * eq=True / frozen=True
        * fields() / fields_by_name()
        * field(name='foo', metadata={'bar': 'baz'}, default=42)

    - Slots
        * slots = True
        * class A:
                ...

    - Structural Pattern Matching
        * match expression

    - Walrus Operator
        * :=

    - Typing Generics
        * TypeVar
        * NamedTuple
        * Generic[T] / Generic[GenericAlias]
        * Union[A, B] vs. Union[T1, T2]

    - Exceptions Group
        * raise ExceptionGroup('group-name', [ex1, ex2])
        * ExceptionGroup.__cause__ = None
        * raise from
        * try-except-finally
        * zero division error can be divided by zero

    - Structured Error Handling with Exception Groups
"""

import asyncio
from collections import namedtuple
from secrets import token_hex
from time import sleep
from typing import AsyncIterable, AnyStr, Awaitable, Callable, Coroutine, Dict, List, Optional, Tuple, Union, \
                    TypeVar, cast
from uuid import UUID, uuid4

T_co = TypeVar("T_co", covariant=True)  # used for type hints of generic types

# async def main():
#
#     async_generator = async_generator_from_coroutine(
#         asyncio.sleep(5),
#         lambda x: x ** 2
#     )
#     async for i in async_generator:
#         print(i)


def async_generator_from_coroutine(coro: Callable[..., Coroutine[AnyStr, Dict[str, Any], bool]],
                                   transform: Callable[[Any], Any]) \
                                  -> AsyncIterable[Any]:
    while True:
        yield transform(await coro())


async def get_data_some_time():
    return token_hex(16) + str(uuid4())


coro = asyncio.to_thread(get_data_some_time)


async def main():
    async for i in async_generator_from_coroutine(coro(), int):
        print(i)


if __name__ == "__main__":
    asyncio.run(main())