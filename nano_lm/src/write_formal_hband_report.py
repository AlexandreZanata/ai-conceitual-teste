"""Render formal H-BAND vs H-CASC / H-DECK markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from band_ops import decide_hband
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "n": st["n"], "wall": st["wall"]}
        for name, st in fam.items()
    }
    decision = decide_hband(stats.get("H-BAND", {}), stats)
    hyp = stats.get("H-BAND", {})
    lines = [
        "# Formal H-BAND vs H-CASC / H-DECK (UCB1 gene arms)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Shared B2 ckpts. n_arms=8 n_pulls=48 (= H-CASC mid+final scores).",
        "Kill if ≤ max(H-DECK, H-CASC).",
        "",
        "| family | mean teacher_lp | Δ vs H-BAND | mean wall_ms | n |",
        "|--------|-----------------|-------------|--------------|---|",
    ]
    for name in ("H-DECK", "H-CASC", "H-BAND"):
        if name not in stats:
            continue
        st = stats[name]
        if name == "H-BAND":
            d = "—"
        else:
            d = f"{st['mean_lp'] - hyp.get('mean_lp', float('nan')):+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {d} | {st['wall']:.0f} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hband` → "
            "`npm run nano:formal:hband:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hband/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hband-vs-hcasc.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
