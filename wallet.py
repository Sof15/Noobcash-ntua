import binascii

#import Crypto
from Crypto import Random
#from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import uuid


class wallet:



	def __init__(self):
		key = RSA.generate(2048)
		self.public_key = key.publickey().exportKey("PEM")
		self.private_key = key.exportKey("PEM")
		
		



