import matplotlib.pyplot as plt


def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]


def union(parent, rank, x, y):
    root_x = find(parent, x)
    root_y = find(parent, y)

    if root_x != root_y:
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1


def kruskal(n, edges):
    edges.sort(key=lambda x: x[2])

    parent = list(range(n))
    rank = [0] * n

    mst_weight = 0
    mst_edges = []

    for u, v, w in edges:
        if find(parent, u) != find(parent, v):
            union(parent, rank, u, v)
            mst_edges.append((u, v, w))
            mst_weight += w

    return mst_weight, mst_edges


def print_kruskal_results(results):
    print("=== Kruskal's Algorithm Results ===")
    for row in results:
        nodes, sparse, dense = row
        print(f"Nodes: {nodes:<3} | Sparse: {sparse:.6f}s | Dense: {dense:.6f}s")


kruskal_data = [
    (10, 0.000013, 0.000010),
    (50, 0.000032, 0.000243),
    (100, 0.000086, 0.000741),
    (200, 0.000137, 0.002918),
    (500, 0.000347, 0.022568),
]

print_kruskal_results(kruskal_data)


nodes = [10, 50, 100, 200, 500]
sparse_times = [0.000013, 0.000032, 0.000086, 0.000137, 0.000347]
dense_times = [0.000010, 0.000243, 0.000741, 0.002918, 0.022568]

plt.figure(figsize=(8, 6))

plt.plot(nodes, sparse_times, label="Sparse Graph", color="tab:blue")
plt.plot(nodes, dense_times, label="Dense Graph", color="tab:orange")

plt.title("Kruskal's Algorithm Runtime")
plt.xlabel("Number of Nodes")
plt.ylabel("Execution Time (seconds)")

plt.ylim(0, 0.088)

plt.legend()
plt.show()
