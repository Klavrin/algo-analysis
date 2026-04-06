import heapq
import matplotlib.pyplot as plt


def dijkstra(graph, start):
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    heap = [(0, start)]
    visited = set()

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        for neighbor, weight in graph[current_node]:
            if neighbor in visited:
                continue
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    return distances, previous


def get_path(previous, start, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    if not path or path[0] != start:
        return []
    return path


def print_results(results):
    print("=" * 45)
    print(f"{'Nodes':<10} {'D-Sparse(ms)':<18} {'D-Dense(ms)':<15}")
    print("-" * 45)

    for nodes, sparse_time, dense_time in results:
        print(f"{nodes:<10} {sparse_time:<18.4f} {dense_time:<15.4f}")


data = [
    (10, 0.0073, 0.0081),
    (50, 0.0214, 0.1353),
    (100, 0.0498, 0.4465),
    (200, 0.1059, 1.9434),
    (500, 0.2846, 10.3136),
]

print_results(data)


nodes = [10, 50, 100, 200, 500]
sparse_times = [0.0073, 0.0214, 0.0498, 0.1059, 0.2846]
dense_times = [0.0081, 0.1353, 0.4465, 1.9434, 10.3136]

plt.figure(figsize=(10, 6))

plt.plot(
    nodes, sparse_times, marker="o", label="Sparse", color="steelblue", linewidth=2
)

plt.plot(nodes, dense_times, marker="s", label="Dense", color="tomato", linewidth=2)

plt.title("Dijkstra's Algorithm — Execution Time vs Number of Nodes")
plt.xlabel("Number of Nodes (V)")
plt.ylabel("Average Execution Time (ms)")

plt.grid(True, linestyle="--", alpha=0.6)

plt.legend()

plt.show()
