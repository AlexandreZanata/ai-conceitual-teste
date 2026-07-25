"""Render H-BTC smoke — PACK tip gate on bitcoin domain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from btc_ops import decide_hbtc
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
    decision = data.get("decision") or decide_hbtc(verdicts)
    title = "Formal H-BTC" if formal else "H-BTC smoke"
    pack = data.get("pack") or {}
    licenses = data.get("licenses") or ["MIT", "BSD-2-Clause"]
    lines = [
        f"# {title} — PACK tip gate on bitcoin domain",
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
            "Wave W domain capacity: **bitcoin** prompts from curated Bitcoin Core "
            "README/developer-notes (MIT) + BIP-0001 / BIP-0032 "
            f"({', '.join(str(x) for x in licenses)}), "
            "disjoint from harness/fit/ood/howto/prog. Teacher remains TinyStories. "
            "Kill if H-PACK loses its dual gate vs H-EARLY on this domain. "
            "No ood_long claim.",
            f"Mode: `{data.get('mode')}`; pack=`{pack}`; "
            f"cpu_threads=`{data.get('cpu_threads')}`; "
            f"H-PACK=`{verdicts.get('H-PACK', '—')}`.",
            "",
            f"**Decision: {decision}**",
            "",
            "## H-PACK on btc @128",
            "",
        ]
    )
    lines.extend(_pack_table(data.get("pack_rows") or []))
    cmd = (
        "`npm run nano:formal:hbtc` → `npm run nano:formal:hbtc:report`"
        if formal
        else "`npm run nano:btc` → `npm run nano:btc:report`"
    )
    lines.extend(
        [
            "",
            "Tips unchanged. Wave W bitcoin domain probe.",
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
        default=Path("results/nano-lm/student-matrix/hbtc_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hbtc-bitcoin.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
