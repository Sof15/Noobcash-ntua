import requests
import threading
import sys
import time

def make_transactions_from_file(sender,file):
	def read_and_post():
		f = open("transactions/5nodes/"+file, "r")
		#f = open(file, "r")
		for line in f.readlines():
			print(line)
			line = line.split()
			receiver_id = line[0][2:]
			amount = line[1]
			
			data = {}
			data["receiver_id"] = receiver_id
			data["amount"] = amount
			
			# edw na ftiaxoume th swsth ip otan ginei apo ta vm!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			ip="http://127.0.0.1"
			port = "500"+str(sender)

			url = ip+":"+port+"/transactions/create"
			print("Posting new transaction data to Node number "+str(sender)+"\n")
			while(1):
				try:
					r = requests.post(url,data)
					if r.status_code == 200:
						break
				except Exception as e:
					time.sleep(2)
		return r

	thread = threading.Thread(target=read_and_post)
	thread.start()
    
if __name__ == '__main__':

	for filename in sys.argv[1:]:
		sender_node=filename[-5][0] 
		make_transactions_from_file(sender_node,filename)
