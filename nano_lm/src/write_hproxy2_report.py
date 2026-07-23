"""Render H-PROXY2 smoke vs H-DECK (CE proxy vs self-lp) markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from proxy2_ops import decide_hproxy2


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    # Attach mean teacher_forwards into stats for decide_hproxy2.
    for fam, rows in _by_family(data["rows"]).items():
        fw = [float(r["teacher_forwards"]) for r in rows]
        stats.setdefault(fam, {})["teacher_forwards"] = sum(fw) / len(fw)
    s = stats.get("H-PROXY2", {})
    decision = decide_hproxy2(s, stats) if s else "needs H-PROXY2 rows"
    deck = stats.get("H-DECK", {})
    delta = s.get("mean_lp", float("nan")) - deck.get("mean_lp", float("nan"))
    lines = [
        "# H-PROXY2 smoke vs H-DECK (CE proxy vs self-lp)",
        "",
        "Equal pop×gens×top_k=1. Proxy: teacher-forced CE on prompt+completion",
        "vs sampling self-lp. Kill if ≤ H-DECK quality@forwards.",
        "",
        "| family | mean teacher_lp | Δ vs H-DECK | mean teacher_fwd | n |",
        "|--------|-----------------|-------------|------------------|---|",
    ]
    for fam in ("H-DECK", "H-PROXY2"):
        if fam not in stats:
            continue
        st = stats[fam]
        d = "—" if fam == "H-DECK" else f"{delta:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d} | "
            f"{st.get('teacher_forwards', float('nan')):.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:proxy2` → `npm run nano:proxy2:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def _by_family(rows: list) -> dict[str, list]:
    out: dict[str, list] = {}
    for r in rows:
        out.setdefault(str(r["family"]), []).append(r)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/proxy2_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hproxy2-vs-hdeck.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
