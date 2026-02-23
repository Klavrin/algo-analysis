"""
quicksort_benchmark.py
----------------------
Tests QuickSort against 10 different array types, from easy to hard,
and prints a formatted table with timing results.

Run:
    python3 quicksort_benchmark.py
"""

import time
import random
import sys

random.seed(42)
sys.setrecursionlimit(500000)

# ── QuickSort (last-element pivot, in-place) ──────────────────────────────────


def quicksort(arr, low, high):
    if low < high:
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        pi = i + 1
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)


def run(arr):
    data = arr[:]
    quicksort(data, 0, len(data) - 1)
    return data


def benchmark(arr, runs=5):
    times = []
    for _ in range(runs):
        data = arr[:]
        t0 = time.perf_counter()
        quicksort(data, 0, len(data) - 1)
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)


# ── Array generators ──────────────────────────────────────────────────────────

N = 5000  # base size for all arrays

arrays = [
    (
        "1. Random integers",
        "Easy — pivot lands near middle on average",
        [random.randint(0, 100_000) for _ in range(N)],
    ),
    (
        "2. Already sorted",
        "Hard — pivot always smallest, O(n²) depth",
        list(range(N)),
    ),
    (
        "3. Reverse sorted",
        "Hard — pivot always largest, O(n²) depth",
        list(range(N, 0, -1)),
    ),
    (
        "4. All identical",
        "Hard — every partition is maximally unbalanced",
        [42] * N,
    ),
    (
        "5. Two distinct values",
        "Hard — large runs of equal elements",
        [random.choice([0, 1]) for _ in range(N)],
    ),
    (
        "6. Nearly sorted (1% swaps)",
        "Medium — mostly ordered with a few disruptions",
        # start sorted, then swap 1% of pairs randomly
        (
            lambda a: [
                a.__setitem__(i, a.__setitem__(j, a[i]) or a[j])  # noqa trick
                for i, j in [
                    (random.randint(0, N - 1), random.randint(0, N - 1))
                    for _ in range(N // 100)
                ]
            ]
            or a
        )(list(range(N))),
    ),
    (
        "7. Pipe-organ (mountain)",
        "Medium — sorted up then sorted down",
        list(range(N // 2)) + list(range(N // 2, 0, -1)),
    ),
    (
        "8. Random with many duplicates",
        "Medium-hard — only 10 distinct values in N elements",
        [random.randint(0, 9) for _ in range(N)],
    ),
    (
        "9. Rotated sorted array",
        "Medium — sorted array shifted by N/3 positions",
        (lambda a: a[N // 3 :] + a[: N // 3])(list(range(N))),
    ),
    (
        "10. Random floats [0, 1)",
        "Easy-medium — uniform distribution, good pivots",
        [random.random() for _ in range(N)],
    ),
]

# fix the nearly-sorted generator — simpler version
sorted_base = list(range(N))
nearly_sorted = sorted_base[:]
for _ in range(N // 100):
    i, j = random.randint(0, N - 1), random.randint(0, N - 1)
    nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]
arrays[5] = (
    "6. Nearly sorted (1% swaps)",
    "Medium — mostly ordered with a few disruptions",
    nearly_sorted,
)

# ── Run benchmarks ────────────────────────────────────────────────────────────

RUNS = 7
print(f"\nBenchmarking QuickSort on {N:,} elements, {RUNS} runs each...\n")

results = []
for name, difficulty, arr in arrays:
    # verify correctness first
    sorted_result = run(arr)
    correct = sorted_result == sorted(arr)

    # time it
    avg_ms = benchmark(arr, runs=RUNS) * 1000

    results.append((name, difficulty, avg_ms, correct))
    status = "✓" if correct else "✗"
    print(f"  {status}  {name:<35}  {avg_ms:>8.3f} ms")

    # ── Matplotlib Graph ──────────────────────────────────────────────────────────
try:
    import matplotlib.pyplot as plt

    print("Generating performance graph...")

    # Sort the results from fastest to slowest for a cleaner graph
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)

    names = [r[0] for r in sorted_results]
    times_plot = [r[2] for r in sorted_results]

    # Set up the figure
    plt.figure(figsize=(12, 7))

    # Create horizontal bars. Color them red if they are "Hard" (slow), green if "Easy"
    colors = ["#e74c3c" if "Hard" in r[1] else "#3498db" for r in sorted_results]
    bars = plt.barh(names, times_plot, color=colors)

    # Add the exact millisecond time to the end of each bar
    for bar in bars:
        plt.text(
            bar.get_width() + (max(times_plot) * 0.01),  # Add a tiny bit of padding
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.1f} ms",
            va="center",
            fontsize=10,
        )

    # Formatting and labels
    plt.xlabel("Average Execution Time (ms)", fontsize=12)
    plt.title(
        f"QuickSort Execution Time by Array Type (n = {N:,})", fontsize=14, pad=15
    )

    # Use a logarithmic scale if the slow ones are completely dwarfing the fast ones
    if max(times_plot) / min(times_plot) > 50:
        plt.xscale("log")
        plt.xlabel("Average Execution Time (ms) - Log Scale", fontsize=12)

    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Show the plot window
    plt.show()

except ImportError:
    print(
        "\nNote: 'matplotlib' is not installed. Run 'pip install matplotlib' to see the graphical chart."
    )

# ── Print table ───────────────────────────────────────────────────────────────

COL1 = 32  # array name
COL2 = 46  # difficulty description
COL3 = 12  # time
COL4 = 9  # correct

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
print(f"  QuickSort Benchmark  —  n = {N:,}  |  {RUNS} runs per array")
print("=" * (COL1 + COL2 + COL3 + COL4 + 11))
print(DIVIDER)
print(HEADER)
print(DIVIDER.replace("-", "="))

# find fastest for relative comparison
times = [r[2] for r in results]
fastest = min(times)

for name, difficulty, avg_ms, correct in results:
    ratio = avg_ms / fastest
    bar = "█" * min(int(ratio * 3), 20)
    status = "  yes ✓" if correct else "  NO ✗ "
    print(
        f"| {name:<{COL1}} | {difficulty:<{COL2}} | {avg_ms:>{COL3}.3f} | {status:<{COL4}} |"
    )

print(DIVIDER)

# summary row
avg_all = sum(times) / len(times)
print(f"| {'AVERAGE':<{COL1}} | {'':<{COL2}} | {avg_all:>{COL3}.3f} | {'':<{COL4}} |")
print(DIVIDER)

# slowest / fastest
slowest_name = results[times.index(max(times))][0]
fastest_name = results[times.index(min(times))][0]
slowdown = max(times) / min(times)

print()
print(f"  Fastest : {fastest_name.strip()}  ({min(times):.3f} ms)")
print(f"  Slowest : {slowest_name.strip()}  ({max(times):.3f} ms)")
print(f"  Slowdown: {slowdown:.1f}× difference between fastest and slowest")
print()

# ── Visual bar chart in terminal ──────────────────────────────────────────────
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
