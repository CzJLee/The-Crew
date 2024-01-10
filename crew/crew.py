import numpy as np
import dataclasses
import enum
import colorama
import random
from typing import List, Optional, Dict
from tqdm.auto import tqdm
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
    value: Value
    suit: Suit

    def is_suit(self, suit: Suit) -> bool:
        return self.suit == suit

    def is_rocket(self) -> bool:
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
    blue_cards = [Card(value, Suit.BLUE) for value in Value]
    green_cards = [Card(value, Suit.GREEN) for value in Value]
    pink_cards = [Card(value, Suit.PINK) for value in Value]
    yellow_cards = [Card(value, Suit.YELLOW) for value in Value]
    rocket_cards = [Card(Value(value), Suit.ROCKET) for value in range(1, 5)]

    def __init__(self):
        self.cards: List[Card] = []

    def __repr__(self):
        return str(self.cards)

    def deal_cards(self, num_cards: int):
        return [self.cards.pop() for _ in range(num_cards)]


class CardDeck(Deck):
    num_cards: int = 40

    def __init__(self):
        """Creates a shuffled deck."""
        self.cards = []
        self.cards.extend(Deck.blue_cards)
        self.cards.extend(Deck.green_cards)
        self.cards.extend(Deck.pink_cards)
        self.cards.extend(Deck.yellow_cards)
        self.cards.extend(Deck.rocket_cards)

        random.shuffle(self.cards)


class TaskDeck(Deck):
    num_cards: int = 36

    def __init__(self):
        """Creates a shuffled deck."""
        self.cards = []
        self.cards.extend(Deck.blue_cards)
        self.cards.extend(Deck.green_cards)
        self.cards.extend(Deck.pink_cards)
        self.cards.extend(Deck.yellow_cards)

        random.shuffle(self.cards)


class Player:
    def __init__(self, game: Optional["Game"] = None):
        self.starting_hand: List[Card] = []
        self.hand: List[Card] = []
        self.game = game
        self.tasks: List[Card] = []

    @property
    def is_commander(self):
        return Card(Value.FOUR, Suit.ROCKET) in self.starting_hand

    @property
    def num_cards(self):
        return len(self.hand)

    def draw(self, cards: List[Card]):
        self.starting_hand = cards
        self.hand = self.starting_hand
        self.sort_hand()

    def sort_hand(self):
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
    def __init__(self):
        self.cards: Dict[Player, Card] = {}
        self.highest_card: Optional[Card] = None
        self.starting_suit: Suit = None

    def __repr__(self):
        return str(list(self.cards.values()))

    def __contains__(self, card: Card):
        return card in self.cards.values()

    def play_card(self, player: Player, card: Card):
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
        for player, card in self.cards.items():
            if card == self.highest_card:
                return player

    @property
    def winning_card(self) -> Card:
        return self.highest_card


class Game:
    deck: CardDeck
    task_deck: TaskDeck
    task_cards: List[Card]
    unchosen_task_cards: List[Card]
    trick: Trick
    played_cards: List[Card]

    def __init__(self, num_players: int = 4):
        self.num_players: int = 0
        self.players: List[Player] = []
        self.add_new_players(num_players)

    @property
    def commander(self) -> Player:
        for player in self.players:
            if player.is_commander:
                return player

    def __repr__(self) -> str:
        game_repr = []
        for i, player in enumerate(self.players):
            game_repr.append(f"Player {i+1}: {player.hand}")
        game_repr.append(f"Task Cards: {self.task_cards}")
        return "\n".join(game_repr)

    def new_mission(self) -> None:
        self.new_card_deck()
        self.new_task_deck()
        self.deal_cards()
        self.new_trick()

    def new_card_deck(self) -> None:
        self.deck = CardDeck()

    def new_task_deck(self) -> None:
        self.task_deck = TaskDeck()

    def new_trick(self) -> None:
        self.trick = Trick()

    def add_new_player(self, player: Player):
        self.players.append(player)
        self.num_players += 1
        player.game = self

    def add_new_players(self, num_players: int) -> None:
        for _ in range(num_players):
            self.players.append(Player(self))
        self.num_players += num_players

    def deal_cards(self) -> None:
        num_cards_per_player = CardDeck.num_cards // self.num_players
        for player in self.players:
            player.draw(self.deck.deal_cards(num_cards_per_player))

    def deal_task_cards(self, num_cards: int):
        self.task_cards = self.task_deck.deal_cards(num_cards)
        self.unchosen_task_cards = self.task_cards.copy()

    def assign_task_cards(self):
        # Start with commander, and then increment
        player_number_selecting_task = self.players.index(game.commander)
        while self.unchosen_task_cards:
            print()
            print(f"Player {player_number_selecting_task + 1} selecting...")
            self.players[player_number_selecting_task].select_task_card()
            player_number_selecting_task = (
                player_number_selecting_task + 1
            ) % self.num_players


if __name__ == "__main__":
    game = Game(5)
    # player = Player(game)
    # game.add_new_player(player)

    game.new_mission()
    game.deal_task_cards(1)
    # game.assign_task_cards()

    print()
    player = game.commander

    commander_index = game.players.index(game.commander)

    # while True:
    # 	for i in range(game.num_players):
    # 		print()
    # 		game.players[(commander_index + i) % game.num_players].player_turn()

    # 	print(game.trick)
    # 	print(game.trick.winning_card)
    # 	print(game.trick.winning_player)
    # 	if game.task_cards[0] in game.trick:
    # 		if game.task_cards[0] in game.trick.winning_player.tasks:
    # 			print("YOU WIN!")
    # 			break
    # 		else:
    # 			print("YOU LOSE GAME OVER")
    # 			break
    # 	else:
    # 		print("TRICK NOT WON, TRYING AGAIN.")
    # 		game.new_trick()

    # player.player_turn()

    # print(f"Current Trick: {game.trick}")

    total_rockets_seen = []

    games_player_has_n = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

    iterations = 1000000
    for i in tqdm(range(iterations)):
        game.new_card_deck()
        game.deal_cards()
        round_seen = []
        for i, player in enumerate(game.players):
            total_rockets = 0
            for card in player.hand:
                if card.is_rocket():
                    total_rockets += 1
            round_seen.append(total_rockets)
            total_rockets_seen.append(total_rockets)
        for i in [0, 1, 2, 3, 4]:
            if i in round_seen:
                games_player_has_n[i] += 1

    total_rockets_seen_count = collections.Counter(total_rockets_seen)
    for key, value in sorted(total_rockets_seen_count.items()):
        print(
            f"{key} Rockets : {round(100 * value / (iterations * game.num_players), 3)}%"
        )
    for n, value in sorted(games_player_has_n.items()):
        print(f"Game with {n} Rockets : {round(100 * value / (iterations), 3)}%")
