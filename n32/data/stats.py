"""Publish corpus statistics and P02 gate summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from n32.data.dedup import exact_dup_rate_in_output, sample_near_dup_rate
from n32.data.io_utils import iter_jsonl, write_json
from n32.data.sources import REJECTED, SOURCES, assert_all_licences_known
from n32.data.tokenize import count_bin_tokens, recount_train_tokens

ROOT = Path(__file__).resolve().parents[2]


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


def bytes_per_token(dedup_path: Path, train_tokens: int) -> float:
    total_bytes = 0
    for row in iter_jsonl(dedup_path):
        total_bytes += int(row.get("bytes") or len(row["text"].encode("utf-8")))
    if train_tokens <= 0:
        return 0.0
    return total_bytes / train_tokens


def verify_manifest_reproducible(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        return {"match_rate": 0.0, "checked": 0}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checked = 0
    matched = 0
    for row in manifest.get("sources", []):
        path = Path(row["path"])
        if not path.exists():
            checked += 1
            continue
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8 << 20), b""):
                h.update(chunk)
        checked += 1
        if h.hexdigest() == row["sha256"]:
            matched += 1
    rate = matched / checked if checked else 0.0
    return {"match_rate": rate, "checked": checked, "matched": matched}


def build_summary(
    tokens_dir: Path,
    dedup_path: Path,
    manifest_path: Path,
    clean_report: dict,
    dedup_report: dict,
    tokenize_report: dict,
    wall_seconds: float,
) -> dict:
    assert_all_licences_known()
    train_tokens = recount_train_tokens(tokens_dir)
    heldout = (
        count_bin_tokens(tokens_dir / "heldout.bin")
        if (tokens_dir / "heldout.bin").exists()
        else 0
    )
    exact_rate = float(dedup_report.get("exact_duplicate_rate_in_output", 1.0))
    near_rate = float(
        dedup_report.get("near_duplicate_rate_jaccard_gt_0_8_sample", 1.0)
    )
    unknown_licence = 0
    contam_removed = int(clean_report.get("contamination_removed", 0))
    kept = int(clean_report.get("kept", 0))
    contam_rate = contam_removed / max(kept + contam_removed, 1)
    overlap = int(tokenize_report.get("doc_overlap", 1))
    repro = verify_manifest_reproducible(manifest_path)
    total_tokens = train_tokens + heldout

    gates = {
        "total_tokens_after_dedup": {
            "threshold": ">=4.0e9",
            "measured": total_tokens,
            "pass": total_tokens >= 4_000_000_000,
        },
        "exact_duplicate_rate_in_output": {
            "threshold": "<0.001",
            "measured": exact_rate,
            "pass": exact_rate < 0.001,
        },
        "near_duplicate_rate_sample": {
            "threshold": "<0.02",
            "measured": near_rate,
            "pass": near_rate < 0.02,
        },
        "unknown_licence_sources": {
            "threshold": "==0",
            "measured": unknown_licence,
            "pass": unknown_licence == 0,
        },
        "contamination_13gram_rate": {
            "threshold": "<0.0001",
            "measured": contam_rate,
            "pass": contam_rate < 0.0001,
        },
        "heldout_split": {
            "threshold": ">=1e7 tokens, zero doc overlap",
            "measured": {"tokens": heldout, "doc_overlap": overlap},
            "pass": heldout >= 10_000_000 and overlap == 0,
        },
        "manifest_reproducibility": {
            "threshold": "100% sha256 match",
            "measured": repro,
            "pass": repro["checked"] > 0 and repro["match_rate"] == 1.0,
        },
    }
    config = {
        "sources": [s.id for s in SOURCES],
        "rejected": [r["source"] for r in REJECTED],
    }
    manifest_files: list[dict] = []
    manifest_rejected: list = []
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_rejected = list(manifest.get("rejected", []))
        for row in manifest.get("sources", []):
            manifest_files.append(
                {
                    "source_id": row.get("source_id"),
                    "name": row.get("name"),
                    "sha256": row.get("sha256"),
                    "bytes": row.get("bytes"),
                    "licence": row.get("licence"),
                }
            )
    return {
        "stage": "P02",
        "git_hash": git_hash(),
        "config_hash": hashlib.sha256(
            json.dumps(config, sort_keys=True).encode()
        ).hexdigest()[:16],
        "seed": 0,
        "wall_seconds": round(wall_seconds, 3),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "held_out_bpb": None,
        "embedding_params": None,
        "non_embedding_params": None,
        "retrieval_score": None,
        "generation_score": None,
        "train_tokens": train_tokens,
        "heldout_tokens": heldout,
        "total_tokens": total_tokens,
        "bytes_per_token_approx": bytes_per_token(dedup_path, max(total_tokens, 1))
        if dedup_path.exists()
        else None,
        "clean_report": clean_report,
        "dedup_report": dedup_report,
        "tokenize_report": tokenize_report,
        "manifest_files": manifest_files,
        "manifest_rejected": manifest_rejected,
        "gates": gates,
        "gate_pass": all(g["pass"] for g in gates.values()),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute N32 corpus statistics")
    p.add_argument("--tokens", type=Path, default=ROOT / "data" / "tokens")
    p.add_argument(
        "--dedup", type=Path, default=ROOT / "data" / "dedup" / "corpus.jsonl"
    )
    p.add_argument("--manifest", type=Path, default=ROOT / "data" / "manifest.json")
    p.add_argument("--clean-report", type=Path, required=True)
    p.add_argument("--dedup-report", type=Path, required=True)
    p.add_argument("--tokenize-report", type=Path, required=True)
    p.add_argument("--wall-seconds", type=float, default=0.0)
    p.add_argument(
        "--out", type=Path, default=ROOT / "results" / "data" / "corpus_stats.json"
    )
    p.add_argument(
        "--summary", type=Path, default=ROOT / "results" / "data" / "summary.json"
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    clean_report = json.loads(args.clean_report.read_text(encoding="utf-8"))
    dedup_report = json.loads(args.dedup_report.read_text(encoding="utf-8"))
    tokenize_report = json.loads(args.tokenize_report.read_text(encoding="utf-8"))
    # Refresh residual rates from on-disk dedup output when available.
    if args.dedup.exists():
        dedup_report["exact_duplicate_rate_in_output"] = exact_dup_rate_in_output(
            args.dedup
        )
        dedup_report["near_duplicate_rate_jaccard_gt_0_8_sample"] = (
            sample_near_dup_rate(args.dedup, sample_size=100_000)
        )
    summary = build_summary(
        args.tokens,
        args.dedup,
        args.manifest,
        clean_report,
        dedup_report,
        tokenize_report,
        args.wall_seconds,
    )
    write_json(args.out, summary)
    write_json(args.summary, summary)
    print(
        json.dumps(
            {
                "gate_pass": summary["gate_pass"],
                "total_tokens": summary["total_tokens"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
