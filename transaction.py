from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import hashlib

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):


        ##set



        self.sender_address = sender_address #: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = recipient_address #: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value #: το ποσό που θα μεταφερθεί
        #self.transaction_id = #: το hash του transaction
        #self.transaction_inputs #: λίστα από Transaction Input 
        #self.transaction_outputs: λίστα από Transaction Output 
        #self.signature = sender_private_key

        self.transaction_id = hashlib.sha256("something here".encode()).hexdigest()
    


    #def to_dict(self):
        

    def sign_transaction(self,sender_public_key,sender_private_key):
        """
        Sign transaction with private key
        """
        