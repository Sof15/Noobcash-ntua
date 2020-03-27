import requests
import threading
import sys

def make_transactions_from_file(sender,file):
	def read_and_post():
		f = open("transaction/5nodes/"+file, "r")
		for line in f.readlines():
			print(line)
			line = line.split()
			receiver_id = line[0][2:]
			amount = line[1]
			
			data = {}
			data["receiver_id"] = receiver_id
			data["amount"] = amount
			
			# edw na ftiaxoume th swsth ip otan ginei apo ta vm!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			ip="http://0.0.0.0"
			port = "500"+str(sender)

			url = ip+":"+port+"/transactions/get"
			print("Posting new transaction data to Node number "+str(sender)+"\n")
			r = requests.post(url,data)
		return r

	thread = threading.Thread(target=read_and_post)
	thread.start()
    
if __name__ == '__main__':

	for filename in sys.argv[1:]:
		sender_node=filename[-5][0] 
		make_transactions_from_file(sender_node,filename)
