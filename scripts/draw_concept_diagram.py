"""Draw the conceptual system diagram (issue #17): docs/figures/concept-diagram.png.

A schematic, not a result: the tank layout and the agents drawn in it are hand-placed to explain the model's
entities and daily update order (docs/model-specification.md sections 2, 3, 9-13). No simulation is run.

Usage:
    python scripts/draw_concept_diagram.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

# Same fixed palette as the result figures (scripts/analyse_results.py): S, I, R keep their colours.
S_COL, I_COL, R_COL = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, SURFACE, REGION_FILL = "#0b0b0b", "#8a8984", "#fcfcfb", "#f0efec"

TANK_R = 0.32
# Region centres and the five tank positions around each centre (schematic layout)
REGION_CENTRES = {0: (1.6, 5.4), 1: (5.4, 5.4), 2: (1.6, 1.6), 3: (5.4, 1.6)}


def tank_positions() -> dict[int, tuple[float, float]]:
    pos = {}
    for region, (cx, cy) in REGION_CENTRES.items():
        for i in range(5):
            angle = math.pi / 2 + 2 * math.pi * i / 5
            pos[5 * region + i] = (cx + 0.95 * math.cos(angle), cy + 0.95 * math.sin(angle))
    return pos


INTRA_EDGES = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 4), (1, 4), (5, 6), (6, 7), (7, 8), (8, 9), (5, 9), (6, 9),
               (10, 11), (11, 12), (12, 13), (13, 14), (10, 14), (11, 13), (15, 16), (16, 17), (17, 18),
               (18, 19), (15, 19), (16, 19)]
BRIDGE_EDGES = [(4, 6), (2, 10), (9, 16), (14, 17)]
BRIDGE_TANK = 4       # drawn with the high-betweenness ring
QUARANTINED_TANK = 9  # drawn as quarantined
# Agents shown in a few tanks: (tank, [states])
AGENTS = {4: "SSIIR", 3: "SISSR", 6: "SSSIS", 9: "SSIIS", 0: "SSSSS", 16: "SSSSS", 18: "SSRSS"}


def draw_system(ax) -> None:
    pos = tank_positions()
    for region, (cx, cy) in REGION_CENTRES.items():
        ax.add_patch(FancyBboxPatch((cx - 1.45, cy - 1.45), 2.9, 2.9, boxstyle="round,pad=0.02,rounding_size=0.25",
                                    facecolor=REGION_FILL, edgecolor="none", zorder=0))
        ax.text(cx - 1.35, cy + 1.3, f"region {region}", fontsize=9, color=INK, va="top")
    for a, b in INTRA_EDGES:
        ax.plot(*zip(pos[a], pos[b]), color=MUTED, lw=1.0, zorder=1)
    for a, b in BRIDGE_EDGES:
        ax.plot(*zip(pos[a], pos[b]), color=INK, lw=2.0, zorder=1)
    for tank, (x, y) in pos.items():
        quarantined = tank == QUARANTINED_TANK
        ax.add_patch(Circle((x, y), TANK_R, facecolor=SURFACE, edgecolor=INK if quarantined else MUTED,
                            lw=2.2 if quarantined else 1.2, ls="--" if quarantined else "-",
                            hatch="////" if quarantined else None, zorder=2))
        if tank == BRIDGE_TANK:
            ax.add_patch(Circle((x, y), TANK_R + 0.09, facecolor="none", edgecolor=INK, lw=3, zorder=3))
        states = AGENTS.get(tank)
        if states:
            for i, state in enumerate(states):
                angle = 2 * math.pi * i / len(states)
                col = {"S": S_COL, "I": I_COL, "R": R_COL}[state]
                ax.add_patch(Circle((x + 0.17 * math.cos(angle), y + 0.17 * math.sin(angle)), 0.065,
                                    facecolor=col, edgecolor=SURFACE, lw=0.8, zorder=4))
    # an accepted transfer along an intra-region edge (region 3, right side), and a blocked one
    (x0, y0), (x1, y1) = pos[18], pos[19]
    ax.add_patch(FancyArrowPatch((x0 + 0.38, y0 + 0.05), (x1 + 0.38, y1 - 0.05), arrowstyle="-|>", mutation_scale=14,
                                 connectionstyle="arc3,rad=0.45", color=INK, lw=1.4, zorder=5))
    ax.annotate("accepted transfer along an edge\n(each agent tries with probability\n= transfer rate; needs an open,\nnon-full neighbouring tank)",
                (x0 + 0.75, (y0 + y1) / 2), xytext=(7.25, 1.35), ha="left", va="center", fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    qx, qy = pos[QUARANTINED_TANK]
    sx, sy = pos[8]
    ax.add_patch(FancyArrowPatch((sx + 0.05, sy - 0.35), (qx - 0.05, qy - 0.42), arrowstyle="-|>", mutation_scale=14,
                                 connectionstyle="arc3,rad=0.4", color=INK, lw=1.4, ls="--", zorder=5))
    ax.text(qx + 0.42, qy - 0.55, "×", fontsize=16, color=INK, ha="center", va="center", zorder=6)
    ax.text(qx + 0.62, qy - 0.55, "blocked", fontsize=7.5, color=INK, ha="left", va="center", zorder=6)
    ax.annotate("quarantined tank:\nno transfers in or out;\ntransmission inside continues",
                (qx + 0.36, qy + 0.12), xytext=(7.25, 6.15), fontsize=7.5, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    bx, by = pos[BRIDGE_TANK]
    ax.annotate("bridge tank: high betweenness,\nchosen by targeted quarantine",
                (bx + 0.45, by + 0.15), xytext=(2.9, 7.45), fontsize=7.5, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("between-region\n(bridge) edge", (3.5, pos[4][1] + 0.0), xytext=(3.5, 3.5), fontsize=7.5, color=INK,
                ha="center", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=12))
    # legend
    handles = [
        plt.Line2D([], [], marker="o", ls="", color=c, markersize=7, label=label)
        for c, label in ((S_COL, "susceptible (S)"), (I_COL, "infectious (I)"), (R_COL, "recovered (R)"))
    ] + [
        plt.Line2D([], [], color=MUTED, lw=1.0, label="within-region edge (p_in)"),
        plt.Line2D([], [], color=INK, lw=2.0, label="between-region edge (p_out)"),
    ]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=3, frameon=False, fontsize=8)
    ax.set_xlim(-0.1, 9.6)
    ax.set_ylim(-1.2, 7.9)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("System: 200 turtles in 20 tanks, 4 regions (schematic, not a generated network)\n"
                 "Each tank holds 10 turtles at the start (capacity 12); dots show a few of them.",
                 fontsize=10, loc="left", color=INK)


STEPS = [
    ("1  Management", "quarantine starts on the response day,\nends after D days"),
    ("2  Movement", "random order; each transfer checked\nat once against quarantine and capacity"),
    ("3  Transmission snapshot", "freeze tank membership after movement"),
    ("4  Infection draws", "S → I with 1 − (1 − β)^I_j"),
    ("5  Recovery draws", "I → R with probability γ"),
    ("6  Commit", "apply all infections and recoveries together"),
    ("7  Record", "daily S, I, R, transfers, affected tanks"),
    ("8  Stop?", "no I left, or day 365"),
]


def draw_daily_loop(ax) -> None:
    top, step_h, gap = 7.5, 0.72, 0.18
    for i, (title, detail) in enumerate(STEPS):
        y = top - i * (step_h + gap)
        ax.add_patch(FancyBboxPatch((0.2, y - step_h), 4.6, step_h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=SURFACE, edgecolor=INK if i in (1, 5) else MUTED, lw=1.2))
        ax.text(0.35, y - 0.2, title, fontsize=8.5, fontweight="bold", color=INK, va="center")
        ax.text(0.35, y - 0.5, detail, fontsize=7, color=INK, va="center")
        if i < len(STEPS) - 1:
            ax.annotate("", (2.5, y - step_h - gap + 0.01), (2.5, y - step_h - 0.01),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0))
    last_y = top - (len(STEPS) - 1) * (step_h + gap) - step_h / 2
    ax.add_patch(FancyArrowPatch((4.8, last_y), (4.8, top - step_h / 2), connectionstyle="arc3,rad=0.45",
                                 arrowstyle="-|>", mutation_scale=12, color=INK, lw=1.0))
    ax.text(5.55, (last_y + top) / 2, "next\nday", fontsize=8, color=INK, ha="center", va="center")
    ax.text(0.2, -0.05, "Bold boxes: movement is asynchronous (one agent at a time);\n"
            "disease updates are synchronous (all at once in step 6).", fontsize=7.5, color=INK, va="top")
    ax.set_xlim(0, 6.2)
    ax.set_ylim(-1.2, 7.9)
    ax.axis("off")
    ax.set_title("One day of the model", fontsize=10, loc="left", color=INK)


def main() -> int:
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 6.6), gridspec_kw={"width_ratios": [1.55, 1]})
    fig.patch.set_facecolor("white")
    draw_system(left)
    draw_daily_loop(right)
    fig.tight_layout()
    out = ROOT / "docs" / "figures" / "concept-diagram.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
