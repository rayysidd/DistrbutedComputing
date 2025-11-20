from flask import Flask,request,jsonify
import threading,requests,time,argparse,sys
from collections import defaultdict
import json

app = Flask(__name__)

NODE_ID =None
PORT=None
Peers=[]
Leader=None
IS_LEADER=False

lamport=0
lamport_lock=threading.lock()

seq_counter = 1
seq_lock = threading.Lock()

transaction_log=[]
log_lock=threading.lock()

balances = defaultdict(int)
balances_lock = threading.Lock()

last_leader_heartbeat= time.time()
HEARTBEAT_INTERVAL=1.0
HEARTBEAT_TIMEOUT=3.0

def increment_lamport(received=None):
    global lamport
    with lamport_lock:
        if received is None:
            lamport+=1

        else:
            lamport=max(lamport,received)+1

        return lamport
    
def apply_transaction_entry(entry):
    with balances_lock:
        balances[entry['from']] -= entry['amount']
        balances[entry['to']] += entry['amount']

