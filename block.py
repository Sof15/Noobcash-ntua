
import blockchain
from datetime import datetime
import Crypto.Random.random as rnd
from Crypto.Hash import SHA,SHA256
import json
import threading
import random

class Block:
	def __init__(self,idx, prev_hash, list_trans,difficulty_bits):
		self.index = idx
		self.previousHash = prev_hash  #hash of the previous block header
		self.timestamp = datetime.timestamp(datetime.now())
		if idx == 0:
			self.nonce = 0
		else:
			self.nonce = random.randint(0,2**32-1)
		self.listOfTransactions = list_trans
		self.hashmerkleroot = self.MerkleRoot()
		self.hash = self.myHash(difficulty_bits)
		
	
	def to_dict(self):
		data = {}
		data["index"] = self.index
		data["previousHash"] = self.previousHash
		data["timestamp"] = self.timestamp
		data["nonce"] = self.nonce
		temp_list = []
		for tx in self.listOfTransactions:
			temp_list.append(tx.to_dict())
		data["listOfTransactions"] = json.dumps(temp_list)
		data["hashmerkleroot"] = self.hashmerkleroot
		data["hash"] = self.hash
		return data

	def myHash(self,difficulty_bits):
		#calculate self.hash
		header = str(self.index)+str(self.previousHash)+ self.hashmerkleroot +str(self.timestamp)+str(difficulty_bits) #+ str(self.nonce)
		hash_result = SHA256.new(header.encode()).hexdigest()
		return hash_result


	def MerkleRoot(self):
		#calculate hash of merkle tree root
		self.hashmerkleroot = []
		for tx in self.listOfTransactions:
			self.hashmerkleroot.append(tx.transaction_id) #get the id (hash) of every transaction in block
	
		if not self.hashmerkleroot:
			return '0'

		while(len(self.hashmerkleroot)>1):
			#make sure it's a complete binary tree
			if (len(self.hashmerkleroot) % 2 != 0) :
				self.hashmerkleroot.append(self.hashmerkleroot[-1])
			j = 0
			for i in range(0, len(self.hashmerkleroot) - 1,2) :
				self.hashmerkleroot[j] = SHA256.new(str(self.hashmerkleroot[i] + self.hashmerkleroot[i+1]).encode()).hexdigest()
				j += 1

			delete_last = len(self.hashmerkleroot) - j
			del self.hashmerkleroot[-delete_last:]

		return self.hashmerkleroot[0]