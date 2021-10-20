import datetime
# for the sha256 function
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# similar to blockchain file except there is a transactions attribute and there is a consensus function
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        # genesis block (first block of the chain)
        self.add_block(proof=1, prev_hash='0')
        self.nodes = set()

    def add_block(self, proof, prev_hash):
        # create a dictionary to represent a block
        block = {
            'index': len(self.chain)+1,
            'time_stamp': str(datetime.datetime.now),
            'proof': proof,
            'prev_hash': prev_hash,
            # empty transactions
            'transactions': self.transactions,
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    # proof of work is the problem that the miners have to solve to register a new block
    def proof_of_work(self, prev_proof):
        new_proof = 1
        is_valid = False
        while(not is_valid):
            # argument passed to sha256 should be different each time hence the squares
            hash_operation = hashlib.sha256(
                str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                is_valid = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            # check if proof of work is working
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True

    def create_transaction(self, sender, reciever, amount):
        self.transactions.append({
            'sender': sender,
            'reciever': reciever,
            'amount': amount
        })
        return self.get_last_block()['index'] + 1

    # create nodes on the blockchain
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # replace chain in a node
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        # iterate over each node in network and check for largest existing chain
        for node in network:
            response = requests.get(node + '/get_entire_chain')
            if response.status == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid():
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

app = Flask(__name__)

# Create an address for the node on each port
node_address = str(uuid4()).replace("-", "")

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_last_block()
    prev_proof = prev_block['proof']
    # mine the block by finding the hash
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    # add the transaction for the miner before adding block to the chain
    blockchain.create_transaction(sender = node_address, reciever = 'Doe', amount = 100)
    block = blockchain.add_block(proof, prev_hash)
    response = {
        'message': 'You successfully mined a block!',
        'index': block['index'],
        'time_stamp': block['time_stamp'],
        'proof': block['proof'],
        'prev_hash': block['prev_hash'],
        'transactions': block['transactions']
    }
    return jsonify(response), 200


@app.route('/get_entire_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/check_validity', methods=['GET'])
def check_validity():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Valid'}
    else:
        response = {'messsage': 'Invalid'}
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Incomplete transaction', 400
    index = blockchain.create_transaction(json['sender'], json['reciever'], json['amount'])
    response = { 'message': f'Transaction will be added to block with index {index}' }
    return jsonify(response), 201

# connect new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    # contains list of all node addresses (ports)
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    return jsonify({ 'message': 'Added', 'total_nodes': list(blockchain.nodes) }), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = { 'message': 'Replaced', 'new_chain': blockchain.chain }
    else:
        response = { 'messsage': 'Had longest chain' }
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5002)
