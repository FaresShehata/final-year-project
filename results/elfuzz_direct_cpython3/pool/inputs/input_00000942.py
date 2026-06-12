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
async def open_connection(host='localhost', port=80):
    connection = Connection()
    try:
        yield connection
    finally:
        connection.close()


class Connection:
    def close(self):
        pass


class Table(NamedTuple):
    name: str
    rows: int


def table_exists(name: str) -> bool:
    for table in tables:
        if table.name == name:
            return True
    else:
        return False


tables = []


async def drop_table(name: str):
    if table_exists(name):
        # do stuff
        tables.remove(Table(name, len(tables)))
    else:
        raise ValueError(f'table "{name}" does not exist')


async def create_table(name: str):
    if not table_exists(name):
        # do stuff
        tables.append(Table(name, len(tables)))
    else:
        raise ValueError(f'table "{name}" already exists')


async def insert_row(table_name: str, *args):
    if not table_exists(table_name):
        raise ValueError(f'no such table "{table_name}"')

    row_num = len(rows)
    row = [None] * len(fields)
    for i, value in enumerate(args):
        row[i] = value
    rows[row_num] = tuple(row)
    

fields = []
rows = []

async def select_all_rows(field_names: list[str]):
    for row in rows:
        values = []
        for field_name in field_names:
            i = fields.index(field_name)
            values.append(row[i])
            
        yield tuple(values)



create_table('tbl_1')
drop_table('does_not_exist')

with open_connection() as conn:  # Context managers are also coroutines!
    await create_table("test1")
    await insert_row("test1", 1, 'Hello World!')
    await insert_row("test1", 2, 'Goodbye cruel world!')
    async for row in select_all_rows(["row_id", "message"]):
        assert row[0] == 1
        assert row[1] == 'Hello World!'
        break

async with open_connection() as conn:  # Use the `async` keyword when calling an `async` method.
    await create_table("test2")
    await insert_row("test2", 1, 'one', 2, 'two', 3, 'three')  
    await insert_row("test2", 11, 'eleven', 21, 'twenty-one', 31, 'thirty-one')
    async for row in select_all_rows(['row_id', 'field1', 'field3']):
        assert row[0] == 1
        assert row[1] == 'one'
        assert row[2] == 'three'
        break
        
async with open_connection() as conn:  # Use the `async` keyword when calling an `async` method.
    await create_table("test3")
    await insert_row("test3", 1, 'one', 2, 'two', 3, 'three')  
    await insert_row("test3", 11, 'eleven', 21, 'twenty-one', 31, 'thirty-one')
    
    async for row in select_all_rows(["field3", "field1", "row_id"]):
        assert row[0] == 'three'
       import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __get__(self, instance: T, owner: Optional[type[T]] = None) -> Any:
        return getattr(instance.__dict__, self.name, None)

    def __set__(self, instance: T, value: Any) -> None:
        self.validate(value)
        setattr(instance, self.name, value)

    def validate(self, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f'{value} is not of type {self.expected_type}')
        
        if self.lo is not None and value < self.lo:
            raise ValueError(f'{value} is less than minimum allowed value {self.lo}')
        
        if self.hi is not None and value > self.hi:
            raise ValueError(f'{value} is greater than maximum allowed value {self.hi}')


class CheesShop:
    _stock: dict = {}
    cheese_price: float = 1.99
    min_cheese_stock_level: int = 10 
    max_cheese_stock_level: int = 20
    
    @property
    def stock(self):
        return self._stock
    
    @stock.setter
    def stock(self, value):
        self.validate_stock_value(value)
        self._stock = value
    
    def validate_stock_value(self, value):
        super().validate_stock_value(value)
        if self.min_cheese_stock_level > value or value > self.max_cheese_stock_level:
            raise ValueError(
                f'Stock must be between {self.min_cheese_stock_level}'
                f'and {self.max_cheese_stock_level}.'
            )
        
        
shop = CheesShop()
shop.stock = {'cheddar': 4, 'swiss': 6}
assert shop.stock == {'cheddar': 4, 'swiss': 6}

shop.stock = {'cheddar': 6, 'swiss': 7}
try:
    shop.stock = {'cheddar': -1, 'swiss': 7}
except Exception as e:
    print(e)
    
shop.stock = {'cheddar': 10, 'swiss': 20}
try:
    shop.stock = {'cheddar': 10, 'swiss': 21}
except Exception as e:
    print(e)
    
    
# ── Meta classes ─────────────────────────────────────────────────────────────

# ❓ Why would you ever use a metaclass?

class SubmetaClass