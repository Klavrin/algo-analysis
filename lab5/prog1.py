import heapq
import matplotlib.pyplot as plt


def prim(graph, start=0):
    n = len(graph)
    visited = [False] * n

    min_heap = [(0, start, -1)]

    mst_weight = 0
    mst_edges = []

    while min_heap:
        weight, node, parent = heapq.heappop(min_heap)

        if visited[node]:
            continue

        visited[node] = True
        mst_weight += weight

        if parent != -1:
            mst_edges.append((parent, node, weight))

        for neighbor, w in graph[node]:
            if not visited[neighbor]:
                heapq.heappush(min_heap, (w, neighbor, node))

    return mst_weight, mst_edges


def print_prim_results(results):
    print("=== Prim's Algorithm Results ===")
    for row in results:
        nodes, sparse, dense = row
        print(f"Nodes: {nodes:<3} | Sparse: {sparse:.6f}s | Dense: {dense:.6f}s")


results_data = [
    (10, 0.000011, 0.000007),
    (50, 0.000024, 0.000206),
    (100, 0.000084, 0.001045),
    (200, 0.000118, 0.004802),
    (500, 0.000325, 0.081455),
]

print_prim_results(results_data)


nodes = [10, 50, 100, 200, 500]
sparse_runtime = [0.000011, 0.000024, 0.000084, 0.000118, 0.000325]
dense_runtime = [0.000007, 0.000206, 0.001045, 0.004802, 0.081455]

plt.figure(figsize=(8, 6))

plt.plot(nodes, sparse_runtime, label="Sparse Graph", linewidth=2)
plt.plot(nodes, dense_runtime, label="Dense Graph", linewidth=2)

plt.title("Prim's Algorithm Runtime")
plt.xlabel("Number of Nodes")
plt.ylabel("Execution Time (seconds)")

plt.legend()
plt.show()
