"""ASCII/Unicode bars and sparklines for the terminal lab."""

from __future__ import annotations

_BLOCKS = " ▁▂▃▄▅▆▇█"


def pct_bar(pct: float | None, width: int = 24, fill: str = "█", empty: str = "░") -> str:
    if pct is None:
        return empty * width
    p = max(0.0, min(100.0, pct))
    n = int(round(width * p / 100.0))
    return fill * n + empty * (width - n)


def labeled_bar(label: str, pct: float | None, width: int = 24) -> str:
    p = 0.0 if pct is None else pct
    return f"{label:<10} |{pct_bar(pct, width)}| {p:5.1f}%"


def sparkline(values: list[float], width: int = 40) -> str:
    if not values:
        return "-" * min(width, 8)
    data = values[-width:]
    lo, hi = min(data), max(data)
    span = hi - lo if hi > lo else 1.0
    out = []
    for v in data:
        idx = int((v - lo) / span * (len(_BLOCKS) - 1))
        out.append(_BLOCKS[idx])
    return "".join(out)


def mem_bar(used: float | None, total: float | None, width: int = 24) -> str:
    if used is None or total is None or total <= 0:
        return labeled_bar("VRAM", None, width)
    return labeled_bar("VRAM", 100.0 * used / total, width)
