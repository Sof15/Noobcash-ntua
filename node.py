import block
import wallet
import transaction
import requests
import json
import time
import blockchain
from Crypto.Hash import SHA,SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import numpy as np
import uuid
import threading
import copy


class node:
	def __init__(self, is_bootstrap, ip="192.168.1.1",port=5000):
		
		print("Initializing Node")
	
		#self.NBC=0;#eixe 100 alla to theloume se transaction

		self.id = 0	
		self.chain = blockchain.Blockchain()
		self.wallet = wallet.wallet()
		self.ip = ip
		self.port = port
		self.utxo = []
		self.ring = []
		self.current_block = None 
		self.current_lock = threading.Lock()
		self.tx_lock = threading.Lock()
		#here we store information for every node, as its id, ...
		#...its address (ip:port) its public key and its balance 
		if is_bootstrap:
			boot_info = {}
			boot_info["address"] = ip+":"+str(port)
			boot_info["id"]=self.id
			boot_info["key"] = self.wallet.public_key.decode()
			
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
			print("New node posting key,ip,port to Bootstrap\n")
			r = requests.post(url,data)
			#print ("data to post:", r.text)
		return r

	def create_genesis_block(self,difficulty,capacity):
		if self.id==0 :
			
			idx = 0
			previous_hash = '1'
			sender = "0".encode()
			#trans = [create_transaction(sender,self.wallet.public_key, 100*5)]
			#edo isos na min einai sostos o tropos pou dimiourgoume to transaction
			first_trans = transaction.Transaction( self.wallet.public_key, self.wallet.private_key, self.wallet.public_key, 100*5,[])
			
			rand_id = uuid.uuid1()
			
			first_utxo = {'id': first_trans.transaction_id + "0", 'amount':500, 'previous_trans_id': -1, 'recipient': self.wallet.public_key.decode()} # isos thelei public key anti gia id 
			self.utxo.append(first_utxo)
			#trans = [first_trans]
			block_new = block.Block(idx, previous_hash,[] ,difficulty)
			self.current_block=block_new
			self.add_transaction_to_block(first_trans,capacity,difficulty)
		else:
			print("error")
		return block_new

	def create_new_block(self,difficulty_bits,tx):
		self.chain.lock.acquire()
		new_block = block.Block(len(self.chain.blocks),self.chain.blocks[-1].hash,tx,difficulty_bits)
		self.chain.lock.release()
		return new_block
		

	def register_node_to_ring(self, is_bootstrap,ip,port,public_key):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		print("Bootstrap registering new node to ring\n")
		if is_bootstrap :

			id_to_give = len(self.ring)
			node_info = {}
			node_info["id"] = id_to_give
			node_info["address"] = ip+":"+str(port)
			node_info["key"] = public_key.decode()
			node_info["utxo"] = []						#balance sto ring??
			
			self.ring.append(node_info)
				
			data = {}
			data["id"] = id_to_give			
			data["utxo"] = json.dumps(self.utxo)
			data["blocks"] = json.dumps(self.chain.to_dict())
			data["current_block"] = json.dumps(self.current_block.to_dict())
			#print(data["current_block"])
			#print(data["blocks"])
			#print("SENDING BLOCKS:",self.chain.blocks[0].listOfTransactions[0].signature)
			url = "http://"+ip+":"+str(port)+"/data/get"
			print("Bootstrap posting blockchain,id,utxos to new node at URL:",url,"\n")
			r = requests.post(url,data)
			if (len(self.ring)==5):
				for i in range(1,5):
					url = "http://"+self.ring[i]["address"]+"/broadcast/ring"
					print("Broadcasting ring....\n")
					#print(self.ring)
					dumped = json.dumps(self.ring)
					data ={"ring":dumped}
					
					r = requests.post(url,data)
			return r

	def create_transaction(self, receiver, amount):
		trans_in = []
		total = 0 
		for utxo in self.utxo:
			if(total < amount):
				if(utxo["recipient"]==self.wallet.public_key.decode()):
					total += utxo["amount"] 
					trans_in.append(utxo)
			else:
				break

		if total >= amount:
			print("Creating Transaction with amount:",amount,"NBCs\n")
			trans = transaction.Transaction( self.wallet.public_key, self.wallet.private_key, receiver, amount, trans_in)
			print("Broadcasting Transaction...\n")
			'''
			threads = []
			#print("THREAD:",threading.get_ident())
			for i in range(len(self.ring)):
				url = "http://" + self.ring[i]["address"] + "/broadcast/transaction"
				print("Broadcasting Transaction at URL:",url,"\n")
				thread = threading.Thread(target=self.broadcast_transaction,args = (trans,url))
				thread.start()
				threads.append(thread)

			for t in threads:
				t.join(timeout = 5)
			'''
			self.broadcast_transaction(trans)
		else:
			print("Not enough NBCs to complete Transaction!\n")
			return 0
		return 1


	def broadcast_transaction(self,transaction):
		data = transaction.to_dict()
		for i in range(len(self.ring)):
			url = "http://" + self.ring[i]["address"] + "/broadcast/transaction"
			r = requests.post(url,data)
		


	def verify_signature(self,sender_public_key,signature,tx_id):
		key = RSA.importKey(sender_public_key)
		h = SHA256.new(tx_id)
		verifier = PKCS1_v1_5.new(key)
		if verifier.verify(h,signature):
			return 1
		return 0


	def validate_transaction(self,tx):
		# use of signature and NBCs balance
		# and check tx inputs/outputs for enough NBCs
		self.tx_lock.acquire()
		print("Validating broadcasted transaction...\n")
		found = True
		for utxo_in in tx.transaction_inputs:
			if ((utxo_in["id"] not in [utxo["id"] for utxo in self.utxo]) or utxo_in["recipient"]!=tx.sender_address.decode()):
				found = False
				break
		#print(found)
		if self.verify_signature(tx.sender_address,tx.signature,tx.temp_id) and found :	
			idx = []
			temp = [(i,utxo["id"]) for i,utxo in enumerate(self.utxo)]

			for utxo_in in tx.transaction_inputs:
				for i,x in temp:
					if x!=utxo_in["id"]:
						idx.append(i)

			# for the id concatenate transaction id with 0 if it's a change utxo otherwise with 1 
			change_utxo = {}
			change_utxo["id"] = tx.transaction_id+"0"
			change_utxo["previous_trans_id"] = tx.transaction_id
			change_utxo["amount"] = self.balance(tx.sender_address,tx.transaction_inputs)-tx.amount
			change_utxo["recipient"] = tx.sender_address.decode()
			recipient_utxo = {}
			recipient_utxo["id"] = tx.transaction_id+"1"
			recipient_utxo["previous_trans_id"] = tx.transaction_id 
			recipient_utxo["amount"] = tx.amount
			recipient_utxo["recipient"] = tx.receiver_address.decode()
			self.utxo = [self.utxo[x] for x in idx]
			self.utxo.append(change_utxo)
			self.utxo.append(recipient_utxo)

			print("Transaction Validated!\n")

			for u in self.utxo:
				print(".............UTXO..................")
				print("amount",u["amount"])

				for i,r in enumerate(self.ring):
					if u["recipient"]==r["key"]:
						print("owner",i)
			self.tx_lock.release()
			return 1
		else: 
			print("Unable to validate Transaction.")
		self.tx_lock.release()
		return 0

	def balance(self,recipient,utxo_list):
		total = 0
		for utxo in utxo_list:
			if (utxo["recipient"]==recipient.decode()):
				total += utxo["amount"]
		return total

	def add_transaction_to_block(self,tx,capacity,difficulty_bits):
		self.current_lock.acquire()
		self.current_block.listOfTransactions.append(tx)
		self.current_block.hashmerkleroot = self.current_block.MerkleRoot()
		self.current_block.hash = self.current_block.myHash(difficulty_bits)
		#print("THREAD",threading.get_ident(),"AT",time.time())
		#print(len(self.current_block.listOfTransactions))
		if len(self.current_block.listOfTransactions) == capacity or self.current_block.index == 0:
			print("Current block full! Creating new current block...\n")
			if self.current_block.index != 0 :
				print("Mining full Block...\n")
				hash_result,nonce = self.mine_block(self.current_block,difficulty_bits)
				if hash_result == 0:
					return 0
				self.current_block.hash = hash_result
				self.current_block.nonce = nonce
			else:
				self.chain.lock.acquire()
				self.chain.add_block(self.current_block)
				self.chain.lock.release()
			'''
			print("..........AFTER ADD BLOCK..........\n")
			for b in self.chain.blocks:
				print("..................BLOCK....................")
				print("index",b.index)
				print("block hash", b.hash)
				print("previous hash",b.previousHash)
				print("block sender", self.id)
				print()
				for tx in b.listOfTransactions:
					print("amount",tx.amount)
					print("transaction hash",tx.transaction_id)
			'''
			self.current_block = self.create_new_block(difficulty_bits,[])
		self.current_lock.release()
		print("\n")
		b = self.current_block
		print("...............CURRENT BLOCK....................")
		print("index",b.index)
		print("block hash", b.hash)
		print("previous hash",b.previousHash)
		print()
		for tx in b.listOfTransactions:
			print("amount",tx.amount)
			print("transaction hash",tx.transaction_id)
		return 1



	def mine_block(self,block,difficulty_bits):
		#nonce is a 32-bit number appended to the header. the whole string is being hashed repeatedly until
		#the hash result starts with difficulty number of zeros
		#header of block without nonce
		print("BLOCK HASH BEFORE MINING:",block.hash)
		header = str(block.index) + str(block.previousHash) + block.hashmerkleroot + str(block.timestamp) + str(difficulty_bits)
		#trying to find the nonce number 32 bits --> 2**32-1 max nonce number
		for nonce in range(2**32):
			hash_result = SHA256.new((header+str(nonce)).encode()).hexdigest()
			if self.valid_proof(hash_result,difficulty_bits):
				print ("Success with nonce",nonce)
				print ("Block Hash is",hash_result,"\n")
				block.hash = hash_result
				block.nonce = nonce
				
				'''
				threads = []
				for i in range(len(self.ring)):
					url = "http://" + self.ring[i]["address"] + "/broadcast/block"
					thread = threading.Thread(target=self.broadcast_block,args = (block,url))
					thread.start()
					threads.append(thread)
				
				for t in threads:
					t.join(timeout=5)
				'''
				self.broadcast_block(block)
				return hash_result, nonce

		print ("Failed after",2**32-1," tries")
		return 0,0


	def broadcast_block(self,block):
		data = block.to_dict()
		for i in range(len(self.ring)):
			url = "http://" + self.ring[i]["address"] + "/broadcast/block"
			data["sender"]=self.id
			print("Broadcasting Mined Block with id",block.index,"at URL:",url,"\n")
			r = requests.post(url,data)
		
		

	def valid_proof(self,hash_result, difficulty):
		target = 2 ** (256-difficulty) #number of leading zeros in bits!
		if np.long(hash_result,16) < target : 
				return 1
		return 0


	def validate_block(self,block,difficulty_bits,chain):
		#validate every new block except for genesis block
		if block.index != 0:
			header = str(block.index) + str(block.previousHash) + block.hashmerkleroot + str(block.timestamp) + str(difficulty_bits) + str(block.nonce)
			h = SHA256.new(header.encode()).hexdigest()
			if self.valid_proof(h,difficulty_bits) and block.previousHash == chain.blocks[block.index-1].hash:
				return 1
			elif block.previousHash != chain.blocks[block.index-1].hash:
				print("before resolve conflicts in validation block")
				if self.resolve_conflicts():
					return 1
				else:
					return 0
			return 0
		return 1

	#concencus functions

	def validate_chain(self,chain,difficulty_bits):
		#check for the longer chain across all nodes
		for block in chain.blocks:
			if not self.validate_block(block,difficulty_bits,chain):
				return 0
		return 1

	def resolve_conflicts(self):
		#resolve correct chain
		chainlength = len(self.chain.blocks)
		while(len(self.chain.blocks) == chainlength):
			#print("here")
			# to ring einai keno ... gt ??????? a nai pairnei to ring afou mpoun oloi. POVLIMA! 
			for i in range(len(self.ring)):
				print("here2")
				if i != self.id:
					print("here3")
					data = {}
					data["address"] = self.ring[self.id]["address"]
					data["mylength"] = len(self.chain.blocks)
					url = "http://" + self.ring[i]["address"] + "/blockchain/request"
					r = requests.post(url,data)

		return 1