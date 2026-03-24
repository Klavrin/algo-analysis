import time
from collections import defaultdict
import random


class Graph_DFS:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def DFSUtil(self, v, visited):
        visited.add(v)
        for neighbour in self.graph[v]:
            if neighbour not in visited:
                self.DFSUtil(neighbour, visited)

    def DFS(self, v):
        visited = set()
        self.DFSUtil(v, visited)


input_sizes = [10, 50, 100, 200, 300, 400, 500]
print(f"{'':<3} {'Input Size':<12} {'DFS':<12}")

for i, size in enumerate(input_sizes):
    g = Graph_DFS()

    for _ in range(size * 2):
        u = random.randint(0, size - 1)
        v = random.randint(0, size - 1)
        g.addEdge(u, v)

    start_time = time.perf_counter()
    g.DFS(0)
    end_time = time.perf_counter()

    duration = end_time - start_time

    print(f"{i:<3} {size:<12} {duration:.6f}")
