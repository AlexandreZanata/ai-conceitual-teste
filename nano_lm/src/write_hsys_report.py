"""Render H-SYS smoke vs CURL default + EARLY/POOL@B2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from sys_ops import SYS_EARLY, SYS_POOL, decide_hsys, decide_hsys_arm


def _curl_rows(out: Path) -> list[dict]:
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(out.glob("HCURL_lo8_seed*_eval.json"))
    ]


def render(
    smoke_path: Path,
    early_path: Path,
    pool_path: Path,
    matrix_dir: Path,
) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    early = json.loads(early_path.read_text(encoding="utf-8"))
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    tip_rows = [
        r
        for r in early["rows"] + pool["rows"]
        if r.get("family") in {"H-EARLY", "H-POOL"}
    ]
    stats = mean_by_family(_curl_rows(matrix_dir) + tip_rows + smoke["rows"])
    decision = decide_hsys(stats)
    lines = [
        "# H-SYS smoke — CURL lo=8 × EARLY|POOL decode",
        "",
        "Compose official train tip (CURL seq_lo=8) with EARLY / POOL decode search.",
        "Kill arm if ≤ CURL default-decode or ≤ same tip on B2 (free lunch).",
        "",
        "| family | mean teacher_lp | mean wall_ms | n |",
        "|--------|-----------------|--------------|---|",
    ]
    for fam in ("H-CURL", "H-EARLY", "H-POOL", SYS_EARLY, SYS_POOL):
        if fam not in stats:
            continue
        st = stats[fam]
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(["", "### Arm decisions", ""])
    for fam, tip in ((SYS_EARLY, "H-EARLY"), (SYS_POOL, "H-POOL")):
        if fam not in stats:
            continue
        lines.append(
            f"- **{fam}:** {decide_hsys_arm(stats[fam], stats, tip_family=tip)}"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:sys` → `npm run nano:sys:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "sys_smoke.json")
    p.add_argument("--early", type=Path, default=root / "early_smoke.json")
    p.add_argument("--pool", type=Path, default=root / "pool_smoke.json")
    p.add_argument("--matrix-dir", type=Path, default=root)
    p.add_argument(
        "--out", type=Path, default=Path("docs/results/nano-lm/hsys-vs-tips.md")
    )
    args = p.parse_args()
    text = render(args.smoke, args.early, args.pool, args.matrix_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
