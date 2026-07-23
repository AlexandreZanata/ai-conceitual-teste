"""Single-line progress + end-of-run summary (no log spam)."""

from __future__ import annotations

import sys
from typing import Any

from aggregate import summarize
from charts import labeled_bar, mem_bar, sparkline
from gpu_stats import GpuSnapshot

_last_len = 0


def progress_bar(done: int, total: int, width: int = 24) -> str:
    if total <= 0:
        return "[" + ("-" * width) + "] 0/0"
    filled = int(width * done / total)
    bar = "#" * filled + "-" * (width - filled)
    pct = 100.0 * done / total
    return f"[{bar}] {done}/{total} ({pct:.0f}%)"


def _eta_s(done: int, total: int, elapsed_s: float) -> str:
    if done <= 0:
        return "ETA --"
    remain = (elapsed_s / done) * (total - done)
    return f"ETA {remain:.0f}s" if remain < 60 else f"ETA {remain / 60:.1f}m"


def status_line(
    *,
    done: int,
    total: int,
    elapsed_s: float,
    current: str,
    gpu: GpuSnapshot,
) -> str:
    util = f"{gpu.util_pct:.0f}%" if gpu.util_pct is not None else "--"
    if gpu.mem_used_mib is not None and gpu.mem_total_mib:
        vram = f"{gpu.mem_used_mib:.0f}/{gpu.mem_total_mib:.0f}MiB"
    else:
        vram = "--"
    cur = current.replace("|", "/").strip()
    if len(cur) > 28:
        cur = cur[:25] + "…"
    return (
        f"Lab {progress_bar(done, total)} {_eta_s(done, total, elapsed_s)} | "
        f"{cur} | GPU {util} VRAM {vram}"
    )


def write_status(line: str) -> None:
    """Overwrite a single terminal line in place (no scrolling logs)."""
    global _last_len
    pad = max(0, _last_len - len(line))
    sys.stdout.write("\r" + line + (" " * pad))
    sys.stdout.flush()
    _last_len = len(line)


def end_status() -> None:
    """Move to next line after the in-place status bar."""
    global _last_len
    sys.stdout.write("\n")
    sys.stdout.flush()
    _last_len = 0


def _cmp_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "vs base model decode (AR) — higher mean_logprob is better",
        f"{'method':<8} {'mean_lp':>10} {'Δ_AR':>8} {'wall_ms':>10} "
        f"{'tok_eval':>10} {'vs_AR':>8} {'n':>4}",
        "-" * 64,
    ]
    if not rows:
        lines.append("(no completed runs)")
        return lines
    summary = summarize(rows)
    ar_lp = next((s["mean_logprob"] for s in summary if s["method"] == "ar"), None)
    for s in summary:
        wr = s["win_rate_vs_ar"]
        wr_s = "BASE" if s["method"] == "ar" else f"{wr * 100:.0f}%"
        delta = (
            0.0
            if ar_lp is None or s["method"] == "ar"
            else s["mean_logprob"] - ar_lp
        )
        lines.append(
            f"{s['method']:<8} {s['mean_logprob']:>10.4f} {delta:>+8.4f} "
            f"{s['mean_wall_ms']:>10.0f} {s['mean_token_evals']:>10.0f} "
            f"{wr_s:>8} {s['n']:>4}"
        )
    return lines


def render_summary(
    *,
    model_id: str,
    device: str,
    gpu: GpuSnapshot,
    hist: list[GpuSnapshot],
    cpu_cores: list[float],
    rows: list[dict[str, Any]],
) -> str:
    utils = [h.util_pct or 0.0 for h in hist]
    mems = [
        100.0 * h.mem_used_mib / h.mem_total_mib
        for h in hist
        if h.mem_used_mib and h.mem_total_mib
    ]
    power_pct = None
    if gpu.power_w is not None and gpu.power_limit_w:
        power_pct = 100.0 * gpu.power_w / gpu.power_limit_w
    cpu_avg = sum(cpu_cores) / len(cpu_cores) if cpu_cores else None
    parts = [
        f"Model: {model_id} | Device: {device}",
        labeled_bar("SM util", gpu.util_pct),
        labeled_bar("Mem ctrl", gpu.mem_util_pct),
        mem_bar(gpu.mem_used_mib, gpu.mem_total_mib),
        labeled_bar("Power", power_pct),
        labeled_bar("CPU avg", cpu_avg),
        f"util hist: {sparkline(utils)}" if utils else "util hist: (n/a)",
        f"VRAM hist: {sparkline(mems)}" if mems else "VRAM hist: (n/a)",
        "",
        *_cmp_table(rows),
    ]
    return "\n".join(parts)
