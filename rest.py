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
from termcolor import colored

app = Flask(__name__)
CORS(app)

parser = ArgumentParser()
parser.add_argument('boot', type=int, help='if the current node is the bootstrap enter 1, oterwise enter 0')
parser.add_argument('ip',  type=str, help='host of the current node')
parser.add_argument('port', type=int, help='port to listen to')
args = parser.parse_args()

difficulty_bits = 4	 #4,5
capacity = 	1 #10,1,5
txs = []
txs_lock = threading.Lock()

new_node = node.node(args.boot,args.ip,args.port)

if args.boot:
	new_node.create_genesis_block(difficulty_bits,capacity)	

#.......................................................................................

#source : https://networklore.com/start-task-with-flask/

def start_register():
	while(1):
		#print("New node being registered...")
		try:
			r = new_node.register(args.boot)
			#print("Status Code:",colored(r.status_code,'green'))
			if r.status_code == 200:
				#print(colored("New node registered!\n",'green'))
				break
		except Exception as e:
			print('Failed: '+ str(e),'\n')
		time.sleep(2)

	
    

@app.route('/node_info', methods=['GET'])
def info():
    response = {'ID': new_node.id,"Ring:":new_node.ring}
    return jsonify(response), 200


@app.route('/register', methods=['POST'])
def register_node():
	#print("Bootstrap got the new node's posted data...\n")
	public_key = request.form["public_key"]
	ip = request.form["ip"]
	port = request.form["port"]
	new_node.register_node_to_ring(args.boot,ip,port,public_key.encode())
	new_node.create_transaction(new_node.ring[-1]["key"].encode(),100)
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/data/get', methods=['POST'])
def get_data():
	chain=blockchain.Blockchain()

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


	if new_node.validate_chain(chain,difficulty_bits):
		new_node.chain=chain
		#print(colored("New Node validated broadcasted Blockchain\n",'green'))
	#else:
		#print(colored("New Node unable to validate broadcasted Blockchain\n",'red'))

	new_node.id = int(request.form["id"])
	

	data = json.loads(request.form["current_block"])
	trans = []
	for tx in json.loads(data["listOfTransactions"]):
		trans.append(transaction.Transaction(tx["sender_address"].encode(),None,tx["receiver_address"].encode(),tx["amount"],json.loads(tx["inputs"])))
		trans[-1].signature = tx["signature"].encode('latin-1')
		trans[-1].transaction_id = tx["hash"]
		trans[-1].outputs = json.loads(tx["outputs"])
		trans[-1].temp_id = tx["temp_id"].encode('latin-1')
	new_block = block.Block(len(new_node.chain.blocks),data["previousHash"],trans,difficulty_bits)
	new_block.hashmerkleroot = data["hashmerkleroot"]
	new_block.hash = data["hash"]
	new_block.timestamp = data["timestamp"]
	new_block.nonce = data["nonce"]
	
	new_node.current_block = new_block

	#new_node.current_block = new_node.create_new_block(difficulty_bits,[])
	new_node.utxo = json.loads(request.form["utxo"])
	#print(colored("New node got ID = " + str(request.form["id"])+"\n",'green'))
	response = {'status': 200}
	return jsonify(response), 200

@app.route('/blockchain/length',methods=['POST'])
def give_length():
	flag = False
	#if not new_node.conflict:
	if not new_node.chain.lock.locked():
		flag = True
		new_node.chain.lock.acquire()
	data = {}
	data["length"] = len(new_node.chain.blocks)
	data["conflict"] = new_node.conflict
	data["id"] = new_node.id
	#print("SENDING LENGTH DATA:",data, "AT:",request.form["address"])
	if flag:
		new_node.chain.lock.release()
	
	return jsonify(data), 200


@app.route('/blockchain/request',methods=['POST'])
def give_blockchain():
	#print("Sending blockchain at URL:",request.form["address"],"\n")
	#if not new_node.conflict: 	#if I dont have a conflict lock chain before sending 
	new_node.chain.lock.acquire()	

	data = {}
	data["blocks"] = json.dumps(new_node.chain.to_dict())
	new_node.utxo_lock.acquire()
	data["utxo"] = json.dumps(new_node.utxo)
	new_node.utxo_lock.release()
	if new_node.chain.lock.locked():  #and  not new_node.conflict:
		new_node.chain.lock.release()
	return jsonify(data), 200



