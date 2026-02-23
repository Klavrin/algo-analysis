"""
bucketsort_animation.py
-----------------------
Manim animation of Bucket Sort.

Visual story:
  1. Show the flat float array as circles
  2. Bucket columns appear — each range labelled [lo, hi)
  3. SCATTER  — every element arcs into its bucket
  4. ISORT    — non-trivial buckets sort themselves with insertion sort
  5. GATHER   — elements pour out left→right into the sorted flat array
  6. Sorted array glows green, buckets fade away

Requirements:
    pip install manim

Run:
    manim -pql bucketsort_animation.py BucketSortScene   # fast preview
    manim -pqh bucketsort_animation.py BucketSortScene   # high quality

Change FLOAT_ARRAY in test_arrays.py (values must be floats in [0, 1)).
"""

from manim import *
import sys, os, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_arrays import FLOAT_ARRAY

# ── palette ───────────────────────────────────────────────────────────────────
BUCKET_PALETTE = [
    "#E74C3C",
    "#E67E22",
    "#F1C40F",
    "#2ECC71",
    "#1ABC9C",
    "#3498DB",
    "#9B59B6",
    "#FF6B9D",
    "#48CAE4",
    "#FF9F1C",
]
COL_DEFAULT = "#3A86FF"
COL_ACTIVE = "#FF6B6B"
COL_COMPARE = "#FFD166"
COL_SORTED = "#06D6A0"
COL_BUCKET = "#111827"


def bcol(bi):
    return BUCKET_PALETTE[bi % len(BUCKET_PALETTE)]


# ── event recorder ────────────────────────────────────────────────────────────
def record_events(arr):
    """
    Returns (events, bucket_order).

    bucket_order[bi] = list of original indices, in their final sorted order
                       within that bucket (after insertion sort).

    Events use 'oi' = original index into arr (stable identity for each circle).
    """
    n = len(arr)
    evts = []
    buckets = [[] for _ in range(n)]  # list of (oi, val)

    def push(kind, **kw):
        evts.append({"kind": kind, **kw})

    # scatter
    for oi, val in enumerate(arr):
        bi = min(int(n * val), n - 1)
        push(
            "scatter",
            oi=oi,
            val=val,
            bi=bi,
            msg=f"{val:.4f}  →  bucket {bi}  " f"(⌊{n} × {val:.4f}⌋ = {bi})",
        )
        buckets[bi].append(oi)

    # insertion sort — track swaps by original index
    for bi, bucket in enumerate(buckets):
        vals = [arr[oi] for oi in bucket]
        if len(bucket) <= 1:
            if len(bucket) == 1:
                push(
                    "bucket_done",
                    bi=bi,
                    msg=f"Bucket {bi}: 1 element — already sorted ✓",
                )
            continue

        push(
            "isort_start",
            bi=bi,
            count=len(bucket),
            msg=f"Insertion-sort bucket {bi}  ({len(bucket)} elements)",
        )

        for i in range(1, len(vals)):
            key = vals[i]
            key_oi = bucket[i]
            j = i - 1
            push("isort_key", bi=bi, slot=i, oi=key_oi, msg=f"  Key = {key:.4f}")

            while j >= 0 and vals[j] > key:
                push(
                    "isort_compare",
                    bi=bi,
                    slot_j=j,
                    oi_j=bucket[j],
                    key_oi=key_oi,
                    key=key,
                    cmp=vals[j],
                    msg=f"  {vals[j]:.4f} > {key:.4f} → shift right",
                )
                # shift right
                vals[j + 1] = vals[j]
                bucket[j + 1] = bucket[j]
                push(
                    "isort_shift",
                    bi=bi,
                    from_slot=j,
                    to_slot=j + 1,
                    oi=bucket[j + 1],
                    msg=f"  Shift {vals[j+1]:.4f} right",
                )
                j -= 1

            vals[j + 1] = key
            bucket[j + 1] = key_oi
            push(
                "isort_place",
                bi=bi,
                slot=j + 1,
                oi=key_oi,
                msg=f"  Place {key:.4f} at slot {j + 1}",
            )

        push("bucket_done", bi=bi, msg=f"Bucket {bi} sorted ✓")

    # gather
    push("gather_start", msg="Concatenating buckets → sorted array")
    dest = 0
    for bi, bucket in enumerate(buckets):
        for slot, oi in enumerate(bucket):
            push(
                "gather",
                bi=bi,
                slot=slot,
                oi=oi,
                dest=dest,
                msg=f"  Bucket {bi}[{slot}] ({arr[oi]:.4f}) → position {dest}",
            )
            dest += 1

    push("done", msg="✓  Array sorted!")
    return evts, buckets


