#!/usr/bin/env python3
import sys
import requests
import json
from termcolor import colored
from pyfiglet import Figlet
from tabulate import tabulate
#import os 
#from urllib3.exceptions import HTTPError as BaseHTTPError


class cli:
	def __init__(self):
		#parser = argparse.ArgumentParser(usage='balance,view,t<><>,help')
		#parser.add_argument('command')
		while(1):
			command = input(colored("\033[1m""[?] ",'blue')).split(" ")	
	
			if command[0]=='balance':
				balance()
			elif command[0]=='view':
				view()
			elif command[0]=='t':
				t()
			elif command[0]=='help':
				help()
			elif command[0]=='exit':
				print(colored("\033[1m""\nBye. See you soon!\n""\033[0m",'blue'))
				break
			else:
				print (colored("\033[1m"'\nInvalid use of CLI! \nType "help" to find out the usage of this CLI.\n','red'))
				        
class balance():
	def __init__(self):
		while(1):
			port = input(colored("\033[1m""\n[port] ",'blue')) 
			url = "http://0.0.0.0:{}/balance/view".format(port)
			if port=='help':
				self.help()
			elif port=="c":
				break
			else:
				try:
					r = requests.get(url)
					if r.status_code == 200:
						print("\033[1m"'\nThe wallet balance is', colored(r.json()["balance"],'yellow'), "\033[1m"'NBCs.\n'"\033[0m")
					break 
				except requests.exceptions.InvalidURL as e:
					print(colored("\033[1m"'\nInvalid input! \nType "help" to find out the usage of this input.\n','red')) 
				except requests.exceptions.ConnectionError as e:
					print(colored("\033[1m"'\nUnable to find a connection with the given input.\nEither the application is not running or the input is wrong.\n','red'))
				except requests.exceptions.RequestException as e:
					print(colored("\033[1m"'\nRequest failed!.\n','red'))
					raise SystemExit(e)
		
	def help(self):
		print(colored("\033[1m"'\n--->Type the port the noobcash is listening to.\n\n--->Type "c" for choosing a different command.\n' ,'blue'))

class view():
	def __init__(self):
		while(1):
			port = input(colored("\033[1m""\n[port] ",'blue'))
			url = "http://0.0.0.0:{}/transactions/view".format(port)
			if port=='help':
				self.help()
			elif port=="c":
				break
			else:
				try:
					r = requests.get(url) 
					if r.status_code == 200:
						header = [colored(x,'yellow') for x in r.json()["transactions"][0].keys()]
						rows = [x.values() for x in r.json()["transactions"]]
						print("\033[1m"'\nThe last block has the following transactions...\n''\033[0m')
						#print(json.dumps(r.json()["transactions"],indent=4))
						print(tabulate(rows,header),"\n")
					break
				except requests.exceptions.InvalidURL as e:
					print(colored("\033[1m"'\nInvalid input! \nType "help" to find out the usage of this input.\n','red')) 
				except requests.exceptions.ConnectionError as e:
					print(colored("\033[1m"'\nUnable to find a connection with the given input.\nEither the application is not running or the input is wrong.\n','red'))
				except requests.exceptions.RequestException as e:
					print(colored("\033[1m"'\nRequest failed!.\n','red'))
					raise SystemExit(e)
		
		
		#sys.stdout.write(json.dumps(r.json(), indent=4))
	def help(self):
		print(colored("\033[1m"'\n--->Type the port the noobcash is listening to.\n\n--->Type "c" for choosing a different command.\n' ,'blue'))

class t():
	def __init__(self):
		while(1):
			to_exit=0
			while(1):#an valo oti na nai sta inputs thelo ena mnm lathous gia na me paei sto usage 
				port = input(colored("\033[1m""\n[port] ",'blue'))
				if port=='help':
					print(self.help('port'))
					continue
				elif port=='c':
					to_exit = 1
					break
				break
			if to_exit: 
				break
			while(1):
				recipient = input(colored("\033[1m""\n[recipient id] ",'blue')) #thelo na aporripto ta arnitika idanika mazi me ta ypoloipa :(
				if recipient=='help':
					print(self.help('recipient'))
					continue
				elif recipient=='c':
					to_exit = 1
					break
				break
			if to_exit: 
				break
			while(1):
				amount = input(colored("\033[1m""\n[amount] ",'blue'))
				if amount=='help':
					print(self.help('amount'))
					continue
				elif amount	=='c':
					to_exit = 1
					break
				break
			if to_exit: 
				break
			url = "http://0.0.0.0:{}/transactions/create".format(port)
			data = {'receiver_id':recipient, 'amount':amount}
			try:
				r = requests.post(url,data) 
				if r.status_code==200:
					if r.json()["status"]:
						print("\nThe transaction went through succesfully!\n")
					else:
						print("\nYou don't have enough money to make the requested transaction!\n")
				elif r.status_code==500:
					print(r.json()["except"])
				break
			except requests.exceptions.InvalidURL as e:
				print(colored("\033[1m"'\nInvalid input! \nType "help" to find out the usage of this input.\n','red')) 
			except requests.exceptions.ConnectionError as e:
				print(colored("\033[1m"'\nUnable to find a connection with the given input.\nEither the application is not running or the given port is wrong.\n','red'))
			except requests.exceptions.RequestException as e:
				print(colored("\033[1m"'\nRequest failed!.\n','red'))
				raise SystemExit(e)
 
	def help(self, help_str):
		out_str=""
		if help_str == 'port':
			out_str = colored("\033[1m"'\n--->Type the port the noobcash is listening to.\n\n--->Type "c" for choosing a different command.\n' ,'blue')
		elif help_str == 'recipient':
			out_str = colored("\033[1m"'\n--->Type the id to which you want to send a transcaction.\n\n--->Type "c" for choosing a different command.\n' ,'blue')
		elif help_str == 'amount':
			out_str = colored("\033[1m"'\n--->Type the amount of NBCs you want to give.\n\n--->Type "c" for choosing a different command.\n' ,'blue')
		return out_str

class help():
	def __init__(self):
		print(colored("\033[1m""\nNoobcash CLI usage:\n\t balance:  Check the wallet balance.\n\t view :  View the transactions of the last block.\n\t t<><>:  New transaction to node with the given id with the given amount.\n\t exit: Quit the noobcash CLI.\n""\033[0m",'blue'))


	

if __name__ == '__main__':
	#.center(os.get_terminal_size().columns)
	result = Figlet(font='slant')
	print(colored(result.renderText("NOOBCASH"),'blue',attrs=['bold']))
	cli()
	