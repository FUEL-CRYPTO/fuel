"""
Fuel Wallet Miner Module

Controls the miner functionality

"""

import hashlib
import requests
import json
from time import time, sleep
from uuid import uuid4
import os
from decimal import *
from threading import Thread
from config import node_protocol, node_host, node_port, address, public_key, public_key_hash, difficulty_int, difficulty_string
from libs.Logger import logger

miner_threads = []
continue_running = False

class Miner(object):
    def proof_of_work(self, last_block):
        """
        proof_of_work(self, last_block):

        :param last_block: <dict> last Block
        :return: <int>

        Proof of work

        """

        last_proof = last_block['proof']
        last_hash = last_block['previous_hash']

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        valid_proof(last_proof, proof, last_hash)

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        Validates the Proof

        """

        guess = '{0}{1}{2}'.format(last_proof, proof, last_hash).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty_int] == difficulty_string

    def authoritative_node(self):
        """
        authoritative_node(self)

        :return:

        Return the authoritative node we should mine with

        """
        longest_chain_node = None
        longest_chain = 0

        nodes = requests.get('{0}://{1}:{2}/nodes'.format(node_protocol, node_host, node_port)).json()['nodes']
        #nodes.append('{0}:{1}'.format(node_host, node_port))

        for node in nodes:
            node_length = requests.get('{0}://{1}/length'.format(node_protocol, node)).json()['length']

            if node_length > longest_chain:
                longest_chain = node_length
                longest_chain_node = node

        return longest_chain_node

    def mine(self, address):
        """
        mine(self, address)

        :param address: <string> Wallet address to mine coins under
        :return:

        Mine coins for address

        """
        authoritative_node = self.authoritative_node()

        public_key = None
        wallets = json.loads(open('{0}/{1}'.format(os.getcwd(), 'wallets'), 'r').read())

        for a in wallets['wallets']:
            if address == a['address']:
                public_key = open(str(a['public_key']), 'r').read()

        last_block = requests.get('{0}://{1}/last_block'.format(node_protocol, authoritative_node)).json()
        proof = self.proof_of_work(last_block)

        submit_and_check = requests.post('{0}://{1}/submit_block'.format(node_protocol, authoritative_node),
                                         headers={"Content-Type": "application/json"},
                                         json={
                                                'solved_block': last_block,
                                                'proof_of_work': proof,
                                                'address': address,
                                                'public_key': str(public_key)
                                              }
                                         )

        submission_response = submit_and_check.json()

        self.run_miner(address)

    def run_miner(self, address):
        """
        run_miner(self)

        :return:

        Run the miner process

        """
        global continue_running
        if continue_running == True:
            process = Thread(target=self.mine, args=(address,))
            process.start()
            miner_threads.append(process)

    def start_mining(self, address):
        """
        start_mining(self)

        :return:

        Start the mining process thread

        """
        global continue_running
        print("Starting miner...")
        continue_running = True
        self.run_miner(address)

    def stop_mining(self):
        """
        stop_mining(self)

        :return:

        Stop the mining process thread

        """
        global continue_running
        continue_running = False
        print("Miner has been stopped!")

    def miner_status(self):
        return continue_running