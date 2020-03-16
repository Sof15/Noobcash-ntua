import block
import wallet
import transaction
import requests
import json
import time 


class node:
	def __init__(self, is_bootstrap, ip="192.168.1.1",port=5000):
		#self.NBC=0;#eixe 100 alla to theloume se transaction
		##set

		#self.chain
		
		#self.id = 0 #bootstrap
		#self.NBCs
		self.wallet = wallet.wallet()
		bootstrap_ip = "192.168.1.1"
		bootstrap_port = 5000
		#here we store information for every node, as its id, ...
		#...its address (ip:port) its public key and its balance 
		
		boot_info = "0"+bootstrap_ip+":"+str(bootstrap_port)+str(self.wallet.public_key, 'utf-8')
		self.ring = []
		# all nodes know the ip:port of bootstrap node 
		self.ring.append(boot_info)
		print("start node")

		# every node when first created 
		# sends its ip/port to bootstrap
		if (is_bootstrap==0):
			data = {}
			data["public_key"] = self.wallet.public_key
			data["ip"] = ip
			data["port"] = port
			#data = json.dumps(data)
			url = "http://127.0.0.1"+":"+str(bootstrap_port)+"/register"
			print("visit node is posting...")
			r = requests.post(url,data)
			#print ("data to post:", r.text)


	def create_new_block(self, is_bootstrap):
		if is_bootstrap :
			nonce = 0
			my_hash = 1
			sender = str.encode("0")

			#trans = [create_transaction(sender,self.wallet.public_key, 100*5)]
			#edo isos na min einai sostos o tropos pou dimiourfoume to transactio
			first_trans = transaction.Transaction(sender, sender, self.wallet.public_key, 100*5)
			trans = [first_trans]
			block_new = block.Block(nonce, my_hash, trans)
		return block_new 

	#def create_wallet():
		#create a wallet for this node, with a public key and a private key
		#DE XREIAZETAI THARRW
		

	def register_node_to_ring(self, is_bootstrap,ip,port,public_key):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		print("in here ?")
		if is_bootstrap :
			id_to_give = len(self.ring)
			node_info = str(id_to_give)+ip+":"+str(port)+str(self.wallet.public_key, 'utf-8')
			self.ring.append(node_info)
			data = {}
			data["id"] = id_to_give
			#ip, port 
			print("boot is registering the guest node!")
			url = "http://127.0.0.1"+":"+str(port)+"/get_id"
			time.sleep(5)
			r = requests.post(url,data)
			

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
		#signature = PKCS1_v1_5.new(self.wallet.private_key)
		trans = transaction.Transaction(self.wallet.public_key, (self.wallet).private_key, receiver, amount)
		return (trans)

	#def broadcast_transaction():





	#def validdate_transaction():
		#use of signature and NBCs balance


	#def add_transaction_to_block():
		#if enough transactions  mine



	#def mine_block():



	#def broadcast_block():


		

	#def valid_proof(.., difficulty=MINING_DIFFICULTY):




	#concencus functions

	#def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	#def resolve_conflicts(self):
		#resolve correct chain



