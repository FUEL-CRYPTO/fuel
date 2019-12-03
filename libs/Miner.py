import logging
import hashlib
import requests
import json
from time import time, sleep
from uuid import uuid4
import os
from decimal import *
from threading import Thread
from config import node_host, address, public_key, public_key_hash


# Basic config for the logging logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('blockchain.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

difficulty_int = 5
difficulty_string = "00000"

miner_threads = []

continue_running = False

class Miner(object):
    def proof_of_work(self, last_block):
        """
        proof_of_work(self, last_block):

        :param last_block: <dict> last Block
        :return: <int>

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
        logger.debug("GUESS: {0} : GUESSED HASH: {1}".format(guess.decode('utf8'), guess_hash))
        return guess_hash[:difficulty_int] == difficulty_string

    def mine(self):
        last_block = requests.get('{0}/last_block'.format(node_host)).json()
        proof = self.proof_of_work(last_block)

        submit_and_check = requests.post('{0}/submit_block'.format(node_host),
                                         headers={"Content-Type": "application/json"},
                                         json={
                                                'solved_block': last_block,
                                                'proof_of_work': proof,
                                                'address': address,
                                                'public_key': str(public_key)
                                              }
                                         )

        submission_response = submit_and_check.json()

        self.run_miner()

    def run_miner(self):
        """
        run_miner(self)

        :return:

        Run the miner process

        """
        global continue_running
        if continue_running == True:
            process = Thread(target=self.mine)
            process.start()
            miner_threads.append(process)

    def start_mining(self):
        """
        start_mining(self)

        :return:

        Start the mining process thread

        """
        global continue_running
        print("Starting miner...")
        continue_running = True
        self.run_miner()

    def stop_mining(self):
        """
        stop_mining(self)

        :return:

        Stop the mining process thread

        """
        global continue_running
        continue_running = False
        print("Miner has been stopped!")