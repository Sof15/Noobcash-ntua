from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA,SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):

        #print(recipient_address)
        self.sender_address = sender_address #: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = recipient_address #: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value #: το ποσό που θα μεταφερθεί
        #self.transaction_inputs #: λίστα από Transaction Input 
        #self.transaction_outputs #: λίστα από Transaction Output 
        h = SHA256.new('something here'.encode())
        self.transaction_id = h.hexdigest() #: το hash του transaction
        self.signature = self.sign_transaction(sender_private_key)


    def to_dict(self):
        #create dictionary of transaction's data for broadcasting
        tx_data = {}
        tx_data["sender_address"] = self.sender_address
        tx_data["receiver_address"] = self.receiver_address
        tx_data["amount"] = self.amount
        tx_data["hash"] = self.transaction_id
        tx_data["signature"] = self.signature
        return tx_data

    def sign_transaction(self,sender_private_key):

        '''
        Sign transaction with private key
        '''
        
        h = SHA256.new('To be signed'.encode()) #message is optional
        key = RSA.importKey(sender_private_key)
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(h)
        return signature
        