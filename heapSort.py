import time
from test_arrays import ARRAY


def heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2
    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heapSort(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)


def benchmark(arr, runs=5):
    total_time = 0
    for _ in range(runs):
        data = arr.copy()
        start = time.perf_counter()
        heapSort(data)
        end = time.perf_counter()
        total_time += end - start
    return total_time / runs


if __name__ == "__main__":
    avg_time = benchmark(ARRAY)
    sorted_arr = ARRAY[:]
    heapSort(sorted_arr)
    print(f"Input:  {ARRAY}")
    print(f"Sorted: {sorted_arr}")
    print(f"Avg time (5 runs): {avg_time:.6f} seconds")
