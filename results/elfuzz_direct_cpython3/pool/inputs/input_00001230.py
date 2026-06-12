"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations
import asyncio
import collections.abc as abc
import dataclasses
import json
import logging

logging.basicConfig(level=logging.INFO)


@dataclasses.dataclass(frozen=True)
class Coordinates:
    latitude: float = dataclasses.field()
    longitude: float = dataclasses.field()


def create_coordinates(latitude: float, longitude: float) -> Coordinates:
    return Coordinates(latitude, longitude)


async def main() -> None:
    """ Try to catch and log exceptions """

    try:
        await asyncio.sleep(1 / 4_000_000_000)
    except KeyboardInterrupt:
        print("Got a KeyboardInterrupt")
        raise


if __name__ == "__main__":
    asyncio.run(main())