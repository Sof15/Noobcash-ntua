import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from argparse import ArgumentParser
import block
import node
import blockchain
import wallet
import transaction
import time
import json
import threading
import logging 


app = Flask(__name__)
CORS(app)

parser = ArgumentParser()
parser.add_argument('boot', type=int, help='if the current node is the bootstrap enter 1, oterwise enter 0')
parser.add_argument('ip',  type=str, help='host of the current node')
parser.add_argument('port', type=int, help='port to listen to')
args = parser.parse_args()

difficulty_bits = 4 #5
capacity = 	2 #5,10

global new_node
new_node = node.node(args.boot,args.ip,args.port)

if args.boot:
	genesis_block = new_node.create_genesis_block(difficulty_bits,capacity)	

#.......................................................................................

#source : https://networklore.com/start-task-with-flask/
def registernode():
	def start_register():
		done = False
		global new_node
		while(not done):
			print("New node being registered...")
			try:
				r = new_node.register(args.boot)
				print("Status Code:",r.status_code)
				if r.status_code == 200:
					print("New node registered!\n")
					done = True
					#thread.join()
			except Exception as e:
				print('Failed: '+ str(e),'\n')
			time.sleep(3)

	thread = threading.Thread(target=start_register)
	thread.start()
    

@app.route('/node_info', methods=['GET'])
def info():
    global new_node
    response = {'ID': new_node.id,"Ring:":new_node.ring}
    return jsonify(response), 200


@app.route('/register', methods=['POST'])
def register_node():
	print("Bootstrap got the new node's posted data...\n")
	global new_node
	public_key = request.form["public_key"]
	ip = request.form["ip"]
	port = request.form["port"]
	new_node.register_node_to_ring(args.boot,ip,port,public_key.encode())
	new_node.create_transaction(new_node.ring[-1]["key"].encode(),100)
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/data/get', methods=['POST'])
def get_data():
	
	global new_node
	chain=blockchain.Blockchain()

	new_node.id = int(request.form["id"])
	for i,data in enumerate(json.loads(request.form["blocks"])):
		trans = []
		for tx in json.loads(data["listOfTransactions"]):
			trans.append(transaction.Transaction(tx["sender_address"].encode(),None,tx["receiver_address"].encode(),tx["amount"],json.loads(tx["inputs"])))
			trans[-1].signature = tx["signature"].encode('latin-1')
			trans[-1].transaction_id = tx["hash"]
			trans[-1].outputs = json.loads(tx["outputs"])
			trans[-1].temp_id = tx["temp_id"].encode('latin-1')
		new_block = block.Block(i,data["previousHash"],trans,difficulty_bits)
		new_block.hashmerkleroot = data["hashmerkleroot"]
		new_block.hash = data["hash"]
		new_block.timestamp = data["timestamp"]
		new_block.nonce = data["nonce"]
		chain.add_block(new_block)

	"""
	for b in chain.blocks:
		print("..................BLOCK....................")
		print("index",b.index)
		print("block hash", b.hash)
		print("previous hash",b.previousHash)
		#print("block sender", request.form["sender"])
		print()
		for tx in b.listOfTransactions:
			print("amount",tx.amount)
			print("transaction hash",tx.transaction_id)
	"""

	if new_node.validate_chain(chain,difficulty_bits):
		new_node.chain=chain
		print("New Node validated broadcasted Blockchain\n")
	else:
		print("New Node unable to validate broadcasted Blockchain\n")

	
	print("Creating current block...\n")
	current_block = json.loads(request.form["current_block"])
	trans = []
	for tx in json.loads(current_block["listOfTransactions"]):
		trans.append(transaction.Transaction(tx["sender_address"].encode(),None,tx["receiver_address"].encode(),tx["amount"],json.loads(tx["inputs"])))
		trans[-1].signature = tx["signature"].encode('latin-1')
		trans[-1].transaction_id = tx["hash"]
		trans[-1].outputs = json.loads(tx["outputs"])
		trans[-1].temp_id = tx["temp_id"].encode('latin-1')
	new_node.current_block = block.Block(int(current_block["index"]), current_block["previousHash"], trans,difficulty_bits)
	new_node.current_block.hash = current_block["hash"]
	new_node.current_block.nonce = current_block["nonce"]
	new_node.current_block.timestamp = current_block["timestamp"]
	new_node.current_block.hashmerkleroot = current_block["hashmerkleroot"] 

	new_node.utxo.extend(json.loads(request.form["utxo"]))
	print("New node got ID =", request.form["id"],"\n")
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/blockchain/request')
def give_blockchain():
	global new_node
	if len(new_node.chain.blocks) > request.form["mylength"]:
		data = {}
		data["blocks"] = json.dumps(new_node.chain.to_dict())
		url = "http://" + request.form["address"] + "/blockchain/get"
		r = requests.post(url,data)
	response = {'t': 1}
	return jsonify(response), 200



