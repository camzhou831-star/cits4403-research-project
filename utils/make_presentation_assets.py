"""Render the original-study timing figure and the notebook's paired-example animation.

    data/results/demo/timing-window.png   first cross-region crossings relative to the quarantine window, by response
                                     delay (from data/results/analysis/formal-nested/mechanism.json)
    data/results/demo/example-block.gif   the demo_final.py block animated for no, targeted and random quarantine
                                     (utils/demo_animation.py), without the title and results cards of the video

The other original-study figures are in data/figures/concept-diagram.png and
data/results/analysis/formal-nested/ (fig1, fig2, fig4, fig7).

Usage:
    python utils/mechanism_analysis.py          # if mechanism.json is missing or stale
    python utils/make_presentation_assets.py    # about 30 s; the GIF needs ffmpeg
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]  # src/: turtlefarm; root: utils/

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from utils.demo_animation import anim_frame, run_block, save
from utils.network_layout import network_layout

MECHANISM = ROOT / "data" / "results" / "analysis" / "formal-nested" / "mechanism.json"
OUT_DIR = ROOT / "data" / "results" / "demo"
BACKGROUND = "#F6F4EF"  # the slide deck's light background
SEGMENTS = {  # key in mechanism.json -> (colour, legend label)
    "crossed_before_start": ("#9AA5B1", "already crossed when quarantine starts"),
    "crossed_during_window": ("#2E6FD8", "inside the {D}-day window"),
    "crossed_after_window": ("#E08A3C", "after the window ends"),
}
GIF_FRAMES, GIF_FPS, GIF_WIDTH = 150, 8, 1280


def timing_figure(path: Path) -> None:
    mech = json.loads(MECHANISM.read_text(encoding="utf-8"))
    duration, timing = mech["quarantine_duration"], mech["timing_by_delay"]
    fig, ax = plt.subplots(figsize=(12.5, 4.6), dpi=150)
    for row, delay in enumerate(timing):
        left = 0.0
        for key, (colour, label) in SEGMENTS.items():
            share = 100 * timing[delay][key]
            ax.barh(row, share, left=left, color=colour, height=0.62, edgecolor=BACKGROUND, linewidth=2,
                    label=label.format(D=duration) if row == 0 else None)
            if share >= 6:
                ax.text(left + share / 2, row, f"{share:.0f}%", ha="center", va="center", color="white",
                        fontsize=17, fontweight="bold")
            left += share
    ax.set_yticks(range(len(timing)))
    ax.set_yticklabels([f"respond on day {d}" for d in timing], fontsize=16)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=13)
    ax.set_xlabel(f"First crossing into a second region (runs without quarantine, transfer rate "
                  f"{mech['focus_rate']:g})", fontsize=14)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, 1.2), ncol=3, frameon=False, fontsize=12.5)
    fig.patch.set_facecolor(BACKGROUND)
    ax.set_facecolor(BACKGROUND)
    fig.tight_layout()
    fig.savefig(path, facecolor=BACKGROUND)
    plt.close(fig)


def example_gif(path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required for the GIF")
    arms, info = run_block()
    pos = network_layout(info["network"]["edges"], info["network"]["regions"])
    last_day = max(len(record.daily) - 1 for _, _, record in arms)
    with tempfile.TemporaryDirectory() as tmp:
        frames = Path(tmp)
        for k in range(GIF_FRAMES):
            day = round(k * last_day / (GIF_FRAMES - 1))
            save(anim_frame(arms, info, pos, day, last_day), frames / f"f{k:04d}.png")
        palette, scale = frames / "palette.png", f"scale={GIF_WIDTH}:-1:flags=lanczos"
        pattern = str(frames / "f%04d.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(GIF_FPS), "-i", pattern,
                        "-vf", f"{scale},palettegen=max_colors=128", str(palette)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(GIF_FPS), "-i", pattern,
                        "-i", str(palette), "-lavfi", f"{scale}[x];[x][1:v]paletteuse=dither=bayer",
                        "-loop", "0", str(path)], check=True)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    timing_figure(OUT_DIR / "timing-window.png")
    example_gif(OUT_DIR / "example-block.gif")
    for name in ("timing-window.png", "example-block.gif"):
        print(f"wrote {(OUT_DIR / name).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
