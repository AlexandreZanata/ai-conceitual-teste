"""Measure P01 ground-truth gate metrics into a committed summary JSON.

CLI:
  python3 bench/p01_measure.py --out results/p01/summary.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_LEGACY = (
    "nano_lm",
    "docs/results/nano-lm",
    "agent-rules",
    "agent-harness",
    "legacy",
)


def git_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_capture(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def count_npm_scripts() -> int:
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    return len(pkg["scripts"])


def count_tracked_files() -> int:
    out = run_capture(["git", "ls-files"])
    return len([line for line in out.stdout.splitlines() if line.strip()])


def count_active_python() -> int:
    files = list((ROOT / "n32").rglob("*.py")) + list((ROOT / "bench").rglob("*.py"))
    return len([p for p in files if "__pycache__" not in p.parts])


def count_training_entrypoints() -> int:
    train_dir = ROOT / "n32" / "train"
    modules = [
        p
        for p in train_dir.glob("*.py")
        if p.name != "__init__.py" and not p.name.startswith("test_")
    ]
    return len(modules)


def legacy_tag_exists() -> bool:
    out = run_capture(["git", "rev-parse", "--verify", "refs/tags/legacy/waves-w-bh"])
    return out.returncode == 0


def legacy_files_in_tree() -> int:
    return sum(1 for rel in FORBIDDEN_LEGACY if (ROOT / rel).exists())


def count_n32_contract_tests() -> int:
    out = run_capture(
        [
            "python3",
            "-m",
            "pytest",
            "n32",
            "--collect-only",
            "-q",
            "--disable-warnings",
        ]
    )
    collected = [line for line in out.stdout.splitlines() if "::" in line]
    if collected:
        return len(collected)
    for line in out.stdout.splitlines():
        token = line.strip().split(" ", 1)[0]
        if token.isdigit() and "collected" in line:
            return int(token)
    return 0


def verify_green() -> tuple[bool, int, float]:
    t0 = time.perf_counter()
    out = run_capture(["npm", "run", "verify"])
    elapsed = time.perf_counter() - t0
    return out.returncode == 0, out.returncode, elapsed


def measure() -> dict:
    wall0 = time.perf_counter()
    npm_scripts = count_npm_scripts()
    tracked = count_tracked_files()
    active_py = count_active_python()
    train_eps = count_training_entrypoints()
    tag_ok = legacy_tag_exists()
    legacy_n = legacy_files_in_tree()
    contract_n = count_n32_contract_tests()
    ok, verify_code, verify_s = verify_green()
    wall = time.perf_counter() - wall0

    gates = {
        "npm_scripts": {
            "threshold": "<=40",
            "measured": npm_scripts,
            "pass": npm_scripts <= 40,
        },
        "tracked_files": {
            "threshold": "<=400",
            "measured": tracked,
            "pass": tracked <= 400,
        },
        "active_python_files": {
            "threshold": "<=80",
            "measured": active_py,
            "pass": active_py <= 80,
        },
        "training_entrypoints": {
            "threshold": "==1",
            "measured": train_eps,
            "pass": train_eps == 1,
        },
        "legacy_tag_exists": {
            "threshold": "exists",
            "measured": tag_ok,
            "pass": tag_ok,
        },
        "legacy_files_in_working_tree": {
            "threshold": "==0",
            "measured": legacy_n,
            "pass": legacy_n == 0,
        },
        "npm_run_verify": {
            "threshold": "green",
            "measured": verify_code,
            "pass": ok,
            "wall_seconds": round(verify_s, 3),
        },
        "contract_tests_that_can_fail": {
            "threshold": ">=1",
            "measured": contract_n,
            "pass": contract_n >= 1,
        },
    }
    config = {
        "forbidden_legacy": list(FORBIDDEN_LEGACY),
        "train_module": "n32.train.loop",
    }
    return {
        "stage": "P01",
        "git_hash": git_hash(),
        "config_hash": hashlib.sha256(
            json.dumps(config, sort_keys=True).encode()
        ).hexdigest()[:16],
        "seed": 0,
        "wall_seconds": round(wall, 3),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "held_out_bpb": None,
        "embedding_params": None,
        "non_embedding_params": None,
        "retrieval_score": None,
        "generation_score": None,
        "latency_p50_ms": None,
        "latency_p99_ms": None,
        "gates": gates,
        "gate_pass": all(g["pass"] for g in gates.values()),
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure P01 ground-truth gates")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = measure()
    write_json(args.out, summary)
    print(
        json.dumps(
            {
                "out": str(args.out),
                "gate_pass": summary["gate_pass"],
                "gates": {
                    k: {"measured": v["measured"], "pass": v["pass"]}
                    for k, v in summary["gates"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
