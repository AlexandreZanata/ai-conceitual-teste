"""Render H-JOINT smoke vs CURL + H-EARLY@B2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from joint_ops import decide_hjoint
from matrix_report_lib import mean_by_family


def _curl_rows(out: Path) -> list[dict]:
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(out.glob("HCURL_lo8_seed*_eval.json"))
    ]


def render(smoke_path: Path, early_path: Path, matrix_dir: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    early = json.loads(early_path.read_text(encoding="utf-8"))
    stats = mean_by_family(
        _curl_rows(matrix_dir) + early["rows"] + smoke["rows"]
    )
    s = stats.get("H-JOINT", {})
    decision = decide_hjoint(s, stats) if s else "needs H-JOINT rows"
    tip = stats.get("H-CURL", {})
    early_s = stats.get("H-EARLY", {})
    d_curl = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_early = s.get("mean_lp", float("nan")) - early_s.get(
        "mean_lp", float("nan")
    )
    lines = [
        "# H-JOINT smoke — joint curriculum ∪ early-exit gene",
        "",
        "Bank train `(seq_lo,n_stages)`; evolve joint early gene on bank ckpts.",
        "Kill if ≤ CURL default-decode or ≤ H-EARLY@B2 (free lunch / paste).",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ vs CURL | Δ vs EARLY | n |",
        "|--------|-----------------|--------------|-----------|------------|---|",
    ]
    for fam in ("H-CURL", "H-EARLY", "H-JOINT"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-CURL":
            d1 = d2 = "—"
        elif fam == "H-EARLY":
            d1 = d2 = "—"
        else:
            d1, d2 = f"{d_curl:+.4f}", f"{d_early:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{d1} | {d2} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:joint` → `npm run nano:joint:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "joint_smoke.json")
    p.add_argument("--early", type=Path, default=root / "early_smoke.json")
    p.add_argument("--matrix-dir", type=Path, default=root)
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hjoint-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, args.early, args.matrix_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
