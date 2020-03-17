import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from argparse import ArgumentParser
import block
import node
import wallet
#import transaction
import time
import threading
import logging 


class Blockchain():
	def __init__(self,):
		self.blocks = [] #list of validated blocks



	def add_block(self,block):
		#add validated block to list
		self.blocks.append(block)

	def remove_block(Self,block):
		#remove a block using its id??
		self.blocks.pop(block.index)
