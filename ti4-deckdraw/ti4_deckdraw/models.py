from dataclasses import dataclass
from enum import Enum


class DeckEnum(str, Enum):
    """An enum to represent the two decks."""

    FRONTIER = "frontier"
    RELIC = "relic"


@dataclass
class Card:
    """A dataclass to represent a card with a title and description."""

    title: str
    description: str
