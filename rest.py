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
import jsonpickle

app = Flask(__name__)
CORS(app)

parser = ArgumentParser()
parser.add_argument('boot', type=int, help='if the current node is the bootstrap enter 1, oterwise enter 0')
parser.add_argument('ip',  type=str, help='host of the current node')
parser.add_argument('port', type=int, help='port to listen to')
args = parser.parse_args()

difficulty_bits = 16 #4,5 hex ->  16,20 bin
capacity = 	10 #10,1,5
txs = []
txs_lock = threading.Lock()

new_node = node.node(args.boot,args.ip,args.port)

if args.boot:
	new_node.create_genesis_block(difficulty_bits,capacity)	

#.......................................................................................

def start_register():
	while(1):
		print("New node being registered...")
		try:
			r = new_node.register(args.boot)
			print("Status Code:",colored(r.status_code,'green'))
			if r.status_code == 200:
				print(colored("New node registered!\n",'green'))
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
	print("Bootstrap got the new node's posted data...\n")
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
	chain.blocks=jsonpickle.decode(request.form["blocks"])


	if new_node.validate_chain(chain,difficulty_bits):
		new_node.chain=chain
		print(colored("New Node validated broadcasted Blockchain\n",'green'))
	else:
		print(colored("New Node unable to validate broadcasted Blockchain\n",'red'))

	new_node.id = int(request.form["id"])	
	#new_node.current_block = jsonpickle.decode(request.form["current_block"])
	new_node.current_block = new_node.create_new_block(difficulty_bits,[])
	new_node.utxo = json.loads(request.form["utxo"])
	print(colored("New node got ID = " + str(request.form["id"])+"\n",'green'))
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
	print("SENDING LENGTH DATA:",data, "AT:",request.form["address"])
	if flag:
		new_node.chain.lock.release()
	
	return jsonify(data), 200


@app.route('/blockchain/request',methods=['POST'])
def give_blockchain():
	print("Sending blockchain at URL:",request.form["address"],"\n")
	#if not new_node.conflict: 	#if I dont have a conflict lock chain before sending 
	new_node.chain.lock.acquire()	

	data = {}
	temp = [b.serialize() for b in new_node.chain.blocks]
	data["blocks"]=json.dumps(temp)
	#new_node.utxo_lock.acquire()
	#data["utxo"] = json.dumps(new_node.utxo)
	#new_node.utxo_lock.release()
	if new_node.chain.lock.locked():  #and  not new_node.conflict:
		new_node.chain.lock.release()
	return jsonify(data), 200



@app.route('/broadcast/ring', methods=['POST'])
def get_ring():
	print("Getting ring from broadcasting....\n")
	new_node.ring = json.loads(request.form["ring"])
	print(colored("New node got ring!\n",'green'))
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/broadcast/transaction', methods=['POST'])
def get_new_transaction():

	while(new_node.conflict):
		pass
	
	new_tx = jsonpickle.decode(request.form["transaction"])
	new_tx.timestamp = float(request.form["time"])
	
	print("Getting transaction from broadcasting....",colored("AMOUNT: " + str(new_tx.amount),'yellow'),"\n")
	
	new_node.list_lock.acquire()
	if not new_node.tx_list or new_tx.timestamp > new_node.tx_list[-1].timestamp:
		new_node.tx_list.append(new_tx)
	else:
		i = 0
		while(new_tx.timestamp > new_node.tx_list[i].timestamp):
			i+=1
		new_node.tx_list.insert(i,new_tx)
	
	for i,tx in enumerate(new_node.tx_list):
		print("TX",i,":",tx.timestamp, "|", tx.transaction_id)
	new_node.list_lock.release()
	
	time.sleep(0.5)
	new_node.list_lock.acquire()
	new_tx = new_node.tx_list.pop(0)
	
	res = []
	new_node.utxo_lock.acquire()
	if new_node.validate_transaction(new_tx):
		new_node.utxo_lock.release()
		res = new_tx.transaction_outputs
		new_node.add_transaction_to_block(new_tx,capacity,difficulty_bits)
		print(colored("Added broadcasted transaction to current block!\n",'green'))
	else:
		new_node.utxo_lock.release()
		print(colored("Unable to validate Transaction.\n",'red'))
	new_node.list_lock.release()

	response = {'outputs': res}
	return jsonify(response), 200


@app.route('/broadcast/block', methods=['POST'])
def get_block():
	
	#adding the first of the broadcasted blocks to blockchain after validating
	
	new_block=jsonpickle.decode(request.form["block"])
	print("Getting block from broadcasting.... BLOCK ID:",new_block.index,colored("AMOUNT: " + str(new_block.listOfTransactions[-1].amount)+"\n",'yellow'))
	#check if the block has already been broadcasted by another miner
	temp = [tx.transaction_id for tx in new_block.listOfTransactions]
	#if (len(new_node.chain.blocks)-1)*capacity > 5:
	txs_lock.acquire()
	for tx_hash in temp:
		if tx_hash in txs[::-1]:
			txs_lock.release()
			print(colored("Transaction ID: " + tx_hash + " already delivered by another miner!\n",'red'))
			response = {'t': 1}
			return jsonify(response), 200

	while(new_node.conflict):
		pass

	new_node.chain.lock.acquire()

	if new_block.index in [b.index for b in new_node.chain.blocks]:
		print(colored("Block with id "+str(new_block.index)+" rejected.\n",'red'))
		new_node.chain.lock.release()
		txs_lock.release()
		response = {'t': 1}
		return jsonify(response), 200
	
	txs.extend(temp)

	txs_lock.release()

	print("Validating broadcasted block...\n")
	if new_node.validate_block(new_block,difficulty_bits,new_node.chain):
		print("Validating Transactions of broadcasted block...\n")
		for new_tx in new_block.listOfTransactions:
			new_node.utxo_lock.acquire()
			new_node.validate_transaction(new_tx)
			new_node.utxo_lock.release()
		new_node.chain.add_block(new_block)
		
		print(colored("Added validated block with id "+str(new_block.index)+" to blockchain\n",'green'))
		
	else:
		print(colored("Unable to validate broadcasted block.\n",'red'))
		'''
		total = 0
		for u in new_node.utxo:
			print("................ UTXOS RECEIVED ..................")
			print(colored("amount:" + str(u["amount"]),'yellow'))
			total+= int(u["amount"])
			for i,r in enumerate(new_node.ring):
				if u["recipient"]==r["key"]:
					print("owner",i)
		print("TOTAL:",colored(total,'yellow'))
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
	
	else:
		print(colored("Block with id "+str(new_block.index)+" rejected.\n",'red'))
	
	new_node.chain.lock.release()
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/transactions/create', methods=['POST'])
def create_transactions():
	print("Getting data to make a new transaction...\n")
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
    global new_node
    response_list=[]
    
    last_block = new_node.chain.blocks[-1]
    for trans in last_block.listOfTransactions:
    	response={}
    	for i,r in enumerate(new_node.ring):
    		if r["key"]==trans.receiver_address.decode():
    			print(i)
    			response["receiver_id"] = i
    		if r["key"]==trans.sender_address.decode():
    			print(i)
    			response["sender_id"] = i
    	response["amount"] = trans.amount
    	#response["output"] = trans.transaction_outputs
    	response_list.append(response)
    print(response_list)
    response = {'transactions': response_list}

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
