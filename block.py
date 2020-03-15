
#import blockchain
from datetime import datetime
import Crypto.Random.random as rnd
import hashlib

class Block:
	#otan kapoios dimiourgei to block theloume na vroume to index
	#gia na ginei ayto theloume to megethos tou blockchain ara the prepei 
	#na to dinei san parametro stin _init_
	def __init__(self,idx, prev_hash, list_trans):
		##set
		self.index = idx
		self.previousHash = prev_hash

		self.timestamp = datetime.timestamp(datetime.now())

		#self.hash 
		if idx == 0:
			self.nonce = 1
		else: 
			self.nonce = int(str(rnd.getrandbits(32)) + str(int(self.timestamp)))

		self.listOfTransactions = list_trans
	
	def myHash(self):
		#info of blockchain to hash
		info = {}
		info["index"] = self.index
		info["timestamp"] = self.timestamp
		info["transactions"] = self.listOfTransactions
		info["nonce"] = self.nonce
		info["previous_hash"] = self.previousHash
		#convert the above dictionary to string 
		#so that it can be hashed
		str_to_hash = str(info)
		#calculate self.hash
		self.hash = hashlib.sha256(str_to_hash.encode()).hexdigest()
		return self.hash


	#def add_transaction(transaction transaction, blockchain blockchain):
		#add a transaction to the block