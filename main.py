# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
import Bots.Register as Register
import pack
import Logging
import game_play as gp
import globals
import Console_Interface as CI
import table as t

names = ['Adam', 'Ben', 'Caleb', 'Dan', 'Eli', 'Frank', 'Gad', 'Huz', 'Isaiah', 'John']
All_players = []


def init_players(num=5, chips=1000):
    for player in range(0, num):
        i = random.randint(0, len(Register.register()) - 1)
        All_players.append(Register.register()[i](names[player], chips))
    return All_players


def update_player_chips(players):
    All_players = players


def get_all_players():
    return All_players


def get_players_at_table():
    players = []
    for player in All_players:
        if not player.busted:
            players.append(player)
    return players


def fold_player(player, bets):
    if player:
        player.fold()
    if player.name in bets.keys():
        bets.__delitem__(player.name)


def betting(players, table, pot, side_pots, dealer, all_players, little_blind=0, big_blind=0):
    loc_side_pots = {}
    current_bet = 0
    bet = 0
    bets = {}  # player, bet
    for player in players:
        bets[player.name] = 0
    Betting_done = False
    side_pots = {}
    round_history = []
    first_round = True
    while not Betting_done:
        for player in players:
            if first_round:
                if player is dealer:
                    first_round = False
                continue
            if player.folded or player.all_in or (0 < current_bet == bets[player.name]):
                continue

            forced = 0
            if little_blind > 0:
                forced = little_blind
                little_blind = 0
            elif big_blind > 0:
                forced = big_blind
                if current_bet < big_blind:
                    current_bet = big_blind
                big_blind = 0

            CI.print_status(get_all_players(), bets, player, pot, table, globals.g_user)
            bet = player.outer_act(current_bet, bets[player.name], table, round_history, pot, forced)
            round_history.append((player, bet))
            if bet is None:
                fold_player(player, bets)
                continue
            pot += bet
            bets[player.name] += bet

            if bets[player.name] < current_bet:
                if player.all_in:
                    loc_side_pots[player.name] = bets[player.name]
                else:
                    fold_player(player, bets)
                continue
            elif bets[player.name] >= current_bet * 2:
                current_bet = bets[player.name]
            elif player.all_in:
                current_bet = bets[player.name]
                if player.name not in loc_side_pots.keys():
                    loc_side_pots[player.name] = bets[player.name]
            elif bets[player.name] != current_bet:
                assert False
        Betting_done = True
        for player in players:
            if player.folded or player.all_in:
                continue
            if bets[player.name] < current_bet:
                Betting_done = False
                break
    CI.print_status(all_players, bets, None, pot, table, globals.g_user, 5)
    for name in loc_side_pots.keys():
        side_pot_value = 0
        for bet in bets.values():
            if bet > loc_side_pots[name]:
                side_pot_value += loc_side_pots[name]
            else:
                side_pot_value += bet
        side_pots[name] = side_pot_value
    return pot, side_pots


round_order = [globals.FLOP, globals.TURN, globals.RIVER]


def deal_round(round_num, dealer_num, all_players, pot, little_blind, big_blind):
    _Table = t.Table(pack.getDeck())
    side_pots = {}
    players = []
    for person in all_players:
        if not person.busted:
            person.new_hand()
            players.append(person)
    if dealer_num >= len(players):
        dealer_num = 0
    dealer = players[dealer_num]
    _Table.deal(players)
    if round_num > 0 and round_num % 25 == 0:
        little_blind *= 2
        big_blind *= 2
    for action in round_order:
        _Table.next_card(action, players)
        pot, side_pots = betting(players, _Table, pot, side_pots, dealer, all_players, little_blind, big_blind)
    payout = pot
    Logging.Log_chips(all_players, _Table, pot)
    pot = gp.payout(payout, side_pots, players, _Table)

    for player in players:
        player.new_hand()
    for person in all_players:
        person.update_stats()
    return pot


def play(num_starting_players):
    all_players = init_players(num_starting_players)
    dealer_num = -1
    little_blind = 5
    big_blind = 10
    pot = 0
    for round in range(0, 1000):
        dealer_num += 1
        if round == 0:
            Logging.Log_chips(all_players, None, 0)
        pot = deal_round(round, dealer_num, all_players, pot, little_blind, big_blind)
        ended = False
        num_busted = 0
        for player in all_players:
            if player.busted:
                num_busted += 1
                if num_busted == len(all_players) - 1:
                    ended = True
        if ended:
            break


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    play(5)
    print("LETS GO")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
