import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from argparse import ArgumentParser
import block
import node
import wallet
import transaction
import time
import threading
import logging 
import jsonpickle


class Blockchain(object):
	def __init__(self,):
		self.blocks = [] #list of validated blocks
		self.lock = threading.Lock()


	def add_block(self,block):
		#add validated block to list
		self.blocks.append(block)

	"""
	def to_dict(self):
		temp_list = []
		for block in self.blocks:
			temp_list.append(block.to_dict())
		return temp_list
	"""

	def serialize(self):
		temp = jsonpickle.encode(self.blocks)
		return temp