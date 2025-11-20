import time
import random

class Server:
    def __init__(self, id):
        self.id = id
        self.is_leader = False
        self.alive = True
        self.clock = 0
        self.balance = 1000

    def increment_clock(self):
        self.clock += 1

    def receive_message(self, timestamp):
        self.clock = max(self.clock, timestamp) + 1

    def crash(self):
        self.alive = False
        self.is_leader = False

    def recover(self):
        self.alive = True

def bully_election(servers):
    alive_servers = [s for s in servers if s.alive]
    leader = max(alive_servers, key=lambda s: s.id)
    leader.is_leader = True
    print(f"Leader elected → Server {leader.id}")
    return leader

def client_transaction(client_id, servers, amount):
    # send to leader only
    leader = next(s for s in servers if s.is_leader)

    leader.increment_clock()
    ts = leader.clock

    leader.balance += amount
    print(f"Client {client_id} → {('Deposit' if amount > 0 else 'Withdraw')} {abs(amount)} | TS={ts}")

    # sync to others
    for s in servers:
        if s != leader and s.alive:
            s.receive_message(ts)
            s.balance = leader.balance

def heartbeat_monitor(servers):
    leader = next((s for s in servers if s.is_leader), None)
    if leader and leader.alive:
        return leader  
    print("Heartbeat failed → leader crashed!")
    return bully_election(servers)

# ---- Simulation ----

servers = [Server(i) for i in [1, 2, 3, 4, 5]]
leader = bully_election(servers)

# 3 transactions
client_transaction(1, servers, +100)
client_transaction(2, servers, -50)

# leader crashes
print("\n*** Leader Crashed ***")
leader.crash()

# new election
leader = heartbeat_monitor(servers)

# more transactions
client_transaction(3, servers, +200)
client_transaction(4, servers, -30)

print("\nFinal Balances:")
for s in servers:
    if s.alive:
        print(f"Server {s.id} | Balance={s.balance} | Clock={s.clock}")
