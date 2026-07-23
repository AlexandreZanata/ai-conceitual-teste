"""Render formal H-DEB vs B2 markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deb_ops import decide_hdeb
from formal_ops import means_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fam = means_by_family(data["rows"])
    stats = {
        name: {"mean_lp": st["lp"], "mean_wall": st["wall"], "n": st["n"]}
        for name, st in fam.items()
    }
    decision = decide_hdeb(stats.get("H-DEB", {}), stats)
    hyp = stats.get("H-DEB", {})
    b2 = stats.get("B2", {})
    d_b2 = hyp.get("mean_lp", float("nan")) - b2.get("mean_lp", float("nan"))
    lines = [
        "# Formal H-DEB vs B2 (dual student; teacher picks)",
        "",
        f"Source: `{path}`",
        f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
        "",
        "Equal budget: 120 steps, seeds 0–2, eval_prompts (batch=2 for dual VRAM).",
        "Kill if ≤ B2.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |",
        "|--------|-----------------|---------|--------------|---|",
    ]
    for name in ("B2", "H-DEB"):
        if name not in stats:
            continue
        st = stats[name]
        delta = "—" if name == "B2" else f"{d_b2:+.4f}"
        lines.append(
            f"| {name} | {st['mean_lp']:.4f} | {delta} | "
            f"{st['mean_wall']:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision:** {decision}",
            "",
            "Commands: `npm run nano:formal:hdeb` → "
            "`npm run nano:formal:hdeb:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hdeb/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hdeb-vs-b2.md"),
    )
    args = p.parse_args()
    text = render(args.formal)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
