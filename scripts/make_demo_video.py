"""Render the 3-minute Week 12 demo video (MP4 and GIF) covering the whole project.

Eight sections: question, model, verification, parameter selection, experiment design, one example, results,
limits and reproduction. Terminal output, tables and figures are produced from the repository when the video
is rendered (pytest, demo_final.py, results/pilot, results/analysis), not typed in by hand. The example
section uses the animation in scripts/demo_animation.py. The video is silent and is presented live; the
presentation script is in docs/demo-video.md.

Usage:
    python scripts/make_demo_video.py           # writes results/demo/demo-3min.mp4 and demo-3min.gif
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from analyse_results import _network_layout
from demo_animation import ARM_COLOURS, DPI, FPS, GRID, H, INK, MUTED, OUT_DIR, QUAR, W, anim_frame, run_block, save

PY = sys.executable
FIGS = ROOT / "results" / "analysis" / "formal-nested"
SECTIONS = [  # (title, seconds)
    ("Question", 15), ("Model", 30), ("Verification", 20), ("Parameter selection", 25),
    ("Experiment design", 20), ("One example", 30), ("Results", 30), ("Limits and reproduction", 10),
]
MONO = "DejaVu Sans Mono"


def chrome(fig: plt.Figure, section: int, header: bool = True) -> None:
    """Section label at the top and an 8-part progress bar at the bottom."""
    if header:
        fig.text(0.04, 0.93, SECTIONS[section][0], fontsize=30, weight="bold", color=INK)
        fig.text(0.96, 0.94, f"{section + 1} / {len(SECTIONS)}", ha="right", fontsize=16, color=MUTED)
    total = sum(s for _, s in SECTIONS)
    x = 0.04
    for i, (_, secs) in enumerate(SECTIONS):
        width = 0.92 * secs / total
        fig.patches.append(plt.Rectangle((x + 0.002, 0.012), width - 0.004, 0.008, transform=fig.transFigure,
                                         color=QUAR if i == section else GRID, alpha=1 if i <= section else 0.6))
        x += width


def blank(section: int, header: bool = True) -> plt.Figure:
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor="white")
    chrome(fig, section, header)
    return fig


def bullets(fig: plt.Figure, items: list[str], x: float, y: float, size: int = 19, step: float = 0.075) -> None:
    for i, item in enumerate(items):
        fig.text(x, y - i * step, "•  " + item, fontsize=size, color=INK, va="top")


def image(fig: plt.Figure, path: Path, box: tuple[float, float, float, float]) -> None:
    ax = fig.add_axes(box)
    ax.imshow(mpimg.imread(path))
    ax.set_axis_off()


def terminal(fig: plt.Figure, box: tuple[float, float, float, float], lines: list[str], size: int = 11) -> None:
    x, y, w, h = box
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.01",
                                      transform=fig.transFigure, facecolor="#0d1117", edgecolor="none"))
    for i, line in enumerate(lines):
        colour = "#7ee787" if line.startswith("$") else "#e6edf3"
        fig.text(x + 0.012, y + h - 0.03 - i * size * 0.0023, line, fontsize=size, family=MONO, color=colour,
                 va="top")


# ----------------------------------------------------------------------------------------------- sections


def s_question() -> plt.Figure:
    fig = blank(0, header=False)
    fig.text(0.5, 0.64, "Bridge transfers and quarantine", ha="center", fontsize=42, weight="bold")
    fig.text(0.5, 0.53, "in a captive turtle farm", ha="center", fontsize=26, color=MUTED)
    fig.text(0.5, 0.36, "Transfers between tanks can carry an outbreak into other regions.", ha="center", fontsize=21)
    fig.text(0.5, 0.29, "With a budget of 2 tanks for 14 days, which tanks should be quarantined, and when?",
             ha="center", fontsize=21, color=QUAR)
    fig.text(0.5, 0.12, "CITS4403 research project", ha="center", fontsize=15, color=MUTED)
    return fig


def s_model() -> plt.Figure:
    fig = blank(1)
    image(fig, ROOT / "docs" / "figures" / "concept-diagram.png", (0.03, 0.08, 0.94, 0.80))
    return fig


def s_verification(pytest_tail: str, demo_lines: list[str]) -> plt.Figure:
    fig = blank(2)
    bullets(fig, ["Invariants checked every day: 200 turtles, no tank over capacity, S + I + R = 200",
                  "Extreme cases (no movement, no infection, full tanks) and a hand-traced 3-tank example",
                  "Event-keyed random draws: every strategy sees the same outbreak until quarantine starts"],
            0.04, 0.86, size=17, step=0.06)
    terminal(fig, (0.04, 0.20, 0.92, 0.40), ["$ python -m pytest -q", pytest_tail, "",
                                            "$ python scripts/demo_final.py", *demo_lines], size=10)
    return fig


def s_pilot(stage2: pd.DataFrame, fixed: dict, delays: list[int], rates: list[float]) -> plt.Figure:
    fig = blank(3)
    bullets(fig, [f"Stage 1: beta = {fixed['beta']}, gamma = {fixed['gamma']}; "
                  f"transfer rates {' / '.join(f'{r:g}' for r in rates)}",
                  f"Response delays {' / '.join(map(str, delays))} days: immediate, first spread to a 2nd tank, "
                  "median peak",
                  "Stage 2 chose the duration D with three pre-set criteria Q1-Q3"], 0.04, 0.86, size=17, step=0.06)
    ax = fig.add_axes((0.08, 0.17, 0.84, 0.44))
    ax.set_axis_off()
    head = ["D (days)", "Q1: quarantine block\nin ≥ 90% of runs", "Q2: D ≤ 25% of\noutbreak length",
            "Q3: D ≥ infectious\nperiod (10 d)", "Selected"]
    rows = [[str(r.quarantine_duration), f"{r.share_quarantine_block_ge_1_started:.1%}",
             "pass" if r.Q2_D_le_25pct_extinction else "fail", "pass" if r.Q3_D_ge_infectious_period else "fail",
             "yes" if str(r.passed) == "True" else ""] for r in stage2.itertuples()]
    table = ax.table(cellText=rows, colLabels=head, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(15)
    table.scale(1, 3.2)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_text_props(weight="bold", fontsize=13)
        text = cell.get_text().get_text()
        if text == "fail":
            cell.get_text().set_color("#cf222e")
        if r > 0 and rows[r - 1][4] == "yes":
            cell.set_facecolor("#ddf4ff")
    fig.text(0.04, 0.10, "Q1 first counted capacity blocks too. We pre-registered quarantine-only counters, reran the",
             fontsize=15, color=MUTED)
    fig.text(0.04, 0.06, "pilot (every earlier output identical), and D = 14 passed all three.", fontsize=15,
             color=MUTED)
    return fig


def s_design(design: dict) -> plt.Figure:
    fig = blank(4)
    n_net, n_epi = len(design["network_seeds"]), len(design["epidemic_seeds"]) // len(design["network_seeds"])
    rates, delays, policy = design["transfer_rates"], design["response_delays"], design["policy_seeds"]
    per_block = 1 + len(delays) * (1 + len(policy))
    total = n_net * n_epi * len(rates) * per_block
    ax = fig.add_axes((0.04, 0.10, 0.92, 0.74))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.set_axis_off()

    def box(x, y, w, h, text, colour=INK, face="#f6f8fa", size=15):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", facecolor=face,
                                    edgecolor=colour, lw=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=colour)

    box(2, 40, 26, 14, f"{n_net} networks\n× {n_epi} outbreak seeds\nnested in each", size=16)
    ax.annotate("", (33, 47), (29, 47), arrowprops=dict(arrowstyle="->", lw=2, color=MUTED))
    box(34, 40, 26, 14, f"{n_net * n_epi} paired blocks\nper transfer rate\n({len(rates)} rates)", size=16)
    ax.annotate("", (65, 47), (61, 47), arrowprops=dict(arrowstyle="->", lw=2, color=MUTED))
    box(66, 40, 32, 14, f"each block: {per_block} runs\n1 no quarantine + for each delay\n1 targeted + "
        f"{len(policy)} random", size=15)
    box(2, 18, 46, 14, "Same seeds in every arm → compare\ntargeted − random within a block", colour=QUAR,
        face="#ddf4ff", size=16)
    box(52, 18, 46, 14, "95% CIs: bootstrap that resamples\nwhole networks, not single runs", colour=QUAR,
        face="#ddf4ff", size=16)
    ax.text(50, 6, f"{total:,} runs.  A first run shared 5 seeds across all networks (too-narrow CIs); "
            "we reran with nested seeds and report that.", ha="center", fontsize=14, color=MUTED)
    return fig


def s_results(path: Path, title: str, lines: list[str]) -> plt.Figure:
    fig = blank(6)
    fig.text(0.04, 0.855, title, fontsize=19, color=QUAR, weight="bold")
    image(fig, path, (0.03, 0.27, 0.94, 0.56))
    bullets(fig, lines, 0.05, 0.22, size=18, step=0.065)
    return fig


def s_close() -> plt.Figure:
    fig = blank(7)
    bullets(fig, ["Synthetic system: not calibrated to a real pathogen or farm",
                  "One budget (2 tanks × 14 days), one disease regime; sensitivity runs not done",
                  "Q1 was measured after the formal run; one denominator choice was post hoc"],
            0.04, 0.84, size=19, step=0.07)
    terminal(fig, (0.04, 0.12, 0.92, 0.30), [
        "$ python scripts/run_experiment.py experiments/config/formal-nested.json",
        "$ python scripts/analyse_results.py formal-nested",
        "$ python scripts/build_report.py",
        "",
        "  every table, figure and report number is regenerated from the seeds",
        "  notebooks/project-walkthrough.ipynb walks through the model and results"], size=14)
    return fig


# ----------------------------------------------------------------------------------------------- render


def capture(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False).stdout


def report_numbers() -> dict[str, str]:
    """Headline numbers read from the generated report, so the video cannot drift from it."""
    text = (ROOT / "report" / "report.md").read_text(encoding="utf-8")
    found = {
        "mult": re.search(r"multiplies the attack rate by (\d+(?:\.\d+)?)", text),
        "tanks": re.search(r"number of affected tanks by (\d+(?:\.\d+)?)", text),
        "max_reduction": re.search(r"reduces the attack rate by at most ([\d.]+%)", text),
        "ci": re.search(r"(\d+) have a 95% CI that excludes 0", text),
    }
    missing = [k for k, m in found.items() if m is None]
    if missing:
        raise SystemExit(f"report/report.md no longer states: {missing}")
    return {k: m.group(1) for k, m in found.items()}


def main() -> int:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required")
    design = json.loads((ROOT / "experiments" / "config" / "formal-nested.json").read_text(encoding="utf-8"))
    stage2 = pd.read_csv(ROOT / "results" / "pilot" / "stage2-criteria.csv")
    nums = report_numbers()
    pytest_tail = capture([PY, "-m", "pytest", "-q"]).strip().splitlines()[-1]
    demo = capture([PY, "scripts/demo_final.py"]).rstrip().splitlines()
    demo_lines = [line for line in demo if line.strip()][2:9] + [demo[-1]]

    arms, info = run_block()
    pos = _network_layout(info["network"]["edges"], info["network"]["regions"])
    last_day = max(len(r.daily) - 1 for _, _, r in arms)

    slides = {
        0: s_question(),
        1: s_model(),
        2: s_verification(pytest_tail, demo_lines),
        3: s_pilot(stage2, design["fixed"], design["response_delays"], design["transfer_rates"]),
        4: s_design(design),
        7: s_close(),
    }
    results = [
        s_results(FIGS / "fig2-attack-rate.png", "Transfer rate decides how far an outbreak spreads",
                  [f"Transfer rate 0.01 → 0.025: attack rate × {nums['mult']}, affected tanks × {nums['tanks']}",
                   f"Quarantine of 2 tanks for 14 days reduces the attack rate by at most {nums['max_reduction']}"]),
        s_results(FIGS / "fig4-paired-effects.png", "Targeted vs random: no consistent advantage",
                  [f"Only {nums['ci']} of 18 targeted − random intervals exclude 0 (both at rate 0.025, delay 33)",
                   "In this model, transfers matter far more than which tanks are closed"]),
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        frames = Path(tmp)
        i = 0

        def hold(fig: plt.Figure, seconds: float) -> None:
            nonlocal i
            still = frames / f"still{i}.png"
            save(fig, still)
            for _ in range(round(seconds * FPS)):
                shutil.copy(still, frames / f"f{i:05d}.png")
                i += 1

        for section, (_, seconds) in enumerate(SECTIONS):
            if section in slides:
                hold(slides[section], seconds)
            elif section == 5:
                n = seconds * FPS
                for k in range(n):
                    fig = anim_frame(arms, info, pos, round(k * last_day / (n - 1)), last_day)
                    chrome(fig, 5, header=False)
                    save(fig, frames / f"f{i:05d}.png")
                    i += 1
            else:
                for fig in results:
                    hold(fig, seconds / len(results))

        mp4, gif = OUT_DIR / "demo-3min.mp4", OUT_DIR / "demo-3min.gif"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", str(mp4)],
                       check=True)
        palette, scale = frames / "palette.png", "fps=8,scale=960:-1:flags=lanczos"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"{scale},palettegen",
                        str(palette)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", str(palette), "-lavfi",
                        f"{scale}[x];[x][1:v]paletteuse", str(gif)], check=True)
    print(f"{i / FPS:.0f} s; wrote {mp4.relative_to(ROOT)} and {gif.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
