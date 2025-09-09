"""Black Jack - ENGG Project 2

This is the main code, it handles playing the blackjack game.
button_blackjack is imported to handle input with the button
(not necassary for terminal play).

Compatiable with micropython, if import requests is changed to
import urequests.
"""

# import connection_home
import lcd_blackjack
import time

# if true then play is done through the terminal, otherwise it is done with the button
TERMINAL_PLAY = False

if not TERMINAL_PLAY:
    # may be ommited when playing with the terminal
    import button_blackjack

# requests is used when playing with a computer
set_cards = False
if set_cards:
    class rq():
        cards = [{"code" : "AH", "value" : "ACE"},
                 {"code" : "AS", "value" : "ACE"},
                 {"code" : "2H", "value" : 2},
                 {"code" : "2D", "value" : 2},
                 {"code" : "2H", "value" : 2},
                 {"code" : "3H", "value" : 3},
                 {"code" : "2D", "value" : 2},
                 {"code" : "3D", "value" : 3},
                 {"code" : "3H", "value" : 3},
                 {"code" : "3D", "value" : 3},
                 {"code" : "4H", "value" : 4},
                 {"code" : "4D", "value" : 4},
                 {"code" : "9H", "value" : 9},
                 {"code" : "0D", "value" : 10} ]
        position = 0
        def __init__(self, card):
            self.cards = card
        def json(self):
            return {"cards" : self.cards}
        def get(input):
            print(input)
            if input[-1] in ("1", "3"):
                number = int(input[-1])
                card = rq.cards[rq.position:rq.position+number]
                print(card)
                rq.position += number
                return rq(card)
    deck_id = None
else:
    import urequests as rq
    print("Creating Deck...")
    deck = rq.get("https://deckofcardsapi.com/api/deck/new/").json()
    deck_id = deck["deck_id"]
    print(deck_id)

import light_strip


funds = 100
bet = 20

PAYOUT_FACTORS = {"blackjack" : 1.5, "win" : 1, "push" : 0, "surrender" : -0.5, "lose" : -1, "bust" : -1}
CARDS_DISPLAYED = False


class Hand():
    """Class for representing a hand in the game, contains a list of cards and methods for manipulating a hand.
    Used as a parent class for PlayerHand and DealerHand, which are used directly in the code.
    """

    conversions = {"ACE" : "11", "JACK" : "10", "QUEEN" : "10", "KING" : "10"}
    
    def __init__(self, cards=[], draw=0):
        """Creates a new hand, which includes the cards from 'cards', and draws 'draw' new cards.
        Attributes:
            self.cards - list - the cards in the hand
            self.sum - interger - the sum of the hand
            self.aces - interger - how many aces are currently acting as an 11, if one than the hand is soft
        """
        if self.name == "Player Hand":
            global player_hand
            player_hand = self

        self.cards = []
        self.sum = 0
        self.aces = 0
        for card in cards:
            self._push_card(card)
        for i in range(draw):
            self.draw_card()

    def _get_value(self, face_name):
        """Gets the face value (number or 10 for a face card, 11 for ace) with a card value."""
        return int(self.conversions.get(face_name, face_name))
    
    def _update_sum(self, face_name):
        """Updates the hands sum and aces attributes, for when a new card is draw."""
        if face_name == "ACE":
            self.aces += 1
        self.sum += self._get_value(face_name)
        for i in range(self.aces): 
            if self.sum > 21: 
                self.sum -= 10
                self.aces -= 1
    
    def _push_card(self, card):
        """Adds a specified card to the hand."""
        self.cards.append(card)
        self._update_sum(card["value"])

    def draw_card(self):
        """Draws a card."""
        card = rq.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=1").json()["cards"][0]
        self._push_card(card)
        print(CARDS_DISPLAYED)
        if CARDS_DISPLAYED and (len(player_hand.cards) + len(dealer_hand.cards)) <= 7:
            lcd_blackjack.print_card(self.card_positions[len(self.cards) - 1], card["code"][0], card["code"][1])
        else:
            print_cards()

