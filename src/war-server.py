import socket
import argparse
from _thread import *
import threading

import math
import random
from enum import IntEnum


def verbose_print(*values):
    if 'VERBOSE' in globals() and VERBOSE:
        print(*values)


print_lock = threading.Lock()


def start_war_server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', port))
    s.listen()
    conn1, addr1 = s.accept()
    verbose_print("CONNECTION STARTED: ", addr1)
    conn2, addr2 = s.accept()
    verbose_print("CONNECTION STARTED: ", addr2)

    try:
        verbose_print("SERVER STARTED: (port:", str(port) + ")")
        client1, client2 = WarClient(conn1, 1), WarClient(conn2, 2)

        client1.lockAndReceiveGameStart()
        client2.lockAndReceiveGameStart()
        client1.resolve()
        client2.resolve()
        verbose_print("Game: Starting game")

        moves_remaining = 26

        # Give client threads data needed to send out decks
        deck = makeShuffledDeck()
        client1.deck = deck[0:26]
        client2.deck = deck[26:52]

        client1.lockAndSendDeck()
        client2.lockAndSendDeck()
        client1.resolve()
        client2.resolve()
        verbose_print("Game: Decks transmitted")

        while moves_remaining != 0:
            verbose_print("Game: Waiting to receive moves")

            client1.lockAndReceiveCardPlayed()
            client2.lockAndReceiveCardPlayed()
            client1.resolve()
            client2.resolve()

            if client1.curCard in client1.playedCards or client2.curCard in client2.playedCards:
                raise ValueError("Card that was already played was sent")

            client1.setRoundResult(client1.curCard.compare(client2.curCard))
            client2.setRoundResult(client2.curCard.compare(client1.curCard))

            verbose_print("Game: Round", str(moves_remaining) + ": comp(c1, c2) =", client1.curCard.compare(client2.curCard))

            client1.waitAndSendPlayResult()
            client2.waitAndSendPlayResult()
            client1.resolve()
            client2.resolve()

            moves_remaining = moves_remaining - 1

        verbose_print("Game: Game Over")
        conn1.close()
        conn2.close()
    except TimeoutError as e:
        print("Caught timeout condition")
        print(e)
    except ValueError as e:
        print("Caught illegal value error")
    finally:
        conn1.close()
        conn2.close()
        s.close()


class WarClient:
    def __init__(self, conn, id):
        self.conn = conn
        self.deck = None
        self.playedCards = []
        self.curCard = None
        self.wonLastRound = None
        self.lock = threading.Lock()
        self.id = id
        self.flag = True

    def resolve(self):
        if not self.lock.acquire():
            raise TimeoutError("Timed out")
        if not self.flag:
            raise ValueError("Illegal data received")
        self.lock.release()

    def releaseLock(self):
        return self.lock.release()

    def lockAndReceiveGameStart(self):
        def getGameStart():
            # Wait to receive start game signal
            data = self.conn.recv(2)
            if len(data) == 2 and data[0] == int(Headers.WANT_GAME):
                pass
            else:
                self.flag = False
            self.releaseLock()

        self.lock.acquire()
        start_new_thread(getGameStart, ())

    def lockAndSendDeck(self):
        def sendDeck():
            verbose_print("Client" + str(self.id) + ":", "Sending deck")
            # Send deck
            self.conn.send(Headers.START_GAME.to_bytes(1, 'big') + bytearray(self.deck))
            self.releaseLock()

        self.lock.acquire()
        start_new_thread(sendDeck, ())

    def lockAndReceiveCardPlayed(self):
        flag = True
        def getCardPlayed():
            data = self.conn.recv(2)
            if len(data) == 2 and data[0] == int(Headers.PLAY_CARD):
                verbose_print("Client" + str(self.id) + ":", "Received card ", self.curCard)
                try:
                    self.curCard = Card(data[1])
                except ValueError:
                    self.flag = False
            else:
                self.flag = False
            self.releaseLock()

        self.lock.acquire()
        start_new_thread(getCardPlayed, ())


    def waitAndSendPlayResult(self):
        def getPlayResult():
            bytes_to_send = (Headers.PLAY_RESULT.to_bytes(1, 'big') + bytearray([self.wonLastRound]))
            verbose_print("Client" + str(self.id) + ":", "Sending packet to user:", bytes_to_send)
            self.conn.send(bytes_to_send)
            self.releaseLock()

        self.lock.acquire()
        start_new_thread(getPlayResult, ())

    def setRoundResult(self, result):
        if result > 0:
            self.wonLastRound = Results.WIN
        elif result < 0:
            self.wonLastRound = Results.LOSS
        else:
            self.wonLastRound = Results.DRAW
        self.playedCards.append(self.curCard)


class Card():
    cards_per_class = 13
    suite_map = ('C', 'D', 'H', 'S')
    face_map = ['2', '3', '4', '5', '6', '7', '8', '9', "10", 'J', 'Q', 'K', 'A']

    def __init__(self, number):
        if number >= 52 or number < 0:
            raise ValueError("Cannot create card not in range [0,52]")
        self.number = number
        self.face = Card.face_map[number % Card.cards_per_class]
        self.suite = Card.suite_map[math.floor(number / Card.cards_per_class)]

    def __eq__(self, other):
        if isinstance(other, bytes):
            return self.number.to_bytes(1, 'big') == other
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
        return self.number.to_bytes(1, 'big')


def makeShuffledDeck():
    res = []
    for i in range(0,52):
        res.append(Card(i))
    random.shuffle(res)
    return res


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


def main():
    """
    Get server port and start listening
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("port", nargs="+", help="The port to run the server from")
    argument_parser.add_argument("-v", "--verbose", help="incrase verbosity output", action="store_true")
    args = argument_parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose
    start_war_server(int(args.port[0]))


if __name__ == "__main__":
    main()
