#!/usr/bin/env python3
import sys
import requests
import json
from termcolor import colored
from pyfiglet import Figlet
from tabulate import tabulate
from argparse import ArgumentParser



class cli:
	def __init__(self):
		#parser = argparse.ArgumentParser(usage='balance,view,t<><>,help')
		#parser.add_argument('command')
		while(1):
			command = input(colored("\033[1m""[?] ",'blue')).split(" ")	
			try:
				if command[0]=='balance':
					balance()
				elif command[0]=='view':
					view()
				elif command[0]=='t':
					t(command[1],command[2])
				elif command[0]=='help':
					help()
				elif command[0]=='exit':
					print(colored("\033[1m""\n\tBye. See you soon!\n""\033[0m",'blue'))
					break
				else:
					print (colored("\033[1m"'\n\tInvalid use of CLI! \n\tType "help" to find out the usage of this CLI.\n','red'))
			except:
				print (colored("\033[1m"'\n\tInvalid use of CLI! \n\tType "help" to find out the usage of this CLI.\n','red'))
					        
class balance():
	def __init__(self):
		
		url = "http://{}:{}/balance/view".format(ip,port)
		
		
		try:
			r = requests.get(url)
			if r.status_code == 200:
				print('\n\tThe wallet balance is', colored(r.json()["balance"],'yellow'), 'NBCs.\n')
			return 
		except requests.exceptions.InvalidURL as e:
			print(colored("\033[1m"'\n\tInvalid input! \nType "help" to find out the usage of this input.\n','red')) 
		except requests.exceptions.ConnectionError as e:
			print(colored("\033[1m"'\n\tUnable to find a connection with the given input.\n\tEither the application is not running or the input is wrong.\n','red'))
		except requests.exceptions.RequestException as e:
			print(colored("\033[1m"'\n\tRequest failed!.\n','red'))
			raise SystemExit(e)
			
		

class view():
	def __init__(self):
		url = "http://{}:{}/transactions/view".format(ip,port)
		
		try:
			r = requests.get(url) 
			if r.status_code == 200:
				header = [colored(x,'yellow') for x in r.json()["transactions"][0].keys()]
				rows = [x.values() for x in r.json()["transactions"]]
				#print('\nThe last block has the following transactions...\n')
				#print(json.dumps(r.json()["transactions"],indent=4))
				print("\n",tabulate(rows,header),"\n")
			return
		except requests.exceptions.InvalidURL as e:
			print(colored("\033[1m"'\n\tInvalid input! \nType "help" to find out the usage of this input.\n','red')) 
		except requests.exceptions.ConnectionError as e:
			print(colored("\033[1m"'\n\tUnable to find a connection with the given input.\n\tEither the application is not running or the input is wrong.\n','red'))
		except requests.exceptions.RequestException as e:
			print(colored("\033[1m"'\n\tRequest failed!.\n','red'))
			raise SystemExit(e)

		

class t():
	def __init__(self, recipient, amount):
		
		url = "http://{}:{}/transactions/create".format(ip,port)
		data = {'receiver_id':recipient, 'amount':amount}
		try:
			r = requests.post(url,data) 
			if r.status_code==200:
				if r.json()["status"]:
					print("\n\tThe transaction went through succesfully!\n")
				else:
					print("\n\tYou don't have enough money to make the requested transaction!\n")
			elif r.status_code==500:
				print(r.json()["except"])
			return
		except requests.exceptions.InvalidURL as e:
			print(colored("\033[1m"'\n\tInvalid input! \n\tType "help" to find out the usage of this input.\n','red')) 
		except requests.exceptions.ConnectionError as e:
			print(colored("\033[1m"'\n\tUnable to find a connection with the given input.\n\tEither the application is not running or the given port is wrong.\n','red'))
		except requests.exceptions.RequestException as e:
			print(colored("\033[1m"'\n\tRequest failed!.\n','red'))
			raise SystemExit(e)

class help():
	def __init__(self):
		help_str = '''
	This is the noobcash CLI.

	To execute the Command Line Interface:

	client.py ip port [-h] 

	positional arguments:
	ip 			ip of the current machine
	port 			port the app listens to

	optional arguments:
	-h, --help 		show this help message and exit

	COMMANDS:

	balance 		show the wallet balance of the current node
  	view 			view all the transactions of the last valid block of the chain
  	t ID AMOUNT 		transaction of AMOUNT NBCs to ID node
  	help 			show help message regarding the commands of CLI
  	exit                  	exit the CLI'''
		print(help_str)
		print()
		

if __name__ == '__main__':
	#.center(os.get_terminal_size().columns)
	parser = ArgumentParser()
	parser.add_argument('ip',  type=str, help='host of the current node')
	parser.add_argument('port', type=int, help='port to listen to')
	args = parser.parse_args()
	ip = args.ip
	port = args.port
	result = Figlet(font='slant')
	print(colored(result.renderText("NOOBCASH"),'blue',attrs=['bold']))
	print(colored("\033[1m""Welcome to Noobcash CLI!""\033[0m",'blue'))
	print(colored("\033[1m""Noobcash is a simple blockchain system.""\033[0m",'blue'))
	print(colored("\033[1m""Type 'help' to find out more information about the usage of this Command Line Interface!\n""\033[0m",'blue'))
	cli()
	