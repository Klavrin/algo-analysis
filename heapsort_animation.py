"""
heapsort_animation.py
---------------------
Manim animation of HeapSort.

Visual story:
  1. Show the flat array
  2. Morph it into a binary tree
  3. BUILD MAX-HEAP — heapify bottom-up, nodes bubble down with swaps
  4. EXTRACT PHASE  — root (max) flies to its sorted slot, heap shrinks,
                      camera follows the action up/down the tree
  5. Morph the tree back into the sorted flat array

Requirements:
    pip install manim

Run:
    manim -pql heapsort_animation.py HeapSortScene   # fast preview
    manim -pqh heapsort_animation.py HeapSortScene   # high quality

Change ARRAY in test_arrays.py — both heapsort.py and this update.
"""

from manim import *
import sys, os, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_arrays import ARRAY

# ── colour constants ───────────────────────────────────────────────────────────
COL_NODE = "#3A86FF"  # normal heap node
COL_HEAP_BG = "#023E8A"  # darker shade for "in heap"
COL_ACTIVE = "#FF6B6B"  # node being compared / swapped
COL_LARGEST = "#FFD166"  # current largest in heapify
COL_SORTED = "#06D6A0"  # extracted / sorted
COL_EDGE = "#778DA9"  # tree edges
COL_ROOT = "#FF9F1C"  # root (max) highlight


