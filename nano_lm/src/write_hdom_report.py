"""Render H-DOM smoke — PACK tip gate on howto domain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dom_ops import decide_hdom
from xfer_score import means_decode


def _pack_table(rows: list[dict]) -> list[str]:
    stats = means_decode(rows)
    tip = stats.get("H-EARLY", {})
    lines = [
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "--------------|--------|-----------------|---|",
    ]
    for fam in ("H-EARLY", "H-SERVE", "H-SROUTE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = d3 = "—"
        else:
            d1 = f"{st['mean_lp'] - tip.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_tps'] - tip.get('mean_tps', float('nan')):+.1f}"
            d3 = f"{st['mean_wall'] - tip.get('mean_wall', float('nan')):+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{int(st['n'])} |"
        )
    return lines


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    verdicts = data.get("verdicts") or {}
    decision = data.get("decision") or decide_hdom(verdicts)
    title = "Formal H-DOM" if formal else "H-DOM smoke"
    pack = data.get("pack") or {}
    lines = [
        f"# {title} — PACK tip gate on howto domain",
        "",
    ]
    if formal:
        lines.extend(
            [
                f"Source: `{path}`",
                f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
                "",
            ]
        )
    lines.extend(
        [
            "New short domain capacity (Wave V): procedural **howto** prompts, "
            "disjoint from harness/fit/ood. Teacher remains TinyStories. "
            "Kill if H-PACK loses its dual gate vs H-EARLY on this domain.",
            f"Mode: `{data.get('mode')}`; pack=`{pack}`; "
            f"cpu_threads=`{data.get('cpu_threads')}`; "
            f"H-PACK=`{verdicts.get('H-PACK', '—')}`.",
            "",
            f"**Decision: {decision}**",
            "",
            "## H-PACK on howto @128",
            "",
        ]
    )
    lines.extend(_pack_table(data.get("pack_rows") or []))
    cmd = (
        "`npm run nano:formal:hdom` → `npm run nano:formal:hdom:report`"
        if formal
        else "`npm run nano:dom` → `npm run nano:dom:report`"
    )
    lines.extend(
        [
            "",
            "Tips unchanged. Wave V domain capacity probe.",
            "",
            f"Commands: {cmd}.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hdom_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdom-howto.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
