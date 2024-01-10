from __future__ import annotations

import dataclasses
import enum
import colorama
import random
from typing import List, Optional, Dict
import collections


class PlayerNotInGameError(Exception):
    pass


class Value(enum.IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


class Suit(enum.StrEnum):
    ROCKET = "Rocket"
    BLUE = "Blue"
    GREEN = "Green"
    PINK = "Pink"
    YELLOW = "Yellow"


class Token(enum.IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    ONE_ARROW = 6
    TWO_ARROW = 7
    THREE_ARROW = 8
    FOUR_ARROW = 9
    OMEGA = 10


suit_color = {
    Suit.ROCKET: colorama.Fore.RESET,
    Suit.BLUE: colorama.Fore.BLUE,
    Suit.GREEN: colorama.Fore.GREEN,
    Suit.PINK: colorama.Fore.MAGENTA,
    Suit.YELLOW: colorama.Fore.YELLOW,
}


@dataclasses.dataclass()
class Card:
    """Card class.

    Attributes:
        value: The value of the card. An integer from 1 to 9.
        suit: The suit of the card. Can be either "Rocket", "Blue", "Green", "Pink", or "Yellow".
    """

    value: Value | int
    suit: Suit | str

    def __post_init__(self):
        """Converts the value and suit to the appropriate enum."""
        self.value = Value(self.value)
        self.suit = Suit(self.suit.capitalize())

    def is_suit(self, suit: Suit) -> bool:
        """Checks if the card is a specific suit."""
        return self.suit == suit

    def is_rocket(self) -> bool:
        """Checks if the card is a rocket."""
        return self.is_suit(Suit.ROCKET)

    def __repr__(self):
        return f"{suit_color[self.suit]}{self.value} {self.suit.value}{colorama.Fore.RESET}"

    def __gt__(self, other: "Card"):
        if self.suit == other.suit:
            return self.value > other.value
        elif self.suit == Suit.ROCKET:
            return True
        elif other.suit == Suit.ROCKET:
            return False
        else:
            return self.suit > other.suit


class Deck:
    """Represents a deck or a hand of cards."""

    blue_cards = [Card(value, Suit.BLUE) for value in Value]
    green_cards = [Card(value, Suit.GREEN) for value in Value]
    pink_cards = [Card(value, Suit.PINK) for value in Value]
    yellow_cards = [Card(value, Suit.YELLOW) for value in Value]
    rocket_cards = [Card(Value(value), Suit.ROCKET) for value in range(1, 5)]

    def __init__(self):
        self.cards: list[Card] = []

    def __repr__(self):
        return str(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __contains__(self, card: Card):
        """Checks if a card is in the deck."""
        return card in self.cards

    def deal_cards(self, num_cards: int):
        """Deals a number of cards.

        Args:
            num_cards: The total number of cards to deal.

        Returns:
            A list of Cards. Cards are removed from the deck.
        """
        return [self.cards.pop() for _ in range(num_cards)]

    def shuffle(self, seed: int | None = None) -> None:
        """Shuffles the deck."""
        random.seed(seed)
        random.shuffle(self.cards)

    def sort(self) -> None:
        """Sorts the deck."""
        self.cards.sort()


class CardDeck(Deck):
    """Deck of cards that are dealt to players."""

    num_cards: int = 40

    def __init__(self):
        """Creates a shuffled deck."""
        super().__init__()

        self.cards = []
        self.cards.extend(Deck.blue_cards)
        self.cards.extend(Deck.green_cards)
        self.cards.extend(Deck.pink_cards)
        self.cards.extend(Deck.yellow_cards)
        self.cards.extend(Deck.rocket_cards)

        self.shuffle()


class TaskDeck(Deck):
    """Deck of task cards."""

    num_cards: int = 36

    def __init__(self):
        """Creates a shuffled deck."""
        super().__init__()

        self.cards = []
        self.cards.extend(Deck.blue_cards)
        self.cards.extend(Deck.green_cards)
        self.cards.extend(Deck.pink_cards)
        self.cards.extend(Deck.yellow_cards)

        self.shuffle()


class Player:
    """Represents a player in the game."""

    def __init__(self, game: Game | None = None):
        """Create a new player.

        Args:
            game: Optional Game to add the player to.
        """
        self.starting_hand: Deck = []
        self.hand: Deck = []
        self.game = game
        self.tasks: Deck = []

    @property
    def is_commander(self):
        """True if the player started as the Commander."""
        return Card(Value.FOUR, Suit.ROCKET) in self.starting_hand

    @property
    def num_cards(self):
        """The number of cards in the player's hand."""
        return len(self.hand)

    def draw(self, cards: list[Card], sort: bool = True):
        """Draws cards to form a starting hand.

        Args:
            cards: The cards to draw.
            sort: Whether to sort the hand.
        """
        self.starting_hand = cards
        self.hand = self.starting_hand

        if sort:
            self.sort_hand()

    def sort_hand(self) -> None:
        """Sorts the cards in the player's hand."""
        self.hand.sort()

    # def assign_task(self, task_card: Card):
    # 	self.tasks.append(task_card)

    def select_task_card(self) -> Card:
        print(f"Your Hand: {self.hand}")
        print("Select a Task Card:")
        for i, task_card in enumerate(self.game.unchosen_task_cards):
            print(f"\t{(i + 1) % 10}: {task_card}")
        valid_index = False
        while not valid_index:
            try:
                index = int(input("Select a task to take: "))
                if index in [
                    (i + 1) % 10 for i in range(len(self.game.unchosen_task_cards))
                ]:
                    valid_index = True
            except ValueError:
                continue
        index = (index - 1) % 10

        confirmation_prompt = f"Would you like to take the task card: {self.game.unchosen_task_cards[index]} (Y/N) "
        confirmation = input(confirmation_prompt)
        if confirmation == "y" or confirmation == "Y":
            selected_task_card = self.game.unchosen_task_cards.pop(index)
            self.tasks.append(selected_task_card)
            return selected_task_card
        else:
            return self.select_task_card()

    def select_card(self, starting_suit: Suit = None) -> Card:
        if starting_suit:
            valid_cards = [card for card in self.hand if card.suit == starting_suit]
        if not starting_suit or not valid_cards:
            valid_cards = self.hand
        print(f"Your Hand: {self.hand}")
        print("Select a card to play:")
        for i, card in enumerate(valid_cards):
            print(f"\t{(i + 1) % 10}: {card}")
        valid_index = False
        while not valid_index:
            try:
                index = int(input("Select a card to play: "))
                if index in [(i + 1) % 10 for i in range(len(valid_cards))]:
                    valid_index = True
            except ValueError:
                continue
        index = (index - 1) % 10
        confirmation_prompt = f"Would you like to play: {valid_cards[index]} (Y/N) "
        confirmation = input(confirmation_prompt)
        if confirmation == "y" or confirmation == "Y":
            return valid_cards[index]
        else:
            return self.select_card(starting_suit)

    def play_card(self, card: Card) -> None:
        if self.game is None:
            raise PlayerNotInGameError

        self.hand.remove(card)
        self.game.trick.play_card(player=self, card=card)

    def player_turn(self):
        player_number = self.game.players.index(self) + 1
        print(f"You are player {player_number}")
        print(f"Current Trick: {self.game.trick}")
        print(f"Remaining Task Cards: {self.game.task_cards}")
        print(f"Your Task Cards: {self.tasks}")

        starting_suit = self.game.trick.starting_suit

        selected_card = self.select_card(starting_suit)
        self.play_card(selected_card)


class Trick:
    """Represents the current trick.

    Attributes:
        cards: The cards that have been played in the trick.
        highest_card: The highest card currently winning the trick.
        starting_suit: The suit that was played first.
    """

    def __init__(self):
        """Set up a new trick."""
        self.cards: dict[Player, Card] = {}
        self.highest_card: Card | None = None
        self.starting_suit: Suit = None

    def __str__(self):
        return str(list(self.cards.values()))

    def __contains__(self, card: Card):
        """Checks if a card has been played in the trick."""
        return card in self.cards.values()

    def play_card(self, player: Player, card: Card):
        """Play a card in the trick."""
        self.cards[player] = card
        if len(self.cards) == 1:
            self.starting_suit = card.suit
            self.highest_card = card
        elif self.highest_card.suit == Suit.ROCKET:
            if card.suit == Suit.ROCKET:
                self.highest_card = max(card, self.highest_card)
        else:
            if card.suit == self.highest_card.suit:
                self.highest_card = max(card, self.highest_card)

    @property
    def winning_player(self) -> Player:
        """Returns the player currently winning the trick."""
        for player, card in self.cards.items():
            if card == self.highest_card:
                return player

    @property
    def winning_card(self) -> Card:
        """Returns the card that is winning the trick."""
        return self.highest_card


class Game:
    """Represents a game of Crew.

    Contains information about the card deck, players, and current trick.

    Attributes:
        deck: The deck of cards.
        task_desk: The deck of task cards.
        task_cards: The task cards for the current mission.
        unchosen_task_cards: The task cards that have not been chosen yet.
        trick: The current trick.
        played_cards: The cards that have been played in previous tricks.
    """

    deck: CardDeck
    task_deck: TaskDeck
    task_cards: TaskDeck
    unchosen_task_cards: TaskDeck
    trick: Trick
    played_cards: Deck

    def __init__(self, num_players: int = 4):
        self.num_players: int = 0
        self.players: List[Player] = []
        self.add_new_players(num_players)

    @property
    def commander(self) -> Player:
        """Returns the player that is the current Commander."""
        for player in self.players:
            if player.is_commander:
                return player

    def __str__(self) -> str:
        """Returns a string representation of the game."""
        game_repr = []
        for i, player in enumerate(self.players):
            game_repr.append(f"Player {i+1}: {player.hand}")
        game_repr.append(f"Task Cards: {self.task_cards}")
        return "\n".join(game_repr)

    def new_mission(self) -> None:
        """Set up a new mission.

        Creates a new card deck, task deck, and deals cards to players.
        """
        self.new_card_deck()
        self.new_task_deck()
        self.deal_cards()
        self.new_trick()

    def new_card_deck(self) -> None:
        """Cretes a new card deck."""
        self.deck = CardDeck()

    def new_task_deck(self) -> None:
        """Creates a new task deck."""
        self.task_deck = TaskDeck()

    def new_trick(self) -> None:
        """Sets up a new trick."""
        self.trick = Trick()

    def add_new_player(self, player: Player):
        """Add a new player to the game."""
        self.players.append(player)
        self.num_players += 1
        player.game = self

    def add_new_players(self, num_players: int) -> None:
        """Add a number of new players to the game."""
        for _ in range(num_players):
            self.players.append(Player(self))
        self.num_players += num_players

    def deal_cards(self) -> None:
        """Deal cards to all players in the game."""
        num_cards_per_player = CardDeck.num_cards // self.num_players
        for player in self.players:
            player.draw(self.deck.deal_cards(num_cards_per_player))

    def deal_task_cards(self, num_cards: int):
        """Deal the number of task cards to be selected from."""
        self.task_cards = self.task_deck.deal_cards(num_cards)
        self.unchosen_task_cards = self.task_cards.copy()

    def assign_task_cards(self, game: Game):
        """Interactive prompt for players to select task cards."""
        # Start with commander, and then increment
        player_number_selecting_task = self.players.index(game.commander)
        while self.unchosen_task_cards:
            print()
            print(f"Player {player_number_selecting_task + 1} selecting...")
            self.players[player_number_selecting_task].select_task_card()
            player_number_selecting_task = (
                player_number_selecting_task + 1
            ) % self.num_players
