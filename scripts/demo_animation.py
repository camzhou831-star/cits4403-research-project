"""Network animation of one paired block of `formal-nested`, used by scripts/make_demo_video.py.

The block is the one `scripts/demo_final.py` reruns: the representative cross-region outbreak of figure 7,
picked by a rule on the no-intervention run only. The random arm shown is the policy seed whose attack rate is
the median of the three random arms, so the animation does not pick the most favourable comparison. One block
illustrates the mechanism; it is not evidence for the hypotheses.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]  # src/: the turtlefarm package; root: utils/

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from turtlefarm import SimulationConfig
from turtlefarm.model import run_baseline

DESIGN = ROOT / "experiments" / "config" / "formal-nested.json"
SELECTION = ROOT / "results" / "analysis" / "formal-nested" / "fig7-selection.json"
OUT_DIR = ROOT / "results" / "demo"

FPS = 10
W, H, DPI = 12.8, 7.2, 100  # 1280 x 720

INK, MUTED, GRID = "#1f2328", "#59636e", "#d0d7de"
NEVER, CLEARED, QUAR = "#eef1f4", "#e8d9b5", "#1f6feb"
ARM_COLOURS = {"none": "#6e7781", "betweenness": "#1f6feb", "random": "#bf8700"}
INFECTED = LinearSegmentedColormap.from_list("inf", ["#ffd8d3", "#cf222e"])

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK, "axes.edgecolor": GRID})


def run_block() -> tuple[list[tuple[str, str, object]], dict]:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    sel = json.loads(SELECTION.read_text(encoding="utf-8"))["cross_region"]
    fixed = design["fixed"]
    common = dict(fixed, design="main", label=design["name"], network_seed=sel["network_seed"],
                  epidemic_seed=sel["epidemic_seed"], transfer_rate=sel["config"]["transfer_rate"])
    delay = max(design["response_delays"])
    none = run_baseline(SimulationConfig(**{**common, "strategy": "none", "quarantine_duration": 0}))
    targeted = run_baseline(SimulationConfig(**common, strategy="betweenness", response_delay=delay))
    randoms = [run_baseline(SimulationConfig(**common, strategy="random", response_delay=delay, policy_seed=s))
               for s in design["policy_seeds"]]
    median_random = sorted(randoms, key=lambda r: r.metrics["final_attack_rate"])[len(randoms) // 2]
    arms = [("none", "No quarantine", none),
            ("betweenness", "Targeted (highest betweenness)", targeted),
            ("random", "Random tanks", median_random)]
    info = dict(delay=delay, duration=fixed["quarantine_duration"], rate=common["transfer_rate"],
                network=none.network, policy_seed=median_random.config["policy_seed"])
    return arms, info


def tank_colour(row: dict, ever: bool) -> object:
    if row["I"] > 0:
        return INFECTED(min(1.0, row["I"] / max(1, row["occupancy"])) ** 0.5)
    return CLEARED if ever else NEVER


def anim_frame(arms, info, pos, day: int, last_day: int) -> plt.Figure:
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor="white")
    grid = fig.add_gridspec(2, 3, height_ratios=[3.1, 1], left=0.06, right=0.97, top=0.83, bottom=0.08,
                            hspace=0.18, wspace=0.04)
    start, end = info["delay"], info["delay"] + info["duration"]
    active = start <= day < end
    status = (f"Day {day}" + (f"   ·   quarantine active (days {start}-{end - 1})" if active else
                              f"   ·   quarantine starts on day {start}" if day < start else ""))
    fig.text(0.03, 0.93, status, fontsize=22, weight="bold", color=QUAR if active else INK)
    fig.text(0.03, 0.885, f"Same network and same random draws in all three; transfer rate {info['rate']}",
             fontsize=13, color=MUTED)
    edges = info["network"]["edges"]
    for col, (key, label, rec) in enumerate(arms):
        ax = fig.add_subplot(grid[0, col])
        ax.set_axis_off()
        d = rec.daily[min(day, len(rec.daily) - 1)]
        ever = {t for dd in rec.daily[: min(day, len(rec.daily) - 1) + 1] for t, row in enumerate(dd.tanks) if row["I"] > 0}
        for a, b in edges:
            ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=GRID, lw=1, zorder=1)
        for t, row in enumerate(d.tanks):
            quarantined = row["management_state"] != "open"
            ax.scatter(*pos[t], s=60 + 45 * row["occupancy"], color=tank_colour(row, t in ever), zorder=3,
                       edgecolors=QUAR if quarantined else "#8c959f", linewidths=4 if quarantined else 0.8,
                       marker="s" if quarantined else "o")
        ar = (d.I + d.R) / (d.S + d.I + d.R)
        ax.set_title(label, fontsize=16, color=ARM_COLOURS[key], weight="bold", pad=4)
        ax.text(0.5, -0.04, f"ever infected {ar:.0%}   ·   tanks hit {len(ever)}", transform=ax.transAxes,
                ha="center", fontsize=13, color=INK)
        ax.set_aspect("equal")
    curve = fig.add_subplot(grid[1, :])
    curve.axvspan(start, end, color=QUAR, alpha=0.08, lw=0)
    for key, label, rec in arms:
        xs = [dd.day for dd in rec.daily if dd.day <= day]
        ys = [dd.I for dd in rec.daily if dd.day <= day]
        style = dict(ls=(0, (4, 2)), lw=2.2, zorder=4) if key == "none" else dict(lw=2.6, zorder=3)
        curve.plot(xs, ys, color=ARM_COLOURS[key], label=label, **style)
    curve.set_xlim(0, last_day)
    curve.set_ylim(0, max(dd.I for _, _, r in arms for dd in r.daily) * 1.1)
    curve.set_ylabel("infectious turtles", fontsize=11, color=MUTED)
    curve.tick_params(colors=MUTED, labelsize=10)
    for side in ("top", "right"):
        curve.spines[side].set_visible(False)
    curve.legend(loc="upper right", frameon=False, fontsize=11)
    return fig


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
