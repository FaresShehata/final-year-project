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
    i = 0
    while len(cards) > 0:
        for idx in range(hand_size):
            if len(cards) > i:
                hands[idx].append(cards[i])
                del cards[i]
        i += 1
    return hands


async def main():
    """Main entry point."""
    with open("seed_01.json", encoding="utf-8") as file:
        suits: dict[str, list[int]] = {
            suit.name.lower(): [value for (_, value) in enumerate(suits[suit])]
            for suit, suits in json.load(file).items()
        }

    ranks = sorted(
        (rank, rank_value) for rank, rank_values in suits.items() for rank_value in rank_values
    )
    cards: list[Card] = [
        Card(rank, suit)
        for rank, rank_values in suits.items()
        for suit, ranks in zip(ranks, rank_values)
    ]

    print("\nCards:")
    hands = play_cards(cards, 3)
    print("\nHands:")
    for hand in hands:
        for card in hand:
            print(f"\t{card}")
        print()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())