# fuel

Manage the Fuel blockchain, wallet accounts and mining from a Linux client interface.


Fuel Wallet Commands
===================================================================================================
fuel> help


Fuel Blockchain Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     start_blockchain                       Start the Fuel blockchain node
     stop_blockchain                        Stop the Fuel blockchain node
     register_node <protocol>://<ip>:<port> Register a new node on the blockchain network
     length                                 Display the current blockchain length
     block                                  Display a block in the blockchain
     last                                   Display the last block in the blockchain


Fuel Wallet Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     balance <address>                      Check current balance of wallet address
     transaction <recipient> <amount>       Make a new transaction
     register_address                       Register an address and store it in the address.book
     address_book                           Display the address.book
     set_address <address>                  Set the address.book address to be used by the wallet
     using_address                          Display the address in use by the wallet


Fuel Miner Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     start_miner <address>                  Start mining for Fuel under <address>
     stop_miner                             Stop mining for Fuel


Fuel CLI Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     banner                                 Display the Fuel banner with statistics
     update                                 Update Fuel Wallet via git pull. Requires restart
     exit                                   Exit wallet


# Configuration and Execution

1. pip3 install -r requirements.txt
2. cp example.config.py config.py
3. vim config.py 

    You only needs to edit the node_host and node_port unless you are making your own blockchain using this code.

4. vim aes.key
     
     Create a 32 char string to be used as the AES Key. This is used to encrypt each block in the key when
     creating a backup that can be loaded with the blockchain node server is shutdown and restarted.
     
5. ./fuel.py

    Note that an address.book will be created in the working directory and the public and private keys will be created 
    into the keys/ directory.
