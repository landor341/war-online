import socket

'''
    Open port and connect to ip/port that is passed in as parameter to main
    After establishing connection send 0000 packet to server
    Wait to receive packet of 01 followed by 26 card values (game start)
    Then send a play card (an 02 followed by a card value)
    Wait to receive result packets (03 followd by 00 if win 01 if draw 02 if loss)
    Then send a play card (an 02 followed by a card value)
    After 26 rounds close TCP connection with clients. Print out if you won or not.

'''

# Header values
class Headers(Enum):
    WANT_GAME = b'0'
    START_GAME = b'1'
    PLAY_CARD = b'2'
    PLAY_RESULT = b'3'

# Play results
class Results(Enum):
    WIN = b'0'
    DRAW = b'1'
    LOSS = b'2'

DEFAULT_PAYLOAD = b'0'


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    program_args = argument_parser.parse_args()
    # TODO: Get port number
    port_num = 20000
    server_port = 4444
    address = '127.0.0.1'

    s = socket.create_connection((address, server_port), source_address=(address, port_num))

    # Send 'want game' packet
    s.send(Headers.WANT_GAME + DEFAULT_PAYLOAD)

    # TODO: Listen for response with the 26 cards
    # TODO: Receive 26 cards and convert them into deck
    cards = []

    for card in cards:
        # Send one of the cards back to server
        s.send(Headers.PLAY_CARD + cards.pop())
        # TODO: Wait for response message
    # TODO: Close connection. Probably use 'with' statement



if __name__ == "__main__":
    main()
