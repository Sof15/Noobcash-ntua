# :money_with_wings: Noobcash :money_with_wings:

## About  
Implementation of a simple blockchain system for the course of Distributed Systems.   
The system allows nodes (participants) to do multiple transactions simultaneously.
The consensus is ensured using Proof-of-Work (PoW).  

## Installation & running  
Install the modules included in requirements.txt file.
```
pip3 install -r requirements.txt
```
Run **rest.py** and the app is running.  
Run **client.py** in a seperate tab to initialize the CLI. 

## Command Line Interface (CLI)
A CLI was developed so that the user can: 
- view his wallet balance
- view the last block's transactions
- make transactions towards other users
- view a help message informing him about the CLI's usage.

## Testing 
The system was tested in a virtual environment consisting of 5 VMs (2 cores, 2Gb RAM, 30Gb disk memory) in order to observe the transaction throughput and the time required for block addition to the chain.  

For the testing run **new_trans.py**.  

Two tests were held:  
- One participant from each VM made transactions to the other 4 users (one at a time). Transactions from all the nodes happened simultaneously.  
- The same experiment was repeated for 10 participants (two at each VM with different port to which they listen).

