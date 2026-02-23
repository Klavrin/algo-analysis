"""
mergesort_animation.py
----------------------
Manim animation of MergeSort — visual split tree with camera movement.

Requirements:
    pip install manim

Run:
    manim -pql mergesort_animation.py MergeSortScene   # fast preview
    manim -pqh mergesort_animation.py MergeSortScene   # high quality

Change ARRAY in test_arrays.py to update both mergesort.py and this file.
"""

from manim import *
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_arrays import ARRAY

# ── palette ───────────────────────────────────────────────────────────────────
PALETTE = [
    "#E74C3C",
    "#E67E22",
    "#F1C40F",
    "#2ECC71",
    "#1ABC9C",
    "#3498DB",
    "#9B59B6",
    "#E91E8C",
]
COL_SORTED = "#4CAF50"
COL_LINE = "#888899"
COL_BG = "#1a1a2e"


def depth_colour(depth, index):
    return PALETTE[(depth * 3 + index) % len(PALETTE)]


# ── build split tree ──────────────────────────────────────────────────────────
def build_tree(arr):
    """
    Returns:
      levels        list[list[dict]]  — each level is a list of node dicts
      merge_order   list[(l,m,r)]     — order merges happen (post-order)

    node dict keys: left, right, depth, index (position in level)
    """
    levels = []
    merge_order = []

    def recurse(left, right, depth):
        while len(levels) <= depth:
            levels.append([])
        node = dict(left=left, right=right, depth=depth, index=len(levels[depth]))
        levels[depth].append(node)
        if left < right:
            mid = (left + right) // 2
            recurse(left, mid, depth + 1)
            recurse(mid + 1, right, depth + 1)
            merge_order.append((left, mid, right))

    recurse(0, len(arr) - 1, 0)
    return levels, merge_order


