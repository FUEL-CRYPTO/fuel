"""
IntruKit Shell

This is the interactive command shell for IntruKit
"""

import os
import re
import subprocess
import requests
import json
from cmd import Cmd
from decimal import Decimal
from libs import Colors, ModuleHandler, Miner
from libs.Keys import create_address, check_keys, generate_key, generate_public_key, generate_private_key
from config import node_host, address, public_key, public_key_hash, currency_total_zero, currency_length_formatter

miner = Miner.Miner()
colors = Colors.Colors()

class Wallet(Cmd):
    def do_quit(self, args):
        """
        do_quit(self, args)

        :param args:
        :return:

        Exit the application

        """
        miner.stop_mining()
        print("Stopping the miner and {}exiting.\n{}".format(colors.FAIL, colors.ENDC))
        raise SystemExit

    def do_exit(self, args):
        """
        do_exit(self, args)

        :param args: None
        :return:

        Exit the wallet

        """
        miner.stop_mining()
        print("Stopping the miner and {}exiting.\n{}".format(colors.FAIL, colors.ENDC))
        raise SystemExit

    def do_help(self, args):
        """
        do_help(self, args)

        :param args: None
        :return:

        Print out help for the user

        """
        print("\n")
        print("Fuel Wallet Commands")
        print("===================================================================================================\n")
        print("     Command                              Description")
        print("     -------                              -----------")
        print("     balance                              Check current balance")
        print("     transaction <recipient> <amount>     Make a new transaction")
        print("     length                               Display the current blockchain length")
        print("     block                                Display a block in the blockchain")
        print("     last                                 Display the last block in the blockchain")
        print("     register_address                     Register an address and store it in the address.book")
        print("     start_miner                          Start mining for Fuel")
        print("     stop_miner                           Stop mining for Fuel")
        print("     update                               Update Fuel Wallet via git pull. Requires restart")
        print("     exit                                 Exit wallet")
        print("\n")

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

    def do_start_miner(self, args):
        """
        do_start_miner(self, args)

        :param args: None
        :return:

        Start the miner

        """
        miner.start_mining()

    def do_stop_miner(self, args):
        """
        do_stop_miner(self, args)

        :param args: None
        :return:

        Stop the miner

        """
        miner.stop_mining()

    def do_balance(self, args):
        """
        do_balance(self, args)

        :param args: None
        :return:

        Return the wallets account balance

        """
        total = currency_total_zero

        chain_req = requests.get('{0}/chain'.format(node_host))

        chain = chain_req.json()['chain']

        for block in chain:
            if len(block['transactions']) >= 1:
                for transaction in block['transactions']:
                    if transaction['recipient'] == address: #and transaction['hash'] == public_key_hash:
                        total = total + Decimal(transaction['amount'])
                    if transaction['sender'] == address: #and transaction['hash'] == public_key_hash:
                        total = total - Decimal(transaction['amount'])

        print(total)

    def do_block(self, args):
        """
        do_block(self, args)

        :param args: <block:int>
        :return:

        Return a block and print the JSON response

        """
        index = int(args) -1

        index_req = requests.post('{0}/block'.format(node_host),
                                  headers={"Content-Type": "application/json"},
                                  json={"index": int(index)})

        print(json.dumps(index_req.json(), indent=4, sort_keys=True))

    def do_length(self, args):
        """
        do_length(self, args)

        :param args: None
        :return:

        Print out the length of the blockchain

        """
        index_req = requests.get('{0}/length'.format(node_host))
        print(index_req.json()['length'])

    def do_last(self, args):
        """
        do_last(self, args)

        :param args: None
        :return:

        Return the last block of the blockchain and print the JSON response

        """
        index_req = requests.get('{0}/last_block'.format(node_host))
        print(json.dumps(index_req.json(), indent=4, sort_keys=True))

    def do_transaction(self, args):
        """
        do_transaction(self, args)

        :param args: <recipient> <amount>
        :return:

        Create a new transaction to send an amount of coin to a recipient

        """
        recipient = args.split(" ")[0]
        amount = args.split(" ")[1]

        index_req = requests.post('{0}/transactions/new'.format(node_host),
                                  headers={"Content-Type": "application/json"},
                                  json={"sender": address,
                                        "recipient": recipient,
                                        "amount": amount,
                                        "public_key": public_key
                                        }
                                  )

        print(index_req.json()['message'])

    def do_register_address(self, args):
        """
        do_register_address(self, args)

        :param args: None
        :return:

        Register a new address and store it in the address.book file. This also creates additional keys
        for use with the address.

        """
        create_address(os.path.abspath("./"))