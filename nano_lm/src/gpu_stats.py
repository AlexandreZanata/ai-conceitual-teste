"""GPU + CPU telemetry for the nano_lm terminal lab."""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class GpuSnapshot:
    available: bool
    name: str
    util_pct: float | None
    mem_util_pct: float | None
    mem_used_mib: float | None
    mem_total_mib: float | None
    temp_c: float | None
    power_w: float | None
    power_limit_w: float | None
    sm_clock_mhz: float | None
    mem_clock_mhz: float | None
    torch_alloc_mib: float | None
    torch_reserved_mib: float | None
    note: str


def _f(parts: list[str], i: int) -> float | None:
    if i >= len(parts):
        return None
    raw = parts[i].strip()
    if raw in {"", "[N/A]", "N/A"}:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _nvidia_parts() -> list[str] | None:
    if not shutil.which("nvidia-smi"):
        return None
    q = (
        "name,utilization.gpu,utilization.memory,"
        "memory.used,memory.total,temperature.gpu,"
        "power.draw,power.limit,clocks.current.sm,clocks.current.memory"
    )
    cmd = ["nvidia-smi", f"--query-gpu={q}", "--format=csv,noheader,nounits"]
    try:
        out = subprocess.check_output(cmd, text=True, timeout=2.0)
    except (subprocess.SubprocessError, OSError):
        return None
    line = out.strip().splitlines()[0] if out.strip() else ""
    return [p.strip() for p in line.split(",")] if line else None


def _torch_mem() -> tuple[float | None, float | None]:
    try:
        import torch

        if not torch.cuda.is_available():
            return None, None
        alloc = torch.cuda.memory_allocated() / (1024.0 * 1024.0)
        reserved = torch.cuda.memory_reserved() / (1024.0 * 1024.0)
        return alloc, reserved
    except Exception:
        return None, None


def read_gpu() -> GpuSnapshot:
    parts = _nvidia_parts()
    alloc, reserved = _torch_mem()
    if parts is None or not parts:
        return GpuSnapshot(
            available=False,
            name="none",
            util_pct=None,
            mem_util_pct=None,
            mem_used_mib=None,
            mem_total_mib=None,
            temp_c=None,
            power_w=None,
            power_limit_w=None,
            sm_clock_mhz=None,
            mem_clock_mhz=None,
            torch_alloc_mib=alloc,
            torch_reserved_mib=reserved,
            note="CPU mode (nvidia-smi unavailable)",
        )
    return GpuSnapshot(
        available=True,
        name=parts[0],
        util_pct=_f(parts, 1),
        mem_util_pct=_f(parts, 2),
        mem_used_mib=_f(parts, 3),
        mem_total_mib=_f(parts, 4),
        temp_c=_f(parts, 5),
        power_w=_f(parts, 6),
        power_limit_w=_f(parts, 7),
        sm_clock_mhz=_f(parts, 8),
        mem_clock_mhz=_f(parts, 9),
        torch_alloc_mib=alloc,
        torch_reserved_mib=reserved,
        note="ok",
    )


def read_cpu_percents() -> list[float]:
    """Per-logical-CPU busy % via two /proc/stat samples."""
    def sample() -> list[tuple[int, int]]:
        rows = []
        with open("/proc/stat", encoding="utf-8") as f:
            for line in f:
                if not line.startswith("cpu") or line.startswith("cpu "):
                    continue
                p = line.split()
                nums = [int(x) for x in p[1:]]
                idle = nums[3] + (nums[4] if len(nums) > 4 else 0)
                total = sum(nums)
                rows.append((idle, total))
        return rows

    a = sample()
    time.sleep(0.05)
    b = sample()
    out: list[float] = []
    for (ia, ta), (ib, tb) in zip(a, b):
        dt, di = tb - ta, ib - ia
        out.append(0.0 if dt <= 0 else 100.0 * (1.0 - di / dt))
    return out


def format_gpu_line(snap: GpuSnapshot) -> str:
    if not snap.available:
        return f"GPU: {snap.note}"
    return (
        f"GPU: {snap.name} | util={snap.util_pct:.0f}% | "
        f"mem={snap.mem_used_mib:.0f}/{snap.mem_total_mib:.0f} MiB | "
        f"temp={snap.temp_c:.0f}C"
    )
