# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
import Bots.Register as Register
import Dealer.Parse_Config as Dealer_Config
import pack
import Logging
import game_play as gp
import globals
import Console_Interface as CI
import table as t
import Animate.animate as ani


names = ['Adam', 'Ben', 'Caleb', 'Dan', 'Eli', 'Frank', 'Gad', 'Huz', 'Isaiah', 'John']


def init_players(num=5, chips=1000):
    all_players = []
    for j in range(0, num):
        i = random.randint(0, len(Register.register()) - 1)
        new_player = Register.register()[i](names[j], chips)
        for player in all_players:
            if not player:
                break
            while player.bot_type() == new_player.bot_type():
                if i == len(Register.register()) - 1:
                    i = 0
                else:
                    i += 1
                new_player = Register.register()[i](names[j], chips)
        all_players.append(new_player)
    return all_players


def blinds(live_players, dealer_num, big_blind):
    little_blind = round(big_blind/2)
    if dealer_num + 1 >= len(live_players):
        little_blind_player = live_players[0]
        big_blind_player = live_players[1]
        little_blind_player = live_players[dealer_num + 1]
    elif dealer_num + 2 >= len(live_players):
        big_blind_player = live_players[0]
    else:
        little_blind_player = live_players[dealer_num + 1]
        big_blind_player = live_players[dealer_num + 2]
    little_blind_player.outer_act(live_players, little_blind)
    big_blind_player.outer_act(live_players, big_blind)


def done_betting(players):
    bets = []
    for player in players:
        bets.append(player.chips_in_round)
    current_bet = max(bets)
    for player in players:
        if player.folded or player.all_in or player.busted:
            continue
        if current_bet > player.chips_in_round:
            return False
    return True


def bet(live_players, on_index, big_blind, _Table):
    if big_blind is not None:
        blinds(live_players, on_index, big_blind)
        on_index += 2
    num_players = len(live_players)
    while True:
        debug_pot = gp.get_current_pot(live_players)
        debug_bet = gp.get_current_bet(live_players)
        if on_index > num_players - 1:
            on_index = 0
        under_gun = live_players[on_index]
        on_index += 1
        if not under_gun.can_bet(live_players):
            debug_pot = gp.get_betting_round_pot(live_players)
            continue
        if under_gun.outer_act(live_players) is None:
            CI.print_status(None, live_players, under_gun, _Table)
            under_gun.fold()
        debug_pot = gp.get_current_pot(live_players)
        if done_betting(live_players):
            break

round_order = [globals.DEAL, globals.FLOP, globals.TURN, globals.RIVER]


def deal_round(round_num, dealer_num, all_players, big_blind):
    _Table = t.Table(pack.get_deck())
    players = []
    for person in all_players:
        if not person.busted:
            person.new_hand()
            players.append(person)
    if round_num > 0 and round_num % 25 == 0:
        big_blind *= 2

    for action in round_order:
        blind = big_blind if action == globals.DEAL else None
        _Table.next_card(action, players)
        for player in players:
            player.new_betting_round()
        bet(players, dealer_num + 1, blind, _Table)
        CI.print_status(round_num, all_players, None, _Table)

    pot = gp.payout(players)
    Logging.log_chips(all_players, _Table, pot)

    for player in players:
        player.new_hand()
    for person in all_players:
        person.update_stats()
    return pot, big_blind


def play(num_starting_players):
    all_players = init_players(num_starting_players)
    dealer_num = -1
    big_blind = 10
    if globals.ANIMATE:
        ani.start_log(all_players)
    for round_num in range(0, 1000):
        dealer_num += 1
        if round_num == 0:
            Logging.log_chips(all_players, None, 0)
        deal_round(round_num, dealer_num, all_players, big_blind)
        ended = False
        num_busted = 0
        for player in all_players:
            if player.busted:
                num_busted += 1
                if num_busted == len(all_players) - 1:
                    ended = True
        if ended:
            break
        if dealer_num > len(all_players) - num_busted:
            dealer_num = -1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    play(5)
    print("LETS GO")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
