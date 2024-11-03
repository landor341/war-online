import socket
import argparse

from card import *


'''
    Open port and connect to ip/port that is passed in as parameter to main
    After establishing connection send 0000 packet to server
    Wait to receive packet of 01 followed by 26 card values (game start)
    Then send a play card (an 02 followed by a card value)
    Wait to receive result packets (03 followd by 00 if win 01 if draw 02 if loss)
    Then send a play card (an 02 followed by a card value)
    After 26 rounds close TCP connection with clients. Print out if you won or not.

'''

VERBOSE = False
def verbosePrint(*values):
    if VERBOSE:
        print(*values)

def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("dest", nargs="+",
                                 help="ip address followed by port num")
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    args = argument_parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose
    # TODO: Get port number
    #port_num = 
    server_port = int(args.dest[1]) # TODO: Use argeparse properly for these
    address = args.dest[0]
    
    verbosePrint("STARTING CLIENT WITH IP ", address, " ON PORT ",  server_port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, server_port))

    # Send 'want game' packet
    s.send(Headers.WANT_GAME.to_bytes() + DEFAULT_PAYLOAD)

    verbosePrint("SENT START GAME PACKET")
    
    results = {
        "wins": 0,
        "ties": 0,
        "losses": 0
    }

    # TODO: Listen for response with the 26 cards
    p = s.recv(27)
    # TODO: Receive 26 cards and convert them into deck
    cards = makeCardList(p[1:])

    if args.verbose:
        print("RECEIVED DECK:", end=' ')
        for card in cards:
            print(card, end=' ')
        print()

    for card in cards:
        # Send one of the cards back to server
        bytes_to_send = Headers.PLAY_CARD.to_bytes() + card.to_byte()
        s.send(bytes_to_send)
        verbosePrint("PLAYED CARD: ", card, "BY SENDING PACKET", bytes_to_send)
        # Wait for response message
        p = s.recv(2)
        verbosePrint("RECEIVED PACKET: ", p)
        # TODO: Do packet validation
        if p[1] == int(Results.WIN):
            verbosePrint("ROUND WON")
            results["wins"] = results["wins"] + 1
        elif p[1] == int(Results.DRAW):
            results["ties"] = results["ties"] + 1
            verbosePrint("ROUND TIED")
        else:
            results["losses"] = results["losses"] + 1
            verbosePrint("ROUND LOST")
    
    # TODO: Close connection. Probably use 'with' statement
    s.close()
    if results["wins"] > 13 - results['ties']:
        verbosePrint("WON GAME WITH", results["wins"], "WINS")
    else:
        verbosePrint("LOST GAME WITH", results["wins"], "WINS")
    verbosePrint(results)

if __name__ == "__main__":
    main()
