"""Contract tests for lab charts and single-line status."""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from charts import labeled_bar, pct_bar, sparkline
from gpu_stats import GpuSnapshot, format_gpu_line
from lab_display import progress_bar, status_line


def _snap() -> GpuSnapshot:
    return GpuSnapshot(
        available=True,
        name="TestGPU",
        util_pct=40.0,
        mem_util_pct=20.0,
        mem_used_mib=1000.0,
        mem_total_mib=8000.0,
        temp_c=55.0,
        power_w=40.0,
        power_limit_w=80.0,
        sm_clock_mhz=1500.0,
        mem_clock_mhz=8000.0,
        torch_alloc_mib=200.0,
        torch_reserved_mib=400.0,
        note="ok",
    )


def test_given_half_done_when_progress_bar_then_shows_fraction():
    text = progress_bar(5, 10, width=10)
    assert "5/10" in text
    assert "(50%)" in text


def test_given_status_when_build_then_single_line_no_newline():
    line = status_line(
        done=3,
        total=12,
        elapsed_s=10.0,
        current="mae/p01/s0",
        gpu=_snap(),
    )
    assert "\n" not in line
    assert "Lab [" in line
    assert "GPU 40%" in line
    assert "1000/8000MiB" in line


def test_given_pct_when_bar_then_fills_proportionally():
    assert pct_bar(50, width=10).count("█") == 5


def test_given_values_when_sparkline_then_non_empty():
    assert len(sparkline([10.0, 20.0, 5.0, 40.0])) == 4


def test_given_gpu_snapshot_when_format_then_includes_util_and_mem():
    line = format_gpu_line(_snap())
    assert "util=40%" in line
    assert "1000/8000" in line
    assert "SM util" in labeled_bar("SM util", 40.0)
