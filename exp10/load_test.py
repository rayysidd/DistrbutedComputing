import requests
import time
from collections import defaultdict
url = "http://127.0.0.1:8080"
counter = defaultdict(int)
errors = 0

print("Sending 1000 requests to load balancer...\n")


for i in range(1000):
    try:
        response = requests.get(url, timeout=1)
        hostname = response.text.strip().split()[-1]
        counter[hostname] += 1
        print(f"[{i+1}] Handled by: {hostname}")
    except Exception as e:
        errors += 1
        print(f"[{i+1}] Error: {e}")

print("\n--- Load Distribution Summary ---")
for name, count in counter.items():
    print(f"{name}: {count} requests")
print(f"\nFailed requests: {errors}")