@app.route('/broadcast/ring', methods=['POST'])
def get_ring():
	#print("Getting ring from broadcasting....\n")
	new_node.ring = json.loads(request.form["ring"])
	#print(colored("New node got ring!\n",'green'))
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/broadcast/transaction', methods=['POST'])
def get_new_transaction():
	#print("Getting transaction from broadcasting....",colored("AMOUNT: " + str(request.form["amount"]),'yellow'),"\n")

	while(new_node.conflict):
		pass
	
	new_tx = transaction.Transaction(request.form["sender_address"].encode(),None,request.form["receiver_address"].encode(),int(request.form["amount"]),request.form["inputs"])
	new_tx.signature = request.form["signature"].encode('latin-1')
	new_tx.transaction_id = request.form["hash"]
	new_tx.temp_id = request.form["temp_id"].encode('latin-1')
	new_tx.transaction_inputs = json.loads(request.form["inputs"])
	new_tx.transaction_outputs = json.loads(request.form["outputs"])
	new_tx.timestamp = float(request.form["time"])
	
	
	new_node.list_lock.acquire()
	if not new_node.tx_list or new_tx.timestamp > new_node.tx_list[-1].timestamp:
		new_node.tx_list.append(new_tx)
	else:
		i = 0
		while(new_tx.timestamp > new_node.tx_list[i].timestamp):
			i+=1
		new_node.tx_list.insert(i,new_tx)
	
	#for i,tx in enumerate(new_node.tx_list):
		#print("TX",i,":",tx.timestamp, "|", tx.transaction_id)
	new_node.list_lock.release()
	
	time.sleep(0.5)
	new_node.list_lock.acquire()
	new_tx = new_node.tx_list.pop(0)
	

	if new_node.validate_transaction(new_tx):
		new_node.add_transaction_to_block(new_tx,capacity,difficulty_bits)
		#print(colored("Added broadcasted transaction to current block!\n",'green'))
	#else:
		#print(colored("Unable to validate Transaction.\n",'red'))
	new_node.list_lock.release()

	response = {'t': 1}
	return jsonify(response), 200


@app.route('/broadcast/block', methods=['POST'])
def get_block():
	
	#adding the first of the broadcasted blocks to blockchain after validating
	#print("Getting block from broadcasting.... BLOCK ID:",request.form["index"],colored("AMOUNT: " + str(json.loads(request.form["listOfTransactions"])[-1]["amount"])+"\n",'yellow'))
	
	#check if the block has already been broadcasted by another miner
	temp = [tx["hash"] for tx in json.loads(request.form["listOfTransactions"])]
	if (len(new_node.chain.blocks)-1)*capacity > 5:
		txs_lock.acquire()
		for tx_hash in temp:
			if tx_hash in txs[::-1]:
				txs_lock.release()
				##print(colored("Block ID: "+ request.form["index"]+" already delivered by another miner!\n",'red'))
				#print(colored("Transaction ID: " + tx_hash + " already delivered by another miner!\n",'red'))
				response = {'t': 1}
				return jsonify(response), 200
			
		txs.extend(temp)

		txs_lock.release()

	while(new_node.conflict):
		pass

	new_node.chain.lock.acquire()

	if int(request.form["index"]) in [b.index for b in new_node.chain.blocks]:
		#print(colored("Block with id "+request.form["index"]+" rejected.\n",'red'))
		new_node.chain.lock.release()
		response = {'t': 1}
		return jsonify(response), 200
	'''
	in_chain = False
	temp = [tx["hash"] for tx in json.loads(request.form["listOfTransactions"])]
	for t in temp:
		for b in new_node.chain.blocks[::-1]:
			for tr in b.listOfTransactions:
				if t == tr.transaction_id:
					in_chain = True
					break
			if in_chain:
				break
	
	if not in_chain:
	'''
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
	#print("Validating broadcasted block...\n")
	if new_node.validate_block(new_block,difficulty_bits,new_node.chain):
		new_node.chain.add_block(new_block)
		
		#print(colored("Added validated block with id "+str(new_block.index)+" to blockchain\n",'green'))
		
	#else:
		#print(colored("Unable to validate broadcasted block.\n",'red'))
	'''
	for b in new_node.chain.blocks:
		print("..................BLOCK....................")
		print("index",b.index)
		print("block hash", b.hash)
		print("previous hash",b.previousHash)
		print("block sender", request.form["sender"],"\n")
		for tx in b.listOfTransactions:
			print(colored("amount: " + str(tx.amount),'yellow'))
			print("transaction hash",tx.transaction_id)
	
	#else:
		#print(colored("Block with id "+request.form["index"]+" rejected.\n",'red'))
	'''
	new_node.chain.lock.release()
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/transactions/create', methods=['POST'])
def create_transactions():
	#print("Getting data to make a new transaction...\n")
	while new_node.conflict:
		pass
	try:
		result = new_node.create_transaction(new_node.ring[int(request.form["receiver_id"])]["key"].encode(),int(request.form["amount"]))
		return jsonify({'status':result}), 200
	except:
		except_str = "\nInvalid recipient id. Try a number in the range [0,"+str(len(new_node.ring)-1)+ "]\n"
		return jsonify({'except':except_str}), 500
	

@app.route('/transactions/view', methods=['GET'])
def view_transactions():
    last_block = new_node.chain.blocks[-1]
    response = {'transactions': json.loads(last_block.to_dict()["listOfTransactions"])}
    return jsonify(response), 200

@app.route('/balance/view', methods=['GET'])
def get_balance():
    balance = new_node.balance(new_node.wallet.public_key,new_node.utxo)
    response = {'balance': balance}
    return jsonify(response), 200
 


# run it once fore every node

if __name__ == '__main__':
	if args.boot == 0 :
		thread = threading.Thread(target=start_register)
		thread.start()
	app.run(host=args.ip,port=args.port,threaded=True)	
