"""Render formal H-CASC vs B4 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from casc_ops import decide_hcasc
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    casc_rows = [r for r in data["rows"] if r.get("family") == "H-CASC"]
    stats: dict[str, dict[str, float]] = {
        name: {"mean_lp": st["lp"], "n": st["n"], "wall": st["wall"]}
        for name, st in fam.items()
    }
    if casc_rows:
        stats["H-CASC"]["wall_save"] = (
            1.0 if all(bool(r.get("wall_save")) for r in casc_rows) else 0.0
        )
    decision = decide_hcasc(stats.get("H-CASC", {}), stats)
    b4 = stats.get("B4", {})
    hyp = stats.get("H-CASC", {})
    delta = hyp.get("mean_lp", float("nan")) - b4.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-CASC vs B4 (proxy → mid teacher → full)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 KD ckpts. pop=8 gens=12 mid_k=3 final_k=1. Fit≠eval.",
        "Kill if no teacher-forward save vs full H-DEC or ≤ B4.",
        "",
        "| family | mean teacher_lp | Δ vs B4 | mean wall_ms | wall_save | n |",
        "|--------|-----------------|---------|--------------|-----------|---|",
    ]
    for name in ("B4", "H-CASC"):
        if name not in stats:
            continue
        st = stats[name]
        d = "—" if name == "B4" else f"{delta:+.4f}"
        save = "—" if name == "B4" else ("yes" if st.get("wall_save", 0) > 0 else "no")
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['wall']:.0f} | "
            f"{save} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hcasc` → "
            "`npm run nano:formal:hcasc:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hcasc/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hcasc-vs-b4.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
