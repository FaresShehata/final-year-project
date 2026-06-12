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
import sys
import types
import weakref


class Byte(enum.IntEnum):
    """
    A class for representing byte values.
    """

    MIN = -128
    MAX = 127

    def __str__(self) -> str:
        return f"{self.name}:{self.value}"

    # def __repr__(self) -> str:
    #     return f"Byte({int(self)})"

    @classmethod
    def from_str(cls, s: str) -> Byte:
        match cls.__members__.get(s.upper()):
            case None | Byte.MIN | Byte.MAX:
                raise ValueError(f"'{s}' is not a valid {cls.__name__}")
            case other:
                return other

    @classmethod
    def get_min_max(cls):
        """
        Returns the minimum and maximum values of a given enum type.
        :return: tuple[min_value, max_value]
        """
        return (min(x.value for x in cls), max(x.value for x in cls))

    def __lt__(self, other: "Byte"):
        if isinstance(other, int):
            return self.value < other
        else:
            return self.value < other.value


def get_byte():
    return Byte.from_str(random.choice(list(Byte.__members__)))


# ---------------------------------------------------------


@dataclasses.dataclass(slots=True)
class Node:
    val: float

    def __post_init__(self):
        pass

    def __hash__(self):
        return hash((type(self), self.val))


def sort_nodes(nodes: list[Node]) -> list[Node]:
    return sorted(nodes, key=lambda n: n.val)

def main():
    nodes = [Node(get_byte()) for _ in range(5)]
    print("Unsorted", nodes)
    print("Sorted", sort_nodes(nodes))


if __name__ == "__main__":
    main()