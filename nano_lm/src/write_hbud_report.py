"""Render H-BUD smoke — hard budget survivors vs tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bud_ops import decide_hbud
from bud_score import means_decode, means_train


def _pack_block(rows: list[dict], tip: str, util: str) -> list[str]:
    stats = means_decode(rows)
    t = stats.get(tip, {})
    u = stats.get(util, {})
    lines = [
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "--------------|--------|-----------------|----------|---|",
    ]
    for fam in (tip, util):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == tip:
            d1 = d2 = d3 = d4 = "—"
        else:
            d1 = f"{st['mean_lp'] - t.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_tps'] - t.get('mean_tps', float('nan')):+.1f}"
            d3 = f"{st['mean_wall'] - t.get('mean_wall', float('nan')):+.0f}"
            d4 = f"{st['mean_gflops'] - t.get('mean_gflops', float('nan')):+.3f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{d4} | {int(st['n'])} |"
        )
    _ = u
    return lines


def _tpack_block(rows: list[dict]) -> list[str]:
    stats = means_train(rows)
    tip = stats.get("H-STAG", {})
    s = stats.get("H-TPACK", {})
    d_lp = s.get("mean_lp", float("nan")) - tip.get("mean_lp", float("nan"))
    d_ms = s.get("mean_ms_step", float("nan")) - tip.get("mean_ms_step", float("nan"))
    lines = [
        "| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | n |",
        "|--------|-----------------|------|--------------|-----------|---|",
    ]
    for fam in ("H-STAG", "H-TPACK"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-STAG":
            d1 = d2 = "—"
        else:
            d1, d2 = f"{d_lp:+.4f}", f"{d_ms:+.1f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_ms_step']:.1f} | "
            f"{d2} | {int(st['n'])} |"
        )
    return lines


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    verdicts = data.get("verdicts") or {}
    decision = data.get("decision") or decide_hbud(verdicts)
    title = "Formal H-BUD" if formal else "H-BUD smoke"
    lines = [
        f"# {title} — hard wall/GFLOPs budget vs tip",
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
            "Pareto hard gate: recipe must stay within tip wall **and** "
            f"tip·(1+δ) GFLOPs (δ=`{data.get('delta_gflops_frac', 0.05)}`), "
            "keep quality floor, and still win wall↓ or tok/s↑. "
            "Train: ms/step ≤ tip with strict ms/step↓. "
            "PACK gated on **SERVE** (min-wall); SROUTE is GFLOPs-inflated by design.",
            f"Mode: `{data.get('mode')}`; n_prompts=`{data.get('n_prompts')}`; "
            f"budgets=`{data.get('budgets')}`; target=`{data.get('target_tokens')}`.",
            "",
            "| recipe | util | tip | verdict |",
            "|--------|------|-----|---------|",
            f"| H-PACK | H-SERVE | H-EARLY | {verdicts.get('H-PACK', '—')} |",
            f"| H-QPACK | H-FLAYB | H-POOL | {verdicts.get('H-QPACK', '—')} |",
            f"| H-TPACK | H-TPACK | H-STAG | {verdicts.get('H-TPACK', '—')} |",
            "",
            f"**Decision: {decision}**",
            "",
            "## H-PACK (SERVE vs EARLY)",
            "",
        ]
    )
    lines.extend(_pack_block(data.get("pack_rows") or [], "H-EARLY", "H-SERVE"))
    lines.extend(["", "## H-QPACK (FLAYB vs POOL)", ""])
    lines.extend(_pack_block(data.get("qpack_rows") or [], "H-POOL", "H-FLAYB"))
    lines.extend(["", "## H-TPACK (vs STAG ms/step)", ""])
    lines.extend(_tpack_block(data.get("tpack_rows") or []))
    cmd = (
        "`npm run nano:formal:hbud` → `npm run nano:formal:hbud:report`"
        if formal
        else "`npm run nano:bud` → `npm run nano:bud:report`"
    )
    lines.extend(
        [
            "",
            "Tips unchanged. Wave U budget hygiene.",
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
        default=Path("results/nano-lm/student-matrix/hbud_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hbud-budget.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
