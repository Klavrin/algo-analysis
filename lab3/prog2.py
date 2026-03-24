import time
import random
from collections import defaultdict, deque


class Graph_DFS:
    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)
        self.graph[v].append(u)

    def DFSUtil(self, v, visited):
        visited.add(v)
        for neighbour in self.graph[v]:
            if neighbour not in visited:
                self.DFSUtil(neighbour, visited)

    def DFS(self, v):
        visited = set()
        self.DFSUtil(v, visited)


class Graph_BFS:
    def __init__(self):
        self.adjList = defaultdict(list)

    def addEdge(self, u, v):
        self.adjList[u].append(v)
        self.adjList[v].append(u)

    def bfs(self, startNode):
        queue = deque()
        max_node = max(self.adjList.keys(), default=-1)
        visited = [False] * (max_node + 1)

        if startNode <= max_node:
            visited[startNode] = True
            queue.append(startNode)

        while queue:
            currentNode = queue.popleft()
            for neighbour in self.adjList[currentNode]:
                if not visited[neighbour]:
                    visited[neighbour] = True
                    queue.append(neighbour)


input_sizes = [10, 50, 100, 200, 300, 400, 500]

print(f"{'':<3} {'Input Size':<12} {'DFS':<12} {'BFS':<12}")

for i, size in enumerate(input_sizes):
    g_dfs = Graph_DFS()
    g_bfs = Graph_BFS()

    for _ in range(size * 2):
        u, v = random.randint(0, size - 1), random.randint(0, size - 1)
        g_dfs.addEdge(u, v)
        g_bfs.addEdge(u, v)

    start_dfs = time.perf_counter()
    g_dfs.DFS(0)
    end_dfs = time.perf_counter()
    dfs_time = end_dfs - start_dfs

    start_bfs = time.perf_counter()
    g_bfs.bfs(0)
    end_bfs = time.perf_counter()
    bfs_time = end_bfs - start_bfs

    print(f"{i:<3} {size:<12} {dfs_time:.6f}   {bfs_time:.6f}")
