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
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────
class Codigo(enum.Enum):
    """
    Enum para representar distintos códigos de error.

    Cada enumeración representa un código de error específico, como el número de línea o la posición del error.
    """

    linea = "linea"
    columna = "columna"


class Error(Exception):
    """
    Clase base para errores personalizados.

    Esta clase define los atributos `codigo` y `mensaje`, que se utilizan para almacenar información sobre el tipo de error y su descripción respectiva.
    """

    codigo: str | None
    mensaje: str | None


@runtime_checkable
class LineException(Protocol[T]):
    """Protocolo para manejar excepciones relacionadas con líneas."""

    def __call__(self, line_number: int, message: str) -> T:
        ...


ErrorLine = LineException[Error]


def raise_error_line(line_number: int, message: str) -> ErrorLine:
    return Error(
        codigo=Codigo.linea.value,
        mensaje=f"Línea {line_number}: {message}",
    )


# ─── Dataclasses ─────────────────────────────────────────────────────────────
@dataclasses.dataclass(slots=True)
class Person:
    name: str
    age: int
    address: str


person1 = Person(name="John Doe", age=30, address="123 Main St.")
person2 = dataclasses.replace(person1, address="456 Elm St.")


# ── Async/Await ──────────────────────────────────────────────────────────────
async def main() -> None:
    print("Hello, World!")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())


# ─── Generics ────────────────────────────────────────────────────────────────
def sort_by_index(lst: list[list[int]]) -> list:
    return sorted(lst, key=lambda x: x[-1])


lst = [[1, 2], [3, 4], [5, 6]]
print(sort_by_index(lst))


# ─── Walrus Operator ─────────────────────────────────────────────────────────
var = (x := 5)
print(x)


# ─── Structural Pattern Matching ──────────────────────────────────────────────
match x:
    case 0:
        return 42
    case _ if not isinstance(x, int):
        raise ValueError("Not an integer!")
    case _ if x <Ejercicio 2.4¶
Escribir un programa que almacene en una lista los siguientes precios, 50, 75, 46, 22, 80, 65, 8 (se puede usar input) y muestre por pantalla el menor y el mayor de los precios.
"""

precios = [50, 75, 46, 22, 80, 65, 8]
print(f"El precio más bajo es: {min(precios)}")
print(f"El precio más alto es: {max(precios)}")