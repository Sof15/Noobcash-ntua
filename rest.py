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

#new_node = node.node(0,"192.168.1.4",5001)

#.......................................................................................



# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #transactions = blockchain.transactions
    #wall=wallet.wallet()
    #print (type(wall.public_key))
    #bl = block.Block(1,2,[])
    #print (bl.nonce)
    new_node = node.node(0,"192.168.1.4",5001)
    #print(nd.node_info)
    response = {'transactions': 1}
    return jsonify(response), 200

@app.route('/register', methods=['POST'])
def register_node():
	public_key = request.form["public_key"]
	ip = request.form["ip"]
	port = request.form["port"]
	new_node.register_node_to_ring(1,ip,port,public_key)
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/get_id', methods=['POST'])
def get_id():
	self.id = request.form["id"]

	response = {'t': 1}
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
	#new_node = node.node(0,"192.168.1.4",5001)
	app.run(port=port)
	print("lalala")
    