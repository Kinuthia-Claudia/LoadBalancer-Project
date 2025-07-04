# Distributed Systems LoadBalancer-Project

## Project OverView

This repository contains the implementation of a customizable load balancer. The load balancer routes asynchronous client requests to multiple server replicas using a consistent hashing algorithm, ensuring near-even load distribution. The system is deployed within a Docker network, with the load balancer managing server replicas and handling failures by spawning new instances. The implementation includes a simple web server, a consistent hash map, and a load balancer with specific HTTP endpoints, all containerized using Docker and orchestrated with Docker Compose.


## Table of Contents

- [Project Structure](#projectstructure)
- [Installation](#installation)
- [Usage](#usage)
- [Design Choices](#designchoices)
- [Testing](#testing)
- [Performance Analysis](#performanceanalysis)
- [Contributing](#contributing)
- [License](#license)
- 
Features

## Insallation
### Prerequisites

OS-  Ubuntu 20.04 LTS or above
Docker- Version 20.10.23 or above
Docker Compose - Latest version
Python - Version 3.8 or above (for local testing)
Git -For version control
Virtual Machine -(Optional)

### Steps to Set-Up
1. Clone the Repository
   ```bash
   ( lisa git hub )
   
2.  Navigate to the Repository

  ### Running the System

3.  Build and Start the services

    # Build the containers
         ```bash
        docker-compose build
   # Start the services
        docker-compose up -d

4. Verify the services
   # Check running containers
   
          docker-compose ps

    # View logs
         docker-compose logs -f

 4.  Test the load balancer

   # Get list of servers
    curl http://localhost:5000/rep

   # Send a test request
    curl http://localhost:5000/home

## Running Performance Test 

1. Create a Python virtual environment
    ```bash
     python3 -m venv .venv

2. Activate the virtual environment
   ```bash
   source .venv/bin/activate

3. Install the required libraries
   ```bash
   pip install -r requirements.txt
   
4. Run all tests
   ```bash
   python -m tests.performance_test

## Usage 

### Running Services in Docker 

1. Build images and start the services
   ```bash
   docker-compose up -d
2. Verify that the containers are running
   ```bash
   docker-compose ps
3.  When you're done, you can stop and remove containers
     ```bash
    docker-compose down
5. Running Python Files
To run Python files while the virtual environment is active
   ```bash
   python app.py
  

## Repository Structure 

├── .gitignore
├── README.md
├── TASK_1
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
├── TASK_2
│   ├── Dockerfile
│   ├── consistent_hash.py
│   ├── docker-compose.yml
│   ├── loadbalancer.py
│   └── requirements.txt
├── TASK_3
│   ├── Dockerfile
│   ├── app.py
│   ├── consistent_hash.py
│   ├── docker-compose.yml
│   └── requirements.txt
├── TASK_4
│   ├── analysis.ipynb
│   ├── analysis_one.py
│   ├── analysis_two.py
│   ├── consistent_hash.py
│   └── figures
│       ├── analysis_one.png
│       └── analysis_two.png
└── requirements.txt


## Design Choices
To implement the load balancer, Object-Oriented programming was applied.
The servers and load balancer are implemented as Flask web servers, comprising the endpoints required for request handling and load balancing operations.
The hashing mechanism was implemented as a class called ConsistentHashRing, which contained attributes such as the servers, slots, and virtual nodes to be created, and methods for implementing hashing and server allocation for a request.
For Language Python was chosen for its simplicity, robust libraries  and ease of prototyping.
Consistent Hashing is Implemented using a sorted list for ( O(\log M) ) lookup efficiency, with linear probing for collision resolution.
Failure Handling - The load balancer periodically checks /heartbeat endpoints and spawns new containers using the Docker Python SDK if failures are detected.

## Assumptions
The following assumptions were made in the load balancer implementation

- Server IDs are set as environment variables during container creation.
- Random hostnames are generated using UUIDs when not specified.
-The system assumes a stable Docker network for communication.

## Project Testing 

## API EXAMPLES
#### Server EndPoints

Each server should have the following endpoints

| Method | Endpoint     | Description                              |
| ------ | ------------ | ---------------------------------------- |
| GET    | `/home`      | Returns message from the specific server |
| GET    | `/heartbeat` | Used by LB to check server availability  |


#### Load Balancer EndPoints
The load balancer exposes the following endpoints

| Method | Endpoint  | Description                                                                  |
| ------ | --------- | ---------------------------------------------------------------------------  |
| GET    | `/rep`    | View list of active replicas                                                 |
| POST   | `/add`    | Adds new backend servers                                                     |
| DELETE | `/rm`     | Remove existing backend servers                                              |
| GET    | `/<path>` | A catch-all route that handles other endpoints to be directed to the servers |

The load balancer is exposed to the public network through the host machine on port 5000



## Testing with cURL

1. Get Replicas
    ```bash
   curl http://localhost:5000/rep
2. Test Load Balancer Routing
    ```bash
   curl http://localhost:5000/home
   
3. Add a New Server
    ```bash
     curl -X POST http://localhost:5000/add \
      -H "Content-Type: application/json" \
      -d '{"n": 1, "hostnames": ["server4:5000"]}'
   
4. Remove a Server
    ```bash
    curl -X DELETE http://localhost:5000/rm \
      -H "Content-Type: application/json" \
      -d '{"n": 1, "hostnames": ["server4:5000"]}'
  
5. List Active Servers
    ```bash
    curl http://localhost:5000/rep
  OR
 Access Server Content
 
    curl http://localhost:5000/home



## Load Balancer Performance Analysis

### A-1: Request Count Per Server Instance
This experiment involved executing 10,000 async requests on the 3 server containers, with the results being displayed in a bar chart.
Asynchronous requests are launched by using aiohttp + asyncio for concurrent request handling.

example of the code that is needed
Test A-1 Results (Completed in 27.76 seconds):
Request distribution: {
  "1": 9642,
  "2": 227,
  "3": 70
}\

we need a diagram

**Observations**
From the graph, most of the requests (more than 90%) are handled by server1, with the rest handling a fairly even number of requests. This may be caused by the hash function mapping requests to servers, which may be returning hash values that direct requests to server1. This represents an imbalance in the number of requests handled across the 3 servers, as server1 handles a large number of requests, leaving the rest of the servers under-utilised.

### A-2: Average Load of Servers for N = 2 to 6

This experiment involved iteratively increasing the number of servers from 2 to 6 while launching async requests.
The results are plotted on a line chart.

**DIAGRAM HERE** 
Observations
Ineffective Load Distribution - The average load doesn't decrease proportionally with the number of servers, indicating that the load balancer isn't distributing requests effectively.
Consistent Issue -  Similar to Test A-1, most requests are being routed to a single server (Server 1), while others remain underutilized.
Scaling Impact -  The system doesn't scale horizontally as expected. Adding more servers doesn't significantly improve load distribution.
Performance Concern - The consistent hashing implementation needs review as it's not providing the expected distribution of requests across available servers.


### A-3: Failure Detection and Handling
This experiment analysed how the load balancer handles server failures.
Server 1 was stopped to represent a server failure.
Observations
From the experiment, it was noted that majority of the requests were routed to server 2 compared to server 3, showing a significant imbalance which still existed based on the setup, despite the removal of server 1 (Refer to the notebook for more information).
Server Management: The system correctly adds and removes servers from the pool.
Naming Inconsistency: There's an inconsistency in server naming (mixing "Server_X" and "serverX" formats).
State Maintenance: The system maintains the correct count of servers (N) after each operation.
Recovery Process: The system successfully handles server removal and addition, though the load distribution issues observed in previous tests would affect the effectiveness of the recovery.

### A-4: Modifying the Hash Functions
The hash ring functions were modified and results gathered, based on the change.
These were the new hash functions (defined arbitrarily) for the requests and servers that were used:
    Request Hash Function: H(i)=(3⋅i)mod S
    Server Hash Function: ϕ(i,j)=(i2+4⋅j)mod S
    
Based on the results gathered, server 1 handled significantly more request traffic than before, based on these new functions. There was no significant change noted for the average load per server, when the number of servers were increased, with the number of requests held constant.


## License
This project is licensed under the MIT License - see the LICENSE file for details.



























