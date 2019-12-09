import hashlib
import os
import json
from decimal import Decimal

app_name = "Fuel"

"""
Node Configurations

node_host               : The node's IP address. Example: 123.123.123.123
node_port               : The node's web port. Example: 5000
start_blockchain        : Start the blockchain at run
miners                  : List of active miners

"""
node_host = '<IP>'
node_port = '<PORT>'
start_blockchain = True
miners = []

"""
Address and Key Configurations

address_book               : The address book to be read for input
address                    : The primary address
public_key                 : The actual public key
public_key_hash            : The public key hashed in sha256

"""
address_book = json.loads(open('{0}/{1}'.format(os.path.dirname(os.path.realpath(__file__)),
                                                'address.book'), 'r').read())

address = address_book['book'][0]['address']

public_key = open(str(address_book['book'][0]['public_key']), 'r').read()
public_key_hash = hashlib.sha256(open(str(address_book['book'][0]['public_key']), 'r').read().encode()).hexdigest()

"""
Encryption Configurations

aes_key  :  Loads our AES key into the variable

"""
aes_key = open('aes.key', 'r').read().replace("\n", "")

"""
Currency Configurations

currency_total_zero       : This is the total of a zero coin value
currency_length_formatter : This is a formatter string used to format Decimals into strings
reward                    : This is the amount of reward received for mining a block; Should be adjusted based on value

"""
currency_total_zero = '0.00000000'
currency_length_formatter = "{:.8f}"
reward = '0.00010000'

"""
Difficulty Configurations

difficulty_int     : This is the number of 0s we look for in our hash
difficulty_string  : This is the string of 0s we look for

"""
difficulty_int = 5
difficulty_string = "00000"

"""
Blockchain Backup Configurations

path                   : This is the path to our running application
backup_storage_dir     : Using the path, we point to the storage directory we use to backup the blockchain
backup_file_prefix     : Prefix of the backup files
blocks_per_backup_file : Number of blocks to save per file

"""
path = os.path.dirname(os.path.realpath(__file__))
backup_storage_dir = "{0}/storage/".format(path)
backup_file_prefix = "chain_"
blocks_per_backup_file = 999999999999
