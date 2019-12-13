#!/usr/bin/python3

import os
from os import listdir, system
from os.path import isfile, join, exists
from libs.Keys import check_keys
check_keys(os.path.dirname(os.path.realpath(__file__)))

from libs.Logger import logger
from libs import Banners, AESCipher
import hashlib
import json
from time import time, sleep
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
from config import app_name, blockchain_aes_key, backup_storage_dir, backup_file_prefix, blocks_per_backup_file, \
    node_host, node_port, blockchain_address, blockchain_public_key_hash, currency_total_zero, \
    currency_length_formatter, reward, difficulty_string, difficulty_int, miners
import threading
from decimal import *

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

cipher = AESCipher.AESCipher(blockchain_aes_key)

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        register_node(self, address)

        :param address: Address of node. Eg. 'http://<server-ip>:<port>'

        Add a new node to the list of nodes

        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
        """
        valid_chain(self, chain)

        :param chain: A blockchain
        :return: True if valid, False if not

        Determine if a given blockchain is valid

        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            logger.info('{0}'.format(last_block))
            logger.info('{0}'.format(block))
            logger.info("-----------")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        resolve_conflicts(self)

        :return: True if our chain was replaced, False if not

        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                # TODO : Resolve bug in valid_chain preventing true authoritative chain.
                if length > max_length:# and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        new_block(self, proof, previous_hash)

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block

        Create a new Block in the Blockchain

        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount, hash):
        """
        new_transaction(self, sender, recipient, amount, hash)

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :param hash: Owners public key hash value
        :return: The index of the Block that will hold this transaction

        Creates a new transaction to go into the next mined Block

        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': currency_length_formatter.format(Decimal(amount)),
            'hash': hash
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        """
        last_block(self)

        :return:

        Returns the last block in the blockchain

        """
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        proof_of_work(self, last_block):

        :param last_block: <dict> last Block
        :return: <int>

        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

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

    #################################################################################################
    # Backup and Key Functions
    #
    # backup_chain              : Backup the blockchain.chain in increments set by the value
    #                             of blocks_per_backup_file
    #
    #################################################################################################

    def backup_chain(self):
        """
        backup_chain()

        :return:

        Backup the blockchain.chain on a 10 second interval

        """
        blockchain.resolve_conflicts()

        threading.Timer(10.0, self.backup_chain).start()

        total_saved = 0
        saved_blocks = 0
        already_saved = []
        total_blocks = len(blockchain.chain)

        # Count how many files are in storage/*
        f_count = 0

        logger.debug("Running backup thread")

        # A list of the files in storage/
        chain_files = [f for f in listdir(backup_storage_dir) if str(f).find('chain_') != -1]
        logger.debug("chain_files: {0}".format(chain_files))

        for f in chain_files:
            argh = open('{0}{1}'.format(backup_storage_dir, f), 'r')
            already_saved = argh.readlines()

            if len(chain_files) > 1:
                f_count = len(chain_files) - 1
            elif len(chain_files) == 1:
                f_count = 0
            else:
                f_count = len(chain_files)

            for line in already_saved:
                total_saved += 1
                argh.close()

        if total_blocks != total_saved:
            try:
                # logger.info("Opening : storage/chain_{0}".format(f_count))
                check_blocks_file = open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'r+')
            except:
                # logger.info("Creating & Opening: storage/chain_{0}".format(f_count))
                open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'x')
                check_blocks_file = open('{0}{1}{2}'.format(backup_storage_dir,
                                                            backup_file_prefix,
                                                            f_count), 'r+')

            # Get number of blocks in the current file storage/chain[f_count] file
            saved_blocks = len(check_blocks_file.readlines())
            logger.debug('saved_blocks: {0}'.format(saved_blocks))

            if saved_blocks >= blocks_per_backup_file:
                f_count += 1

            check_blocks_file.close()

            if saved_blocks > blocks_per_backup_file:
                f_count += 1

            if saved_blocks > blocks_per_backup_file:
                logger.info("Setting saved_blocks to 0")
                saved_blocks = 0

            logger.debug('total_blocks: {0} total_saved: {1}'.format(total_blocks, total_saved))
            logger.debug('check_blocks_file: {0}'.format('{0}{1}{2}'.format(backup_storage_dir,
                                                                            backup_file_prefix,
                                                                            f_count)))

            logger.debug('check_blocks % blocks_per_backup_file: {0}'.format(saved_blocks % blocks_per_backup_file))

            backup = None

            if saved_blocks % blocks_per_backup_file != 0 and saved_blocks < blocks_per_backup_file:
                logger.debug("Opening : {0}{1}{2}".format(backup_storage_dir,
                                                          backup_file_prefix,
                                                          f_count))

                backup = open('{0}{1}{2}'.format(backup_storage_dir,
                                                 backup_file_prefix,
                                                 f_count), 'r+')

                if len(backup.readlines()) >= blocks_per_backup_file:
                    backup.close()
                    f_count += 1
                    open('{0}{1}{2}'.format(backup_storage_dir,
                                            backup_file_prefix,
                                            f_count), 'x')

                    backup = open('{0}{1}{2}'.format(backup_storage_dir,
                                                     backup_file_prefix,
                                                     f_count), 'r+')
            elif saved_blocks <= blocks_per_backup_file:
                try:
                    logger.debug("Opening from try: {0}{1}{2}".format(backup_storage_dir, backup_file_prefix, f_count))
                    open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'x')
                    backup = open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'r+')
                except:
                    logger.debug(
                        "Opening from except: {0}{1}{2}".format(backup_storage_dir, backup_file_prefix, f_count))
                    backup = open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'r+')
            else:
                f_count += 1
                logger.debug("Creating & Opening : {0}{1}{2}".format(backup_storage_dir,
                                                                     backup_file_prefix,
                                                                     f_count))

                open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'x')

                backup = open('{0}{1}{2}'.format(backup_storage_dir, backup_file_prefix, f_count), 'r+')

            # Add blocks to the storage/chain_[f_count] file
            for link in blockchain.chain[total_saved:]:
                logger.debug("New blockchain.chain transactions: {0}".format(blockchain.chain[saved_blocks:]))
                logger.debug("backup.readlines: {0}".format(backup.readlines()))
                # try:
                # if link not in already_saved:
                if link not in backup.readlines() and link not in already_saved:
                    backup.write("{0}\n".format(cipher.encrypt("{0}".format(link))))
                    # backup.write("{0}\n".format("{0}".format(link)))
                    saved_blocks += 1
                    total_saved += 1
                    # If we have N lines (blocks_per_backup_file) in the file break and start over
                    if (saved_blocks % blocks_per_backup_file) == 0:
                        return
                # except Exception as e:
                #    logger.error(e)

                logger.debug('saved_blocks: {0} total_blocks: {1} total_saved: {2}'.format(saved_blocks,
                                                                                           total_blocks,
                                                                                           total_saved))

                if total_saved == total_blocks:
                    run = False
                    backup.close()
                    return

            backup.close()

    def restore_chain(self):
        """
        restore_chain()

        :return:

        Restores the blockchain.chain from files stored in the storage directory.
        File names are configured in the config.py file. backup_file_prefix

        """
        chain_files = [f for f in listdir(backup_storage_dir) if str(f).find(backup_file_prefix) != -1]
        chain_files.sort()
        restore = []

        for f in chain_files:
            fh = open('{0}{1}'.format(backup_storage_dir, f), 'r')

            imported_chain = fh.readlines()

            if len(imported_chain) >= 1:
                for line in imported_chain:
                    line = cipher.decrypt(line)
                    restore.append(json.loads(line.replace("\n", "").replace("'", '"')))
        if len(restore) >= 1:
            blockchain.chain = restore

    def total_coin(self):
        """
        total_coin(self)

        :return:

        Return the blockchain's total coin in circulation

        """
        chain = blockchain.chain
        length = len(blockchain.chain)
        total = Decimal(currency_total_zero)

        for link in chain:
            if len(link['transactions']) >= 1:
                for transaction in link['transactions']:
                    if transaction['sender'] == "0":  # and transaction['hash'] == node_public_key_hash:
                        total = total + Decimal(transaction['amount'])

        return currency_length_formatter.format(total)

