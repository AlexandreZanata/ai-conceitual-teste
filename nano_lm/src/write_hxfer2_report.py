"""Render H-XFER2 smoke — PACK-only transfer deepen (+ optional BPACK)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from xfer2_ops import XFER2_PACKS, decide_hxfer2
from xfer_score import means_decode


def _pack_table(rows: list[dict], tip: str, fams: tuple[str, ...]) -> list[str]:
    stats = means_decode(rows)
    tip_s = stats.get(tip, {})
    lines = [
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "--------------|--------|-----------------|---|",
    ]
    for fam in fams:
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == tip:
            d1 = d2 = d3 = "—"
        else:
            d1 = f"{st['mean_lp'] - tip_s.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_tps'] - tip_s.get('mean_tps', float('nan')):+.1f}"
            d3 = f"{st['mean_wall'] - tip_s.get('mean_wall', float('nan')):+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{int(st['n'])} |"
        )
    return lines


def _verdict_row(verdicts: dict, recipe: str) -> str:
    row = verdicts.get(recipe, {})
    cells = [str(row.get(p, "—"))[:40] for p in XFER2_PACKS]
    return f"| {recipe} | {cells[0]} | {cells[1]} | {cells[2]} |"


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    verdicts = data.get("verdicts") or {}
    decision = data.get("decision") or decide_hxfer2(verdicts)
    title = "Formal H-XFER2" if formal else "H-XFER2 smoke"
    lines = [
        f"# {title} — PACK on elongated / OOD / OOD-long",
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
            "PACK-only transfer deepen (Wave V). Kill if H-PACK loses dual gate "
            "vs EARLY on any pack. BPACK is report-only (does not fail the gate).",
            f"Mode: `{data.get('mode')}`; packs=`{data.get('packs')}`.",
            "",
            "| recipe | elongated | ood | ood_long |",
            "|--------|-----------|-----|----------|",
            _verdict_row(verdicts, "H-PACK"),
        ]
    )
    if "H-BPACK" in verdicts:
        lines.append(_verdict_row(verdicts, "H-BPACK"))
    lines.extend(["", f"**Decision: {decision}**", ""])
    for pack in XFER2_PACKS:
        meta = (data.get("packs") or {}).get(pack, {})
        lines.extend(
            [
                f"## Pack `{pack}` (n={meta.get('n_prompts')}, "
                f"target={meta.get('target_tokens')})",
                "",
                "### H-PACK",
                "",
            ]
        )
        lines.extend(
            _pack_table(
                data.get("pack_rows", {}).get(pack, []),
                "H-EARLY",
                ("H-EARLY", "H-SERVE", "H-SROUTE"),
            )
        )
        lines.extend(["", "### H-BPACK (report-only)", ""])
        lines.extend(
            _pack_table(
                data.get("bpack_rows", {}).get(pack, []),
                "H-EARLY",
                ("H-EARLY", "H-SKIP", "H-LAYB"),
            )
        )
        lines.append("")
    cmd = (
        "`npm run nano:formal:hxfer2` → `npm run nano:formal:hxfer2:report`"
        if formal
        else "`npm run nano:xfer2` → `npm run nano:xfer2:report`"
    )
    lines.extend(
        [
            "Tips unchanged. Wave V PACK transfer deepen.",
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
        default=Path("results/nano-lm/student-matrix/xfer2_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hxfer2-transfer.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
