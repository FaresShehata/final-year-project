"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (TYPE_CHECKING, Any, Callable, Dict, Generic, List, NamedTuple, Optional, Protocol, Sequence, Tuple,
                    TypeVar, Union)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec # noqa: F401


class ExampleEnum(enum.Enum):
    A = 'a'
    B = 'b'
    C = 'c'


@dataclasses.dataclass(frozen=True)
class DataClassExample():
    foo: str
    bar: int
    baz: float
    qux: bool


def example_dataclass_function(data_class_instance) -> None:
    data_class_instance.baz *= 3.5
    print(f'foo={data_class_instance.foo}, bar={data_class_instance.bar}, '
            f'baz={data_class_instance.baz}, qux={data_class_instance.qux}')


async def example_async_function(data_class_instance) -> None:
    await asyncio.sleep(random.randint(0, 9))
    data_class_instance.bar += 7
    print(f'foo={data_class_instance.foo}, bar={data_class_instance.bar}, '
            f'baz={data_class_instance.baz}, qux={data_class_instance.qux}')

    
T = TypeVar('T')


# https://stackoverflow.com/a/69881482
P = ParamSpec('P') 
R = TypeVar('R', covariant=True)
def curried(func: Callable[P, R]) -> Callable[[P], R]:
    if not isinstance(func, Callable): raise TypeError()
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper

# https://docs.python.org/3/library/typing.html#typing.Generic
class MyGeneric(Generic[T]):
    pass
    
    
# https://www.geeksforgeeks.org/python-structural-pattern-matching/
class Match(NamedTuple):
    case: Any
    value: Any
    

def match(value: Any) -> Match:
    # code to determine which case is met with `value`
    return Match(case=... or ... or ..., value=value)

    

def main():

    # https://docs.python.org/3/library/asyncio-task.html
    print('--- Asynchronous functions and coroutines ---\n')
    print('--- Example sync function ---\n')
    instance_a = DataClassExample(foo='a', bar=-1, baz=0.0, qux=False)
    print(instance_a)
    print(f'instance_a.foo: {instance_a.foo}')
    print(f'instance_a.bar: {instance_a.bar}')
    print(f'instance_a.baz: {instance_a.baz}')
    print(f'instance_a.qux: {instance_a.qux}')
    print('\n--- Example async function ---\n')
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.create_task(example_async_function(DataClassExample(foo='d',    
    
    print('\n--- Awaitable tasks ---\n')
    for task in tasks:
        print(f'{type(task).__name__}({repr(task.__defaults__)})')

    print('\n=== Running the tasks ===\n')
    tasks_names = [str(type(t).__name__).replace('_', ' ').capitalize().strip() for t in tasks]
    tasks_start_time = [time.time()] * len(tasks)
    tasks_result = []
    total_elapsed_time = 0
    
    while True:
        elapsed_time = time.time() - tasks_start_time.pop(0)
        total_elapsed_time +=