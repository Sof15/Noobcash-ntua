import requests
import threading
import sys
import time
from termcolor import colored
from pyfiglet import Figlet
import json

def read_and_post(file,sender,num_nodes):
	f = open("transactions/"+str(num_nodes)+"nodes/"+file, "r")
	#f = open(file, "r")
	count=1
	for line in f.readlines():
		#print(line)
		global c_lock
		global c

		c_lock.acquire()
		c+=1
		c_lock.release()
		line = line.split()
		receiver_id = line[0][2:]
		amount = line[1]
		
		data = {}
		data["receiver_id"] = receiver_id
		data["amount"] = amount
		print("receiver",receiver_id)
		print("sender",sender)		
		# edw na ftiaxoume th swsth ip otan ginei apo ta vm!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		#ip="http://127.0.0.1"
		ip="http://192.168.1."+str((int(sender)%5)+1)
		port = "500"+sender

		url = ip+":"+port+"/transactions/create"
		print("Transaction number",count,"of Node number",sender,"\n")
		count+=1
		while(1):
			try:
				r = requests.post(url,data)
				if r.status_code == 200:
					break
			except Exception as e:
				time.sleep(2)
	return r
    
if __name__ == '__main__':

	c_lock=threading.Lock()
	c=0
	num_nodes=len(sys.argv[1:])
	start=time.time()
	
	threads=[]
	for file in sys.argv[1:]:
		sender=file[-5][0] 
		thread = threading.Thread(target=read_and_post, args=(file,sender,num_nodes))
		thread.start()
		threads.append(thread)

	for t in threads:
		t.join()

	total_time=time.time()-start
	throughput=c/total_time
	total_time=time.strftime("%M:%S", time.localtime(total_time))


	total_mining_times=[]
	nums=[]

	time.sleep(5)
	for i in range(len(sys.argv[1:])):
		ip = "192.168.1."+str((i%5)+1)
		#ip = "127.0.0.1"
		port = "500"+str(i)
		url = "http://"+ip+":"+port+"/mining/stats"
		while(1):
			try:
				r = requests.get(url)
				if r.status_code == 200:
					break
			except Exception as e:
				print(str(e))
				time.sleep(2)
		total_mining_times.append(json.loads(r.text)["total_mining_time"])
		nums.append(json.loads(r.text)["num_of_minings"])

	print(colored("\nDONE !","green"))
	print(colored("**********************************************************","yellow"))
	print(colored("Total time elapsed:","blue"),total_time)
	print(colored("Number of Transactions:","blue"),c)
	print(colored("Throughput:","blue"),throughput,"transaction/sec")
	print(colored("**********************************************************","yellow"))
	print(colored("                       Mining Stats","blue"))
	node=0
	for t, count in zip(total_mining_times,nums):
		print(colored("**********************************************************","yellow"))
		print(colored("Node "+str(node)+":","blue"))
		#temp=time.strftime("%M:%S.%f", time.localtime(t))
		#avg= time.strftime("%M:%S.%f", time.localtime(t/count))
		print("Total Mining Time:",t,"sec")
		print("Num of Successful Minings:",count)
		if count != 0:
			print("Average Mining Time per Block:",t/count,"sec")
		else:
			print("Average Mining Time per Block: - ")
		node+=1
	print(colored("**********************************************************","yellow"))
	print(colored("All Nodes:","blue"))
	t=sum(total_mining_times)
	count=sum(nums)
	#temp=time.strftime("%M:%S.%f", time.localtime(t))
	#avg= time.strftime("%M:%S.%f", time.localtime(t/count))
	print("Total Mining Time:",t,"sec")
	print("Num of Successful Minings:",count)
	print("Average Mining Time per Block:",t/count,"sec")
	print(colored("**********************************************************","yellow"))


