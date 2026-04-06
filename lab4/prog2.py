import copy
import matplotlib.pyplot as plt


def floyd_warshall(matrix):
    n = len(matrix)
    dist = copy.deepcopy(matrix)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


def has_negative_cycle(dist):
    for i in range(len(dist)):
        if dist[i][i] < 0:
            return True
    return False


def print_performance_table(data):
    header = f"{'Nodes':<8} {'D-Sparse(ms)':<16} {'D-Dense(ms)':<16} {'FW-Sparse(ms)':<18} {'FW-Dense(ms)':<15}"
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    for row in data:
        nodes, ds, dd, fws, fwd = row
        print(f"{nodes:<8} {ds:<16.4f} {dd:<16.4f} {fws:<18.4f} {fwd:<15.4f}")


results_data = [
    (10, 0.0073, 0.0081, 0.0888, 0.0697),
    (50, 0.0214, 0.1353, 7.6318, 6.0200),
    (100, 0.0498, 0.4465, 51.2191, 41.1693),
    (200, 0.1059, 1.9434, 419.1561, 313.0293),
    (500, 0.2846, 10.3136, 7232.1616, 5430.2508),
]

print_performance_table(results_data)

nodes = [10, 50, 100, 200, 500]
fw_sparse = [0.0888, 7.6318, 51.2191, 419.1561, 7232.1616]
fw_dense = [0.0697, 6.0200, 41.1693, 313.0293, 5430.2508]

plt.figure(figsize=(8, 6))

plt.plot(nodes, fw_sparse, marker="o", label="Sparse", color="steelblue")
plt.plot(nodes, fw_dense, marker="s", label="Dense", color="tomato")

plt.title("Floyd-Warshall Algorithm (all-pairs)")
plt.xlabel("Number of Nodes (V)")
plt.ylabel("Average Execution Time (ms)")

plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()

plt.show()
