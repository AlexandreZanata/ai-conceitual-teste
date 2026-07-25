"""Render H-PARETO smoke — formal-corpus efficiency audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pareto_ops import decide_hpareto


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    pairs = data.get("pairs") or []
    n_pairs = int(data.get("n_pairs", len(pairs)))
    n_flag = int(data.get("n_flagged", sum(1 for p in pairs if p.get("flagged"))))
    decision = data.get("decision") or decide_hpareto(
        n_pairs=n_pairs, n_flagged=n_flag
    )
    delta = data.get("delta_frac", 0.05)
    lines = [
        "# H-PARETO smoke — tok/s↑ but GFLOPs↑ beyond tip+δ",
        "",
        "Report-only instrumentation: scan formal util/tip pairs with est. GFLOPs. "
        f"FLAG iff tok/s↑ **and** GFLOPs > tip·(1+δ) with δ=`{delta}`. "
        "Does not tip-paste or delete code — flags dishonest efficiency claims.",
        f"Mode: `{data.get('mode')}`; wall_s=`{data.get('wall_s', float('nan')):.3f}`.",
        "",
        "| util | control | source | Δ tok/s | Δ GFLOPs | verdict |",
        "|------|---------|--------|---------|----------|---------|",
    ]
    for p in pairs:
        lines.append(
            f"| {p['family']} | {p['control']} | `{p['source']}` | "
            f"{p['delta_tps']:+.1f} | {p['delta_gflops']:+.3f} | "
            f"{'FLAG' if p['flagged'] else 'KEEP'} |"
        )
    flagged = [p for p in pairs if p.get("flagged")]
    lines.extend(["", f"**Decision: {decision}**", ""])
    if flagged:
        names = ", ".join(sorted({p["family"] for p in flagged}))
        lines.extend(
            [
                f"Flagged utils (do not claim GFLOPs efficiency): **{names}**.",
                "",
            ]
        )
    lines.extend(
        [
            "Tips unchanged. Measurement hygiene (Wave R).",
            "",
            "Commands: `npm run nano:pareto` → `npm run nano:pareto:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/pareto_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpareto-audit.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
