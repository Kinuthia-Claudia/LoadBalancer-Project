# analysis/test_scripts/plot_load.py
import matplotlib.pyplot as plt
import os

# Path is in analysis/test_scripts/)
file_path = os.path.join(os.path.dirname(__file__), "..", "results", "load_distribution.txt")


try:
    with open(file_path, "r") as f:
        servers = []
        counts = []
        for line in f:
            server, count = line.strip().split()
            servers.append(f"Server {server}")
            counts.append(int(count))
        
    plt.bar(servers, counts, color=['blue', 'green', 'red'])
    plt.title("Load Distribution Across Servers")
    plt.xlabel("Server ID")
    plt.ylabel("Request Count")
    plt.savefig("analysis/results/load_distribution.png")  # Save plot to results/
    plt.show()

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"Error: {e}")

