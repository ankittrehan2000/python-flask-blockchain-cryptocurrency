import datetime
# for the sha256 function
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    def __init__(self):
        self.chain = []
        # genesis block (first block of the chain)
        self.add_block(proof=1, prev_hash='0')

    def add_block(self, proof, prev_hash):
        # create a dictionary to represent a block
        block = {
            'index': len(self.chain)+1,
            'time_stamp': str(datetime.datetime.now),
            'proof': proof,
            'prev_hash': prev_hash,
        }
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


app = Flask(__name__)
blockchain = Blockchain()

# mine a block


@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_last_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.add_block(proof, prev_hash)
    response = {
        'message': 'You successfully mined a block!',
        'index': block['index'],
        'time_stamp': block['time_stamp'],
        'proof': block['proof'],
        'prev_hash': block['prev_hash']
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


app.run(host='0.0.0.0', port=5000)
