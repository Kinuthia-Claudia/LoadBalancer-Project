from hashing import ConsistentHashMap
from collections import Counter

# Initialize consistent hash map
chm = ConsistentHashMap()

# Add 3 servers
chm.add_server(1)
chm.add_server(2)
chm.add_server(3)

# Simulate 10,000 request routings
counts = Counter()
for request_id in range(10000):
    server = chm.get_server_for_request(request_id)
    counts[server] += 1

# Print results
print("=== Request Distribution ===")
for server_id in sorted(counts):
    print(f"Server {server_id}: {counts[server_id]} requests")
