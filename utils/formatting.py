"""Number formatting shared by the report builder: every number in the report is printed through these."""

from __future__ import annotations


def f2(x: float) -> str:
    return f"{x:.2f}"


def f3(x: float) -> str:
    return f"{x:.3f}"


def pct(x: float, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}%"


def ci(lo: float, hi: float, fmt=f3) -> str:
    return f"[{fmt(lo)}, {fmt(hi)}]"


def rate_key(rate: float) -> str:
    return f"{rate:g}".replace(".", "p")


def excludes_zero(lo: float, hi: float) -> bool:
    return lo > 0 or hi < 0
