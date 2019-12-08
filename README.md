# fuel

Manage the Fuel blockchain, wallet accounts and mining from a Linux client interface.


Fuel Wallet Commands
===================================================================================================
fuel> help

     Command                              Description
     -------                              -----------
     start_blockchain                     Start the Fuel blockchain node
     stop_blockchain                      Stop the Fuel blockchain node
     balance                              Check current balance
     transaction <recipient> <amount>     Make a new transaction
     length                               Display the current blockchain length
     block                                Display a block in the blockchain
     last                                 Display the last block in the blockchain
     register_address                     Register an address and store it in the address.book
     start_miner                          Start mining for Fuel
     stop_miner                           Stop mining for Fuel
     update                               Update Fuel Wallet via git pull. Requires restart
     exit                                 Exit wallet

# Configuration and Execution

1. pip3 install -r requirements.txt
2. cp example.config.py config.py
3. vim config.py 

    You only needs to edit the node_host unless you are making your own blockchain using this code. http://ip:port
    
4. ./fuel.py

    Note that an address.book will be created in the working directory and the public and private keys will be created 
    into the keys/ directory.
