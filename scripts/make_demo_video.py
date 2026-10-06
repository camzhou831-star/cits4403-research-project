"""Render the 30-second Week 12 demo video (MP4 and GIF) from one paired block of `formal-nested`.

The block is the same one `scripts/demo_final.py` reruns: the representative cross-region outbreak of figure 7,
picked by a rule on the no-intervention run only. The random arm shown is the policy seed whose attack rate is
the median of the three random arms, so the clip does not pick the most favourable comparison. One block
illustrates the mechanism; the closing card states the formal results from the report.

Usage:
    python scripts/make_demo_video.py            # writes results/demo/demo-30s.mp4 and demo-30s.gif
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from analyse_results import _network_layout
from turtlefarm import SimulationConfig
from turtlefarm.model import run_baseline

DESIGN = ROOT / "experiments" / "config" / "formal-nested.json"
SELECTION = ROOT / "results" / "analysis" / "formal-nested" / "fig7-selection.json"
OUT_DIR = ROOT / "results" / "demo"

FPS = 10
TITLE_S, END_S, ANIM_S = 3, 7, 20
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


def title_frame(info: dict) -> plt.Figure:
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor="white")
    fig.text(0.5, 0.60, "Bridge transfers and quarantine", ha="center", fontsize=40, weight="bold")
    fig.text(0.5, 0.48, "200 turtles in 20 tanks, 4 regions.  Transfers move infection between tanks.",
             ha="center", fontsize=20, color=MUTED)
    fig.text(0.5, 0.40, f"Quarantine budget: 2 tanks for {info['duration']} days.  Which 2 tanks should we close?",
             ha="center", fontsize=20, color=MUTED)
    return fig


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


def end_frame() -> plt.Figure:
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor="white")
    fig.text(0.07, 0.83, "That was one block.  Over 100 blocks per condition:", fontsize=28, weight="bold")
    lines = [
        ("Transfer rate 0.01 → 0.025", "attack rate × 3.3, affected tanks × 3.4"),
        ("Quarantine, 2 tanks × 14 days", "reduces attack rate by at most 10.6%"),
        ("Targeted vs random", "no consistent advantage: 2 of 18 comparisons exclude 0"),
    ]
    for i, (head, body) in enumerate(lines):
        y = 0.64 - i * 0.15
        fig.text(0.07, y, head, fontsize=22, weight="bold", color=QUAR)
        fig.text(0.07, y - 0.06, body, fontsize=20, color=INK)
    fig.text(0.07, 0.10, "In this model, transfers matter far more than which tanks are closed, at this budget.", fontsize=20,
             color=MUTED, style="italic")
    return fig


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)


def main() -> int:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required")
    arms, info = run_block()
    net = info["network"]
    pos = _network_layout(net["edges"], net["regions"])
    last_day = max(len(r.daily) - 1 for _, _, r in arms)
    n_anim = ANIM_S * FPS
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        frames = Path(tmp)
        i = 0
        title = frames / "title.png"
        save(title_frame(info), title)
        for _ in range(TITLE_S * FPS):
            shutil.copy(title, frames / f"f{i:05d}.png"); i += 1
        for k in range(n_anim):
            day = round(k * last_day / (n_anim - 1))
            save(anim_frame(arms, info, pos, day, last_day), frames / f"f{i:05d}.png"); i += 1
        end = frames / "end.png"
        save(end_frame(), end)
        for _ in range(END_S * FPS):
            shutil.copy(end, frames / f"f{i:05d}.png"); i += 1
        mp4, gif = OUT_DIR / "demo-30s.mp4", OUT_DIR / "demo-30s.gif"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", str(mp4)],
                       check=True)
        palette = frames / "palette.png"
        scale = "fps=10,scale=960:-1:flags=lanczos"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"{scale},palettegen",
                        str(palette)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", str(palette), "-lavfi",
                        f"{scale}[x];[x][1:v]paletteuse", str(gif)], check=True)
    for key, label, rec in arms:
        print(f"{label:32s} attack rate {rec.metrics['final_attack_rate']:.3f}  "
              f"tanks {rec.metrics['affected_tanks']}  selected {rec.selected_tanks or '-'}")
    print(f"random arm shown: policy seed {info['policy_seed']} (median of the random arms)")
    print(f"wrote {mp4.relative_to(ROOT)} and {gif.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
