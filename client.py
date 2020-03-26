#!/usr/bin/env python3
import argparse
import sys
import requests
import json
from termcolor import colored
from pyfiglet import Figlet
from tabulate import tabulate

	        
class balance:
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--port', type=str, required=True)
		args = parser.parse_args(sys.argv[2:])
		url = "http://0.0.0.0:{}/balance/view".format(args.port)
		r = requests.get(url) 

		print("\033[1m"'The wallet balance is', colored(r.json()["balance"],'yellow'), "\033[1m"'NBC.\n')

class view:
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--port', type=str, required=True)
		args = parser.parse_args(sys.argv[2:])
		url = "http://0.0.0.0:{}/transactions/view".format(args.port)
		r = requests.get(url) 

		print(colored("\033[1m"'The last block has the following transactions...''\033[0m'))
		
		'''for trans in r.json()["transactions"]:
									print(colored("\033[1m"'Transaction: \n','blue'))
									for k,v in trans.items():
										print(colored(k,'yellow'),v)'''
		
		

		print(json.dumps(r.json()["transactions"],indent=4))

		#sys.stdout.write(json.dumps(r.json(), indent=4))

class t:
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--port', type=str, required=True)
		parser.add_argument('--recipient', type=int, required=True)
		parser.add_argument('--amount', type=int, required=True)
		args = parser.parse_args(sys.argv[2:])
		url = "http://0.0.0.0:{}/transaction/create".format(args.port)
		data = {'recipient':args.recipient, 'amount':args.amount}
		r = requests.post(url,data) 
		if(r.status_code==200):
			print(colored("Successfull transaction to node with id {}\n".format(args.recipient),'green'))
		#print(r.status_code)
		#sys.stdout.write(r.text)

class help:
	def __init__(self):
		sys.stdout.write('\nNoobcash CLI: \n\nThe following operations are available! \n\n\tbalance: copmute the current wallet balance \n\n\tview: view the transactions of the last block of the blockchain \n\n') 

		

if __name__ == '__main__':
	result = Figlet(font='slant')
	print(result.renderText("NOOBCASH"))
	
	try:	
		if sys.argv[1]=='balance':
			balance()
		elif sys.argv[1]=='view':
			view()
		elif sys.argv[1]=='t':
			t() #???
		elif sys.argv[1]=='help':
			help()
	except:
		print (colored("\033[1m"'Invalid use of CLI! \nType "help" to find out the usage of this CLI.\n','red'))
