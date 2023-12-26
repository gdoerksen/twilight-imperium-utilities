from pathlib import Path
from typing_extensions import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from .file_utils import (
    load_deck_enum,
    save_to_removed_enum,
    delete_removed_enum,
    load_removed_as_history,
)
from .models import Card, DeckEnum


app = typer.Typer()
show_app = typer.Typer()
app.add_typer(show_app, name="show")
console = Console()


def panel_width_formatter(width: int) -> int:
    """Format the width for the panel."""
    max_width = 50
    return max(min(width, max_width), 0)


def print_card_as_panel(card: Card):
    """Print the card as a panel."""
    console.print(
        Panel(
            card.description,
            title=card.title,
            title_align="left",
            expand=False,
            border_style="green",
            padding=(0, 1, 0, 1),
            width=panel_width_formatter(console.width),
        )
    )


@show_app.command()
def remaining(deckname: DeckEnum):
    """Show what is remaining in the chosen deck."""
    deck = load_deck_enum(deckname)
    for card in deck:
        print_card_as_panel(card)


@show_app.command()
def history(deckname: DeckEnum):
    """Show what has been removed from the chosen deck."""
    removed = load_removed_as_history(deckname)
    for card in removed:
        print_card_as_panel(card)


@app.command()
def draw(
    deckname: DeckEnum,
    number: Annotated[int, typer.Argument(help="Number of cards to draw")] = 1,
):
    """Draw cards from the chosen deck equal to the number."""
    deck = load_deck_enum(deckname)

    deck_remaining = len(deck)
    if number > deck_remaining:
        delta = number - deck_remaining
        for card in deck:
            print_card_as_panel(card)
        console.print(f"Deck is empty. {delta} cards were not drawn.")

        # Handle special cases such as attachments and relic fragments
        # gamma wormhole, demilitarized zone, etc

        # prompt for how many relic fragments in discard
        relic_fragments_left = typer.prompt(
            "How many relic fragments are in the discard?"
        )
        if relic_fragments_left:
            relic_fragments_left = int(relic_fragments_left)

    else:
        cards = []
        for _ in range(number):
            card = deck.pop()
            print_card_as_panel(card)
            cards.append(card)
        save_to_removed_enum(deckname, cards)


@app.command()
def reset(deckname: DeckEnum):
    """Resets the chosen deck to full."""
    delete_removed_enum(deckname)


@app.command()
def start_game():
    """Reset all decks so you can start a new game."""
    response = typer.prompt("Are you sure you want to reset all decks? (y/n)")
    if response.lower() != "y":
        typer.echo("Aborting.")
        raise typer.Abort()

    for deckname in DeckEnum:
        reset(deckname)


if __name__ == "__main__":
    app()

    # try:
    #     main()
    # except Exception:
    #     console.print_exception(show_locals=True)
