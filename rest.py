import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from argparse import ArgumentParser
import block
import node
#import blockchain
import wallet
import transaction
import time
import json
import threading
import logging 


app = Flask(__name__)
CORS(app)
#blockchain = Blockchain()

parser = ArgumentParser()
parser.add_argument('boot', type=int, help='if the current node is the bootstrap enter 1, oterwise enter 0')
parser.add_argument('ip',  type=str, help='host of the current node')
parser.add_argument('port', type=int, help='port to listen to')
args = parser.parse_args()

difficulty_bits = 4 #5
capacity = 1	#5,10

global new_node
new_node = node.node(args.boot,args.ip,args.port)

if args.boot:
	new_block = new_node.create_genesis_block(difficulty_bits)

#.......................................................................................
logger = logging.getLogger("lal")
#source : https://networklore.com/start-task-with-flask/
def registernode():
	def start_register():
		done = False
		global new_node
		while(not done):
			print("Registering new node...")
			try:
				r = new_node.register(args.boot)
				if r.status_code == 200:
					print("New node registered!")
					done = True
				print("Status Code:",r.status_code)
			except Exception as e:
				logger.error('Failed: '+ str(e))
			time.sleep(3)

	thread = threading.Thread(target=start_register)
	thread.start()
    

@app.route('/node_info', methods=['GET'])
def info():
    global new_node
    response = {'ID': new_node.id,"Ring:":new_node.ring}
    return jsonify(response), 200


# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    global new_node
    #transactions = blockchain.transactions
    #wall=wallet.wallet()
    #print (type(wall.public_key))
    #bl = block.Block(1,2,[])
    #print (bl.nonce)
    #print(nd.node_info)
    response = {'transactions': 1}
    return jsonify(response), 200

@app.route('/register', methods=['POST'])
def register_node():
	print("Bootstrap got the new node's posted data...")
	global new_node
	public_key = request.form["public_key"]
	ip = request.form["ip"]
	port = request.form["port"]
	new_node.register_node_to_ring(args.boot,ip,port,public_key)
	#edo na steiloyme kai to blockchain
	response = {'t': 1}
	
	return jsonify(response), 200

@app.route('/data/get', methods=['POST'])
def get_data():
	
	global new_node
	
	new_node.id = request.form["id"]

	temp_utxo = {}
	'''temp_utxo["id"] = request.form["utxo_id"]
				temp_utxo["recipient"] = request.form["recipient"]
				temp_utxo["amount"] = request.form["amount"]
				temp_utxo["previous_trans_id"] = request.form["previous_trans_id"]'''
	temp_utxo = request.form["utxo"]
	
	new_node.utxo.append(temp_utxo)
	
	print("New node got ID =", request.form["id"])
	url = "http://"+new_node.ring[0]["address"]+"/data/confirm" 
	requests.post(url,{'data':"ok"})
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/data/confirm', methods=['POST'])
def confirm():
	global new_node
	new_node.send_initial_transaction(new_node.wallet.public_key)
	
	response = request.form
	return jsonify(response), 200


@app.route('/broadcast/ring', methods=['POST'])
def get_ring():
	print("Getting ring from broadcasting....")
	global new_node
	new_node.ring = json.load(request.form["ring"])
	print("New node got ring =", type(new_node.ring))
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/broadcast/transaction', methods=['POST'])
def get_new_transaction():
	print("Getting transaction from broadcasting....")
	global new_node
	print("transaction....." , request.form)
	new_tx = transaction.Transaction(request.form["sender_address"],None,request.form["receiver_address"],request.form["amount"],request.form["inputs"])
	new_tx.signature = request.form["signature"]
	new_tx.transaction_id = request.form["hash"]
	new_tx.transaction_input = json.load(request.form["inputs"])
	print(request.form["inputs"])
	new_tx.transaction_output = request.form["outputs"]

	if new_node.validate_transaction(new_tx):
		new_node.add_transaction_to_block(block,new_tx,capacity,difficulty_bits) #blockchain??)
	print("Added broadcasted transaction to block!")
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/broadcast/block', methods=['POST'])
def get_block():
	print("Getting validated block from broadcasting....")
	global new_node
	#first create a block then update it's data 
	new_block = block.Block(request.form["index"], request.form["previousHash"], request.form["listOfTransactions"],difficulty_bits)
	new_block.hash = request.form["hash"]
	new_block.nonce = request.form["nonce"]
	new_block.timestamp = request.form["timestamp"]
	new_block.hashmerkleroot = request.form["hashmerkleroot"] 
	print("Got validated block")
	response = {'t': 1}
	return jsonify(response), 200

# run it once fore every node

if __name__ == '__main__':
	if args.boot == 0 :
		registernode()
	app.run(host=args.ip,port=args.port)	
