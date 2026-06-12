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
    

def func_with_default_args(arg1=1, arg2=int()):
    pass


def main():
    
    awaitable_example()
    protocols_example()
    
    example_data_classes()


# Awaitables -------------------------------------------------------------

async def wait_for(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def get_random_number(min_num: float, max_num: float) -> float:
    return random.uniform(min_num, max_num)
    

async def make_random_numbers(max_count: int) -> List[float]:
    numbers: List[float] = []
    for _ in range(max_count):
        number = await get_random_number(1.0, 10.0)
        numbers.append(number)
    return numbers
    

def awaitable_example() -> None:
    print('Awaitable example...')
    
    start_time = time.time()

    count = sum([num // 3 for num in await make_random_numbers(5_000)])
    print(count)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f'Execution time: {elapsed_time:.6f} seconds.')
    
    
# Protocols ---------------------------------------------------------------

T = TypeVar('T')
P = ParamSpec('P')
R = TypeVar('R')


class BaseProtocol(Generic[T], Protocol[P]): 
    """Base protocol implementation""" 
    
    def transform(self, value: T) -> R: ... 


class TransformingProtocol(BaseProtocol[int]):
    """Transforms an integer into a string by adding the word 'transformed!' to it.""" 

    def transform(self, value: int) -> str:
        if not isinstance(value, int):
            raise TypeError("Argument must be of type int.")
        return f'{value} transformed!'
    

class StringTransformer(TransformingProtocol[str]):
    """String transformer that implements the transforming protocol."""

    def transform(self, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("Argument must be of type str.")
        
        return f'Transformed string: {value}'
        

def protocols_example() -> None:
    print('\nProtocols example...')

    example_protocol = TransformingProtocol[int]
    assert isinstance(example_protocol, TransformingProtocol)
    assert issubclass(TransformingProtocol, BaseProtocol)
    assert issubclass(BaseProtocol, Generic[example_protocol])

    try:
        non_existent_instance = TransformingProtocol['str']()
        print(non_existent_instance.transform('Hello'))
    except TypeError as ex:
        print(ex)
        

# Data classes ------------------------------------------------------------

def example_data_classes() -> None:
    print('\nData Classes example...')
    
    class Person(dataclasses.dataclass):
        name: str
        age: int
        
    john = Person(name='John', age=30)
    mary = Person(age=25, name='Mary')
    print(john == mary)
     