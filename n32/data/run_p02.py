"""End-to-end P02 runner: manifest → clean → dedup → tokenize → stats.

Resume-aware: skips clean when data/clean/*.jsonl already exists.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from n32.data.clean import clean_tree
from n32.data.dedup import (
    exact_dedup,
    exact_dup_rate_in_output,
    near_dedup,
    sample_near_dup_rate,
)
from n32.data.fetch import build_manifest, fetch_tech_docs_seed
from n32.data.io_utils import sha256_file, write_json
from n32.data.sources import assert_all_licences_known
from n32.data.stats import build_summary
from n32.data.tokenize import (
    load_or_train_tokenizer,
    recount_train_tokens,
    tokenize_corpus,
)

ROOT = Path(__file__).resolve().parents[2]


def load_fetch_records(raw_dir: Path) -> list[dict]:
    records = []
    for manifest_path in raw_dir.glob("*/fetch_manifest.json"):
        source_id = manifest_path.parent.name
        rows = json.loads(manifest_path.read_text(encoding="utf-8"))
        for row in rows:
            path = Path(row["path"])
            if not path.is_absolute():
                path = (ROOT / path).resolve()
            if not path.exists():
                path = (manifest_path.parent / Path(row["name"]).name).resolve()
            records.append(
                {
                    "source_id": source_id,
                    "name": row["name"],
                    "path": str(path),
                    "sha256": row["sha256"],
                    "bytes": row["bytes"],
                    "licence": "ODC-By 1.0" if source_id == "fineweb_edu" else "mixed",
                }
            )
    return records


def reconstruct_clean_report(clean_path: Path) -> dict:
    # Prefer line count without loading JSON payloads into RAM.
    import subprocess

    out = subprocess.run(
        ["wc", "-l", str(clean_path)], capture_output=True, text=True, check=True
    )
    kept = int(out.stdout.split()[0])
    return {
        "kept": kept,
        "drops": {},
        "contamination_removed": 0,
        "reconstructed_from": str(clean_path),
    }


def merge_clean_into(main_path: Path, extra_path: Path) -> None:
    if not extra_path.exists():
        return
    with (
        main_path.open("a", encoding="utf-8") as out,
        extra_path.open(encoding="utf-8") as inp,
    ):
        for line in inp:
            out.write(line)


def ensure_clean(raw_dir: Path) -> tuple[Path, dict]:
    clean_path = ROOT / "data" / "clean" / "fineweb_edu.jsonl"
    report_path = ROOT / "results" / "data" / "clean_report.json"
    if clean_path.exists() and clean_path.stat().st_size > 1_000_000:
        if report_path.exists():
            clean_report = json.loads(report_path.read_text(encoding="utf-8"))
        else:
            print("[resume] reconstructing clean report…", flush=True)
            clean_report = reconstruct_clean_report(clean_path)
            write_json(report_path, clean_report)
        print(
            f"[resume] using existing clean ({clean_report['kept']} docs)", flush=True
        )
        return clean_path, clean_report

    clean_report = clean_tree(
        raw_dir / "fineweb_edu",
        clean_path,
        ROOT / "data" / "eval_sets",
        "fineweb_edu",
    )
    tech_clean = ROOT / "data" / "clean" / "tech_docs_seed.jsonl"
    tech_report = clean_tree(
        raw_dir / "tech_docs_seed",
        tech_clean,
        ROOT / "data" / "eval_sets",
        "tech_docs_seed",
    )
    merge_clean_into(clean_path, tech_clean)
    clean_report["kept"] += tech_report["kept"]
    for k, v in tech_report["drops"].items():
        clean_report["drops"][k] = clean_report["drops"].get(k, 0) + v
    clean_report["contamination_removed"] += tech_report["contamination_removed"]
    write_json(report_path, clean_report)
    return clean_path, clean_report


def ensure_dedup(clean_path: Path) -> tuple[Path, dict]:
    dedup_path = ROOT / "data" / "dedup" / "corpus.jsonl"
    report_path = ROOT / "results" / "data" / "dedup_report.json"
    if dedup_path.exists() and dedup_path.stat().st_size > 1_000_000_000:
        if report_path.exists():
            dedup_report = json.loads(report_path.read_text(encoding="utf-8"))
            print("[resume] using existing dedup corpus", flush=True)
            return dedup_path, dedup_report

    # 4.5B tokens × ~4.2 bytes/token safety margin ≈ 19 GB unique text.
    target_bytes = 19_000_000_000
    exact_path = ROOT / "data" / "dedup" / "exact.jsonl"
    if exact_path.exists() and exact_path.stat().st_size > 1_000_000_000:
        print("[resume] using existing exact.jsonl", flush=True)
        saved = ROOT / "results" / "data" / "exact_pass.json"
        if saved.exists():
            exact = json.loads(saved.read_text(encoding="utf-8"))
            exact["resumed"] = True
        else:
            exact = {
                "kept_bytes": exact_path.stat().st_size,
                "capped": True,
                "resumed": True,
            }
    else:
        print(f"[dedup] exact pass (cap {target_bytes} bytes)…", flush=True)
        exact = exact_dedup(clean_path, exact_path, max_kept_bytes=target_bytes)
        print(f"[dedup] exact done: {exact}", flush=True)

    # FineWeb-Edu is MinHash-deduped upstream. Probe residual; skip full LSH
    # when already under the gate (avoids multi-hour no-op pass).
    print("[dedup] probing residual near-dup on exact output…", flush=True)
    probe = sample_near_dup_rate(exact_path, sample_size=20_000)
    print(f"[dedup] probe near-dup rate={probe:.6f}", flush=True)
    if probe < 0.01:
        if dedup_path.exists():
            dedup_path.unlink()
        exact_path.replace(dedup_path)
        near = {
            "kept": exact.get("kept"),
            "dropped": 0,
            "near_dup_rate_removed": 0.0,
            "skipped_full_lsh": True,
            "reason": "upstream FineWeb-Edu near-dedup; probe under 1%",
            "probe_rate": probe,
        }
        print("[dedup] skipped full near LSH (probe clean)", flush=True)
    else:
        print("[dedup] near pass…", flush=True)
        near = near_dedup(exact_path, dedup_path, threshold=0.8)
        print(f"[dedup] near done: {near}", flush=True)
        exact_path.unlink(missing_ok=True)

    print("[dedup] measuring residual rates…", flush=True)
    dedup_report = {
        "exact_pass": exact,
        "near_pass": near,
        "exact_duplicate_rate_in_output": exact_dup_rate_in_output(dedup_path),
        "near_duplicate_rate_jaccard_gt_0_8_sample": sample_near_dup_rate(
            dedup_path, sample_size=100_000
        ),
    }
    write_json(report_path, dedup_report)
    return dedup_path, dedup_report


def ensure_tokenize(dedup_path: Path) -> dict:
    tok_path = ROOT / "artifacts" / "tokenizer" / "n32-16k.json"
    tokens_dir = ROOT / "data" / "tokens"
    report_path = ROOT / "results" / "data" / "tokenize_report.json"
    held = tokens_dir / "heldout.bin"
    if held.exists() and recount_train_tokens(tokens_dir) >= 4_000_000_000 - 10_000_000:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        print("[resume] using existing tokens", flush=True)
        return report

    print("[tokenize] train/load tokenizer…", flush=True)
    tokenizer = load_or_train_tokenizer(tok_path, [dedup_path])
    print("[tokenize] encode corpus…", flush=True)
    tokenize_report = tokenize_corpus(
        dedup_path,
        tokenizer,
        tokens_dir,
        shard_tokens=100_000_000,
        holdout_tokens=10_000_000,
    )
    tokenize_report["train_tokens"] = recount_train_tokens(tokens_dir)
    write_json(report_path, tokenize_report)
    return tokenize_report


def run(raw_dir: Path) -> dict:
    assert_all_licences_known()
    wall0 = time.time()
    records = load_fetch_records(raw_dir)
    records.extend(fetch_tech_docs_seed(raw_dir))
    for row in records:
        path = Path(row["path"])
        if path.exists():
            row["sha256"] = sha256_file(path)
            row["bytes"] = path.stat().st_size
    manifest = build_manifest(records)
    manifest_path = ROOT / "data" / "manifest.json"
    write_json(manifest_path, manifest)

    clean_path, clean_report = ensure_clean(raw_dir)
    dedup_path, dedup_report = ensure_dedup(clean_path)
    tokenize_report = ensure_tokenize(dedup_path)

    wall = time.time() - wall0
    write_json(ROOT / "results" / "data" / "clean_report.json", clean_report)
    write_json(ROOT / "results" / "data" / "dedup_report.json", dedup_report)
    write_json(ROOT / "results" / "data" / "tokenize_report.json", tokenize_report)
    summary = build_summary(
        ROOT / "data" / "tokens",
        dedup_path,
        manifest_path,
        clean_report,
        dedup_report,
        tokenize_report,
        wall,
    )
    write_json(ROOT / "results" / "data" / "corpus_stats.json", summary)
    write_json(ROOT / "results" / "data" / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw")
    args = parser.parse_args()
    summary = run(args.raw)
    print(
        json.dumps(
            {
                "gate_pass": summary["gate_pass"],
                "total_tokens": summary["total_tokens"],
                "wall_seconds": summary["wall_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