# ── scene ─────────────────────────────────────────────────────────────────────
class MergeSortScene(MovingCameraScene):
    def construct(self):
        arr = list(ARRAY)
        n = len(arr)

        levels, merge_order = build_tree(arr)
        num_levels = len(levels)

        # ── layout ────────────────────────────────────────────────────────────
        BOX = min(0.78, 5.6 / n)
        H_GAP = BOX * 0.28
        ROW_H = BOX + 1.5
        FW = config.frame_width
        FH = config.frame_height
        ASPECT = FW / FH

        def ex(i):  # x centre of global index i
            total = n * BOX + (n - 1) * H_GAP
            return -total / 2 + i * (BOX + H_GAP) + BOX / 2

        def ry(depth):  # y centre of depth row
            return -(depth * ROW_H)

        # ── build Manim objects for every node ────────────────────────────────
        # node_grp[(l,r)] = VGroup of (Square, Text) pairs, one per element
        node_grp = {}

        for depth, level in enumerate(levels):
            for node in level:
                l, r = node["left"], node["right"]
                col = depth_colour(depth, node["index"])
                grp = VGroup()
                y = ry(depth)
                for k in range(r - l + 1):
                    gi = l + k
                    sq = Square(
                        BOX,
                        fill_color=col,
                        fill_opacity=0.88,
                        stroke_color=WHITE,
                        stroke_width=1.5,
                    )
                    sq.move_to([ex(gi), y, 0])
                    lb = Text(
                        str(arr[gi]), font_size=int(BOX * 36), color=WHITE, weight=BOLD
                    )
                    lb.move_to(sq.get_center())
                    grp.add(VGroup(sq, lb))
                node_grp[(l, r)] = grp

        # ── connector lines (parent → children) ──────────────────────────────
        # lines[(l,r)] = (left_line, right_line)
        lines = {}
        for depth, level in enumerate(levels):
            for node in level:
                l, r = node["left"], node["right"]
                if l == r:
                    continue
                mid = (l + r) // 2
                py = ry(depth)
                cy = ry(depth + 1)
                pcx = (ex(l) + ex(r)) / 2
                lcx = (ex(l) + ex(mid)) / 2
                rcx = (ex(mid + 1) + ex(r)) / 2
                ll = Line(
                    [pcx, py - BOX / 2 - 0.06, 0],
                    [lcx, cy + BOX / 2 + 0.06, 0],
                    stroke_color=COL_LINE,
                    stroke_width=1.8,
                    stroke_opacity=0.7,
                )
                rl = Line(
                    [pcx, py - BOX / 2 - 0.06, 0],
                    [rcx, cy + BOX / 2 + 0.06, 0],
                    stroke_color=COL_LINE,
                    stroke_width=1.8,
                    stroke_opacity=0.7,
                )
                lines[(l, r)] = (ll, rl)

        cam = self.camera.frame

        def pan(y_target, zoom=1.0, rt=1.0):
            self.play(
                cam.animate.move_to([0, y_target, 0]).set(width=FW * zoom),
                run_time=rt,
                rate_func=smooth,
            )

        # status bar — redrawn each time
        status = Text("", font_size=24, color=YELLOW)
        self.add(status)

        def set_status(msg, col=YELLOW, rt=0.2):
            nonlocal status
            fs = max(14, int(24 * FW / cam.width))
            new = Text(msg, font_size=fs, color=col)
            new.move_to([0, cam.get_center()[1] - cam.height / 2 + 0.4, 0])
            self.play(FadeOut(status), FadeIn(new), run_time=rt)
            status = new

        # ── INTRO: show the full array ────────────────────────────────────────
        root = node_grp[(0, n - 1)]
        title = Text("Merge Sort", font_size=42, color=WHITE, weight=BOLD)
        title.next_to(root, UP, buff=0.5)
        self.add(title)

        self.play(FadeIn(root, shift=DOWN * 0.3), run_time=0.9)
        self.wait(0.4)
        set_status("Here is the full array — we'll split it all the way down")
        self.wait(0.9)
        self.play(FadeOut(title), run_time=0.4)

        # ── SPLIT PHASE ───────────────────────────────────────────────────────
        set_status("Splitting in half recursively ↓")
        self.wait(0.3)

        for depth in range(num_levels - 1):
            # pan camera down to the new child row
            zoom = 1.0 + depth * 0.22
            pan(ry(depth + 1) * 0.6, zoom=zoom, rt=0.85)

            # gather lines and child groups for this depth
            depth_lines = []
            child_groups = []
            for node in levels[depth]:
                l, r = node["left"], node["right"]
                if l == r:
                    continue
                mid = (l + r) // 2
                depth_lines += list(lines[(l, r)])
                child_groups += [node_grp[(l, mid)], node_grp[(mid + 1, r)]]

            if depth_lines:
                self.play(*[Create(ln) for ln in depth_lines], run_time=0.45)
            if child_groups:
                self.play(
                    *[FadeIn(cg, shift=DOWN * 0.3) for cg in child_groups],
                    run_time=0.55,
                )
            self.wait(0.2)

        set_status("Every sub-array is now a single element ✓", col=WHITE)
        self.wait(0.5)

        # ── ZOOM OUT to see the whole tree ────────────────────────────────────
        set_status("Now merge back up in sorted order ↑")
        total_h = (num_levels - 1) * ROW_H + BOX
        mid_y = -((num_levels - 1) * ROW_H) / 2
        need_w = max(FW, total_h * ASPECT * 1.1)
        self.play(
            cam.animate.move_to([0, mid_y, 0]).set(width=need_w),
            run_time=1.5,
            rate_func=smooth,
        )
        self.wait(0.7)

        # ── MERGE PHASE ───────────────────────────────────────────────────────
        sim = arr[:]  # simulated data — kept in sync with merges

        for left, mid, right in merge_order:
            depth = next(
                node["depth"]
                for level in levels
                for node in level
                if node["left"] == left and node["right"] == right
            )
            idx = next(
                node["index"]
                for level in levels
                for node in level
                if node["left"] == left and node["right"] == right
            )

            # pan to the parent row
            zoom_m = 1.0 + max(0, (num_levels - depth - 1)) * 0.18
            pan(ry(depth) * 0.55, zoom=zoom_m, rt=0.65)

            # highlight children with a yellow stroke pulse
            lc = node_grp[(left, mid)]
            rc = node_grp[(mid + 1, right)]
            self.play(
                *[p[0].animate.set_stroke(YELLOW, width=3.5) for p in lc],
                *[p[0].animate.set_stroke(YELLOW, width=3.5) for p in rc],
                run_time=0.3,
            )

            # compute merged result
            L = sim[left : mid + 1][:]
            R = sim[mid + 1 : right + 1][:]
            merged, i, j = [], 0, 0
            while i < len(L) and j < len(R):
                if L[i] <= R[j]:
                    merged.append(L[i])
                    i += 1
                else:
                    merged.append(R[j])
                    j += 1
            merged += L[i:] + R[j:]
            for k, v in enumerate(merged):
                sim[left + k] = v

            # build the new merged VGroup at the parent row y
            col_new = depth_colour(depth, idx)
            new_grp = VGroup()
            parent_y = ry(depth)
            for k, v in enumerate(merged):
                gi = left + k
                sq = Square(
                    BOX,
                    fill_color=col_new,
                    fill_opacity=0.92,
                    stroke_color=WHITE,
                    stroke_width=2,
                )
                sq.move_to([ex(gi), parent_y, 0])
                lb = Text(str(v), font_size=int(BOX * 36), color=WHITE, weight=BOLD)
                lb.move_to(sq.get_center())
                new_grp.add(VGroup(sq, lb))

            # animate children flying up into the parent row
            src_pairs = list(lc) + list(rc)
            tgt_pairs = list(new_grp)

            # map child boxes to their target position by sort order
            arc_dir = [0.45 if i < len(lc) else -0.45 for i in range(len(src_pairs))]

            # find which src box maps to which target slot by value
            src_vals = [int(p[1].text) for p in src_pairs]
            used_src = [False] * len(src_pairs)
            mapping = []  # mapping[tgt_k] = src_k
            for k, v in enumerate(merged):
                for si, sv in enumerate(src_vals):
                    if sv == v and not used_src[si]:
                        mapping.append(si)
                        used_src[si] = True
                        break

            self.play(
                *[
                    Transform(
                        src_pairs[mapping[k]],
                        tgt_pairs[k],
                        path_arc=arc_dir[mapping[k]],
                    )
                    for k in range(len(tgt_pairs))
                ],
                run_time=0.85,
            )

            # replace in scene
            self.remove(node_grp[(left, right)])
            self.add(new_grp)
            node_grp[(left, right)] = new_grp
            for p in new_grp:
                p[0].set_stroke(WHITE, width=2)

            is_done = left == 0 and right == n - 1
            msg = (
                "✓  Fully sorted!"
                if is_done
                else f"Merged [{left}..{right}]  →  {merged}"
            )
            set_status(msg, col=COL_SORTED if is_done else YELLOW)
            self.wait(0.3 if not is_done else 1.0)

        # ── FINALE ────────────────────────────────────────────────────────────
        pan(0, zoom=1.0, rt=1.3)

        final = node_grp[(0, n - 1)]
        self.play(
            *[
                p[0].animate.set_fill(COL_SORTED, opacity=1).set_stroke(WHITE, width=2)
                for p in final
            ],
            run_time=0.8,
        )
        set_status("Array sorted! ✓", col=COL_SORTED)
        self.wait(2.5)
