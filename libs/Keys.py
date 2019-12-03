import os
import json
import requests
from os.path import exists
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

# Needs the node_host here. For now, manually input
node_host = ''

def create_address(path):
    """
    create_address(path)

    :param path:
    :return: True if success

    Create address.
    Create public and private keys.
    Write their entry to the address.book.

    """
    if exists('{0}/{1}'.format(path, 'address.book')):
        # If the address.book exists, pass and append new address
        pass
    else:
        # If address.book don't exist create new file
        open('{0}/{1}'.format(path, 'address.book'), 'x')
        fh = open('{0}/{1}'.format(path, 'address.book'), 'w')
        fh.write("{\"book\": []}")
        fh.close()


    address_book = json.loads(open('{0}/{1}'.format(path, 'address.book'), 'r').read())
    address_book2 = open('{0}/{1}'.format(path, 'address.book'), 'w')

    index_req = requests.get('{0}/account/register_address'.format(node_host))
    address = index_req.json()['address']

    key = generate_key()

    generate_public_key(key, "{0}/keys/{1}.pub".format(path, address))

    generate_private_key(key, "{0}/keys/{1}.prv".format(path, address))

    entry = {
        "address": address,
        "public_key": "{0}/keys/{1}.pub".format(path, address),
        "private_key": "{0}/keys/{1}.prv".format(path, address)
    }

    address_book['book'].append(entry)

    address_book2.write(json.dumps(address_book))
    address_book2.close()
    return True


def check_keys(path):
    """
    check_keys(path)

    :param path: Relative path of fuel-wallet/keys
    :return:

    If address.book exists, continue else create first address in the book

    """
    if exists('address.book'):
        return True
    else:
        create_address(path)


def generate_key():
    """
    generate_key()

    :return: key

    Generate the key

    """
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    return key


def generate_public_key(key, path):
    """
    generate_public_key(key, path)

    :param key: The key returned from generate_key()
    :param path: Relative path of fuel-wallet/keys
    :return: True|False for verification purposes

    Generate the public key

    """
    try:
        open(path, 'x')
        fh = open(path, 'wb')
        # fh.write(public_key.decode('utf-8'))
        pub = key.public_key()
        fh.write(pub.public_bytes(
            encoding=crypto_serialization.Encoding.PEM,
            format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        fh.close()
        return True
    except Exception as e:
        print(e)
        return False


def generate_private_key(key, path):
    """
    generate_private_key(key, path)

    :param key: The key returned from generate_key()
    :param path: Relative path of fuel-wallet/keys
    :return: True|False for verification purposes

    Generate the private key

    """
    try:
        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption()
        )
        open(path, 'x')
        fh = open(path, 'w')
        fh.write(private_key.decode('utf-8'))
        fh.close()
        return True
    except Exception as e:
        print(e)
        return False