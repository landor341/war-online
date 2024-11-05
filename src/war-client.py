import socket
import argparse

import math
from enum import IntEnum


def verbosePrint(*values):
    if 'VERBOSE' in globals() and VERBOSE:
        print(*values)


def run_war_client(addr, server_port):
    verbosePrint("Starting Connection: ( addr,", addr, ") ( port,",  server_port, ")")

    results = {
        "wins": 0,
        "ties": 0,
        "losses": 0
    }

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((addr, server_port))
        s.send(Headers.WANT_GAME.to_bytes(1, 'big') + DEFAULT_PAYLOAD)
        verbosePrint("Started Game")

        p = s.recv(27)
        if len(p) < 27 or p[0] != int(Headers.START_GAME):
            raise ValueError()

        cards = makeCardList(p[1:])

        if 'VERBOSE' in globals() and VERBOSE:
            print("Deck:", end=' ')
            for card in cards:
                print(card, end=' ')
            print()

        for card in cards:
            # Send one of the cards back to server
            bytes_to_send = Headers.PLAY_CARD.to_bytes(1, 'big') + card.to_byte()

            # bytes_to_send = Headers.PLAY_CARD.to_bytes(1, 'big') + (255).to_bytes(1, 'big') # For testing illegal data
            # bytes_to_send = Headers.PLAY_CARD.to_bytes(1, 'big') + cards[0].to_byte() # For testing malformed data
            # return s.close() # For testing client ending early
            # bytes_to_send = Headers.PLAY_CARD.to_bytes(1, 'big') # For testing missing data

            s.send(bytes_to_send)
            verbosePrint("played: ", card, "    by sending data: ", bytes_to_send)
            # Wait for response message
            p = s.recv(2)
            if len(p) < 2 or p[0] != int(Headers.PLAY_RESULT):
                raise ValueError()
               
            if p[1] == int(Results.WIN):
                verbosePrint("Win")
                results["wins"] = results["wins"] + 1
            elif p[1] == int(Results.DRAW):
                results["ties"] = results["ties"] + 1
                verbosePrint("Tie")
            else:
                results["losses"] = results["losses"] + 1
                verbosePrint("Loss")
            
        if results["wins"] > 13 - results['ties']:
            verbosePrint("won with", results["wins"], "wind")
        else:
            verbosePrint("failed to win with", results["wins"], "wins")
        verbosePrint(results)
    except TimeoutError as e:
        verbosePrint("Caught timeout error in client")
    except ValueError as e:
        verbosePrint("Caught value error in client")
    finally:
        s.close()


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


def makeCardList(cardBytes):
    res = []
    for i in range(0, len(cardBytes)):
        res.append(Card(cardBytes[i]))
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


DEFAULT_PAYLOAD = b'0'

def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("dest", type=str)
    argument_parser.add_argument("port", type=int)
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    args = argument_parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose
    run_war_client(args.dest, int(args.port))


if __name__ == "__main__":
    main()
