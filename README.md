# fuel-wallet


# Configuration

1. pip3 install -r requirements.txt
2. cp example.config.py config.py
3. vim config.py 

    You only needs to edit the node_host unless you are making your own blockchain using this code. http://ip:port
    
4. ./fuel-wallet.py

    Note that an address.book will be created in the working directory and the public and private keys will be created 
    into the keys/ directory.
