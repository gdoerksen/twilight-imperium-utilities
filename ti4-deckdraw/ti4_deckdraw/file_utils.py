import csv
import json
import random

from pathlib import Path

from .models import Card, DeckEnum

# Data Paths
PROJECT_ROOT = Path(__file__).parent
DATA_PATH = PROJECT_ROOT / "data"
CACHE_PATH = PROJECT_ROOT / ".cache"
FRONTIER_SOURCE = DATA_PATH / "frontier_source.json"
FRONTIER_REMOVED = CACHE_PATH / "frontier_removed.csv"
RELIC_SOURCE = DATA_PATH / "relics_source.json"
RELIC_REMOVED = CACHE_PATH / "relics_removed.csv"


def convert_csv_to_json(source_file: Path, dest_file: Path):
    """Convert the csv file to a json file."""
    deck: list[dict] = []
    with source_file.open() as f:
        reader = csv.DictReader(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for row in reader:
            deck.append(
                {
                    "Card": row["Card"],
                    "Effect": row["Effect"],
                    "Number in Deck": int(row["Number in Deck"]),
                }
            )

    with dest_file.open("w") as f:
        json.dump(deck, f, indent=4)


# TODO wrap all the functions we care about using this nice wrapper as the interface
def enum_wrapper(deckname: DeckEnum, func):
    """Wrapper for the deck enum."""
    match deckname:
        case DeckEnum.FRONTIER:
            func(Path(FRONTIER_SOURCE), Path(FRONTIER_REMOVED))
        case DeckEnum.RELIC:
            func(Path(RELIC_SOURCE), Path(RELIC_REMOVED))
        case _:
            raise ValueError(f"Invalid deck: {deckname}")


def load_deck_source_csv(source_file: Path) -> list[Card]:
    """Load the deck from the source csv file."""
    deck: list[Card] = []
    with source_file.open() as f:
        reader = csv.DictReader(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for row in reader:
            for _ in range(int(row["Number in Deck"])):
                deck.append(Card(title=row["Card"], description=row["Effect"]))

    return deck


def load_deck_source_json(source_file: Path) -> list[Card]:
    """Load the deck from the source json file."""
    deck: list[Card] = []
    with source_file.open() as f:
        data = json.load(f)
        for card in data:
            for _ in range(card["Number in Deck"]):
                deck.append(Card(title=card["Card"], description=card["Effect"]))

    return deck


def load_deck_source_enum(deckname: DeckEnum) -> list[Card]:
    """Load the deck from the source file."""
    match deckname:
        case DeckEnum.FRONTIER:
            deck = load_deck_source_json(Path(FRONTIER_SOURCE))
        case DeckEnum.RELIC:
            deck = load_deck_source_json(Path(RELIC_SOURCE))
        case _:
            raise ValueError(f"Invalid deck: {deckname}")

    return deck


def load_removed_deck(removed_file: Path) -> list[str]:
    """Load the removed deck from the removed file."""
    removed_deck = []

    if not removed_file.exists():
        removed_file.touch()
        return removed_deck

    with removed_file.open() as f:
        for line in f:
            removed_deck.append(line.strip())
    return removed_deck


def load_removed_deck_enum(deckname: DeckEnum) -> list[str]:
    """Load the removed deck from the removed file."""
    match deckname:
        case DeckEnum.FRONTIER:
            removed_deck = load_removed_deck(Path(FRONTIER_REMOVED))
        case DeckEnum.RELIC:
            removed_deck = load_removed_deck(Path(RELIC_REMOVED))
        case _:
            raise ValueError(f"Invalid deck: {deckname}")

    return removed_deck


def load_removed_as_history(deckname: DeckEnum) -> list[Card]:
    """Load the removed deck from the removed file as a list of cards."""
    removed_deck = load_removed_deck_enum(deckname)
    deck = load_deck_source_enum(deckname)

    return [card for card in deck if card.title in removed_deck]


def load_deck(source_file: Path, removed_file: Path) -> list[Card]:
    """Load the deck from the source file and remove the cards in the removed file."""
    # Load the source file as a list
    deck = load_deck_source_json(source_file)

    # Load the removed deck file as a list
    removed_deck = load_removed_deck(removed_file)

    # Remove the cards in the removed deck from the deck
    for card in removed_deck:
        for i, c in enumerate(deck):
            if c.title == card:
                deck.pop(i)
                break

    # Shuffle the deck
    random.shuffle(deck)
    return deck


def load_deck_enum(deckname: DeckEnum) -> list[Card]:
    """Load the deck from the source file and remove the cards in the removed file."""
    match deckname:
        case DeckEnum.FRONTIER:
            deck = load_deck(Path(FRONTIER_SOURCE), Path(FRONTIER_REMOVED))
        case DeckEnum.RELIC:
            deck = load_deck(Path(RELIC_SOURCE), Path(RELIC_REMOVED))
        case _:
            raise ValueError(f"Invalid deck: {deckname}")

    return deck


def save_to_removed(deck: list[Card], removed_file: Path):
    """Save the deck to the removed file."""
    with removed_file.open("a") as f:
        for card in deck:
            f.write(f"{card.title}\n")


def save_to_removed_enum(deckname: DeckEnum, deck: list[Card]):
    """Save the deck to the removed file."""
    match deckname:
        case DeckEnum.FRONTIER:
            save_to_removed(deck, Path(FRONTIER_REMOVED))
        case DeckEnum.RELIC:
            save_to_removed(deck, Path(RELIC_REMOVED))
        case _:
            raise ValueError(f"Invalid deck: {deckname}")


def delete_removed_enum(deckname: DeckEnum):
    """Delete the removed file."""
    match deckname:
        case DeckEnum.FRONTIER:
            Path(FRONTIER_REMOVED).unlink()
        case DeckEnum.RELIC:
            Path(RELIC_REMOVED).unlink()
        case _:
            raise ValueError(f"Invalid deck: {deckname}")
