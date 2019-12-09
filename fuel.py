#!/usr/bin/python3

"""
Fuel

Developed by: Unknown
Last Modified: 2019-12-08

This application is a CLI interface developed to control the Fuel blockchain, wallet, and miner.

"""

import os
import random
from time import sleep
from termcolor import colored
from libs.Keys import check_keys

check_keys(os.path.dirname(os.path.realpath(__file__)))

from libs import Banners, Wallet, Miner
from config import start_blockchain

if __name__ == '__main__':
    try:
        #n = random.randint(0, 2)
        print("{0}".format(Banners.banner[:Banners.banner.rfind("\n")]))
    except:
        pass

    gsh = Wallet.Wallet()

    if start_blockchain:
        gsh.do_start_blockchain(None)

    print("\n\n")
    gsh.prompt = '{0}> '.format(colored('fuel', 'green'))
    gsh.cmdloop('')