import crew
from tqdm.auto import tqdm
import collections

if __name__ == "__main__":
    game = crew.Game(5)
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

    iterations = 100000
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