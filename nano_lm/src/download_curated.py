"""Download public curated corpora into nano_lm/data/curated/."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

from curated_sources import SOURCES
from matrix_common import ROOT

OUT_ROOT = ROOT / "data" / "curated"
MANIFEST = OUT_ROOT / "manifest.json"
UA = "EvoGen-nano-curated/1.0 (+research; polite fetch)"


def _fetch(url: str, *, max_bytes: int | None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read(max_bytes + 1 if max_bytes else -1)
    if max_bytes is not None and len(data) > max_bytes:
        data = data[:max_bytes]
    return data


def download_one(row: dict, dest_root: Path) -> dict:
    """
    GIVEN a registry row
    WHEN fetching URL
    THEN write file under dest_root and return manifest entry.
    """
    rel = Path(str(row["path"]))
    out = dest_root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    max_b = row.get("max_bytes")
    body = _fetch(str(row["url"]), max_bytes=int(max_b) if max_b else None)
    out.write_bytes(body)
    return {
        "id": row["id"],
        "domain": row["domain"],
        "license": row["license"],
        "url": row["url"],
        "path": str(rel).replace("\\", "/"),
        "bytes": len(body),
    }


def download_all(
    dest_root: Path = OUT_ROOT,
    *,
    domains: set[str] | None = None,
) -> list[dict]:
    """Download all (or domain-filtered) curated sources; write manifest."""
    dest_root.mkdir(parents=True, exist_ok=True)
    rows = SOURCES
    if domains:
        rows = [s for s in SOURCES if s["domain"] in domains]
    entries: list[dict] = []
    for row in rows:
        try:
            entries.append(download_one(row, dest_root))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            entries.append(
                {
                    "id": row["id"],
                    "domain": row["domain"],
                    "url": row["url"],
                    "error": str(exc),
                }
            )
    manifest = {"root": str(dest_root), "entries": entries}
    (dest_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return entries


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--domain",
        action="append",
        choices=("bitcoin", "programming", "frontier"),
        help="Repeatable domain filter (default: all)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=OUT_ROOT,
        help="Output root (default: nano_lm/data/curated)",
    )
    p.add_argument(
        "--no-proxy",
        action="store_true",
        help="Ignore HTTP(S)_PROXY env (broken local SOCKS)",
    )
    args = p.parse_args()
    if args.no_proxy:
        import os

        for key in (
            "http_proxy",
            "https_proxy",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "all_proxy",
        ):
            os.environ.pop(key, None)
    domains = set(args.domain) if args.domain else None
    entries = download_all(args.out, domains=domains)
    ok = sum(1 for e in entries if "error" not in e)
    print(f"curated: {ok}/{len(entries)} ok → {args.out}")


if __name__ == "__main__":
    main()
