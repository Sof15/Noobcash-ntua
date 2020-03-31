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
from termcolor import colored

N = 5

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
		self.list_lock = threading.Lock()
		self.tx_list = []
		self.conflict = False
		self.times = 0
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
			while(1):
				try:
					r = requests.post(url,data)
					if r.status_code == 200:
						break
				except Exception as e:
					time.sleep(2)
			#print ("data to post:", r.text)
		return r

	def create_genesis_block(self,difficulty,capacity):
		if self.id==0 :
			sender = "0".encode()
			#trans = [create_transaction(sender,self.wallet.public_key, 100*5)]
			#edo isos na min einai sostos o tropos pou dimiourgoume to transaction
			first_trans = transaction.Transaction( self.wallet.public_key, self.wallet.private_key, self.wallet.public_key, 100*N,[])
			
			rand_id = uuid.uuid1()
			
			first_utxo = {'id': first_trans.transaction_id + "0", 'amount':100*N, 'previous_trans_id': -1, 'recipient': self.wallet.public_key.decode()} # isos thelei public key anti gia id 
			self.utxo.append(first_utxo)
			#trans = [first_trans]
			self.current_block = block.Block(0, '1',[] ,difficulty)
			self.add_transaction_to_block(first_trans,capacity,difficulty)
		else:
			print("error")
		return 1

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
			while(1):
				try:
					r = requests.post(url,data)
					if r.status_code == 200:
						break
				except Exception as e:
					time.sleep(2)

			if (len(self.ring)==N):
				for i in range(1,N):
					url = "http://"+self.ring[i]["address"]+"/broadcast/ring"
					print("Broadcasting ring....\n")
					data = {}
					dumped = json.dumps(self.ring)
					data ={"ring":dumped}
					
					while(1):
						try:
							r = requests.post(url,data)
							if r.status_code == 200:
								break
						except Exception as e:
							time.sleep(2)
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
			
			
			threads = []
			#print("THREAD:",threading.get_ident())
			start = time.time()
			for i in range(len(self.ring)):
				if i!=self.id:
					url = "http://" + self.ring[i]["address"] + "/broadcast/transaction"
					print("Broadcasting Transaction at URL:",url,"\n")
					thread = threading.Thread(target=self.broadcast_transaction,args = (trans,url,start))
					thread.start()
					threads.append(thread)

			if self.id < len(self.ring):
				url = "http://" + self.ring[self.id]["address"] + "/broadcast/transaction"
				self.broadcast_transaction(trans,url,start)

			for t in threads:
				t.join()
			
			
		else:
			print(colored("Not enough NBCs to complete Transaction with AMOUNT: " +str(amount)+"!\n",'red'))
			return 0
		return 1


	def broadcast_transaction(self,transaction,url,start):
		#print("THREAD:",threading.get_ident())
		data = transaction.to_dict()
		data["time"] = start
		#for i in range(len(self.ring)):
		#	url = "http://" + self.ring[i]["address"] + "/broadcast/transaction"
		while(1):
			try:
				r = requests.post(url,data)
				if r.status_code == 200:
					break
			except Exception as e:
				time.sleep(2)
		


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
					if x==utxo_in["id"]:
						idx.append(i)

			# for the id concatenate transaction id with 0 if it's a change utxo otherwise with 1
			idx = [i for i in range(len(self.utxo)) if i not in idx]
			change_utxo = {}
			change_utxo["id"] = tx.transaction_id+"0"
			change_utxo["previous_trans_id"] = tx.transaction_id
			change_utxo["amount"] = self.balance(tx.sender_address,tx.transaction_inputs)-tx.amount
			change_utxo["recipient"] = tx.sender_address.decode()

			tx.transaction_outputs.append(change_utxo)

			recipient_utxo = {}
			recipient_utxo["id"] = tx.transaction_id+"1"
			recipient_utxo["previous_trans_id"] = tx.transaction_id 
			recipient_utxo["amount"] = tx.amount
			recipient_utxo["recipient"] = tx.receiver_address.decode()
			self.utxo = [self.utxo[x] for x in idx]
			if change_utxo["amount"] != 0:
				self.utxo.append(change_utxo)
			self.utxo.append(recipient_utxo)

			print(colored("Transaction Validated!\n",'green'))
			total = 0
			for u in self.utxo:
				print(".............UTXO..................")
				print(colored("amount:" + str(u["amount"]),'yellow'))
				total+= int(u["amount"])
				for i,r in enumerate(self.ring):
					if u["recipient"]==r["key"]:
						print("owner",i)
			print("TOTAL:",colored(total,'yellow'))
			self.tx_lock.release()
			return 1
		else: 
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
		b = self.current_block
		print("...............CURRENT BLOCK....................")
		print("index",b.index)
		print("block hash", b.hash)
		print("previous hash",b.previousHash)
		print()
		for tx in b.listOfTransactions:
			print("amount",tx.amount)
			print("transaction hash",tx.transaction_id)
		#print("THREAD",threading.get_ident(),"AT",time.time())
		#print(len(self.current_block.listOfTransactions))
		if len(self.current_block.listOfTransactions) == capacity or self.current_block.index == 0:
			print("Current block full! Creating new current block...\n")
			if self.current_block.index != 0 :
				print("Mining full Block...\n")
				hash_result,nonce = self.mine_block(self.current_block,difficulty_bits)
				#time.sleep(1) #wait for the full block to be added to the blockchain first by some miner
				if hash_result == 0:
					return 0
				self.current_block.hash = hash_result
				self.current_block.nonce = nonce
			else:
				self.chain.lock.acquire()
				self.chain.add_block(self.current_block)
				self.chain.lock.release()
			
			#if not self.conflict:
			self.current_block = self.create_new_block(difficulty_bits,[])
			#else:
				#self.conflict = False
		
		self.current_lock.release()
		'''
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
				
		print("\n")
		'''
		
		return 1



	def mine_block(self,block,difficulty_bits):
		#nonce is a 32-bit number appended to the header. the whole string is being hashed repeatedly until
		#the hash result starts with difficulty number of zeros
		#header of block without nonce
		print("BLOCK HASH BEFORE MINING:",block.hash)
		header = str(block.index) + str(block.previousHash) + block.hashmerkleroot + str(block.timestamp) + str(difficulty_bits)
		#trying to find the nonce number 32 bits --> 2**32-1 max nonce number
		for nonce in range(block.nonce,2**32):
			hash_result = SHA256.new((header+str(nonce)).encode()).hexdigest()
			if self.valid_proof(hash_result,difficulty_bits):
				print (colored("Success with nonce: " + str(nonce),'green'))
				print ("Block Hash is",hash_result,"\n")
				block.hash = hash_result
				block.nonce = nonce
				
				
				threads = []
				
				for i in range(len(self.ring)):
					url = "http://" + self.ring[i]["address"] + "/broadcast/block"
					thread = threading.Thread(target=self.broadcast_block,args = (block,url))
					thread.start()
					threads.append(thread)
				
				for t in threads:
					t.join()
				
				
				return hash_result, nonce

		print (colored("Failed after " +str(2**32-1) +" tries\n",'red'))
		return 0,0


	def broadcast_block(self,block,url):
		data = block.to_dict()
		#for i in range(len(self.ring)):
		#	url = "http://" + self.ring[i]["address"] + "/broadcast/block"
		data["sender"]=self.id
		print("Broadcasting Mined Block with id",block.index,"at URL:",url,"\n")
		while(1):
			try:
				r = requests.post(url,data)
				if r.status_code == 200:
					break
			except Exception as e:
				time.sleep(2)
		
		

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
			if block.index > len(chain.blocks):
				idx = -1
			else:
				idx = block.index-1
			if self.valid_proof(h,difficulty_bits) and block.previousHash == chain.blocks[idx].hash:
				return 1
			elif block.previousHash != chain.blocks[idx].hash:
				self.conflict = True
				print(colored("ERROR - BLOCKCHAIN CONFLICT\n",'red'))
				#print("GOT BLOCK WITH PREVHASH:", block.previousHash, "MY PREVHASH IS:",chain.blocks[idx].hash,"\n")
				print("Resolving blockchain conflicts...\n")
				if self.resolve_conflicts():
					self.conflict = False
				#self.resolve_conflicts()
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
		
		data = {"address": self.ring[self.id]["address"]}
		#self.chain.lock.acquire()	#exei klidothei sto broadcast block ap opou kaleitai
		
		lengths = []
		for i in range(len(self.ring)):
			if i != self.id:
				url = "http://" + self.ring[i]["address"] + "/blockchain/length"
				while(1):
					try:
						r = requests.post(url,data)
						if r.status_code == 200:
							lengths.append({"length":json.loads(r.text)["length"],"id":json.loads(r.text)["id"], "conflict":json.loads(r.text)["conflict"]})
							break
					except Exception as e:
						time.sleep(2)
	
		s = 0
		for length in lengths:
			s += length["conflict"]
		
		if s == 4 :
			lengths.append({"length":len(self.chain.blocks),"id":self.id,"conflict":True})
		else:
			lengths = [length for length in lengths if length["conflict"] == False]


		lengths = sorted(lengths,key=lambda k: k["length"],reverse=True)
		print(lengths)
		idxs = [int(length["id"]) for length in lengths if length["length"] == lengths[0]["length"]]
		idx = min(idxs)


		if idx == self.id:
			self.tx_lock.acquire()
			for i in range(len(self.utxo)):
				for tx in self.current_block.listOfTransactions:
					if self.utxo[i]["previous_trans_id"] == tx.transaction_id:
						self.utxo[i]["recipient"] = tx.sender_address.decode()
						break
			
			self.tx_lock.release()
			#self.times = 4
			
		else:
			url = "http://" + self.ring[idx]["address"] + "/blockchain/request"
			print("Asking blockchain from URL:",url)
			data["conflict"] = [length["conflict"] for length in lengths  if length["id"] ==idx][0]
			while(1):
				try:
					r = requests.post(url,data)
					if json.loads(r.text)["status"] == "error":
						self.resolve_conflicts()
						break
					if r.status_code == 200:
						break
				except Exception as e:
					time.sleep(2)
		

		return 1