import requests

def authoritative_node():
    """
    authoritative_node()

    :param args: <url>
    :return:

    Return the authoritative node connected to the network

    """
    # Find the authoritative node
    longest_chain_node = None
    longest_chain = 0

    nodes = requests.get('{0}://{1}:{2}/nodes'.format(node_protocol, node_host, node_port)).json()['nodes']
    nodes.append('{0}:{1}'.format(node_host, node_port))

    for node in nodes:
        try:
            node_length = requests.get('{0}://{1}/length'.format(node_protocol, node)).json()['length']
        except:
            node_length = 0

        if node_length > longest_chain:
            longest_chain = node_length
            longest_chain_node = node

    return longest_chain_node