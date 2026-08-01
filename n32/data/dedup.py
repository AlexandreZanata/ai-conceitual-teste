"""Exact and near-duplicate deduplication for N32 corpora."""

from __future__ import annotations

import argparse
import json
import os
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from datasketch import MinHash, MinHashLSH

from n32.data.io_utils import append_jsonl, iter_jsonl, sha256_text, write_json

ROOT = Path(__file__).resolve().parents[2]
_NUM_PERM = 128


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def char_ngrams(text: str, n: int = 5) -> list[str]:
    # Word 5-grams: same Jaccard target, far cheaper than character n-grams.
    words = normalize(text).split()
    if len(words) < n:
        return [" ".join(words)] if words else []
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def minhash_signature(text: str, num_perm: int = _NUM_PERM) -> MinHash:
    mh = MinHash(num_perm=num_perm)
    for gram in char_ngrams(normalize(text), 5):
        mh.update(gram.encode("utf-8"))
    return mh


def _hashvalues_for_text(text: str) -> np.ndarray:
    return np.array(minhash_signature(text).hashvalues, dtype=np.uint64)


def exact_dedup(
    in_path: Path, out_path: Path, max_kept_bytes: int | None = None
) -> dict:
    seen: set[str] = set()
    kept = 0
    dropped = 0
    kept_bytes = 0
    if out_path.exists():
        out_path.unlink()
    batch = []
    for row in iter_jsonl(in_path):
        digest = sha256_text(normalize(row["text"]))
        if digest in seen:
            dropped += 1
            continue
        seen.add(digest)
        kept += 1
        row = dict(row)
        row["norm_sha256"] = digest
        kept_bytes += int(row.get("bytes") or len(row["text"].encode("utf-8")))
        batch.append(row)
        if len(batch) >= 1000:
            append_jsonl(out_path, batch)
            batch = []
            if kept % 100_000 == 0:
                print(
                    f"[exact] kept={kept} dropped={dropped} bytes={kept_bytes}",
                    flush=True,
                )
        if max_kept_bytes is not None and kept_bytes >= max_kept_bytes:
            break
    if batch:
        append_jsonl(out_path, batch)
    total = kept + dropped
    rate = (dropped / total) if total else 0.0
    return {
        "kept": kept,
        "dropped": dropped,
        "exact_dup_rate": rate,
        "kept_bytes": kept_bytes,
        "capped": max_kept_bytes is not None and kept_bytes >= (max_kept_bytes or 0),
    }


def _mh_from_hashvalues(values: np.ndarray) -> MinHash:
    mh = MinHash(num_perm=_NUM_PERM)
    mh.hashvalues = np.asarray(values, dtype=np.uint64)
    return mh


def _flush_near_chunk(
    lsh: MinHashLSH,
    rows: list[dict],
    signatures: list[np.ndarray],
    out_path: Path,
    state: dict,
) -> None:
    batch_out: list[dict] = state["batch_out"]
    for row, values in zip(rows, signatures):
        key = f"d{state['kept'] + state['dropped']}"
        mh = _mh_from_hashvalues(values)
        if lsh.query(mh):
            state["dropped"] += 1
            continue
        lsh.insert(key, mh)
        state["kept"] += 1
        batch_out.append(row)
        if len(batch_out) >= 1000:
            append_jsonl(out_path, batch_out)
            state["batch_out"] = []
            batch_out = state["batch_out"]
            if state["kept"] % 50_000 == 0:
                print(
                    f"[near] kept={state['kept']} dropped={state['dropped']}",
                    flush=True,
                )


def near_dedup(
    in_path: Path,
    out_path: Path,
    threshold: float = 0.8,
    workers: int | None = None,
    chunk_size: int = 512,
) -> dict:
    """MinHash LSH with b=16, r=8 (num_perm=128). Signatures computed in parallel."""
    lsh = MinHashLSH(threshold=threshold, num_perm=_NUM_PERM)
    if out_path.exists():
        out_path.unlink()
    n_workers = workers or max(1, min(8, (os.cpu_count() or 2) - 1))
    state = {"kept": 0, "dropped": 0, "batch_out": []}
    chunk_rows: list[dict] = []

    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        for row in iter_jsonl(in_path):
            chunk_rows.append(row)
            if len(chunk_rows) < chunk_size:
                continue
            texts = [r["text"] for r in chunk_rows]
            sigs = list(pool.map(_hashvalues_for_text, texts, chunksize=16))
            _flush_near_chunk(lsh, chunk_rows, sigs, out_path, state)
            chunk_rows = []
        if chunk_rows:
            texts = [r["text"] for r in chunk_rows]
            sigs = list(pool.map(_hashvalues_for_text, texts, chunksize=16))
            _flush_near_chunk(lsh, chunk_rows, sigs, out_path, state)
    if state["batch_out"]:
        append_jsonl(out_path, state["batch_out"])
    total = state["kept"] + state["dropped"]
    rate = (state["dropped"] / total) if total else 0.0
    return {
        "kept": state["kept"],
        "dropped": state["dropped"],
        "near_dup_rate_removed": rate,
    }


def sample_near_dup_rate(
    path: Path, sample_size: int = 100_000, seed: int = 0
) -> float:
    """Estimate residual near-dup rate on a sample via LSH self-join."""
    rows = []
    for row in iter_jsonl(path):
        rows.append(row["text"])
        if len(rows) >= sample_size * 2:
            break
    rng = random.Random(seed)
    if len(rows) > sample_size:
        rows = rng.sample(rows, sample_size)
    lsh = MinHashLSH(threshold=0.8, num_perm=_NUM_PERM)
    hits = 0
    # Parallel signature build, sequential LSH.
    workers = max(1, min(8, (os.cpu_count() or 2) - 1))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        signatures = list(pool.map(_hashvalues_for_text, rows, chunksize=32))
    for i, values in enumerate(signatures):
        mh = _mh_from_hashvalues(values)
        if lsh.query(mh):
            hits += 1
        else:
            lsh.insert(f"s{i}", mh)
    return hits / len(rows) if rows else 0.0


def exact_dup_rate_in_output(path: Path) -> float:
    seen: set[str] = set()
    total = 0
    dups = 0
    for row in iter_jsonl(path):
        total += 1
        digest = row.get("norm_sha256") or sha256_text(normalize(row["text"]))
        if digest in seen:
            dups += 1
        else:
            seen.add(digest)
    return dups / total if total else 0.0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deduplicate N32 cleaned documents")
    p.add_argument("--in", dest="in_path", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--report", type=Path, default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    tmp = args.out.with_suffix(".exact.jsonl")
    exact = exact_dedup(args.in_path, tmp)
    near = near_dedup(tmp, args.out, threshold=args.threshold)
    tmp.unlink(missing_ok=True)
    residual_exact = exact_dup_rate_in_output(args.out)
    residual_near = sample_near_dup_rate(
        args.out, sample_size=min(100_000, near["kept"])
    )
    report = {
        "exact_pass": exact,
        "near_pass": near,
        "exact_duplicate_rate_in_output": residual_exact,
        "near_duplicate_rate_jaccard_gt_0_8_sample": residual_near,
    }
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
