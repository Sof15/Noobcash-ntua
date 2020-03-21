import block
import wallet
import transaction
import requests
import json
import time 
import hashlib
from Crypto.Hash import SHA,SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import numpy as np
import uuid

class node:
	def __init__(self, is_bootstrap, ip="192.168.1.1",port=5000):
		
		print("Initializing Node")
	
		#self.NBC=0;#eixe 100 alla to theloume se transaction

		self.id = 0	
		#self.chain = blockchain.Blockchain()	
		#self.NBCs
		
		self.wallet = wallet.wallet()
		self.ip = ip
		self.port = port
		self.utxo = []

		bootstrap_ip = "192.168.1.1"
		bootstrap_ip = "127.0.0.1"
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

	def create_genesis_block(self,difficulty):
		if self.id==0 :
			
			idx = 0
			previous_hash = 1
			sender = "0".encode()
			#trans = [create_transaction(sender,self.wallet.public_key, 100*5)]
			#edo isos na min einai sostos o tropos pou dimiourgoume to transaction
			first_trans = transaction.Transaction( self.wallet.public_key, self.wallet.private_key, self.wallet.public_key, 100*5,[])
			
			rand_id = uuid.uuid1()
			
			first_utxo = {'id': rand_id.int, 'amount':500, 'previous_trans_id': -1, 'recipient': self.wallet.public_key.decode("utf-8") } # isos thelei public key anti gia id 
			self.utxo.append(first_utxo)
			trans = [first_trans]
			#block_new = block.Block(idx, previous_hash, trans,difficulty)
		else:
			print("error")
		#return block_new

	def create_new_block(self, is_bootstrap,difficulty_bits):
		 pass

	#def create_wallet(self):		#DE XREIAZETAI THARRW
		#create a wallet for this node, with a public key and a private key
		#return wallet.wallet()
		

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
			node_info["utxo"] = []
			self.ring.append(node_info)
				
			data = {}
			data["id"] = id_to_give

			
			dumped = json.dumps(self.utxo)
			print(dumped)
			data["utxo"] = dumped
			
			url = "http://"+ip+":"+str(port)+"/data/get"
			print("Bootstrap posting id to new node at URL:",url)
			r = requests.post(url,data)

			if (len(self.ring)==5):
				for i in range(1,5):
					url = "http://"+self.ring[i]["address"]+"/broadcast/ring"
					print("Broadcasting ring....")

					dumped = json.dumps(self.ring)
					data ={"ring":dumped}
					
					r = requests.post(url,data)

	def send_initial_transaction(self, public_key):	
		trans = self.create_transaction(public_key, 100)
		print(trans.amount)		

	def create_transaction(self, receiver, amount):
		#remember to broadcast it
	
		trans_in = []
		total = 0 
		
		print("amount=", amount, type(amount))
		for utxo in self.utxo:
			while(total < amount):
				print("....", utxo["recipient"], "\n ....", self.wallet.public_key)
				if(utxo["recipient"]==self.wallet.public_key.decode("utf-8")):
					total += utxo["amount"] 
					trans_in.append(utxo)
					
	
		trans = transaction.Transaction( self.wallet.public_key, self.wallet.private_key, receiver, amount, trans_in)
		print("Broadcasting transaction...")	
		self.broadcast_transaction(trans)
		return (trans)


	def broadcast_transaction(self,transaction):
		data = transaction.to_dict()
		for i in range(len(self.ring)):
			url = "http://" + self.ring[i]["address"] + "/broadcast/transaction"
			r = requests.post(url,data)



	def verify_signature(self,sender_public_key,signature):
		key = RSA.importKey(sender_public_key)
		h = SHA256.new('To be signed'.encode())  #isos to hash edo??
		verifier = PKCS1_v1_5.new(key)
		if verifier.verify(h,signature):
			return 1
		return 0


	def validate_transaction(self,tx):
		# use of signature and NBCs balance
		# and check tx inputs/outputs for enough NBCs
		found = True
		for utxo_in in tx.transaction_inputs:
			if ((utxo_in["id"] not in [utxo["id"] for utxo in self.utxo]) or utxo_in["recipient"]!=tx.sender_address):
				found = False
				break
		
		# na kanoume kapou na elegxei an aytos poy telnei stelnei dika toy giouria kai oxi tou geitona
		if self.verify_signature(tx.sender_address,tx.signature) and found :	
			idx = []
			temp = [(i,utxo["id"]) for i,utxo in enumerate(self.utxo)]
			for utxo_in in tx.transaction_inputs:
				for i,x in temp:
					if x==utxo_in["id"]:
						idx.append(i)

			self.utxo = [self.utxo[x] for x in idx]	
			change_utxo = {}
			change_utxo["id"] = random.get_random_bytes(48) # str() hexdigest() kati apo ayta 
			change_utxo["previous_trans_id"] = tx.transaction_id 
			change_utxo["amount"] = self.balance(sender_address,self.utxo)-tx.amount
			change_utxo["recipient"] = tx.sender_address
			recipient_utxo = {}
			recipient_utxo["id"] = random.get_random_bytes(48)
			recipient_utxo["previous_trans_id"] = tx.transaction_id 
			recipient_utxo["amount"] = tx.amount
			recipient_utxo["recipient"] = self.wallet.public_key
			self.utxo.append(change_utxo)
			self.utxo.append(recipient_utxo)
			return 1
		else: 
			print("no validated!")
		return 0

	def balance(recipient,utxo_list):
		total = 0
		for utxo in utxo_list:
			if (utxo["recipient"]==recipient):
				total += utxo["amount"]
		return total

	def add_transaction_to_block(self,block,tx,capacity,difficulty_bits): #blockchain??
		
		block.listOfTransactions.append(tx)
		block.hashmerkleroot = block.MerkleRoot()
		block.hash = block.myHash(difficulty_bits)
		if len(block.listOfTransactions) == capacity:
			hash_result,nonce = self.mine_block(block,difficulty_bits)
			if hash_result != 0:
				return block.listOfTransactions,block.hashmerkleroot,hash_result,nonce
		return block.listOfTransactions,block.hashmerkleroot



	def mine_block(self,block,difficulty_bits):
		#nonce is a 32-bit number appended to the header. the whole string is being hashed repeatedly until
		#the hash result starts with difficulty number of zeros
		#header of block without nonce
		header = str(block.index) + str(block.previousHash) + block.hashmerkleroot[0] + str(block.timestamp) + str(difficulty_bits)
		#trying to find the nonce number 32 bits --> 2**32-1 max nonce number
		for nonce in range(2**32):
			hash_result = hashlib.sha256((header+str(nonce)).encode()).hexdigest()
			if self.valid_proof(hash_result,difficulty_bits):
				print ("Success with nonce",nonce)
				print ("Hash is",hash_result)
				block.hash = hash_result
				block.nonce = nonce
				self.broadcast_block(block)
				return hash_result, nonce

		print ("Failed after",2**32-1," tries")
		return 0,0


	def broadcast_block(self,block):
		data = {}
		data["index"] = block.index
		data["previousHash"] = block.previousHash
		data["hash"] = block.hash
		data["nonce"] = block.nonce
		data["hashmerkleroot"] = block.hashmerkleroot
		data["timestamp"] = block.timestamp
		#data["listOfTransactions"] = block.listOfTransactions auto na kanoyme
		for i in range(len(self.ring)):
			if i != self.id:
				url = "http://" + self.ring[i]["address"] + "/broadcast/block"
				r = requests.post(url,data)

		

	def valid_proof(self,hash_result, difficulty):

		target = 2 ** (256-difficulty) #number of leading zeros in bits!
		if np.long(hash_result,16) < target : 
				return 1
		return 0


	def validate_block(self,block,blockchain,difficulty_bits):
		#validate every new block except for genesis block
		if block.index != 0:
			header = str(block.index) + str(block.previousHash) + block.hashmerkleroot[0] + str(block.timestamp) + str(difficulty_bits) #+ str(block.nonce)
			h = SHA256.new(header.encode()).hexdigest()
			if block.hash == h and block.previousHash == blockchain.blocks[block.index-1].hash:
				return 1
			return 0
		return 1

	#concencus functions

	#def validate_chain(self, chain):
		#check for the longer chain accroose all nodes


	#def resolve_conflicts(self):
		#resolve correct chain



