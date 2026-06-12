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
import typing
from collections.abc import AsyncIterable, Callable, Coroutine, Iterator
from contextlib import suppress


class Suit(enum.Enum):
    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"


@dataclasses.dataclass(init=False)
class Card:
    rank: int
    suit: Suit

    def __init__(self, rank: int, suit: Suit):
        self.rank = rank
        self.suit = suit

    @property
    def value(self) -> str:
        return f"{self.rank}{self.suit.value}"

    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return (
            self.rank == other.rank and self.suit == other.suit
        )  # TODO: this should be better

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))


def play_cards(cards: list[Card], hand_size: int) -> list[list[Card]]:
    """Play the cards from a given deck."""
    hands = [[] for _ in range(hand_size)]
    for card in cards:
        i = len(hands)
        while i > 1 and sum(len(x) for x in hands[:i]) >= hand_size - 1:
            i -= 1
        hands[i].append(card)

    return [sorted(lst, key=lambda c: (c.suit, c.rank)) for lst in hands]


async def main() -> None:
    suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
    ranks = [*range(2, 15)] * 4
    random.shuffle(ranks)
    cards = [Card(rank, suit) for rank in ranks for suit in suits]

    print("Cards:")
    for card in cards:
        print(f"\t{card}")

    hands = play_cards(cards, 3)
    print("\nHands:")
    for hand in hands:
        for card in hand:
            print(f"\t{card}")
        print()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())