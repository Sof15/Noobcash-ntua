from collections import OrderedDict

import binascii
import json
import Crypto
import Crypto.Random
from Crypto.Hash import SHA,SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import uuid

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self,sender_address, sender_private_key, recipient_address, value, trans_in):

        #print(recipient_address)
        self.sender_address = sender_address #: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = recipient_address #: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value #: το ποσό που θα μεταφερθεί
        self.transaction_inputs = trans_in #: λίστα από Transaction Input 
        self.transaction_outputs = [] #: λίστα από Transaction Output 
        temp_id = uuid.uuid1()
        h = SHA256.new(temp_id.bytes)
        self.transaction_id = h.hexdigest() #: το hash του transaction
        if (sender_private_key): 
            self.signature = self.sign_transaction(sender_private_key)
        print("AMOUNT",self.amount)


    def to_dict(self):
        #create dictionary of transaction's data for broadcasting
        tx_data = {}
        tx_data["sender_address"] = self.sender_address
        tx_data["receiver_address"] = self.receiver_address
        tx_data["amount"] = self.amount
        tx_data["hash"] = self.transaction_id
        tx_data["signature"] = self.signature
        tx_data["inputs"] = json.dumps(self.transaction_inputs)
        print("typeeee..", tx_data["inputs"])
        tx_data["outputs"] = json.dumps(self.transaction_outputs)

        return tx_data

    def sign_transaction(self,sender_private_key):

        '''
        Sign transaction with private key
        '''
        print("signature...")
        h = SHA256.new('To be signed'.encode()) #isos to hash edo??
        key = RSA.importKey(sender_private_key)
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(h)
        return signature
        