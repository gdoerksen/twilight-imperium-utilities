import csv
import json
import random

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

@dataclass
class Card:
    """A dataclass to represent a card with a title and description."""
    title: str
    description: str

# Data Paths
PROJECT_ROOT = Path(__file__).parent
DATA_PATH = PROJECT_ROOT / 'data'
CACHE_PATH = PROJECT_ROOT / '.cache'
FRONTIER_SOURCE = DATA_PATH / 'frontier_source.json'
FRONTIER_REMOVED = CACHE_PATH / 'frontier_removed.csv'
RELIC_SOURCE = DATA_PATH / 'relics_source.json'
RELIC_REMOVED = CACHE_PATH / 'relics_removed.csv'

class DeckEnum(str, Enum):
    """An enum to represent the two decks."""
    FRONTIER = 'frontier'
    RELIC = 'relic'

app = typer.Typer()
console = Console()

def convert_csv_to_json(source_file: Path, dest_file: Path):
    """Convert the csv file to a json file."""
    deck: list[dict] = []
    with source_file.open() as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            deck.append({
                'Card': row['Card'],
                'Effect': row['Effect'],
                'Number in Deck': int(row['Number in Deck'])
            })

    with dest_file.open('w') as f:
        json.dump(deck, f, indent=4)

def load_deck_source_csv(source_file: Path) -> list[Card]:
    """Load the deck from the source csv file."""
    deck: list[Card] = []
    with source_file.open() as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            for _ in range(int(row['Number in Deck'])):
                deck.append(Card(title=row['Card'], description=row['Effect']))

    return deck

def load_deck_source_json(source_file: Path) -> list[Card]:
    """Load the deck from the source json file."""
    deck: list[Card] = []
    with source_file.open() as f:
        data = json.load(f)
        for card in data:
            for _ in range(card['Number in Deck']):
                deck.append(Card(title=card['Card'], description=card['Effect']))

    return deck

def load_deck(source_file: Path, removed_file: Path) -> list:
    """Load the deck from the source file and remove the cards in the removed file."""
    # Load the source file as a list
    deck = load_deck_source_json(source_file)

    # Load the removed deck file as a list 
    removed_deck = []
    with removed_file.open() as f:
        for line in f:
            removed_deck.append(line.strip())

    # Remove the cards in the removed deck from the deck
    for card in removed_deck:
        for i, c in enumerate(deck):
            if c.title == card:
                deck.pop(i)
                break

    # Shuffle the deck
    random.shuffle(deck)
    return deck

def load_deck_enum(deck: DeckEnum) -> list[Card]:
    """Load the deck from the source file and remove the cards in the removed file."""
    match deck:
        case DeckEnum.FRONTIER:
            deck = load_deck(Path(FRONTIER_SOURCE), Path(FRONTIER_REMOVED))
        case DeckEnum.RELIC:
            deck = load_deck(Path(RELIC_SOURCE), Path(RELIC_REMOVED))
        case _:
            raise ValueError(f'Invalid deck: {deck}')
        
    return deck

def save_to_removed(deck: list[Card], removed_file: Path):
    """Save the deck to the removed file."""
    with removed_file.open('w') as f:
        for card in deck:
            f.write(f'{card.title}\n')

def save_to_removed_enum(deckname: DeckEnum, deck: list[Card]):
    """Save the deck to the removed file."""
    match deckname:
        case DeckEnum.FRONTIER:
            save_to_removed(deck, Path(FRONTIER_REMOVED))
        case DeckEnum.RELIC:
            save_to_removed(deck, Path(RELIC_REMOVED))
        case _:
            raise ValueError(f'Invalid deck: {deckname}')


def panel_width_formatter(width: int) -> int:
    """Format the width for the panel."""
    max_width = 50
    return max(min(width, max_width), 0)

def print_card_as_panel(card: Card):
    """Print the card as a panel."""
    console.print(Panel(
        card.description,
        title=card.title,
        title_align='left',
        expand=False,
        border_style='green',
        padding=(0, 1, 0, 1),
        width=panel_width_formatter(console.width)
        ))

@app.command()
def show(deckname: DeckEnum):
    """Show the chosen deck."""
    deck = load_deck_enum(deckname)
    for card in deck:
        print_card_as_panel(card)

@app.command()
def draw(deckname: DeckEnum, number: int = 1):
    """Draw cards from the chosen deck equal to the number."""
    deck = load_deck_enum(deckname)
    removed = []
    for _ in range(number):
        card = deck.pop()
        removed.append(card)
        print_card_as_panel(card)
    save_to_removed_enum(deckname, removed)

@app.command()
def reset(deckname: DeckEnum):
    """Resets the chosen deck to full."""
    pass



if __name__ == "__main__":
    app()

    # try:
    #     main()
    # except Exception:
    #     console.print_exception(show_locals=True)