#!/usr/bin/python3

"""

"""
import os
import random
from time import sleep
from termcolor import colored
from libs.Keys import check_keys

check_keys(os.path.dirname(os.path.realpath(__file__)))

from libs import Banners, Wallet, Miner

if __name__ == '__main__':
    try:
        n = random.randint(0, 2)
        print("{0}".format(Banners.banner[:Banners.banner.rfind("\n")]))
    except:
        pass

    gsh = Wallet.Wallet()
    gsh.do_start_blockchain(None)
    print("")
    print("")
    gsh.prompt = '{0}> '.format(colored('fuel', 'green'))
    gsh.cmdloop('')