# ── event recorder ────────────────────────────────────────────────────────────
def record_events(original):
    """
    Simulate heapsort and return a list of events.
    Events:
      phase        "build" | "extract"
      compare      i, j, largest  (during heapify comparison)
      swap         i, j            (swap in array)
      heapify_done i               (subtree rooted at i is now a heap)
      extract      idx             (arr[0] moved to sorted position idx)
      done
    """
    arr = original[:]
    events = []

    def push(kind, **kw):
        events.append({"kind": kind, "arr": arr[:], **kw})

    def heapify(n, i):
        while True:
            largest = i
            l, r = 2 * i + 1, 2 * i + 2
            push(
                "compare",
                n=n,
                i=i,
                l=l if l < n else -1,
                r=r if r < n else -1,
                largest=largest,
                msg=f"Heapify node {i}: checking children",
            )
            if l < n and arr[l] > arr[largest]:
                largest = l
            if r < n and arr[r] > arr[largest]:
                largest = r
            push(
                "largest_found",
                n=n,
                i=i,
                largest=largest,
                msg=f"Largest is node {largest}  (value {arr[largest]})",
            )
            if largest != i:
                push(
                    "swap",
                    n=n,
                    a=i,
                    b=largest,
                    msg=f"Swap  {arr[i]}  ↔  {arr[largest]}",
                )
                arr[i], arr[largest] = arr[largest], arr[i]
                push(
                    "after_swap",
                    n=n,
                    a=i,
                    b=largest,
                    msg=f"Swapped → continue heapify at {largest}",
                )
                i = largest  # tail-recurse iteratively
            else:
                push(
                    "heapify_done", n=n, i=i, msg=f"Node {i} satisfies heap property ✓"
                )
                break

    n = len(arr)
    push("phase", phase="build", msg="Phase 1: Build Max-Heap (bottom-up)")

    for i in range(n // 2 - 1, -1, -1):
        push(
            "start_heapify",
            n=n,
            i=i,
            msg=f"Start heapify at node {i}  (value {arr[i]})",
        )
        heapify(n, i)

    push("heap_ready", msg="Max-Heap is built — root holds the maximum ✓")
    push("phase", phase="extract", msg="Phase 2: Extract elements one by one")

    for size in range(n - 1, 0, -1):
        push(
            "extract",
            n=size + 1,
            idx=size,
            msg=f"Move max ({arr[0]}) → sorted position {size}",
        )
        arr[0], arr[size] = arr[size], arr[0]
        push(
            "after_extract",
            n=size,
            idx=size,
            msg=f"{arr[size]} is now in its final position ✓",
        )
        if size > 1:
            heapify(size, 0)

    push("done", msg="✓  Array sorted!")
    return events


# ── tree geometry helpers ──────────────────────────────────────────────────────
def tree_pos(i, n, cx=0.0, top_y=2.8, level_h=1.55, spread=4.5):
    """
    Return (x, y) for node at index i in a 0-based binary heap of size n.
    We compute the position recursively based on depth and in-level index.
    """
    depth = int(math.log2(i + 1))
    in_lvl = i - (2**depth - 1)  # 0-based position in this level
    n_nodes = 2**depth  # nodes at this depth
    # horizontal span shrinks by half each level
    total_w = spread / (2 ** (depth - 1)) if depth > 0 else spread * 2
    x_start = (
        cx - (n_nodes - 1) * (total_w / max(1, n_nodes - 1)) / 2 if n_nodes > 1 else cx
    )
    x = cx if n_nodes == 1 else x_start + in_lvl * (total_w / (n_nodes - 1))
    y = top_y - depth * level_h
    return x, y


def all_tree_positions(n, **kw):
    return [tree_pos(i, n, **kw) for i in range(n)]


# ── flat array geometry ────────────────────────────────────────────────────────
def flat_positions(n, y=0.0, box=0.72):
    gap = box + 0.2
    x0 = -(n - 1) * gap / 2
    return [(x0 + i * gap, y) for i in range(n)]


# ── scene ─────────────────────────────────────────────────────────────────────
class HeapSortScene(MovingCameraScene):
    def construct(self):
        arr = list(ARRAY)
        n = len(arr)

        FW = config.frame_width
        FH = config.frame_height
        BOX = min(0.72, 5.2 / n)
        FONT = int(BOX * 38)
        cam = self.camera.frame

        # precompute positions
        flat_pos = flat_positions(n, y=0.0, box=BOX)
        tree_kw = dict(cx=0.0, top_y=2.6, level_h=1.5, spread=min(6.5, n * 0.95))
        t_pos = all_tree_positions(n, **tree_kw)

        # ── build Manim node objects ──────────────────────────────────────────
        # circles[i] and labels[i] track the visual for heap index i.
        # IMPORTANT: unlike quicksort we don't swap the Python lists —
        # we animate position/colour changes only.
        # val[i] mirrors arr[i] and is updated on every swap event.
        val = arr[:]
        circles = []
        labels = []

        for i in range(n):
            x, y = flat_pos[i]
            c = Circle(
                BOX / 2,
                fill_color=COL_NODE,
                fill_opacity=0.92,
                stroke_color=WHITE,
                stroke_width=2,
            )
            c.move_to([x, y, 0])
            lb = Text(str(val[i]), font_size=FONT, color=WHITE, weight=BOLD)
            lb.move_to(c.get_center())
            circles.append(c)
            labels.append(lb)

        # edges (drawn between tree positions)
        edges = []
        for i in range(1, n):
            parent = (i - 1) // 2
            e = Line(
                [0, 0, 0],
                [0, 0, 0],
                stroke_color=COL_EDGE,
                stroke_width=1.8,
                stroke_opacity=0.0,
            )  # invisible until tree phase
            edges.append(e)  # edges[i-1] connects i to parent

        # index badges (flat array only)
        idx_badges = []
        for i, (x, y) in enumerate(flat_pos):
            t = Text(str(i), font_size=12, color=GRAY)
            t.move_to([x, y - BOX / 2 - 0.22, 0])
            idx_badges.append(t)

        # status text
        status = Text("", font_size=22, color=YELLOW)
        self.add(status)

        title = Text("Heap Sort", font_size=44, color=WHITE, weight=BOLD)
        title.move_to([0, 3.5, 0])

        def set_status(msg, col=YELLOW, rt=0.18):
            nonlocal status
            new = Text(msg, font_size=22, color=col)
            new.move_to(
                [cam.get_center()[0], cam.get_center()[1] - cam.height / 2 + 0.4, 0]
            )
            self.play(FadeOut(status), FadeIn(new), run_time=rt)
            status = new

        def pan(target_y, zoom=1.0, rt=0.9):
            self.play(
                cam.animate.move_to([0, target_y, 0]).set(width=FW * zoom),
                run_time=rt,
                rate_func=smooth,
            )

        # ── PHASE 0: show flat array ──────────────────────────────────────────
        self.add(title, *edges, *circles, *labels, *idx_badges)
        self.play(
            LaggedStart(
                *[
                    FadeIn(VGroup(circles[i], labels[i]), shift=UP * 0.3)
                    for i in range(n)
                ],
                lag_ratio=0.08,
            ),
            run_time=1.0,
        )
        self.wait(0.4)
        set_status("The input array — indices 0 … " + str(n - 1))
        self.wait(0.8)

        # ── PHASE 1: morph flat → binary tree ────────────────────────────────
        set_status("Visualising as a binary tree (index i → children 2i+1, 2i+2)")
        self.play(FadeOut(VGroup(*idx_badges)), run_time=0.3)

        # move each node to its tree position
        move_anims = []
        for i in range(n):
            x, y = t_pos[i]
            move_anims += [
                circles[i].animate.move_to([x, y, 0]),
                labels[i].animate.move_to([x, y, 0]),
            ]

        # draw edges simultaneously
        edge_anims = []
        for i in range(1, n):
            parent = (i - 1) // 2
            px, py = t_pos[parent]
            cx, cy = t_pos[i]
            new_edge = Line(
                [px, py, 0],
                [cx, cy, 0],
                stroke_color=COL_EDGE,
                stroke_width=1.8,
                stroke_opacity=0.7,
            )
            edge_anims.append(Transform(edges[i - 1], new_edge))

        self.play(*move_anims, *edge_anims, run_time=1.2, rate_func=smooth)
        self.wait(0.5)

        # ── PHASE 2: replay events ────────────────────────────────────────────
        events = record_events(arr)
        heap_size = n  # tracks active heap size (shrinks on extract)
        sorted_from = n  # nodes from this index onwards are sorted

        # helper: recolour node i
        def col_node(i, col, rt=0.22):
            self.play(circles[i].animate.set_fill(col, opacity=0.92), run_time=rt)

        def col_nodes(idxs, col, rt=0.25):
            self.play(
                *[
                    circles[i].animate.set_fill(col, opacity=0.92)
                    for i in idxs
                    if 0 <= i < n
                ],
                run_time=rt,
            )

        def col_now(i, col):
            circles[i].set_fill(col, opacity=0.92)

        # animated swap of two nodes in tree
        def do_swap(a, b, rt=0.7):
            # arc paths
            ax, ay = circles[a].get_center()[:2]
            bx, by = circles[b].get_center()[:2]
            path_a = ArcBetweenPoints([ax, ay, 0], [bx, by, 0], angle=PI / 2.5)
            path_b = ArcBetweenPoints([bx, by, 0], [ax, ay, 0], angle=PI / 2.5)
            self.play(
                MoveAlongPath(circles[a], path_a),
                MoveAlongPath(labels[a], path_a),
                MoveAlongPath(circles[b], path_b),
                MoveAlongPath(labels[b], path_b),
                run_time=rt,
            )
            # update val and swap Python objects so indices stay correct
            val[a], val[b] = val[b], val[a]
            circles[a], circles[b] = circles[b], circles[a]
            labels[a], labels[b] = labels[b], labels[a]

        # update label text of node i to match val[i]
        def refresh_label(i):
            new_lb = Text(str(val[i]), font_size=FONT, color=WHITE, weight=BOLD)
            new_lb.move_to(circles[i].get_center())
            self.remove(labels[i])
            self.add(new_lb)
            labels[i] = new_lb

        # ── event loop ────────────────────────────────────────────────────────
        for ev in events:
            kind = ev["kind"]

            if kind == "phase":
                if ev["phase"] == "build":
                    set_status(
                        "Phase 1 — Build Max-Heap (heapify bottom-up) ↑", col="#FF9F1C"
                    )
                    self.wait(0.5)
                else:
                    set_status(
                        "Phase 2 — Extract max to build sorted array ↓", col="#3A86FF"
                    )
                    self.wait(0.5)

            elif kind == "start_heapify":
                i = ev["i"]
                # pan camera to show subtree
                x, y = t_pos[i]
                pan(y * 0.5, zoom=1.0, rt=0.5)
                col_node(i, COL_ACTIVE, rt=0.2)
                set_status(ev["msg"])

            elif kind == "compare":
                i, l, r = ev["i"], ev["l"], ev["r"]
                targets = [x for x in [i, l, r] if 0 <= x < ev["n"]]
                col_nodes(targets, COL_ACTIVE, rt=0.2)
                self.wait(0.15)

            elif kind == "largest_found":
                i, largest = ev["i"], ev["largest"]
                # restore non-largest to default
                for x in [i, (2 * i + 1), (2 * i + 2)]:
                    if 0 <= x < ev["n"] and x != largest:
                        col_now(x, COL_HEAP_BG)
                col_now(largest, COL_LARGEST)
                set_status(ev["msg"])
                self.wait(0.2)

            elif kind == "swap":
                a, b = ev["a"], ev["b"]
                set_status(ev["msg"], col=COL_ROOT)
                col_nodes([a, b], COL_ACTIVE, rt=0.18)
                do_swap(a, b)

            elif kind == "after_swap":
                a, b = ev["a"], ev["b"]
                col_now(a, COL_LARGEST)
                col_now(b, COL_HEAP_BG)

            elif kind == "heapify_done":
                i = ev["i"]
                col_now(i, COL_HEAP_BG)
                set_status(ev["msg"], col=WHITE)
                self.wait(0.15)

            elif kind == "heap_ready":
                set_status(ev["msg"], col="#FFD166")
                # flash root gold
                self.play(
                    circles[0].animate.set_fill(COL_ROOT, opacity=1), run_time=0.4
                )
                self.wait(0.6)
                # reset all to heap colour
                self.play(
                    *[
                        circles[i].animate.set_fill(COL_HEAP_BG, opacity=0.95)
                        for i in range(n)
                    ],
                    run_time=0.4,
                )
                self.wait(0.3)

            elif kind == "extract":
                idx = ev["idx"]  # sorted destination index
                heap_size -= 1
                sorted_from -= 1

                # highlight root (the max)
                set_status(ev["msg"], col=COL_ROOT)
                self.play(
                    circles[0].animate.set_fill(COL_ROOT, opacity=1).scale(1.15),
                    run_time=0.35,
                )
                self.wait(0.2)

                # pan to show both root and destination
                root_y = t_pos[0][1]
                dest_y = t_pos[idx][1]
                mid_y = (root_y + dest_y) / 2
                pan(mid_y * 0.4, zoom=1.05, rt=0.5)

                # swap root and last active node
                do_swap(0, idx)

            elif kind == "after_extract":
                idx = ev["idx"]
                # mark extracted node as sorted (green, scale back)
                self.play(
                    circles[idx]
                    .animate.set_fill(COL_SORTED, opacity=1)
                    .scale(1 / 1.15),
                    run_time=0.4,
                )
                # dim the edge connecting it
                if idx >= 1:
                    self.play(
                        edges[idx - 1].animate.set_stroke(opacity=0.15),
                        run_time=0.3,
                    )
                set_status(ev["msg"], col=COL_SORTED)
                self.wait(0.25)

                # re-highlight root
                if heap_size > 1:
                    col_now(0, COL_ROOT)

            elif kind == "done":
                set_status(ev["msg"], col=COL_SORTED)
                self.play(
                    *[
                        circles[i].animate.set_fill(COL_SORTED, opacity=1)
                        for i in range(n)
                    ],
                    run_time=0.7,
                )
                self.wait(0.8)

                # ── FINALE: morph tree back to flat sorted array ───────────────
                set_status("Sorted! Morphing back to flat array…", col=WHITE)
                flat_y = -0.5
                flat_pos2 = flat_positions(n, y=flat_y, box=BOX)

                # fade out edges
                self.play(*[FadeOut(e) for e in edges], run_time=0.5)

                # slide all nodes to flat positions
                sort_anims = []
                for i in range(n):
                    x, y = flat_pos2[i]
                    sort_anims += [
                        circles[i].animate.move_to([x, y, 0]),
                        labels[i].animate.move_to([x, y, 0]),
                    ]
                pan(flat_y, zoom=1.0, rt=0.9)
                self.play(*sort_anims, run_time=1.1, rate_func=smooth)

                # final green flash wave
                self.play(
                    LaggedStart(
                        *[
                            circles[i]
                            .animate.set_fill(COL_SORTED, opacity=1)
                            .set_stroke(WHITE, width=2.5)
                            for i in range(n)
                        ],
                        lag_ratio=0.1,
                    ),
                    run_time=0.8,
                )
                set_status("✓  Array sorted with Heap Sort!", col=COL_SORTED)
                self.wait(2.5)
