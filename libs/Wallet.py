"""
Fuel Wallet Module

Controls the wallet functionality

"""

import os
import re
import subprocess
import requests
import json
import random
import hashlib
from cmd import Cmd
from decimal import Decimal
from time import sleep
from libs import Colors, Miner, Banners
from libs.Keys import create_address, check_keys, generate_key, generate_public_key, generate_private_key
from config import app_name, node_protocol, node_host, node_port, wallets, address, miners, public_key, public_key_hash, \
    currency_total_zero, currency_length_formatter, difficulty_int
from libs.Logger import logger
from libs.Functions import authoritative_node

miner = Miner.Miner()
colors = Colors.Colors()

blockchain_proc = None

class Wallet(Cmd):
    #################################################################################################
    # Help Functionality
    #
    # help            : Print out help for the user
    #
    #
    #################################################################################################

    def do_help(self, args):
        """
        do_help(self, args)

        :param args: None
        :return:

        Print out help for the user

        """
        print("\n")
        print("Fuel Blockchain Commands")
        print("===================================================================================================\n")
        print("     Command                                Description")
        print("     -------                                -----------")
        print("     authoritative                          Display the authoritative node")
        print("     blockchain <start|stop|status>         Manage the blockchain process")
        print("     block <index>                          Display a block in the blockchain")
        print("     last                                   Display the last block in the blockchain")
        print("     length                                 Display the current blockchain length")
        print("     nodes                                  Display the list of nodes connected to the network")
        print("     register <protocol>://<ip>:<port>      Register a new node on the blockchain network")
        print("\n")
        print("Fuel Wallet Commands")
        print("===================================================================================================\n")
        print("     Command                                Description")
        print("     -------                                -----------")
        print("     balance <address>                      Check current balance of wallet address")
        print("     transaction <recipient> <amount>       Make a new transaction")
        print("     create                                 Create a new wallet.")
        print("     set_address <address>                  Set the wallet default address to be used")
        print("     wallets                                Display the wallet")
        print("     wstats                                 Display the address in use by the wallet")
        print("\n")
        print("Fuel Miner Commands")
        print("===================================================================================================\n")
        print("     Command                                Description")
        print("     -------                                -----------")
        print("     miner <start|stop|status> <address>    Manage the miners. If 'start' <address> is required")
        print("\n")
        print("Fuel CLI Commands")
        print("===================================================================================================\n")
        print("     Command                                Description")
        print("     -------                                -----------")
        print("     banner                                 Display the Fuel banner with statistics")
        print("     update                                 Update Fuel Wallet via git pull. Requires restart")
        print("     exit                                   Exit wallet")
        print("\n\n")

    #################################################################################################
    # Blockchain Functionality
    #
    # authoritative   : Display the authoritative node
    # blockchain      : Manage the blockchain process
    # block           : Return a block and print the JSON response
    # last            : Return the last block of the blockchain and print the JSON response
    # length          : Return the length of the blockchain
    # nodes           : Display the list of nodes connected to the network
    # register        : Register a new node
    #
    #################################################################################################
    def do_blockchain(self, args):
        """
        do_blockchain(self, args)

        :param args: <start|stop|status>
        :return:

        Manage the blockchain process

        """
        global blockchain_proc

        if not args:
            args = input("start|stop|status: ")

        if args == "start":
            print("Starting blockchain...")
            f = open("blockchain.log", "wb")
            blockchain_proc = subprocess.Popen(["python3", "blockchain.py"], cwd="./", stdout=f, stderr=f)
        elif args == "stop":
            blockchain_proc.kill()
            print("Blockchain has been stopped!")
        elif args == "status":
            print(blockchain_proc)

    def do_block(self, args):
        """
        do_block(self, args)

        :param args: <block:int>
        :return:

        Return a block and print the JSON response

        """
        if not args:
            args = input("Block: ")

        index = int(args)

        index_req = requests.post('{0}://{1}:{2}/block'.format(node_protocol, node_host, node_port),
                                  headers={"Content-Type": "application/json"},
                                  json={"index": int(index)})

        print(json.dumps(index_req.json(), indent=4, sort_keys=True))

    def do_last(self, args):
        """
        do_last(self, args)

        :param args: None
        :return:

        Return the last block of the blockchain and print the JSON response

        """
        index_req = requests.get('{0}://{1}:{2}/last_block'.format(node_protocol, node_host, node_port))
        print(json.dumps(index_req.json(), indent=4, sort_keys=True))

    def do_length(self, args):
        """
        do_length(self, args)

        :param args: None
        :return:

        Return the length of the blockchain

        """
        auth_node = authoritative_node()
        local_node_index_req = requests.get('{0}://{1}:{2}/length'.format(node_protocol, node_host, node_port))
        auth_node_index_req = requests.get('{0}://{1}/length'.format(node_protocol, auth_node))
        print(f"Local Node: {local_node_index_req.json()['length']}")
        print(f"Authoritative Node: {auth_node_index_req.json()['length']}")

    def do_register(self, args):
        """
        do_register(self, args)

        :param args: <url>
        :return:

        Register a new node

        """
        if not args:
            args = input("URL ({0}://123.123.123.123:5000): ".format(node_protocol))

        register_node_req = requests.post('{0}://{1}:{2}/nodes/register'.format(node_protocol, node_host, node_port),
                                          headers={"Content-Type": "application/json"},
                                          json={"nodes": ["{0}".format(args)]})

        print(json.dumps(register_node_req.json(), indent=4, sort_keys=True))

    def do_nodes(self, args):
        """
        do_nodes(self, args)

        :param args: <url>
        :return:

        Display the list of nodes connected to the network

        """
        # Find the authoritative node
        longest_chain_node = None
        longest_chain = 0

        nodes = requests.get('{0}://{1}:{2}/nodes'.format(node_protocol, node_host, node_port)).json()['nodes']
        #nodes.append('{0}:{1}'.format(node_host, node_port))

        for node in nodes:
            node_length = requests.get('{0}://{1}/length'.format(node_protocol, node)).json()['length']

            if node_length > longest_chain:
                longest_chain = node_length
                longest_chain_node = node

        # Get this list of nodes from the authoritative node
        registered_nodes = requests.get('{0}://{1}/nodes'.format(node_protocol, longest_chain_node))

        print(json.dumps(registered_nodes.json(), indent=4, sort_keys=True))

    def do_authoritative(self, args):
        """
        do_authoritative(self, args)

        :param args: <url>
        :return:

        Display the list of nodes connected to the network

        """
        longest_chain_node = authoritative_node()
        print("Authoritative Node: {0}".format(longest_chain_node))

    #################################################################################################
    # Wallet Functionality
    #
    # wallets         : Display the wallet
    # balance         : Return the wallets account balance
    # create          : Create a new wallet.
    # set_address     : Set the wallet default address to be used
    # transaction     : Create a new transaction to send an amount of coin to a recipient
    # wstats          : Display the address in use by the wallet
    #################################################################################################

    def do_balance(self, args):
        """
        do_balance(self, args)

        :param args: <string> Address to check balance for
        :return:

        Return the wallets account balance

        """
        if not args:
            args = input("Address: ")

        total = Decimal(currency_total_zero)

        chain_req = requests.get('{0}://{1}:{2}/chain'.format(node_protocol, node_host, node_port))

        chain = chain_req.json()['chain']

        for block in chain:
            if len(block['transactions']) >= 1:
                for transaction in block['transactions']:
                    if transaction['recipient'] == args: #and transaction['hash'] == public_key_hash:
                        total = total + Decimal(transaction['amount'])
                    if transaction['sender'] == args: #and transaction['hash'] == public_key_hash:
                        total = total - Decimal(transaction['amount'])

        print("Balance: {0}".format(total))

    def do_create(self, args):
        """
        do_create(self, args)

        :param args: None
        :return:

        Create a new wallet.

        Register a new address and store it in the wallets file.
        This also creates additional keys for use with the wallet address.

        """
        create_address(os.path.abspath("./"))

    def do_set_address(self, args):
        """
        do_set_address(self, args)

        :param args:
        :return:

        Set the wallet address to be used by the wallet

        """
        global wallets
        global address
        global public_key
        global public_key_hash

        if not args:
            print("Please supply the address to set as the current wallet default address")
            return

        index = 0

        wallets = json.loads(open('{0}/{1}'.format(os.getcwd(), 'wallets'), 'r').read())

        for address in wallets['wallets']:
            if args == address['address']:
                break
            index += 1

        address = wallets['wallets'][index]['address']

        public_key = open(str(wallets['wallets'][index]['public_key']), 'r').read()
        public_key_hash = hashlib.sha256(
            open(str(wallets['wallets'][index]['public_key']), 'r').read().encode()).hexdigest()

    def do_transaction(self, args):
        """
        do_transaction(self, args)

        :param args: <recipient> <amount>
        :return:

        Create a new transaction to send an amount of coin to a recipient

        """
        recipient = None
        amount = None

        if not args:
            recipient = input("Recipient Account: ")
            amount = input("Amount: ")

        else :
            recipient = args.split(" ")[0]
            amount = args.split(" ")[1]

        auth_node = authoritative_node()

        index_req = requests.post('{0}://{1}/transactions/new'.format(node_protocol, auth_node),
                                  headers={"Content-Type": "application/json"},
                                  json={"sender": address,
                                        "recipient": recipient,
                                        "amount": amount,
                                        "public_key": public_key
                                        }
                                  )

        print(index_req.json()['message'])

    def do_wallets(self, args):
        """
        do_wallet(self, args)

        :param args:
        :return:

        Display the wallet

        """
        global wallets
        wallets = json.loads(open('{0}/{1}'.format(os.getcwd(), 'wallets'), 'r').read())
        print(json.dumps(wallets, indent=4, sort_keys=True))

    def do_wstats(self, args):
        """
        do_wallet(self, args)

        :param args:
        :return:

        Display the address in use by the wallet

        """
        global wallets
        global address
        global public_key
        global public_key_hash

        wallets = json.loads(open('{0}/{1}'.format(os.getcwd(), 'wallets'), 'r').read())

        for page in wallets['wallets']:
            if address == page['address']:
                print("")
                print("Address: {0}".format(page['address']))
                print("Public Key: {0}".format(page['public_key']))
                print("Private Key: {0}".format(page['private_key']))
                print("Public Key Hash: {0}".format(hashlib.sha256(open(str(
                    page['public_key']), 'r').read().encode()).hexdigest()))
                self.do_balance(page['address'])
                print("")

    #################################################################################################
    # Miner Functionality
    #
    # miner           : Manage the miner thread
    #
    #################################################################################################

    def do_miner(self, args):
        """
        do_start_miner(self, args)

        :param args: None
        :return:

        Start, status or view the status of the miner

        """
        do = None
        address = None

        if not args:
            do = input("start|stop|status: ")
            if do == "start":
                address = input("Account: ")
        else:
            do = args.split(" ")[0]
            if do == "start":
                address = args.split(" ")[1]

        if do == "start":
            args.split(" ")[1]
            miner.start_mining(address)
        elif do == "stop":
            miner.stop_mining()
        elif do == "status":
            print("Miner Running: {0}".format(miner.miner_status()))

    #################################################################################################
    # CLI Functionality
    #
    # banner          : Display the Fuel banner with statistics
    # exit            : Exit/Quit the wallet
    # quit            : Exit/Quit the wallet
    # update          : Automagically update the Fuel Wallet by performing a "git pull" if the app was cloned from repo
    #
    #################################################################################################

    def do_banner(self, args):
        """
        do_banner(self, args)

        :param args:
        :return:

        Display the Fuel banner with statistics

        """
        nodes = len(requests.get('{0}://{1}:{2}/nodes'.format(node_protocol, node_host, node_port)).json()['nodes'])
        length = requests.get('{0}://{1}:{2}/length'.format(node_protocol, node_host, node_port)).json()['length']
        miners = 0
        circu = requests.get('{0}://{1}:{2}/circulation'.format(node_protocol, node_host, node_port)
                             ).json()['circulation']

        try:
            #n = random.randint(0, 2)
            print("{0}\n\n".format(Banners.banner.format(length, nodes, miners, circu, difficulty_int)))
        except:
            pass

    def do_exit(self, args):
        """
        do_exit(self, args)

        :param args: None
        :return:

        Exit the wallet

        """
        status = requests.get('{0}://{1}:{2}/status'.format(node_protocol, node_host, node_port)).text

        if status != "RESOLVING":
            print("{0}Stopping the miner....{1}".format(colors.FAIL, colors.ENDC))
            miner.stop_mining()
            global blockchain_proc

            sleep(5)

            if blockchain_proc:
                blockchain_proc.terminate()
                print("Blockchain has been stopped!")

            sleep(2)

            raise SystemExit
        else:
            print("Blockchain is currently being resolved and saved. Please try again in few moments.")

    def do_quit(self, args):
        """
        do_quit(self, args)

        :param args:
        :return:

        Exit the application

        """
        status = requests.get('{0}://{1}:{2}/status'.format(node_protocol, node_host, node_port)).text

        if status != "RESOLVING":
            print("{0}Stopping the miner...{1}".format(colors.FAIL, colors.ENDC))
            miner.stop_mining()
            global blockchain_proc

            sleep(5)

            if blockchain_proc:
                blockchain_proc.terminate()
                print("Blockchain has been stopped!")

            sleep(2)

            raise SystemExit
        else:
            print("Blockchain is currently being resolved and saved. Please try again in few moments.")

    def do_update(self, args):
        """
        do_update(self, args)

        :param args: None
        :return:

        Automagically update the Fuel Wallet by performing a "git pull" if the app was cloned from repo

        """
        print("\n")
        print("Fuel Wallet Update")
        print("========================\n")
        print(subprocess.check_output("git pull", shell=True).decode('utf-8'))
        print("Please exit and restart the application.")
        print("\n")