@app.route('/blockchain/get')
def get_blockchain():
	
	global new_node
	new_node.chain.blocks = []
	new_node.chain.lock.acquire()
	for i,data in enumerate(json.loads(request.form["blocks"])):
		trans = []
		for tx in json.loads(data["listOfTransactions"]):
			trans.append(transaction.Transaction(tx["sender_address"].encode(),None,tx["receiver_address"].encode(),tx["amount"],json.loads(tx["inputs"])))
			trans[-1].signature = tx["signature"].encode('latin-1')
			trans[-1].transaction_id = tx["hash"]
			trans[-1].outputs = json.loads(tx["outputs"])
			trans[-1].temp_id = tx["temp_id"].encode('latin-1')
		new_block = block.Block(i,data["previousHash"],trans,difficulty_bits)
		new_block.hashmerkleroot = data["hashmerkleroot"]
		new_block.hash = data["hash"]
		new_block.timestamp = data["timestamp"]
		new_block.nonce = data["nonce"]
		new_node.chain.add_block(new_block)
	new_node.chain.lock.release()
	print("New Node got Blockchain")
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/broadcast/ring', methods=['POST'])
def get_ring():
	print("Getting ring from broadcasting....\n")
	global new_node
	new_node.ring = json.loads(request.form["ring"])
	print("New node got ring!\n")
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/broadcast/transaction', methods=['POST'])
def get_new_transaction():
	print("THREAD:",threading.get_ident())
	print("Getting transaction from broadcasting.... AMOUNT:", request.form["amount"],"\n")
	global new_node
	new_tx = transaction.Transaction(request.form["sender_address"].encode(),None,request.form["receiver_address"].encode(),int(request.form["amount"]),request.form["inputs"])
	new_tx.signature = request.form["signature"].encode('latin-1')
	new_tx.transaction_id = request.form["hash"]
	new_tx.temp_id = request.form["temp_id"].encode('latin-1')
	new_tx.transaction_inputs = json.loads(request.form["inputs"])
	new_tx.transaction_outputs = json.loads(request.form["outputs"])
	if new_node.validate_transaction(new_tx):
		new_node.add_transaction_to_block(new_tx,capacity,difficulty_bits)
		print("Added broadcasted transaction to current block!\n")
	else:
		print("Could not add transaction to current block.\n")
	#for i in range(len(new_node.utxo)):
	#	print(new_node.utxo[i]["amount"])
	#	print(new_node.utxo[i]["recipient"])
	#	print()
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/broadcast/block', methods=['POST'])
def get_block():
	global new_node
	#adding the first of the broadcasted blocks to blockchain after validating
	new_node.chain.lock.acquire()
	#if request.form["hashmerkleroot"] not in [b.hashmerkleroot for b in new_node.chain.blocks] and \
	#int(request.form["index"]) not in [b.index for b in new_node.chain.blocks]:
	ok = True
	temp = [tx["hash"] for tx in json.loads(request.form["listOfTransactions"])]
	for t in temp:
		for b in new_node.chain.blocks:
			for tr in b.listOfTransactions:
				if t == tr.transaction_id:
					ok = False
					break
			if not ok:
				break
	if ok and int(request.form["index"]) not in [b.index for b in new_node.chain.blocks]:
		trans = []
		for tx in json.loads(request.form["listOfTransactions"]):
			trans.append(transaction.Transaction(tx["sender_address"].encode(),None,tx["receiver_address"].encode(),tx["amount"],json.loads(tx["inputs"])))
			trans[-1].signature = tx["signature"].encode('latin-1')
			trans[-1].transaction_id = tx["hash"]
			trans[-1].outputs = json.loads(tx["outputs"])
			trans[-1].temp_id = tx["temp_id"].encode('latin-1')
		new_block = block.Block(int(request.form["index"]), request.form["previousHash"], trans,difficulty_bits)
		new_block.hash = request.form["hash"]
		new_block.nonce = request.form["nonce"]
		new_block.timestamp = request.form["timestamp"]
		new_block.hashmerkleroot = request.form["hashmerkleroot"] 
		print("Getting block from broadcasting.... BLOCK ID:",request.form["index"],"AMOUNT:",trans[-1].amount,"\n")
		print("Validating broadcasted block...")
		if new_node.validate_block(new_block,difficulty_bits,new_node.chain):
			new_node.chain.add_block(new_block)
			print("Added validated block to blockchain\n")
			for b in new_node.chain.blocks:
				print("..................BLOCK....................")
				print("index",b.index)
				print("block hash", b.hash)
				print("previous hash",b.previousHash)
				print("block sender", request.form["sender"])
				print()
				for tx in b.listOfTransactions:
					print("amount",tx.amount)
					print("transaction hash",tx.transaction_id)
			
		else:
			print("Unable to validate broadcasted block.\n")
	else:
		print("Block with id "+request.form["index"]+" rejected.\n")
	new_node.chain.lock.release()
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/transactions/get', methods=['POST'])
def get_transactions():
	print("Getting data to make a new transaction...\n")
	global new_node

	receiver_id=int(request.form["receiver_id"])
	amount=int(request.form["amount"])
	trans = new_node.create_transaction(new_node.ring[receiver_id]["key"].encode(),amount)
	response = {'transactions': 1}
	return jsonify(response), 200

# run it once fore every node

if __name__ == '__main__':
	if args.boot == 0 :
		registernode()
	app.run(host=args.ip,port=args.port,threaded=True)	
