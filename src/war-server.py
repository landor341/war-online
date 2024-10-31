import socket
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

def start_war_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind('127.0.0.1', port)
        s.listen(2)
        conn1, addr1 = s.accept()
        conn2, addr2 = s.accept()
        with conn1, conn2:
            pass
            # TODO: Wait for both to ask for new game
            # TODO: Make new deck, split it into two
            # TODO: Send each connection half the deck
            # Enter loop of 26 rounds
                # TODO: Create two threads that return once both connections sent back a card
                # TODO: Save the cards sent to do cheating detection
                # TODO: Save the result of the cards given
                # TODO: Send respective result back to each connection
            # TODO: Close connections. Should happend automatically because of 'with' block



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
    for a_domain_name in program_args.name:
        print_results(collect_results(a_domain_name))


if __name__ == "__main__":
    main()
