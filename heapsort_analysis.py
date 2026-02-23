"""
heapsort_benchmark.py
---------------------
Tests HeapSort against 10 different array types, from easy to hard,
and prints a formatted table with timing results + matplotlib graph.

Run:
    python3 heapsort_benchmark.py
"""

import time
import random
import sys

random.seed(42)
sys.setrecursionlimit(500000)

# ── HeapSort ──────────────────────────────────────────────────────────────────


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


def heapsort(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)


def run(arr):
    data = arr[:]
    heapsort(data)
    return data


def benchmark(arr, runs=5):
    times = []
    for _ in range(runs):
        data = arr[:]
        t0 = time.perf_counter()
        heapsort(data)
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)


# ── Array generators ──────────────────────────────────────────────────────────

N = 5000

arrays = [
    (
        "1. Random integers",
        "Medium — heap jumps around memory randomly",
        [random.randint(0, 100_000) for _ in range(N)],
    ),
    (
        "2. Already sorted",
        "Medium — build-heap phase does extra work",
        list(range(N)),
    ),
    (
        "3. Reverse sorted",
        "Easy — build-heap is near-free, good sifts",
        list(range(N, 0, -1)),
    ),
    (
        "4. All identical",
        "Easy — every heapify returns immediately",
        [42] * N,
    ),
    (
        "5. Two distinct values",
        "Easy — very few swaps needed in heapify",
        [random.choice([0, 1]) for _ in range(N)],
    ),
    (
        "6. Nearly sorted (1% swaps)",
        "Medium — heap must fix a mostly-sorted input",
        None,  # filled below
    ),
    (
        "7. Pipe-organ (mountain)",
        "Medium — ascending first half is a valid heap",
        list(range(N // 2)) + list(range(N // 2, 0, -1)),
    ),
    (
        "8. Random with many duplicates",
        "Easy — heapify short-circuits on equal values",
        [random.randint(0, 9) for _ in range(N)],
    ),
    (
        "9. Rotated sorted array",
        "Medium — similar to sorted, cache unfriendly",
        (lambda a: a[N // 3 :] + a[: N // 3])(list(range(N))),
    ),
    (
        "10. Random floats [0, 1)",
        "Medium — same as random integers in practice",
        [random.random() for _ in range(N)],
    ),
]

# nearly sorted
nearly_sorted = list(range(N))
for _ in range(N // 100):
    i, j = random.randint(0, N - 1), random.randint(0, N - 1)
    nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]
arrays[5] = (
    "6. Nearly sorted (1% swaps)",
    "Medium — heap must fix a mostly-sorted input",
    nearly_sorted,
)

# ── Run benchmarks ────────────────────────────────────────────────────────────

RUNS = 7
print(f"\nBenchmarking HeapSort on {N:,} elements, {RUNS} runs each...\n")

results = []
for name, difficulty, arr in arrays:
    sorted_result = run(arr)
    correct = sorted_result == sorted(arr)

    avg_ms = benchmark(arr, runs=RUNS) * 1000

    results.append((name, difficulty, avg_ms, correct))
    status = "✓" if correct else "✗"
    print(f"  {status}  {name:<35}  {avg_ms:>8.3f} ms")

# ── Matplotlib graph ──────────────────────────────────────────────────────────
try:
    import matplotlib.pyplot as plt

    print("\nGenerating performance graph...")

    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    names = [r[0] for r in sorted_results]
    times_plot = [r[2] for r in sorted_results]

    colors = [
        "#e74c3c" if "Hard" in r[1] else "#f39c12" if "Medium" in r[1] else "#2ecc71"
        for r in sorted_results
    ]

    plt.figure(figsize=(12, 7))
    bars = plt.barh(names, times_plot, color=colors)

    for bar in bars:
        plt.text(
            bar.get_width() + max(times_plot) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.2f} ms",
            va="center",
            fontsize=10,
        )

    plt.xlabel("Average Execution Time (ms)", fontsize=12)
    plt.title(f"HeapSort Execution Time by Array Type (n = {N:,})", fontsize=14, pad=15)

    if max(times_plot) / min(times_plot) > 50:
        plt.xscale("log")
        plt.xlabel("Average Execution Time (ms) — Log Scale", fontsize=12)

    from matplotlib.patches import Patch

    legend = [
        Patch(color="#2ecc71", label="Easy"),
        Patch(color="#f39c12", label="Medium"),
        Patch(color="#e74c3c", label="Hard"),
    ]
    plt.legend(handles=legend, loc="lower right", fontsize=10)

    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

except ImportError:
    print("\nNote: install matplotlib with 'pip install matplotlib' to see the graph.")

# ── Print table ───────────────────────────────────────────────────────────────

COL1, COL2, COL3, COL4 = 32, 46, 12, 9

DIVIDER = (
    "+"
    + "-" * (COL1 + 2)
    + "+"
    + "-" * (COL2 + 2)
    + "+"
    + "-" * (COL3 + 2)
    + "+"
    + "-" * (COL4 + 2)
    + "+"
)
HEADER = (
    f"| {'Array type':<{COL1}} | {'Difficulty / notes':<{COL2}} "
    f"| {'Avg time (ms)':>{COL3}} | {'Correct?':<{COL4}} |"
)

print()
print("=" * (COL1 + COL2 + COL3 + COL4 + 11))
print(f"  HeapSort Benchmark  —  n = {N:,}  |  {RUNS} runs per array")
print("=" * (COL1 + COL2 + COL3 + COL4 + 11))
print(DIVIDER)
print(HEADER)
print(DIVIDER.replace("-", "="))

times = [r[2] for r in results]
fastest = min(times)

for name, difficulty, avg_ms, correct in results:
    status = "  yes ✓" if correct else "  NO ✗ "
    print(
        f"| {name:<{COL1}} | {difficulty:<{COL2}} | {avg_ms:>{COL3}.3f} | {status:<{COL4}} |"
    )

print(DIVIDER)
avg_all = sum(times) / len(times)
print(f"| {'AVERAGE':<{COL1}} | {'':<{COL2}} | {avg_all:>{COL3}.3f} | {'':<{COL4}} |")
print(DIVIDER)

slowest_name = results[times.index(max(times))][0]
fastest_name = results[times.index(min(times))][0]
slowdown = max(times) / min(times)

print()
print(f"  Fastest : {fastest_name.strip()}  ({min(times):.3f} ms)")
print(f"  Slowest : {slowest_name.strip()}  ({max(times):.3f} ms)")
print(f"  Slowdown: {slowdown:.1f}× difference between fastest and slowest")
print()

print("-" * 70)
print("  Relative speed (bar length ∝ time, shortest = fastest)")
print("-" * 70)
max_bar = 40
for name, _, avg_ms, _ in results:
    bar_len = max(1, int(avg_ms / max(times) * max_bar))
    bar = "█" * bar_len
    label = name[:28].ljust(30)
    print(f"  {label}  {bar:<{max_bar}}  {avg_ms:.2f} ms")
print()
