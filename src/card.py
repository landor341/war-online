import math
import random
from enum import IntEnum



class Card():
    cards_per_class = 13
    suite_map = ('C', 'D', 'H', 'S')
    face_map = ['2', '3', '4', '5', '6', '7', '8', '9', "10", 'J', 'Q', 'K', 'A']

    def __init__(self, number):
        self.number = number
        self.face = Card.face_map[number % Card.cards_per_class]
        self.suite = Card.suite_map[math.floor(number / Card.cards_per_class)]

    def __eq__(self, other):
        if isinstance(other, bytes):
            return self.number.to_bytes() == other
        if isinstance(other, int):
            return self.number == other
        return self.number == other.number

    def __lt__(self, other):
        return self.number < other.number

    def __str__(self):
        return self.suite + self.face

    def __int__(self):
        return self.number

    def __index__(self):
        return self.__int__()

    def compare(self, other):
        return (self.number % Card.cards_per_class) - (other.number % Card.cards_per_class)

    def to_byte(self):
        return self.number.to_bytes()


def makeShuffledDeck():
    res = []
    for i in range(0,52):
        res.append(Card(i))
    random.shuffle(res)
    return res



def makeCardList(cardBytes):
    res = []
    for i in range(0, len(cardBytes)):
        res.append(Card(cardBytes[i]))
    return res

#test = Card(14)
#print(Card(5).to_byte())
#print(test.to_byte())
#print(test in makeCardList(((13 << 8) + 14).to_bytes(2)))
# for card in  makeCardList(((13 << 8) + 14).to_bytes(2)):
#    print(card, end=' ')
#for card in makeShuffledDeck():
#    print(card, end=' ')
'''
    The server will wait until it receives a start game request
        The server will create a shuffled deck then split it into two halfs
        The server will wait until it receives another start game request
        It will send each client a a deck on each thread
        The clients will receive their decks and use makeCardList to store them (after converting from bytes to ints)
        Each client will remove the 0th card and send it to the server
        The server will receive
    The server will send the result of the war back to the client
    ...

'''


# Header values
class Headers(IntEnum):
    WANT_GAME = 0
    START_GAME = 1
    PLAY_CARD = 2
    PLAY_RESULT = 3


# Play results
class Results(IntEnum):
    WIN = 0
    DRAW = 1
    LOSS = 2


DEFAULT_PAYLOAD = b'0'


