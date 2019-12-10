import os
import json
import requests
import hashlib
from os.path import exists
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from libs.Logger import logger
from uuid import uuid4

def create_address(path):
    """
    create_address(path)

    :param path:
    :return: True if success

    Create address.
    Create public and private keys.
    Write their entry to the wallet.

    """
    if exists('{0}/{1}'.format(path, 'wallets')):
        # If the wallet exists, pass and append new address
        pass
    else:
        # If wallet don't exist create new file
        open('{0}/{1}'.format(path, 'wallets'), 'x')
        fh = open('{0}/{1}'.format(path, 'wallets'), 'w')
        fh.write("{\"wallets\": []}")
        fh.close()


    ab = json.loads(open('{0}/{1}'.format(path, 'wallets'), 'r').read())
    wallet2 = open('{0}/{1}'.format(path, 'wallets'), 'w')

    address = str(uuid4()).replace('-', '')

    key = generate_key()

    generate_public_key(key, "{0}/keys/{1}.pub".format(path, address))

    generate_private_key(key, "{0}/keys/{1}.prv".format(path, address))

    entry = {
        "address": address,
        "public_key": "{0}/keys/{1}.pub".format(path, address),
        "private_key": "{0}/keys/{1}.prv".format(path, address),
        "hash": "{0}".format(hashlib.sha256(open(str("{0}/keys/{1}.pub".format(path,
                                                                          address)), 'r').read().encode()).hexdigest())
    }

    ab['wallets'].append(entry)

    wallet2.write(json.dumps(ab))
    wallet2.close()

    global wallets
    wallets = json.loads(open('{0}/{1}'.format(os.getcwd(), 'wallets'), 'r').read())
    return True


def check_keys(path):
    """
    check_keys(path)

    :param path: Relative path of fuel-wallet/keys
    :return:

    If wallet exists, continue else create first address in the wallet

    """
    if exists('wallets'):
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