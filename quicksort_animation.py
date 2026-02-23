"""
quicksort_animation.py
----------------------
Manim animation of QuickSort that reads the array from test_arrays.py.

Requirements:
    pip install manim

Run:
    manim -pql quicksort_animation.py QuickSortScene   # fast preview
    manim -pqh quicksort_animation.py QuickSortScene   # high quality

Change ARRAY in test_arrays.py — both quicksort.py and this animation update.
"""

from manim import *
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_arrays import ARRAY

# ── colours ───────────────────────────────────────────────────────────────────
COL_DEFAULT = "#4A90D9"
COL_PIVOT = "#E8A838"
COL_COMPARE = "#E84040"
COL_SWAP = "#FF6B35"
COL_SORTED = "#4CAF50"


# ── record every quicksort event (plain Python, no Manim) ─────────────────────
def record_events(original):
    """
    Simulate quicksort and record every decision as an event.
    Event indices (a, b, j, pivot_idx …) are indices into the *data* list,
    which at any point equals the screen-slot positions, because both
    the simulation and the visual representation start identical and stay
    in sync through the at_pos / slot maps in the scene.
    """
    data = original[:]
    events = []
    sorted_set = set()

    def push(kind, **kw):
        events.append({"kind": kind, "data": data[:], **kw})

    def partition(lo, hi):
        pivot = data[hi]
        push("pivot", lo=lo, hi=hi, pivot_idx=hi, msg=f"Pivot = {pivot}  (index {hi})")

        i = lo - 1
        for j in range(lo, hi):
            push(
                "compare",
                lo=lo,
                hi=hi,
                pivot_idx=hi,
                j=j,
                msg=f"Is  {data[j]}  <  pivot {pivot} ?",
            )
            if data[j] < pivot:
                i += 1
                if i != j:
                    push(
                        "swap",
                        lo=lo,
                        hi=hi,
                        pivot_idx=hi,
                        a=i,
                        b=j,
                        msg=f"Swap  {data[i]}  ↔  {data[j]}",
                    )
                    data[i], data[j] = data[j], data[i]

        pi = i + 1
        if pi != hi:
            push(
                "swap",
                lo=lo,
                hi=hi,
                pivot_idx=hi,
                a=pi,
                b=hi,
                msg=f"Place pivot {data[hi]} → index {pi}",
            )
            data[pi], data[hi] = data[hi], data[pi]

        sorted_set.add(pi)
        push(
            "sorted_idx",
            lo=lo,
            hi=hi,
            idx=pi,
            sorted_set=sorted_set.copy(),
            msg=f"{data[pi]}  is in its final position ✓",
        )
        return pi

    def qs(lo, hi):
        if lo < hi:
            pi = partition(lo, hi)
            qs(lo, pi - 1)
            qs(pi + 1, hi)
        elif lo == hi:
            sorted_set.add(lo)
            push(
                "sorted_idx",
                lo=lo,
                hi=hi,
                idx=lo,
                sorted_set=sorted_set.copy(),
                msg=f"Single element  {data[lo]}  is already sorted ✓",
            )

    qs(0, len(data) - 1)
    push("done", sorted_set=sorted_set.copy(), msg="✓  Array sorted!")
    return events


