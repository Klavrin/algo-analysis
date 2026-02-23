import time
from test_arrays import ARRAY


def merge(arr, left, mid, right):
    n1 = mid - left + 1
    n2 = right - mid
    L = [0] * n1
    R = [0] * n2
    for i in range(n1):
        L[i] = arr[left + i]
    for j in range(n2):
        R[j] = arr[mid + 1 + j]
    i = 0
    j = 0
    k = left
    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1


def mergeSort(arr, left, right):
    if left < right:
        mid = (left + right) // 2
        mergeSort(arr, left, mid)
        mergeSort(arr, mid + 1, right)
        merge(arr, left, mid, right)


def benchmark(arr, runs=5):
    total_time = 0
    for _ in range(runs):
        data = arr.copy()
        start = time.perf_counter()
        mergeSort(data, 0, len(data) - 1)
        end = time.perf_counter()
        total_time += end - start
    return total_time / runs


if __name__ == "__main__":
    avg_time = benchmark(ARRAY)
    sorted_arr = ARRAY[:]
    mergeSort(sorted_arr, 0, len(sorted_arr) - 1)
    print(f"Input:  {ARRAY}")
    print(f"Sorted: {sorted_arr}")
    print(f"Avg time (5 runs): {avg_time:.6f} seconds")
