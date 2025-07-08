import hashlib
import bisect

def H(i):
    return int(hashlib.md5(str(i).encode()).hexdigest(), 16)

def PHI(i, j):
    return int(hashlib.md5(f"{i}-{j}".encode()).hexdigest(), 16)

class ConsistentHashMap:
    def __init__(self, num_slots=104729, virtual_replicas=500):
        self.num_slots = num_slots
        self.virtual_replicas = virtual_replicas
        self.ring = {}
        self.sorted_slots = []

    def add_server(self, server_id):
        for j in range(self.virtual_replicas):
            slot = PHI(server_id, j) % self.num_slots
            while slot in self.ring:
                slot = (slot + 1) % self.num_slots
            self.ring[slot] = server_id
            bisect.insort(self.sorted_slots, slot)

    def remove_server(self, server_id):
        to_remove = [slot for slot, sid in self.ring.items() if sid == server_id]
        for slot in to_remove:
            self.sorted_slots.remove(slot)
            del self.ring[slot]

    def get_server_for_request(self, request_id):
        req_slot = H(request_id) % self.num_slots
        idx = bisect.bisect_right(self.sorted_slots, req_slot)
        if idx == len(self.sorted_slots):
            idx = 0
        return self.ring[self.sorted_slots[idx]]