# Instantiate the Node
app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain()

#################################################################################################
# Before Request
#
# before_request_func          : Deny any requests that we do not have a route for
#
#################################################################################################

@app.before_request
def before_request_func():
    logger.info(request.path)
    print(request.path)
    routes = ['/mine', '/submit_block', '/transactions/new', '/chain', '/block', '/length', '/nodes', '/nodes/register',
              '/nodes/resolve', '/account/balance', '/account/register_address', '/last_block', '/circulation']

    if request.path not in routes:
        return "Invalid route."

#################################################################################################
# Chain Routes
#
# /chain          : Return the full blockchain.chain
#
#################################################################################################

@app.route('/chain', methods=['GET', 'POST'])
def get_chain():
    """
    get_chain()

    :return: JSON response

    Return a the full chain and chain length if the request comes from another node.
    If the request comes from a wallet or API user, return the modified chain, hiding the public key hashes

    """

    values = request.get_json()

    if values is None or len(values) == 0:
        # Return the full chain
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200
    else:
        # Return the next 100 results starting at the value of index
        response = {
            'chain': blockchain.chain[int(values['index']):int(values['index'])+500],
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200

#################################################################################################
# Nodes Routes
#
# /nodes/hosts        : Return the registered nodes
# /nodes/resolve      : Consensus; Resolve conflicts between nodes
# /nodes/register     : Register a new node to the blockchain
#
#################################################################################################

@app.route('/nodes', methods=['GET'])
def nodes():
    lst = []
    for n in blockchain.nodes:
        lst.append(n)

    logger.info(blockchain.nodes)

    response = {
        "nodes": lst
    }
    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    consensus()

    :return:

    Consensus algorithm. Calls resolve_conflicts()

    """
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    register_node()

    :nodes: A list of nodes. Ex: ['http://1.2.3.4:5000', 'http://5.6.7.8:5000']
    :return: JSON response

    Add a new node to our list of nodes

    """
    values = request.get_json()

    nodes = values.get('nodes')

    print(nodes)

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

#################################################################################################
# Local Mining Routes
#
# /mine       : Mine blocks locally on the server; This should be removed and only used for
#               coin node ownership and creating the circulation limit.
#
#################################################################################################

@app.route('/mine', methods=['GET'])
def mine():
    """
    mine()

    :return: JSON response

    Mine and forge a new block. Give miner (node) a coin for reward

    """
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=blockchain_address,
        amount=currency_length_formatter.format(Decimal(reward)),
        hash=blockchain_public_key_hash,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

#################################################################################################
# Block Routes
#
# /block          : Return N block
# /last_block     : Return the last block
# /length         : Return the chain length. N blocks
# /submit_block   : Submit a block via mining
# /circulation    : Return the blockchains total coin in circulation
#
#################################################################################################

@app.route('/block', methods=['POST'])
def get_block():
    """
    get_block()

    :return: JSON response

    Return a the block index from chain

    """
    values = request.get_json()
    index_num = int(values.get('index')) - 1
    return jsonify(blockchain.chain[index_num]), 200

@app.route('/last_block', methods=['GET'])
def get_last_block():
    """
     get_last_block()

    :return:

    Return the blockchain's last block

    """
    return jsonify(blockchain.last_block)

@app.route('/length', methods=['GET'])
def get_length():
    """
    get_length()

    :return: JSON response

    Return a the blockchain length

    """
    response = {
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/submit_block', methods=['POST'])
def submit_block():
    """
    submit_block()

    :return: JSON response

    Check mined block PoW and give miner (sender) a coin for reward if correct.

    """
    global miners
    values = request.get_json()

    solved_block = values.get('solved_block')
    proof = values.get('proof_of_work')
    address = values.get('address')
    public_key = values.get('public_key')

    if address not in miners:
        miners.append(address)

    # Check that the Proof of Work is correct
    if not blockchain.valid_proof(blockchain.last_block['proof'], proof, blockchain.last_block['previous_hash']):
        response = {
            'message': "Block has already been solved or is proof of work is incorrect."
        }
        return jsonify(response), 200

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=address,
        amount=currency_length_formatter.format(Decimal(reward)),
        hash=hashlib.sha256(public_key.encode()).hexdigest()
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(solved_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

#################################################################################################
# Transaction Routes
#
# /transactions/new           : Create a new transaction to send coins
#
#################################################################################################

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    new_transaction()

    :sender: Senders address
    :recipient: Recipients address
    :amount: Amount to be sent
    :public_key: Public key of the sender to verify ownership
    :return: JSON response

    Create a new transaction and return a JSON response

    """
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount', 'public_key']
    if not all(k in values for k in required):
        return 'Missing values', 400

    public_key_hash = hashlib.sha256(values['public_key'].encode()).hexdigest()

    # TODO : Be sure sender has enough available coin to send to the recipient
    total = Decimal(currency_total_zero)

    for block in blockchain.chain:
        if len(block['transactions']) >= 1:
            for transaction in block['transactions']:
                if transaction['recipient'] == values['sender'] and transaction['hash'] == public_key_hash:
                    total = total + Decimal(transaction['amount'])
                if transaction['sender'] == values['sender'] and transaction['hash'] == public_key_hash:
                    total = total - Decimal(transaction['amount'])

    if total >= Decimal(str(values['amount'])):
        # Create a new Transaction
        index = blockchain.new_transaction(values['sender'], values['recipient'],
                                           currency_length_formatter.format(Decimal(str(values['amount']))),
                                           public_key_hash)

        response = {'message': 'Transaction will be added to Block {0}.'.format(index)}
        return jsonify(response), 201
    else:
        response = {'message': 'You do not own enough coin to make this transaction or the public key is invalid.'}
        return jsonify(response), 402

#################################################################################################
# Account & Balance Routes
#
# /circulation                : Return the blockchains total coin in circulation
# /account/balance            : Get an accounts balance
# /account/register_address   : Register a new address on the blockchain
#
#################################################################################################

@app.route('/circulation', methods=['GET'])
def get_circulation():
    """
    get_circulation()

    :return:

    Return the blockchains total coin in circulation

    """
    response = {
        "circulation": blockchain.total_coin()
    }
    return jsonify(response), 200

@app.route('/account/balance', methods=['POST'])
def account_balance():
    """
    account_balance()

    :return:

    Return balance of an address

    """
    global public_key
    values = request.get_json()

    chain = blockchain.chain
    length = len(blockchain.chain)
    address = values.get('address')
    hash = hashlib.sha256(open(str(public_key), 'r').read().encode()).hexdigest()
    total = Decimal(currency_total_zero)

    for link in chain:
        if len(link['transactions']) >= 1:
                for transaction in link['transactions']:
                    if transaction['recipient'] == address and transaction['hash'] == hash:
                        total = total + Decimal(transaction['amount'])
                    if transaction['sender'] == address and transaction['hash'] == hash:
                        total = total - Decimal(transaction['amount'])

    response = {"address": address, "balance": currency_length_formatter.format(total)}
    return jsonify(response)

@app.route('/account/register_address', methods=['GET'])
def register_address():
    """
    register_address()

    :hash: The public_key hashed of the address owner
    :return:

    Return a new address registered to the public_key hash

    TODO:
        save address with public_key hash to file for verification
        Should address contain public_key hash in a way it can be decrypted and verified? namespace?

    """
    address = str(uuid4()).replace('-', '')

    response = {"address": address}
    return jsonify(response)

#################################################################################################
# Main Application
#
# Start up the Fuel Blockchain & API
#
#################################################################################################

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = node_port if node_port else args.port

    logger.info("Restoring chains......")
    blockchain.restore_chain()

    logger.info("Initiating chain backup thread...")
    threading.Timer(10.0, blockchain.backup_chain).start()

    logger.info("Node Address: {0}".format(blockchain_address))
    logger.info(Banners.banner.format(len(blockchain.chain), len(blockchain.nodes) +1,
                                      len(miners), blockchain.total_coin(), difficulty_int))

    logger.info("Starting {0} Fuel Blockchain & API..".format(app_name))
    #app.run(host=node_host, port=port, debug=True, threading=False)
    app.run(host=node_host, port=port, debug=False)
