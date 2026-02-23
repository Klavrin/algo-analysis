import time
from test_arrays import FLOAT_ARRAY


def insertion_sort(bucket):
    for i in range(1, len(bucket)):
        key = bucket[i]
        j = i - 1
        while j >= 0 and bucket[j] > key:
            bucket[j + 1] = bucket[j]
            j -= 1
        bucket[j + 1] = key


def bucket_sort(arr):
    n = len(arr)
    buckets = [[] for _ in range(n)]

    # put elements into buckets
    for val in arr:
        bi = min(int(n * val), n - 1)
        buckets[bi].append(val)

    # sort each bucket with insertion sort
    for bucket in buckets:
        insertion_sort(bucket)

    # concatenate back
    index = 0
    for bucket in buckets:
        for val in bucket:
            arr[index] = val
            index += 1


def benchmark(arr, runs=5):
    total_time = 0
    for _ in range(runs):
        data = arr.copy()
        start = time.perf_counter()
        bucket_sort(data)
        end = time.perf_counter()
        total_time += end - start
    return total_time / runs


if __name__ == "__main__":
    avg_time = benchmark(FLOAT_ARRAY)
    sorted_arr = FLOAT_ARRAY[:]
    bucket_sort(sorted_arr)
    print(f"Input:  {FLOAT_ARRAY}")
    print(f"Sorted: {sorted_arr}")
    print(f"Avg time (5 runs): {avg_time:.6f} seconds")
