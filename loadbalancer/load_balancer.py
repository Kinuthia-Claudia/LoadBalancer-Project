from flask import Flask, request, jsonify
import os
import random
import string
import subprocess
from hashing import ConsistentHashMap

app = Flask(__name__)

# Initialize consistent hash ring
ch = ConsistentHashMap()
replicas = {}

# Start with 3 default servers
N = 3
for i in range(1, N + 1):
    hostname = f"Server{i}"
    ch.add_server(i)
    subprocess.run([
        "docker", "run", "-d", "--rm",
        "--network", "net1",
        "--name", hostname,
        "-e", f"SERVER_ID={i}",
        "ds-server"
    ])
    replicas[hostname] = i

@app.route('/rep', methods=['GET'])
def get_replicas():
    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": list(replicas.keys())
        },
        "status": "successful"
    }), 200

@app.route('/add', methods=['POST'])
def add_servers():
    data = request.get_json()
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400

    for i in range(n):
        sid = max(replicas.values(), default=0) + 1
        name = hostnames[i] if i < len(hostnames) else random_hostname()
        ch.add_server(sid)
        subprocess.run([
            "docker", "run", "-d", "--rm",
            "--network", "net1",
            "--name", name,
            "-e", f"SERVER_ID={sid}",
            "ds-server"
        ])
        replicas[name] = sid

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": list(replicas.keys())
        },
        "status": "successful"
    }), 200

@app.route('/rm', methods=['DELETE'])
def remove_servers():
    data = request.get_json()
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    to_remove = hostnames[:]
    if len(to_remove) < n:
        remaining = list(set(replicas.keys()) - set(to_remove))
        if len(remaining) < (n - len(to_remove)):
            return jsonify({
                "message": "<Error> Not enough replicas to remove",
                "status": "failure"
            }), 400
        to_remove += random.sample(remaining, n - len(to_remove))

    for h in to_remove:
        if h in replicas:
            sid = replicas[h]
            ch.remove_server(sid)
            subprocess.run(["docker", "stop", h])
            del replicas[h]

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": list(replicas.keys())
        },
        "status": "successful"
    }), 200

@app.route('/<path:path>', methods=['GET'])
def forward(path):
    request_id = random.randint(10000, 99999)
    server = ch.get_server_for_request(request_id)
    container_name = next((name for name, sid in replicas.items() if sid == server), None)

    if container_name:
        try:
            curl_check = f"docker exec {container_name} curl -s -o /dev/null -w '%{{http_code}}' http://localhost:5000/{path}"
            status_code = subprocess.getoutput(curl_check)

            if status_code == "200":
                response = subprocess.getoutput(f"docker exec {container_name} curl -s http://localhost:5000/{path}")
                return response, 200
            else:
                return jsonify({
                    "message": f"<Error> '/{path}' endpoint does not exist in server replicas",
                    "status": "failure"
                }), 400
        except Exception as e:
            return jsonify({
                "message": f"<Error> Internal server error: {str(e)}",
                "status": "failure"
            }), 500

    return jsonify({
        "message": "<Error> No available server to handle request",
        "status": "failure"
    }), 400

def random_hostname(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
