
#import blockchain
from datetime import datetime
import Crypto.Random.random as rnd
import hashlib

class Block:
	#otan kapoios dimiourgei to block theloume na vroume to index
	#gia na ginei ayto theloume to megethos tou blockchain ara the prepei 
	#na to dinei san parametro stin _init_
	def __init__(self,idx, prev_hash, list_trans,difficulty_bits):
		##set
		self.index = idx
		self.previousHash = prev_hash  #hash of the previous block header
		self.timestamp = datetime.timestamp(datetime.now())
		
		#if idx == 0:
		self.nonce = 0
		#else: 
		#	self.nonce = int(str(rnd.getrandbits(32)) + str(int(self.timestamp)))
		#print("nonce=",self.nonce)

		self.listOfTransactions = list_trans
		self.hashmerkleroot = self.MerkleRoot()
		self.hash = self.myHash(difficulty_bits)
	

	def myHash(self,difficulty_bits):
		
		header = str(self.index)+str(self.previousHash)+ self.hashmerkleroot[0] +str(self.timestamp)+str(difficulty_bits) #+ str(self.nonce)
		#calculate self.hash
		hash_result = hashlib.sha256(header.encode()).hexdigest()
		return hash_result


	#def add_transaction(transaction transaction, blockchain blockchain):
		#add a transaction to the block
		#update merkleroot, hash

	def MerkleRoot(self):
		#calculate hash of merkle tree root
		self.hashmerkleroot = []
		for tx in self.listOfTransactions:
			self.hashmerkleroot.append(tx.transaction_id) #get the id (hash) of every transaction in block
	
		while(len(self.hashmerkleroot)>1):
			#make sure it's a complete binary tree
			if (len(self.hashmerkleroot) % 2 != 0) :
				self.hashmerkleroot.append(self.hashmerkleroot[-1])
			j = 0
			for i in range(0, len(self.hashmerkleroot) - 1,2) :
				self.hashmerkleroot[j] = hashlib.sha256(str(self.hashmerkleroot[i] + self.hashmerkleroot[i+1]).encode()).hexdigest()
				j += 1

			delete_last = len(self.hashmerkleroot) - j
			del self.hashmerkleroot[-delete_last:]

		return self.hashmerkleroot