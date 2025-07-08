# analysis/test_scripts/plot_scalability.py
import matplotlib.pyplot as plt

x, y = [], []
with open("analysis/results/scalability.txt", "r") as f:
    for line in f:
        n, load = line.strip().split()
        x.append(int(n))
        y.append(float(load))

plt.plot(x, y, marker='o')
plt.xlabel("Number of Servers (N)")
plt.ylabel("Average Requests per Server")
plt.title("Load Balancer Scalability")
plt.grid(True)
plt.savefig("analysis/results/scalability.png")
plt.close()