# ── scene ─────────────────────────────────────────────────────────────────────
class QuickSortScene(Scene):
    def construct(self):
        arr = list(ARRAY)
        n = len(arr)

        # ── layout ────────────────────────────────────────────────────────────
        BOX = min(0.9, 6.8 / n)
        GAP = BOX + 0.18
        Y = 0.3
        x0 = -(n - 1) * GAP / 2

        def slot_x(s):
            return x0 + s * GAP

        # ── KEY DATA STRUCTURES ───────────────────────────────────────────────
        #
        #  boxes[i] / num_labels[i]  →  the Square/Text for original value arr[i]
        #  slot[i]   = which screen position (0..n-1) value i currently sits at
        #  at_pos[s] = which value index is currently at screen position s
        #
        #  Event indices from record_events() refer to screen positions (slots),
        #  so we convert:  val_index = at_pos[slot_from_event]
        #
        slot = list(range(n))  # slot[val_idx]  = current screen pos
        at_pos = list(range(n))  # at_pos[screen] = current val_idx

        boxes = []
        num_labels = []
        for i, v in enumerate(arr):
            sq = Square(
                side_length=BOX,
                color=WHITE,
                fill_color=COL_DEFAULT,
                fill_opacity=1,
                stroke_width=2,
            )
            sq.move_to([slot_x(i), Y, 0])

            lb = Text(str(v), font_size=int(BOX * 40), color=WHITE, weight=BOLD)
            lb.move_to(sq.get_center())

            boxes.append(sq)
            num_labels.append(lb)

        # small index labels below slots
        idx_labels = []
        for s in range(n):
            t = Text(str(s), font_size=14, color=GRAY)
            t.move_to([slot_x(s), Y - BOX / 2 - 0.25, 0])
            idx_labels.append(t)

        # title
        title = Text("QuickSort Visualisation", font_size=30, color=WHITE)
        title.to_edge(UP, buff=0.25)

        # legend
        def leg_item(col, txt):
            sq = Square(0.2, fill_color=col, fill_opacity=1, stroke_width=0)
            t = Text(txt, font_size=15, color=WHITE)
            t.next_to(sq, RIGHT, buff=0.08)
            return VGroup(sq, t)

        legend = VGroup(
            leg_item(COL_DEFAULT, "Unsorted"),
            leg_item(COL_PIVOT, "Pivot"),
            leg_item(COL_COMPARE, "Compare"),
            leg_item(COL_SWAP, "Swap"),
            leg_item(COL_SORTED, "Sorted"),
        ).arrange(RIGHT, buff=0.3)
        legend.next_to(title, DOWN, buff=0.18)

        status_mob = Text("", font_size=21, color=YELLOW)
        status_mob.to_edge(DOWN, buff=0.4)

        self.add(title, legend, *boxes, *num_labels, *idx_labels, status_mob)
        self.wait(0.4)

        # ── helpers ───────────────────────────────────────────────────────────

        def recolour(val_idx, col, rt=0.22):
            self.play(boxes[val_idx].animate.set_fill(col, opacity=1), run_time=rt)

        def recolour_now(val_idx, col):
            boxes[val_idx].set_fill(col, opacity=1)

        def update_status(msg, col=YELLOW):
            nonlocal status_mob
            new = Text(msg, font_size=21, color=col)
            new.to_edge(DOWN, buff=0.4)
            self.play(FadeOut(status_mob), FadeIn(new), run_time=0.18)
            status_mob = new

        def do_swap(va, vb):
            """Animate boxes for value-indices va and vb swapping screen slots."""
            sa, sb = slot[va], slot[vb]
            path_a = ArcBetweenPoints(
                [slot_x(sa), Y, 0], [slot_x(sb), Y, 0], angle=PI / 2.8
            )
            path_b = ArcBetweenPoints(
                [slot_x(sb), Y, 0], [slot_x(sa), Y, 0], angle=PI / 2.8
            )
            self.play(
                MoveAlongPath(boxes[va], path_a),
                MoveAlongPath(num_labels[va], path_a),
                MoveAlongPath(boxes[vb], path_b),
                MoveAlongPath(num_labels[vb], path_b),
                run_time=0.75,
            )
            # keep maps in sync
            slot[va], slot[vb] = sb, sa
            at_pos[sb], at_pos[sa] = va, vb

        # ── replay events ──────────────────────────────────────────────────────
        events = record_events(arr)

        # track which val_idx is currently the pivot
        current_pivot_val = None

        for ev in events:
            kind = ev["kind"]

            # ── new partition call: highlight pivot, reset sub-array ───────────
            if kind == "pivot":
                lo, hi = ev["lo"], ev["hi"]
                pivot_slot = ev["pivot_idx"]  # screen slot = hi
                current_pivot_val = at_pos[pivot_slot]

                for s in range(lo, hi + 1):
                    vi = at_pos[s]
                    recolour_now(vi, COL_DEFAULT)

                update_status(ev["msg"])
                recolour(current_pivot_val, COL_PIVOT)

            # ── compare element j against pivot ───────────────────────────────
            elif kind == "compare":
                j_val = at_pos[ev["j"]]
                update_status(ev["msg"])
                recolour(j_val, COL_COMPARE)
                self.wait(0.2)
                if j_val != current_pivot_val:
                    recolour(j_val, COL_DEFAULT)

            # ── swap elements at screen slots a and b ─────────────────────────
            elif kind == "swap":
                va = at_pos[ev["a"]]
                vb = at_pos[ev["b"]]
                update_status(ev["msg"], col=COL_SWAP)
                recolour(va, COL_SWAP)
                recolour(vb, COL_SWAP)

                # remember which val is the pivot BEFORE the move
                pivot_is_va = va == current_pivot_val
                pivot_is_vb = vb == current_pivot_val

                do_swap(va, vb)

                # restore colours: pivot keeps its colour, other goes default
                if pivot_is_va:
                    recolour(va, COL_PIVOT, rt=0.18)
                    recolour(vb, COL_DEFAULT, rt=0.18)
                elif pivot_is_vb:
                    recolour(vb, COL_PIVOT, rt=0.18)
                    recolour(va, COL_DEFAULT, rt=0.18)
                else:
                    recolour(va, COL_DEFAULT, rt=0.18)
                    recolour(vb, COL_DEFAULT, rt=0.18)

            # ── mark confirmed sorted positions green ─────────────────────────
            elif kind == "sorted_idx":
                update_status(ev["msg"], col=COL_SORTED)
                anims = [
                    boxes[at_pos[s]].animate.set_fill(COL_SORTED, opacity=1)
                    for s in ev["sorted_set"]
                ]
                if anims:
                    self.play(*anims, run_time=0.4)
                self.wait(0.25)

            # ── final frame ───────────────────────────────────────────────────
            elif kind == "done":
                update_status(ev["msg"], col=GREEN)
                self.play(
                    *[b.animate.set_fill(COL_SORTED, opacity=1) for b in boxes],
                    run_time=0.6,
                )
                self.wait(2)
