"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
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
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""
    
    def __init__(self, func: Callable[[Self], T]) -> None:
        assert callable(func)
        
        self.func = func
        self.cache: WeakKeyDictionary[Object, T] = {}
        self.name: str = ""
    
    # noinspection PyAttributeOutsideInit
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"
    
    def __get__(self, instance: Object, owner: type) -> T:
        if instance is None:
            return self
        
        try:
            return self.cache.get(instance, None)
            
        except KeyError as e:
            result = self.func(instance)
            self.cache[e.value] = result
            return result


# ─── Context Managers ────────────────────────────────────────────────────────

@contextlib.contextmanager
def append_list(l: list[Any]) -> Iterator[list[Any]]:
    l.append(sys.exc_info())
    yield l
    del l[-1]


with append_list([]) as l:
    print(l)
    x = 1 / 0
    
    print(l)
    

@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


class SuppressOutputManager:
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_stdout_output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.old_stdout
        return False


with SuppressOutputManager() as s:
    print(s)
    x = 1 / 0
    

class SuppressOutputContext(ContextDecorator):
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_stdout_output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.old_stdout
        return False

 
SOMETHING_TO_SUPPRESS_OUTPUT_INTO = object()


class SuppressOutput(SuppressOutputContext):
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self.old_stdout

        if SOMETHING_TO_SUPPRESS_OUTPUT_INTO in locals():
            locals()[SOMETHING_TO_SUPPRESS_OUTPUT_INTO].append(output)
        else:
            print(output)
        

def do_nothing(*args, **kwargs) -> int:
    pass
    

do_nothing()

SuppressOutput[SOMETHING_TO_SUPPRESS_OUTPUT_INTO] = []



@functools.lru_cache(maxsize=100)
def fibonacci(nEjercicio 2.4¶
Escribir un programa que almacene en una lista los siguientes precios, 50, 75, 46, 22, 80, 65, 8 (se puede usar input) y muestre por pantalla el menor y el mayor de los precios.
"""

precios = [50, 75, 46, 22, 80, 65, 8]
print(f"El precio más bajo es: {min(precios)}")
print(f"El precio más alto es: {max(precios)}")

"""
Ejercicio 2.13
Realizar un programa donde se solicite ingresar un número entero positivo. La función debe retornar True si dicho número es primo o False en caso contrario.

NOTA: Un número primo es aquel que solo es divisible entre sí mismo y la unidad
"""