# ── scene ─────────────────────────────────────────────────────────────────────
class BucketSortScene(MovingCameraScene):
    def construct(self):
        arr = [round(v, 6) for v in FLOAT_ARRAY]
        n = len(arr)
        nb = n

        FW = config.frame_width
        cam = self.camera.frame

        # ── layout ────────────────────────────────────────────────────────────
        R = min(0.34, 2.4 / n)
        FONT = int(R * 50)
        FLAT_Y = 2.8
        FLAT_GAP = R * 2 + 0.24
        flat_xs = [-(n - 1) * FLAT_GAP / 2 + i * FLAT_GAP for i in range(n)]

        BUCKET_W = min(1.1, (FW - 0.5) / nb)
        BUCKET_H = 3.6
        BUCKET_BOT = -0.2
        bk_xs = [-(nb - 1) * BUCKET_W / 2 + i * BUCKET_W for i in range(nb)]

        ELEM_STEP = R * 2 + 0.12  # vertical spacing of stacked elements

        def elem_y_in_bucket(stack_count):
            return BUCKET_BOT + R + stack_count * ELEM_STEP

        # ── Manim objects — one circle + label per original element ───────────
        # circles[oi] and nlabs[oi] are permanently bound to arr[oi].
        # We move them; we never reorder these Python lists.
        circles = []
        nlabs = []
        for oi, v in enumerate(arr):
            c = Circle(
                R,
                fill_color=COL_DEFAULT,
                fill_opacity=0.92,
                stroke_color=WHITE,
                stroke_width=1.8,
            )
            c.move_to([flat_xs[oi], FLAT_Y, 0])
            lb = Text(f"{v:.3f}", font_size=FONT, color=WHITE, weight=BOLD)
            lb.move_to(c.get_center())
            circles.append(c)
            nlabs.append(lb)

        # index badges below flat array
        ibadges = []
        for i in range(n):
            t = Text(str(i), font_size=11, color=GRAY)
            t.move_to([flat_xs[i], FLAT_Y - R - 0.22, 0])
            ibadges.append(t)

        # bucket rects + range labels
        brects = []
        blabels = []
        for bi in range(nb):
            x = bk_xs[bi]
            lo = round(bi / nb, 2)
            hi = round((bi + 1) / nb, 2)
            rect = Rectangle(
                width=BUCKET_W * 0.86,
                height=BUCKET_H,
                fill_color=COL_BUCKET,
                fill_opacity=0.55,
                stroke_color=bcol(bi),
                stroke_width=2,
            )
            rect.move_to([x, BUCKET_BOT + BUCKET_H / 2, 0])
            lbl = Text(
                f"[{lo:.2f},{hi:.2f})",
                font_size=max(9, int(BUCKET_W * 12)),
                color=bcol(bi),
            )
            lbl.move_to([x, BUCKET_BOT - 0.3, 0])
            brects.append(rect)
            blabels.append(lbl)

        # title + status
        title = Text("Bucket Sort", font_size=44, color=WHITE, weight=BOLD)
        title.move_to([0, FLAT_Y + R + 0.55, 0])

        status = Text("", font_size=19, color=YELLOW)
        self.add(status)

        def set_status(msg, col=YELLOW, rt=0.14):
            nonlocal status
            new = Text(msg, font_size=19, color=col)
            new.move_to([0, cam.get_center()[1] - cam.height / 2 + 0.36, 0])
            self.play(FadeOut(status), FadeIn(new), run_time=rt)
            status = new

        def pan(y, zoom=1.0, rt=0.8):
            self.play(
                cam.animate.move_to([0, y, 0]).set(width=FW * zoom),
                run_time=rt,
                rate_func=smooth,
            )

        # ── INTRO ─────────────────────────────────────────────────────────────
        self.add(title, *circles, *nlabs, *ibadges)
        self.play(
            LaggedStart(
                *[
                    FadeIn(VGroup(circles[i], nlabs[i]), shift=UP * 0.25)
                    for i in range(n)
                ],
                lag_ratio=0.1,
            ),
            run_time=0.9,
        )
        self.wait(0.3)
        set_status(
            "Float values in [0, 1) — we'll sort with n = " + str(n) + " buckets"
        )
        self.wait(0.8)

        # reveal buckets
        self.play(FadeOut(VGroup(*ibadges)), run_time=0.2)
        pan(0.8, zoom=1.15, rt=0.7)
        self.play(
            LaggedStart(
                *[FadeIn(VGroup(brects[bi], blabels[bi])) for bi in range(nb)],
                lag_ratio=0.07,
            ),
            run_time=0.7,
        )
        set_status("Each bucket covers an equal slice of [0, 1)")
        self.wait(0.7)

        # ── replay events ─────────────────────────────────────────────────────
        evts, _ = record_events(arr)

        # track how many elements are in each bucket (for y stacking)
        bk_count = [0] * nb

        # track current bucket-slot position for each oi
        # oi_slot[oi] = (bi, slot_index) once scattered, None before
        oi_slot = [None] * n

        # track the "key" oi currently being insertion-sorted
        current_key_oi = None

        for ev in evts:
            kind = ev["kind"]

            # ── scatter ───────────────────────────────────────────────────────
            if kind == "scatter":
                oi, bi = ev["oi"], ev["bi"]
                col = bcol(bi)
                set_status(ev["msg"])

                dest_x = bk_xs[bi]
                dest_y = elem_y_in_bucket(bk_count[bi])

                self.play(
                    circles[oi].animate.set_fill(col, opacity=1).scale(1.12),
                    run_time=0.22,
                )
                path = ArcBetweenPoints(
                    circles[oi].get_center(),
                    [dest_x, dest_y, 0],
                    angle=-PI / 3.5,
                )
                self.play(
                    MoveAlongPath(circles[oi], path),
                    MoveAlongPath(nlabs[oi], path),
                    run_time=0.48,
                )
                circles[oi].scale(1 / 1.12)
                oi_slot[oi] = (bi, bk_count[bi])
                bk_count[bi] += 1

            # ── insertion sort ────────────────────────────────────────────────
            elif kind == "isort_start":
                bi = ev["bi"]
                set_status(ev["msg"], col="#FFD166")
                self.play(
                    brects[bi].animate.set_stroke(WHITE, width=3.5),
                    run_time=0.22,
                )

            elif kind == "isort_key":
                oi = ev["oi"]
                current_key_oi = oi
                self.play(
                    circles[oi].animate.set_fill(COL_ACTIVE, opacity=1).scale(1.12),
                    run_time=0.2,
                )
                set_status(ev["msg"])

            elif kind == "isort_compare":
                oi_j = ev["oi_j"]
                self.play(
                    circles[oi_j].animate.set_fill(COL_COMPARE, opacity=1),
                    run_time=0.18,
                )
                set_status(ev["msg"])
                self.wait(0.12)

            elif kind == "isort_shift":
                # a non-key element shifts one slot up (visually up in bucket)
                oi = ev["oi"]
                to_slot = ev["to_slot"]
                bi = ev["bi"]
                dest_x = bk_xs[bi]
                dest_y = elem_y_in_bucket(to_slot)
                self.play(
                    circles[oi]
                    .animate.move_to([dest_x, dest_y, 0])
                    .set_fill(bcol(bi), opacity=0.95),
                    nlabs[oi].animate.move_to([dest_x, dest_y, 0]),
                    run_time=0.25,
                )
                oi_slot[oi] = (bi, to_slot)

            elif kind == "isort_place":
                # key drops into its correct slot
                oi = ev["oi"]
                slot = ev["slot"]
                bi = ev["bi"]
                dest_x = bk_xs[bi]
                dest_y = elem_y_in_bucket(slot)
                self.play(
                    circles[oi]
                    .animate.move_to([dest_x, dest_y, 0])
                    .set_fill(bcol(bi), opacity=0.95)
                    .scale(1 / 1.12),
                    nlabs[oi].animate.move_to([dest_x, dest_y, 0]),
                    run_time=0.28,
                )
                oi_slot[oi] = (bi, slot)
                current_key_oi = None

            elif kind == "bucket_done":
                bi = ev["bi"]
                set_status(ev["msg"], col=COL_SORTED)
                self.play(
                    brects[bi]
                    .animate.set_stroke(COL_SORTED, width=2.5)
                    .set_fill(COL_BUCKET, opacity=0.65),
                    run_time=0.28,
                )
                self.wait(0.18)

            # ── gather ────────────────────────────────────────────────────────
            elif kind == "gather_start":
                set_status(ev["msg"], col="#3A86FF")
                pan(FLAT_Y * 0.35, zoom=1.1, rt=0.8)
                self.wait(0.25)

            elif kind == "gather":
                oi = ev["oi"]
                dest = ev["dest"]
                set_status(ev["msg"])
                dest_x = flat_xs[dest]
                dest_y = FLAT_Y
                self.play(
                    circles[oi]
                    .animate.move_to([dest_x, dest_y, 0])
                    .set_fill(COL_SORTED, opacity=1)
                    .set_stroke(WHITE, width=2),
                    nlabs[oi].animate.move_to([dest_x, dest_y, 0]),
                    run_time=0.35,
                )

            elif kind == "done":
                set_status(ev["msg"], col=COL_SORTED)
                self.play(
                    *[FadeOut(VGroup(brects[bi], blabels[bi])) for bi in range(nb)],
                    run_time=0.45,
                )
                pan(FLAT_Y, zoom=1.0, rt=0.7)
                # wave
                self.play(
                    LaggedStart(
                        *[
                            VGroup(circles[i], nlabs[i]).animate.set_fill(
                                COL_SORTED, opacity=1
                            )
                            for i in range(n)
                        ],
                        lag_ratio=0.11,
                    ),
                    run_time=0.8,
                )
                set_status("✓  Array sorted with Bucket Sort!", col=COL_SORTED)
                self.wait(2.5)
