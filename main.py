# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random

import pack
import hand_helpers as Hands
import Logging
import Bots.Register as Register
import Bots.user as user
import game_play as gp
import globals
import Console_Interface as CI

class Table:
    def __init__(self, deck):
        self.deck = deck
        self.burned = []
        self.flop1 = None
        self.flop2 = None
        self.flop3 = None
        self.turn = None
        self.river = None

    def _turn(self):
        print("\nTURN:", end="\t")
        self.burned = self.deck.pop(0)
        self.turn = self.deck.pop(0)
        self.flop1.print_with_color()
        self.flop2.print_with_color()
        self.flop3.print_with_color()
        self.turn.print_with_color()
        print("******")

    def flop(self):
        print("\nFLOP:", end="\t")
        self.burned = self.deck.pop(0)
        self.flop1 = self.deck.pop(0)
        self.flop2 = self.deck.pop(0)
        self.flop3 = self.deck.pop(0)
        self.flop1.print_with_color()
        self.flop2.print_with_color()
        self.flop3.print_with_color()
        print("******")

    def _river(self):
        print("\nRIVER:", end="\t")
        self.burned = self.deck.pop(0)
        self.river = self.deck.pop(0)
        self.flop1.print_with_color()
        self.flop2.print_with_color()
        self.flop3.print_with_color()
        self.turn.print_with_color()
        self.river.print_with_color()
        print("******")

    def show(self):
        show_string = ""
        if (self.flop1):
            show_string += self.flop1.log_string() + ','
        if (self.flop2):
            show_string += self.flop2.log_string() + ','
        if (self.flop3):
            show_string += self.flop3.log_string() + ','
        if (self.turn):
            show_string += self.turn.log_string() + ','
        if (self.river):
            show_string += self.river.log_string() + ','
        return show_string


names = ['Adam', 'Ben', 'Caleb', 'Dan', 'Eli', 'Frank', 'Gad', 'Huz', 'Isiah', 'John']

def deal(players, table):
    print(table.deck.pop(0))
    for i in range(0, 2):
        for player in players:
            player.add_card(table.deck.pop(0))

def flop(table):
    table.flop()

def turn(table):
    table._turn()

def river(table):
    table._river()

def show_all_hands(players, table):
    for player in players:
        player.show_hand(table)

def end(players):
    Table(pack.getDeck())
    for player in players:
        player.new_hand()

#def betting():
    # later

class Actions:
    fold = 0
    call = 1
    bet = 2
    check = 3
    allin = 4


def fold_player(player, players, bets):
    if globals.g_user_playing:
        print(player.name + " folds")
    if player:
        player.fold()
    if player in players:
        players.remove(player)
    if player.name in bets.keys():
        bets.__delitem__(player.name)


def betting(players, table, pot, side_pots):
    loc_side_pots = {}
    current_bet = 0
    bet = 0
    bets = {} # player, bet
    for player in players:
        bets[player.name] = 0
    Betting_done = False
    side_pots = {}
    betting_round = 0
    round_history = {}
    while not Betting_done:
        for player in players:
            CI.print_status(players, bets, player, pot, table, globals.g_user, "")
            if player.folded:
                fold_player(player, players, bets)
                continue
            if player.all_in:
                continue
            if current_bet > 0 and bets[player.name] == current_bet:
                continue
            bet = player.outer_act(current_bet, bets[player.name], table, round_history, pot)

            if bet is None:
                fold_player(player, players, bets)
                continue
            pot += bet
            bets[player.name] += bet
            if bets[player.name] < current_bet:
                if player.all_in:
                    loc_side_pots[player.name] = bets[player.name]
                else:
                    fold_player(player, players, bets)
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
            if bets[player.name] < current_bet and not player.all_in:
                Betting_done = False
                break
    for name in loc_side_pots.keys():
        side_pot_value = 0
        for bet in bets.values():
            if bet > loc_side_pots[name]:
                side_pot_value += loc_side_pots[name]
            else:
                side_pot_value += bet
        side_pots[name] = side_pot_value
    print("pot: " + str(pot))
    return pot, side_pots


def play(num_starting_players):
    all_players = []
    for player in range(0, num_starting_players):
        i = random.randint(0, len(Register.register())-1)
        all_players.append(Register.register()[i](names[player], 1000))
    if globals.g_user_playing:
        globals.g_user = user.User(input("Your name:"), 1000)
        all_players.append(globals.g_user)

    for round in range(0, 1000):
        if globals.g_user_playing:
            input("press ENTER for new round ")
            print("\n*****NEW ROUND*****")
        table = Table(pack.getDeck())
        if round == 0:
            Logging.Log_chips(all_players, table, 0)
        players = []
        for person in all_players:
            if not person.busted:
                person.new_hand()
                players.append(person)

        deal(players, table)
        if not globals.g_user_playing:
            show_all_hands(players, table)
        pot = 0
        side_pots = {}

        pot, side_pots = betting(players, table, pot, side_pots)
        flop(table)
        if not globals.g_user_playing:
            show_all_hands(players, table)

        pot, side_pots = betting(players, table, pot, side_pots)
        turn(table)
        if not globals.g_user_playing:
            show_all_hands(players, table)

        pot, side_pots = betting(players, table, pot, side_pots)
        river(table)
        if not globals.g_user_playing:
            show_all_hands(players, table)

        pot, side_pots = betting(players, table, pot, side_pots)
        if globals.g_user_playing:
            print("\nSHOWDOWN:")
        show_all_hands(players, table)
        payout = pot
        gp.payout(payout, side_pots, players, table)

        Logging.Log_chips(all_players, table, pot)
        for person in all_players:
            person.status(table)
        end(players)
        ended = False
        num_busted = 0
        for player in all_players:
            if player.busted:
                num_busted += 1
                if num_busted == len(all_players) - 1:
                    ended = True
        if ended:
            break

def print_hi(name):
    play(7)
    # Use a breakpoint in the code line below to debug your script.
    print("LETS GO")  # Press Ctrl+F8 to toggle the breakpoint.

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
