import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from argparse import ArgumentParser
import block
import node
#import blockchain
import wallet
#import transaction
import time
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
	new_block = new_node.create_new_block(args.boot,difficulty_bits)

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
	response = {'t': 1}
	
	return jsonify(response), 200

@app.route('/get_id', methods=['POST'])
def get_id():
	global new_node
	new_node.id = request.form["id"] 
	print("New node got ID =", request.form["id"])
	response = {'t': 1}
	return jsonify(response), 200


@app.route('/broadcast/ring', methods=['POST'])
def get_ring():
	print("Getting ring from broadcasting....")
	global new_node
	new_node.ring = []
	for i in range(5):
		data = {}
		for k in ['id','address','key']:
			data[k] = request.form.get(key = "{}{}".format(k,i))
		new_node.ring.append(data)
	print("New node got ring =",new_node.ring)
	response = {'t': 1}
	return jsonify(response), 200

@app.route('/broadcast/transaction', methods=['POST'])
def get_new_transaction():
	print("Getting transaction from broadcasting....")
	global new_node
	request.form["sender_address"]
    request.form["receiver_address"]
    request.form["amount"]
    request.form["hash"]
    request.form["signature"]
    #create new transaction??
    if new_node.validate_transaction(new_tx):
    	new_node.add_transaction_to_block()
	print("New node got ring =",new_node.ring)
	response = {'t': 1}
	return jsonify(response), 200

# run it once fore every node

if __name__ == '__main__':
	if args.boot == 0 :
		registernode()
	app.run(host=args.ip,port=args.port)	
