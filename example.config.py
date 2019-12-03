import hashlib
import os
import json
from decimal import Decimal

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
Node Configurations

node_host               : The host running this node. Example: http://123.123.123.123:5000

"""
node_host = ''

"""
Currency Configurations

currency_total_zero       : This is the total of a zero coin value
currency_length_formatter : This is a formatter string used to format Decimals into strings

"""
currency_total_zero = Decimal('0.00000000')
currency_length_formatter = "{:.8f}"
