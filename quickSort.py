import time
from test_arrays import ARRAY


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            swap(arr, i, j)
    swap(arr, i + 1, high)
    return i + 1


def quickSort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)


def benchmark(arr, runs=5):
    total_time = 0
    for _ in range(runs):
        data = arr.copy()
        start = time.perf_counter()
        quickSort(data, 0, len(data) - 1)
        end = time.perf_counter()
        total_time += end - start
    return total_time / runs


if __name__ == "__main__":
    avg_time = benchmark(ARRAY)
    sorted_arr = ARRAY[:]
    quickSort(sorted_arr, 0, len(sorted_arr) - 1)
    print(f"Input:  {ARRAY}")
    print(f"Sorted: {sorted_arr}")
    print(f"Avg time ({5} runs): {avg_time:.6f} seconds")
