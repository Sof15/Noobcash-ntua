import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import argparse

import block
import node
#import blockchain
import wallet
#import transaction
#import wallet


### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



app = Flask(__name__)
CORS(app)
#blockchain = Blockchain()


#.......................................................................................



# get all transactions in the blockchain

'''@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #transactions = blockchain.transactions
    #wall=wallet.wallet()
    #print (type(wall.public_key))
    #bl = block.Block(1,2,[])
    #print (bl.nonce)
    nd = node.node(1,"192.168.1.1",5000)
    print(nd.node_info)
    response = {'transactions': 1}
    return jsonify(response), 200'''

@app.route('/register', methods=['POST'])
def register_node():
	data = request.json()
	print(data)
	response = {'transactions': 1}
	return jsonify(response), 200

# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('boot', type=int, help='if the current node is the bootstrap enter 1, oterwise enter 0')
    parser.add_argument('ip',  type=str, help='host of the current node')
    parser.add_argument('port', type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port

    app.run(host=args.ip, port=port)
    new_node = node.node(args.boot,args.ip,args.port)