class PlayerHand(Hand):
    """Subclass of hand, for handling methods specific to the player."""
    name = "Player Hand"
    card_positions = [0, 1, 2, 3, 4, 5, 6, 7]
    def player_turn(self, dealer_hand):
        """Completes the player's turn by (repeatedly) asking for what action the player will do.
        Returns the player hand(s) (several may come from splitting) that will be evalutated compared 
        to the dealers hand. An empty list is returned if the hand is completed (if the player busts or
        surrenders).
        """
        while True:
            action = get_input(any=False, prompt="Hit or Stand? ").lower()
            if action == "hit":
                self.draw_card()
            elif action == "stand":
                return [self]
            elif action == "double down":
                global bet
                bet *= 2
                self.draw_card()
                if self.sum > 21:
                    self.push_results("bust")  
                    return []
                else:    
                    return [self]
            elif action == "split":
                if self.check_for_split():
                    return self.split_hand(dealer_hand)
                else:
                    lcd_blackjack.print_input("hand cannot be split")
            elif action == "surrender":
                self.push_results("surrender")
                return []
            else:
                print("invalid input")
            if self.sum > 21: 
                self.push_results("bust")    
                return []
    
    def check_results(self, dealer_hand):
        """Compares the sum of this player hand to the dealer's hand and pushes the corresponding result."""
        if dealer_hand.sum > 21 or self.sum > dealer_hand.sum:
            self.push_results("win")
        elif self.sum == dealer_hand.sum:
            self.push_results("push")
        else:
            self.push_results("lose")
        
    def push_results(self, result):
        global CARDS_DISPLAYED
        """Takes a result as an argument and changes the player's funds based on it."""
        global funds
        change = bet * PAYOUT_FACTORS[result]
        funds += change
        
        lcd_blackjack.print_results(result)
        light_strip.results[result]()
        
        time.sleep(1)
        
        lcd_blackjack.print_funds(change, funds)
        
        time.sleep(2)
        
        print("Reset")
        CARDS_DISPLAYED = False

    def check_blackjack(self, dealer_hand):
        """Called at the start of the hand, checks if the player has a blackjack and pushes results (for blackjack bonus)."""
        if self.sum == 21:
            dealer_hand.draw_card()
            if dealer_hand.sum == 21:
                self.push_results("push") 
            else:
                self.push_results("blackjack")
            return True

    def check_for_split(self):
        """Checks if the hand is able to be split."""
        return len(self.cards) == 2 and self._get_value(self.cards[0]["value"]) == self._get_value(self.cards[1]["value"])
        
    def split_hand(self, dealer_hand):
        """Returns two new hands, with a card from the orginal hand and a newly dealt card."""
        lcd_blackjack.print_input("Hand 1:")
        time.sleep(1)
        hand_1 = PlayerHand([self.cards[0]], 1).player_turn(dealer_hand)
        lcd_blackjack.print_input("Hand 2:")
        time.sleep(1)
        hand_2 = PlayerHand([self.cards[1]], 1).player_turn(dealer_hand)
        return hand_1 + hand_2

class DealerHand(Hand):
    """Subclass of hand, one is created per round to act as the dealer's hand."""
    name = "Dealer Hand"
    card_positions = [7, 6, 5, 4, 3, 2, 1, 0]
    def dealer_turn(self):
        """Completes the dealer's turn, drawing cards until the total is at least 17."""
        while self.sum < 17:
            self.draw_card()

def print_cards():
    lcd_blackjack.clear()

    player_location = 0
    dealer_location = 7
    player_card_number = len(player_hand.cards)
    dealer_card_number = len(dealer_hand.cards)
    total = player_card_number + dealer_card_number
    
    while total > 7:
        print("run")
        if player_card_number >= 4:
            print("player run")
            lcd_blackjack.print_quadruple(player_location, player_hand.cards)
            player_location += 1
            player_card_number -= 4
        else:
            lcd_blackjack.print_quadruple(dealer_location, dealer_hand.cards)
            dealer_location -= 1
            dealer_card_number -= 4
        total -= 3
            
        
    else:
        for card in player_hand.cards[player_location * 4:]:
            lcd_blackjack.print_card(player_location, card["code"][0], card["code"][1])
            player_location += 1
        for card in dealer_hand.cards[(7 - dealer_location) * 4:]:
            lcd_blackjack.print_card(dealer_location, card["code"][0], card["code"][1])
            dealer_location -= 1
        
    global CARDS_DISPLAYED
    CARDS_DISPLAYED = True



def display_card(position, code):
    lcd_blackjack.print_card(position, code[0], code[1])


def get_input(any, prompt):
    global CARDS_DISPLAYED
    """Used to get user input for their actions or starting a round, from the terminal or button depending on TERMINAL_PLAY"""
    if TERMINAL_PLAY:
        return input(prompt)
    else:
        button_blackjack.setup_input()
        light_strip.set_gradient()
        i = 0
        while not (output := button_blackjack.check_input(any)):
            if i % 20 == 0:
                light_strip.rotate()
            time.sleep(0.01)
            i += 1
        if any:
            print("Dealing")
            lcd_blackjack.print_input("Dealing...")
        else:
            lcd_blackjack.print_input(output)
            CARDS_DISPLAYED = False
        return output


def deal_cards():
    global CARDS_DISPLAYED
    """Creates the player and dealer hands at the start of the round, all cards are drawn at once then distruibuted for faster response time."""
    CARDS_DISPLAYED = False
    rq.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/shuffle/")
    cards = rq.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=3").json()["cards"]
    player_hand = PlayerHand(cards=cards[0:2])
    dealer_hand = DealerHand(cards=[cards[2]])
    return player_hand, dealer_hand

def set_bet():
    """Determines the players bet, which is capped at 20."""
    global bet, funds
    print(funds)
    if funds < 20:
        bet = funds
    else:
        bet = 20
    lcd_blackjack.print_input("Deal?")
    get_input(any=True, prompt="Deal? ")


def play_hand():
    global player_hand, dealer_hand
    """Main function, runs thorugh a single round."""
    player_hand, dealer_hand = deal_cards()
    print_cards()
    if not player_hand.check_blackjack(dealer_hand):
        player_hands = player_hand.player_turn(dealer_hand)
        if player_hands:
            dealer_hand.dealer_turn()
            for player_hand in player_hands:
                player_hand.check_results(dealer_hand)

if __name__ == "__main__":
    while True:
        set_bet()
        play_hand()
