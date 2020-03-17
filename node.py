import block
import wallet
import transaction
import requests
import json
import time 
#from flask_socketio import SocketIO


class node:
	def __init__(self, is_bootstrap, ip="192.168.1.1",port=5000):
		
		print("Initializing Node")
	
		#self.NBC=0;#eixe 100 alla to theloume se transaction
		##set

		#self.chain
		self.id = 0	
			
		#self.NBCs
		
		self.wallet = wallet.wallet()
		self.ip = ip
		self.port = port

		bootstrap_ip = "192.168.1.1"
		bootstrap_port = 5000
		#here we store information for every node, as its id, ...
		#...its address (ip:port) its public key and its balance 
		
		boot_info = {}
		boot_info["address"] = bootstrap_ip+":"+str(bootstrap_port)
		boot_info["id"]=self.id
		boot_info["key"] = str(self.wallet.public_key, 'utf-8')
		self.ring = []
		# all nodes know the ip:port of bootstrap node 
		self.ring.append(boot_info)
		

		# every node when first created 
		# sends its ip/port to bootstrap
		
	def register(self,is_bootstrap):
		if (is_bootstrap==0):
			bootstrap_ip = "http://192.168.1.1"
			bootstrap_ip = "http://127.0.0.1"
			bootstrap_port = 5000
			data = {}
			data["public_key"] = self.wallet.public_key
			data["ip"] = self.ip
			data["port"] = self.port
			#data = json.dumps(data)
			url = bootstrap_ip+":"+str(bootstrap_port)+"/register"
			print("New node posting key,ip,port to bootstrap")
			r = requests.post(url,data)
			#print ("data to post:", r.text)
		return r

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
		print("Bootstrap registering new node to ring")
		if is_bootstrap :
			id_to_give = len(self.ring)
			node_info = {}
			node_info["id"] = id_to_give
			node_info["address"] = ip+":"+str(port)
			node_info["key"] = str(self.wallet.public_key, 'utf-8')
			self.ring.append(node_info)
			data = {}
			data["id"] = id_to_give
			print("Bootstrap posting id to new node")
			#ip,port
			url = "http://"+ip+":"+str(port)+"/get_id"
			print("URL:", url)
			r = requests.post(url,data)

			if (len(self.ring)==5):
				#time.sleep(5)
				for i in range(1,5):
					url = "http://"+self.ring[i]["address"]+"/broadcast/ring"
					print("broadcasting....")
					#print(self.ring)
					data = {'net':self.ring}
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



