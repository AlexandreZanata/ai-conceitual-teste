"""Render H-DEPL smoke — deploy policy vs BUD survivors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bud_score import means_decode, means_train
from depl_ops import decide_hdepl


def _pack_block(rows: list[dict], tip: str, util: str) -> list[str]:
    stats = means_decode(rows)
    t = stats.get(tip, {})
    lines = [
        "| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | "
        "mean wall_ms | Δ wall | mean est GFLOPs | n |",
        "|--------|-----------------|------|------------|---------|"
        "--------------|--------|-----------------|---|",
    ]
    for fam in (tip, util):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == tip:
            d1 = d2 = d3 = "—"
        else:
            d1 = f"{st['mean_lp'] - t.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_tps'] - t.get('mean_tps', float('nan')):+.1f}"
            d3 = f"{st['mean_wall'] - t.get('mean_wall', float('nan')):+.0f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_tps']:.1f} | "
            f"{d2} | {st['mean_wall']:.0f} | {d3} | {st['mean_gflops']:.3f} | "
            f"{int(st['n'])} |"
        )
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
    bud = data.get("bud_verdicts") or {}
    decision = data.get("decision") or decide_hdepl(bud)
    title = "Formal H-DEPL" if formal else "H-DEPL smoke"
    lines = [
        f"# {title} — deploy policy gated on BUD survivors",
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
            "Runnable deploy policy (Wave V): **speed** → H-PACK (not ood_long); "
            "**quality** → H-QPACK only if in-dist; **train** → H-TPACK. "
            "Kill if any chosen recipe fails H-BUD SURVIVE (policy contradicts BUD).",
            f"Mode: `{data.get('mode')}`; n_prompts=`{data.get('n_prompts')}`; "
            f"budgets=`{data.get('budgets')}`; target=`{data.get('target_tokens')}`; "
            f"cpu_threads=`{data.get('cpu_threads')}`; δ=`{data.get('delta_gflops_frac')}`.",
            "",
            "## BUD survivors",
            "",
            "| recipe | util | tip | verdict |",
            "|--------|------|-----|---------|",
            f"| H-PACK | H-SERVE | H-EARLY | {bud.get('H-PACK', '—')} |",
            f"| H-QPACK | H-FLAYB | H-POOL | {bud.get('H-QPACK', '—')} |",
            f"| H-TPACK | H-TPACK | H-STAG | {bud.get('H-TPACK', '—')} |",
            "",
            "## Deploy routes",
            "",
            "| scenario | goal | in_dist | ood_long | choice |",
            "|----------|------|---------|----------|--------|",
        ]
    )
    for r in data.get("routes") or []:
        lines.append(
            f"| {r.get('id')} | {r.get('goal')} | {r.get('in_dist')} | "
            f"{r.get('ood_long')} | {r.get('choice')} |"
        )
    lines.extend(["", f"**Decision: {decision}**", "", "## H-PACK (SERVE vs EARLY)", ""])
    lines.extend(_pack_block(data.get("pack_rows") or [], "H-EARLY", "H-SERVE"))
    lines.extend(["", "## H-QPACK (FLAYB vs POOL)", ""])
    lines.extend(_pack_block(data.get("qpack_rows") or [], "H-POOL", "H-FLAYB"))
    lines.extend(["", "## H-TPACK (vs STAG ms/step)", ""])
    lines.extend(_tpack_block(data.get("tpack_rows") or []))
    cmd = (
        "`npm run nano:formal:hdepl` → `npm run nano:formal:hdepl:report`"
        if formal
        else "`npm run nano:depl` → `npm run nano:depl:report`"
    )
    lines.extend(
        [
            "",
            "Tips unchanged. Wave V deploy policy.",
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
        default=Path("results/nano-lm/student-matrix/hdepl_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdepl-policy.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
