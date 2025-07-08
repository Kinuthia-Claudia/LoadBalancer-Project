# analysis/test_scripts/load_test.py
import requests
from collections import defaultdict
import concurrent.futures
import os

counts = defaultdict(int)

def make_request(_):
    try:
        response = requests.get("http://localhost:5000/home", timeout=5)
        response.raise_for_status()
        server_id = response.json()["message"].split(":")[1].strip()
        return server_id
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Starting load test...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(make_request, range(10000))

for server_id in results:
    if server_id:
        counts[server_id] += 1

print("Requests per server:")
for server, count in counts.items():
    print(f"{server}: {count} requests")

# Create results directory if it doesn't exist
os.makedirs(os.path.dirname("../analysis/results/load_distribution.txt"), exist_ok=True)

# Save results
with open("analysis/results/load_distribution.txt", "w") as f:
    for server, count in counts.items():
        f.write(f"{server} {count}\n")

