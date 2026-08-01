"""Fetch licence-clean sources into data/raw/ with checksums."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from huggingface_hub import hf_hub_download, list_repo_files

from n32.data.io_utils import sha256_file, write_json
from n32.data.sources import REJECTED, assert_all_licences_known, sources_by_id

ROOT = Path(__file__).resolve().parents[2]


def download_hf_file(repo: str, name: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cached = Path(hf_hub_download(repo, name, repo_type="dataset")).resolve()
    if dest.exists() or dest.is_symlink():
        if (
            dest.is_symlink()
            or not dest.exists()
            or dest.stat().st_size != cached.stat().st_size
        ):
            dest.unlink(missing_ok=True)
    if not dest.exists():
        try:
            dest.hardlink_to(cached)
        except OSError:
            shutil.copy2(cached, dest)
    digest = sha256_file(dest)
    return {
        "repo": repo,
        "name": name,
        "path": str(dest),
        "sha256": digest,
        "bytes": dest.stat().st_size,
        "wall_seconds": round(time.time() - t0, 3),
    }


def resolve_hf_files(source_id: str, repo: str, limit: int) -> list[str]:
    src = sources_by_id()[source_id]
    if src.hf_files:
        return list(src.hf_files)[:limit]
    files = [
        f
        for f in list_repo_files(repo, repo_type="dataset")
        if f.endswith(".parquet") or f.endswith(".jsonl") or f.endswith(".jsonl.gz")
    ]
    return files[:limit]


def fetch_source(source_id: str, out_dir: Path, max_files: int) -> list[dict]:
    src = sources_by_id()[source_id]
    if not src.hf_repo:
        return []
    files = resolve_hf_files(source_id, src.hf_repo, max_files)
    records = []
    for name in files:
        dest = out_dir / source_id / Path(name).name
        rec = download_hf_file(src.hf_repo, name, dest)
        rec["source_id"] = source_id
        rec["licence"] = src.licence
        records.append(rec)
    return records


def fetch_tech_docs_seed(out_dir: Path) -> list[dict]:
    """Pull a small licence-checked HTML/text seed; not the 280M token slice alone."""
    import urllib.request

    urls = [
        (
            "python_tutorial_intro",
            "https://docs.python.org/3/tutorial/introduction.html",
        ),
        ("rfc791", "https://www.rfc-editor.org/rfc/rfc791.txt"),
    ]
    records = []
    dest_dir = out_dir / "tech_docs_seed"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for doc_id, url in urls:
        dest = dest_dir / f"{doc_id}.txt"
        t0 = time.time()
        if dest.exists() and dest.stat().st_size > 0:
            data_len = dest.stat().st_size
        else:
            with urllib.request.urlopen(url, timeout=60) as resp:
                data = resp.read()
            dest.write_bytes(data)
            data_len = len(data)
        records.append(
            {
                "source_id": "tech_docs_seed",
                "name": url,
                "path": str(dest),
                "sha256": sha256_file(dest),
                "bytes": data_len,
                "licence": sources_by_id()["tech_docs_seed"].licence,
                "wall_seconds": round(time.time() - t0, 3),
            }
        )
    return records


def build_manifest(records: list[dict]) -> dict:
    return {
        "sources": [r for r in records],
        "rejected": list(REJECTED),
        "unknown_licence_count": 0,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch N32 pretraining sources")
    p.add_argument("--out", type=Path, default=ROOT / "data" / "raw")
    p.add_argument("--manifest", type=Path, default=ROOT / "data" / "manifest.json")
    p.add_argument("--max-files-per-source", type=int, default=7)
    p.add_argument(
        "--sources",
        nargs="*",
        default=["fineweb_edu"],
        help="Source ids to fetch (default: fineweb_edu widened for token gate)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    assert_all_licences_known()
    records: list[dict] = []
    for source_id in args.sources:
        if source_id == "tech_docs_seed":
            records.extend(fetch_tech_docs_seed(args.out))
            continue
        records.extend(fetch_source(source_id, args.out, args.max_files_per_source))
    manifest = build_manifest(records)
    write_json(args.manifest, manifest)
    print(
        json.dumps(
            {"files": len(records), "bytes": sum(r["bytes"] for r in records)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
