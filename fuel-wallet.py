#!/usr/bin/python3

"""

"""
import os
from time import sleep
from libs.Keys import check_keys

check_keys(os.path.dirname(os.path.realpath(__file__)))

import random
from termcolor import colored
from libs import Banners, Wallet, Miner

if __name__ == '__main__':
    try:
        n = random.randint(0, 2)
        print("{0}".format(Banners.banner))
    except:
        pass

    gsh = Wallet.Wallet()

    gsh.prompt = '{0}> '.format(colored('fuel-wallet', 'green'))
    gsh.cmdloop('')