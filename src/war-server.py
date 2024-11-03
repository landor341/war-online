import socket
import argparse
from _thread import *
import threading

from card import *
#a
'''
    Open port that is passed in as parameter to main
    Then wait until two TCP connections have been created by war-clients
    
    After receiving 0000 packets from two clients then
    First packet of game is 01 followed by 26 card values
    Then after receiving a play card from both clients (an 02 followed by a card value)
    Send a card result packets to both (03 followd by 00 if win 01 if draw 02 if loss)
    Then wait until next play card packet is received from both clients
    After 26 rounds close TCP connection with clients. No need to send a win message since they'll know if they kept track of the packets

'''

VERBOSE = False
def verbosePrint(*values):
    if VERBOSE:
        print(*values)

print_lock = threading.Lock()

def start_war_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', port))
        s.listen()
        verbosePrint("OPENED SERVER ON PORT", port)

        conn1, addr1 = s.accept()
        verbosePrint("CONNECTION RECEIVED WITH", addr1)
        conn2, addr2 = s.accept()
        verbosePrint("CONNECTION RECEIVED WITH", addr2)

        client1 = warClient(conn1)
        client2 = warClient(conn2)
        start_new_thread(client1.runClientThread, (1,))
        verbosePrint("FINISHED STARTING CLIENT1 THREAD")
        start_new_thread(client2.runClientThread, (2,))
        verbosePrint("FINISHED STARTING CLIENT2 THREAD")
        print_lock.acquire()

        movesRemaining = 26
        verbosePrint("Game thread started")

        # Wait until both clients have signaled to start game
        while not (client1.gameBeingPlayed and client2.gameBeingPlayed):
            pass

        # Give client threads data needed to send out decks
        deck = makeShuffledDeck()
        client1.deck = deck[0:26]
        client2.deck = deck[26:52]

        verbosePrint("Game STARTED")

        while movesRemaining != 0:
            verbosePrint("Game WAITING FOR CLIENTS TO RECEIVE CARDS")
            while client1.waitingForCard or client2.waitingForCard:
                pass
            verbosePrint("Game SENDING OUT ROUND RESULT WITH", movesRemaining, "ROUNDS REMAINING")
            # TODO: send both clients the result of the round
            if movesRemaining == 1:
                client1.gameBeingPlayed = False
                client2.gameBeingPlayed = False

            client1.setRoundResult(client1.curCard.compare(client2.curCard))
            client2.setRoundResult(client2.curCard.compare(client1.curCard))
            movesRemaining = movesRemaining - 1

        # TODO: End of game loop. Make sure both clients know to end game
        verbosePrint("Game ENDED")
        while (client1.wonLastRound is not None) or (client2.wonLastRound is not None):
            pass
        conn1.close()
        conn2.close()
        print_lock.release()


class warClient():
    def __init__(self, conn):
        self.conn = conn
        self.deck = None
        self.waitingForCard = True
        self.curCard = None
        self.gameBeingPlayed = False
        self.wonLastRound = None

    def receiveGameStart(self, lock):
        lock.acquire()
        # Wait to receive start game signal
        while not self.gameBeingPlayed:
            data = self.conn.recv(2)
            if data[0] == int(Headers.WANT_GAME):
                self.gameBeingPlayed = True
                lock.release()
                return

    def sendDeck(self, lock):
        lock.acquire()
        verbosePrint("Client" + str(id), "Sending deck")
        # Send deck
        self.conn.send(Headers.START_GAME.to_bytes() + bytearray(self.deck))
        lock.release()

    def receiveCardPlayed(self, lock):
        lock.acquire()
        while self.waitingForCard:
            data = self.conn.recv(2)
            verbosePrint("RECEIVED PACKET: ", data)
            if len(data) > 0 and data[0] == int(Headers.PLAY_CARD):
                verbosePrint("Client" + str(id), "Just received card ", self.curCard)
                lock.release()
                return Card(data[1])

    def sendPlayResult(self, lock):
        lock.acquire()
        bytes_to_send = (Headers.PLAY_RESULT.to_bytes() + bytearray([self.wonLastRound]))
        verbosePrint("Client" + str(id), "Sending packet to user:", bytes_to_send)
        self.conn.send(bytes_to_send)
        lock.release()


    def runClientThread(self, id):
        verbosePrint("Client" + str(id), "thread started")

        # Wait to receive start game signal
        while not self.gameBeingPlayed:
            data = self.conn.recv(2)
            if data[0] == int(Headers.WANT_GAME):
                self.gameBeingPlayed = True
                break

        # Wait for deck to be defined by warInstance
        while self.deck is None:
            pass

        verbosePrint("Client" + str(id), "Sending deck")
        # Send deck
        self.conn.send(Headers.START_GAME.to_bytes() + bytearray(self.deck))

        while self.gameBeingPlayed:
            while self.waitingForCard:
                data = self.conn.recv(2)
                verbosePrint("RECEIVED PACKET: ", data)
                if len(data) > 0 and data[0] == int(Headers.PLAY_CARD):
                    self.waitingForCard = False
                    self.curCard = Card(data[1])

            verbosePrint("Client" + str(id), "Just received card ", self.curCard)

            # Wait for warThread to send out result of the play
            while self.wonLastRound is None:
                pass

            bytes_to_send = (Headers.PLAY_RESULT.to_bytes() + bytearray([self.wonLastRound]))
            verbosePrint("Client" + str(id), "Sending packet to user:", bytes_to_send)
            self.conn.send(bytes_to_send)
            self.wonLastRound = None
        verbosePrint("Client" + str(id), "Ending")

    def setRoundResult(self, result):
        if result > 0:
            self.wonLastRound = Results.WIN
        elif result < 0:
            self.wonLastRound = Results.LOSS
        else:
            self.wonLastRound = Results.DRAW
        self.waitingForCard = True


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
