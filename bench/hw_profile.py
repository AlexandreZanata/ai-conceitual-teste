"""Measure real hardware throughput for the N32 compute budget.

CLI:
  python bench/hw_profile.py --out results/hw/profile.json --sustained-minutes 10
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

MATMUL_N = 4096
WARMUP_ITERS = 10
PEAK_ITERS = 50
COPY_BYTES = 1 << 30  # 1 GiB
DISK_BYTES = 4 << 30  # 4 GiB
VRAM_CHUNK_MB = 64
FLOPS_PER_MATMUL = 2 * (MATMUL_N**3)


def git_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def driver_version() -> str:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip().splitlines()[0]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return "unknown"


def median(xs: list[float]) -> float:
    return float(statistics.median(xs))


def tflops_from_seconds(seconds: float) -> float:
    if seconds <= 0:
        return 0.0
    return (FLOPS_PER_MATMUL / seconds) / 1e12


def sync_cuda() -> None:
    torch.cuda.synchronize()


def matmul_once(a: torch.Tensor, b: torch.Tensor) -> float:
    sync_cuda()
    t0 = time.perf_counter()
    torch.matmul(a, b)
    sync_cuda()
    return time.perf_counter() - t0


def peak_bf16_tflops(device: torch.device) -> dict:
    a = torch.randn(MATMUL_N, MATMUL_N, device=device, dtype=torch.bfloat16)
    b = torch.randn(MATMUL_N, MATMUL_N, device=device, dtype=torch.bfloat16)
    for _ in range(WARMUP_ITERS):
        matmul_once(a, b)
    times = [matmul_once(a, b) for _ in range(PEAK_ITERS)]
    med = median(times)
    del a, b
    torch.cuda.empty_cache()
    return {
        "tflops_median": tflops_from_seconds(med),
        "seconds_p50": median(times),
        "seconds_p99": float(sorted(times)[max(0, int(0.99 * (len(times) - 1)))]),
        "iters": PEAK_ITERS,
        "shape": MATMUL_N,
    }


def sustained_bf16_tflops(device: torch.device, minutes: float) -> dict:
    a = torch.randn(MATMUL_N, MATMUL_N, device=device, dtype=torch.bfloat16)
    b = torch.randn(MATMUL_N, MATMUL_N, device=device, dtype=torch.bfloat16)
    for _ in range(WARMUP_ITERS):
        matmul_once(a, b)
    deadline = time.perf_counter() + minutes * 60.0
    samples: list[tuple[float, float]] = []
    while time.perf_counter() < deadline:
        dt = matmul_once(a, b)
        samples.append((time.perf_counter(), tflops_from_seconds(dt)))
    final_cut = samples[-1][0] - 60.0 if samples else 0.0
    final_minute = [t for ts, t in samples if ts >= final_cut]
    del a, b
    torch.cuda.empty_cache()
    return {
        "tflops_final_minute_median": median(final_minute) if final_minute else 0.0,
        "tflops_overall_median": median([t for _, t in samples]) if samples else 0.0,
        "samples": len(samples),
        "minutes": minutes,
    }


def hbm_bandwidth_gbs(device: torch.device) -> dict:
    n = COPY_BYTES // 2  # bf16 = 2 bytes
    src = torch.empty(n, device=device, dtype=torch.bfloat16)
    dst = torch.empty(n, device=device, dtype=torch.bfloat16)
    sync_cuda()
    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        dst.copy_(src)
        sync_cuda()
        times.append(time.perf_counter() - t0)
    med = median(times)
    del src, dst
    torch.cuda.empty_cache()
    return {
        "gbs_median": (COPY_BYTES / med) / 1e9 if med > 0 else 0.0,
        "bytes": COPY_BYTES,
    }


def usable_vram_mb(device: torch.device) -> dict:
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)
    chunks: list[torch.Tensor] = []
    allocated = 0
    try:
        while True:
            chunks.append(
                torch.empty(
                    VRAM_CHUNK_MB * 1024 * 1024 // 2,
                    device=device,
                    dtype=torch.bfloat16,
                )
            )
            allocated += VRAM_CHUNK_MB
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
    usable = int(allocated * 0.95)
    del chunks
    torch.cuda.empty_cache()
    return {
        "allocated_until_oom_mb": allocated,
        "usable_mb": usable,
        "total_mb": int(
            torch.cuda.get_device_properties(device).total_memory / (1024 * 1024)
        ),
    }


def host_device_bandwidth_gbs(device: torch.device) -> dict:
    n = COPY_BYTES // 4  # float32 pinned
    host = torch.empty(n, pin_memory=True, dtype=torch.float32)
    times_h2d = []
    times_d2h = []
    for _ in range(5):
        sync_cuda()
        t0 = time.perf_counter()
        dev = host.to(device, non_blocking=False)
        sync_cuda()
        times_h2d.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        _ = dev.to("cpu", non_blocking=False)
        sync_cuda()
        times_d2h.append(time.perf_counter() - t0)
        del dev
    torch.cuda.empty_cache()
    h2d = median(times_h2d)
    d2h = median(times_d2h)
    return {
        "h2d_gbs_median": (COPY_BYTES / h2d) / 1e9 if h2d > 0 else 0.0,
        "d2h_gbs_median": (COPY_BYTES / d2h) / 1e9 if d2h > 0 else 0.0,
        "bytes": COPY_BYTES,
    }


def disk_sequential_read_gbs(path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write once, then measure sequential read. Truncate after.
    chunk = os.urandom(16 * 1024 * 1024)
    written = 0
    with path.open("wb") as f:
        while written < DISK_BYTES:
            f.write(chunk)
            written += len(chunk)
        f.flush()
        os.fsync(f.fileno())
    t0 = time.perf_counter()
    read = 0
    with path.open("rb") as f:
        while True:
            buf = f.read(16 * 1024 * 1024)
            if not buf:
                break
            read += len(buf)
    elapsed = time.perf_counter() - t0
    path.unlink(missing_ok=True)
    return {
        "gbs_median": (read / elapsed) / 1e9 if elapsed > 0 else 0.0,
        "bytes_read": read,
        "seconds": elapsed,
    }


def cpu_bf16_gemm_tflops(threads: int = 16) -> dict:
    torch.set_num_threads(threads)
    # CPU often lacks fast bf16 matmul; use float32 and note the dtype.
    a = torch.randn(2048, 2048, dtype=torch.float32)
    b = torch.randn(2048, 2048, dtype=torch.float32)
    flops = 2 * (2048**3)
    for _ in range(3):
        torch.matmul(a, b)
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        torch.matmul(a, b)
        times.append(time.perf_counter() - t0)
    med = median(times)
    return {
        "tflops_median": (flops / med) / 1e12 if med > 0 else 0.0,
        "dtype": "float32",
        "note": "CPU bf16 GEMM unavailable or slow; float32 used as fallback budget",
        "threads": threads,
        "shape": 2048,
    }


def relative_delta(a: float, b: float) -> float:
    if a == 0 and b == 0:
        return 0.0
    denom = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / denom


def build_profile(sustained_minutes: float, disk_path: Path) -> dict:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for P00 hardware profiling")
    device = torch.device("cuda:0")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    wall0 = time.perf_counter()
    peak1 = peak_bf16_tflops(device)
    sustained = sustained_bf16_tflops(device, sustained_minutes)
    hbm = hbm_bandwidth_gbs(device)
    vram = usable_vram_mb(device)
    host = host_device_bandwidth_gbs(device)
    disk = disk_sequential_read_gbs(disk_path)
    cpu = cpu_bf16_gemm_tflops()
    peak2 = peak_bf16_tflops(device)
    wall = time.perf_counter() - wall0
    props = torch.cuda.get_device_properties(device)
    profile = {
        "git_hash": git_hash(),
        "config_hash": hashlib.sha256(
            json.dumps(
                {"matmul_n": MATMUL_N, "sustained_minutes": sustained_minutes},
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16],
        "seed": 0,
        "wall_seconds": round(wall, 3),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "driver_version": driver_version(),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "gpu_name": props.name,
        "peak_bf16_tflops": peak1,
        "peak_bf16_tflops_rerun": peak2,
        "peak_tflops_repro_delta": relative_delta(
            peak1["tflops_median"], peak2["tflops_median"]
        ),
        "sustained_bf16_tflops": sustained,
        "hbm_bandwidth": hbm,
        "usable_vram": vram,
        "host_device_bandwidth": host,
        "disk_sequential_read": disk,
        "cpu_gemm": cpu,
        "held_out_bpb": None,
        "embedding_params": None,
        "non_embedding_params": None,
        "retrieval_score": None,
        "generation_score": None,
    }
    return profile


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="N32 hardware profiler")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--sustained-minutes", type=float, default=10.0)
    p.add_argument(
        "--disk-probe",
        type=Path,
        default=Path("data/.hw_disk_probe.bin"),
        help="Temp file on the data volume for sequential read probe",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    profile = build_profile(args.sustained_minutes, args.disk_probe)
    write_json(args.out, profile)
    print(
        json.dumps(
            {
                "out": str(args.out),
                "peak_tflops": profile["peak_bf16_tflops"]["tflops_median"],
                "sustained_tflops": profile["sustained_bf16_tflops"][
                    "tflops_final_minute_median"
                ],
                "usable_vram_mb": profile["usable_vram"]["usable_mb"],
                "repro_delta": profile["peak_tflops_repro_delta"],
                "wall_seconds": profile["wall_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
