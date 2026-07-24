"""Render H-Q8 smoke vs H-CURL (same EARLY decode)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from q8_ops import decide_hq8


def render(smoke_path: Path) -> str:
    smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
    stats = mean_by_family(smoke["rows"])
    s = stats.get("H-Q8", {})
    decision = decide_hq8(s, stats) if s else "needs H-Q8 rows"
    tip = stats.get("H-CURL", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    lines = [
        "# H-Q8 smoke — INT8 dynamic quant + frozen EARLY genes",
        "",
        "Inference-only `quantize_dynamic` (qint8 Linear) on H-CURL ckpt;",
        "claim with tip EARLY genes. Dynamic kernels are CPU-backed;",
        "control stays on tip device (CUDA when available).",
        "Kill if quality < CURL−ε or no wall win.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs CURL | n |",
        "|--------|-----------------|--------------|--------------|---|",
    ]
    for fam in ("H-CURL", "H-Q8"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam == "H-CURL" else f"{d_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | "
            f"{delta} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:q8` → `npm run nano:q8:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    root = Path("results/nano-lm/student-matrix")
    p.add_argument("--smoke", type=Path, default=root / "q8_smoke.json")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hq8-vs-hcurl.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
