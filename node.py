import block
import wallet
import transaction
import requests
import json
import time 
import hashlib
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
			url = bootstrap_ip+":"+str(bootstrap_port)+"/register"
			print("New node posting key,ip,port to Bootstrap")
			r = requests.post(url,data)
			#print ("data to post:", r.text)
		return r

	def create_new_block(self, is_bootstrap,difficulty_bits):
		if is_bootstrap :
			idx = 0
			previous_hash = 1
			sender = str.encode("0")
			#trans = [create_transaction(sender,self.wallet.public_key, 100*5)]
			#edo isos na min einai sostos o tropos pou dimiourfoume to transaction
			first_trans = transaction.Transaction(sender, sender, self.wallet.public_key, 100*5)
			trans = [first_trans]
			block_new = block.Block(idx, previous_hash, trans,difficulty_bits)
		return block_new 

	#def create_wallet():
		#create a wallet for this node, with a public key and a private key
		#DE XREIAZETAI THARRW
		

	def register_node_to_ring(self, is_bootstrap,ip,port,public_key):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
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
			url = "http://"+ip+":"+str(port)+"/get_id"
			print("Bootstrap posting id to new node at URL:",url)
			r = requests.post(url,data)

			if (len(self.ring)==5):
				for i in range(1,5):
					url = "http://"+self.ring[i]["address"]+"/broadcast/ring"
					print("broadcasting....")
					data = {}
					for i in range(5):
						for k in ['id','address','key']:
							data["{}{}".format(k,i)] = self.ring[i][k]
					r = requests.post(url,data)
		
			

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
		#signature = PKCS1_v1_5.new(self.wallet.private_key)
		trans = transaction.Transaction(self.wallet.public_key, self.wallet.private_key, receiver, amount)
		return (trans)



	#def broadcast_transaction():

	
	#def validate_transaction():
		#use of signature and NBCs balance


	#def add_transaction_to_block():
		#if enough transactions  mine



	def mine_block(self,block,difficulty_bits):
		#nonce is a 32-bit number appended to the header. the whole string is being hashed repeatedly until
		#the hash result starts with difficulty number of zeros
		#header of block without nonce
		header = str(block.idx) + str(block.previousHash) + block.hashmerkleroot[0] + str(block.timestamp) + str(difficulty)
		target = 2 ** (256-difficulty_bits) #number of leading zeros in bits!
		#trying to find the nonce number 32 bits --> 2**32-1 max nonce number
		for nonce in range(2**32):
			hash_result = hashlib.sha256(str(header).encode()+str(nonce).encode()).hexdigest()

			if np.long(hash_result,16) < target : 
				print ("Success with nonce",nonce)
				print ("Hash is",hash_result)
				return (hash_result, nonce)

		print ("Failed after",2**32-1," tries")
		return nonce


	#def broadcast_block():


		

	#def valid_proof(.., difficulty=MINING_DIFFICULTY):




	#concencus functions

	#def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	#def resolve_conflicts(self):
		#resolve correct chain



