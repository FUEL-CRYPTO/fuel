# fuel

Manage the Fuel blockchain, wallet accounts and mining from a Linux client interface.


Fuel Wallet Commands
===================================================================================================
fuel> help


Fuel Blockchain Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     authoritative                          Display the authoritative node
     blockchain <start|stop|status>         Manage the blockchain process
     block <index>                          Display a block in the blockchain
     last                                   Display the last block in the blockchain
     length                                 Display the current blockchain length
     nodes                                  Display the list of nodes connected to the network
     register <protocol>://<ip>:<port>      Register a new node on the blockchain network


Fuel Wallet Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     balance <address>                      Check current balance of wallet address
     transaction <recipient> <amount>       Make a new transaction
     create                                 Create a wallet. Register new address and keys.
     set_address <address>                  Set the address.book address to be used by the wallet
     wallets                                Display the address.book
     wstats                                 Display the address in use by the wallet


Fuel Miner Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     miner <start|stop|status> <address>    Manage the miners. If 'start' <address> is required

Fuel CLI Commands
===================================================================================================

     Command                                Description
     -------                                -----------
     banner                                 Display the Fuel banner with statistics
     exit                                   Exit wallet
     update                                 Update Fuel Wallet via git pull. Requires restart


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

# Wallets

When you start the ./fuel application it will create an address, public key and private key. 

If you are planning to run a blockchain the first address created will be the blockchain address and set of keys and 
when running ./fuel it will be used as the default wallet address.

To create a personal wallet address use 'create'. Every address created thereafter will be a personal wallet address. 

To change the Fuel CLI from being set to the defaulted blockchain address you can use the 'set_address' to change it 
to a personal wallet address. Note this will default back to the blockchain adress upon restart.

# Mining

You can mine under the blockchain address or personal wallet addresses by using the 'miner' command. 

# Help

See the 'help' command.