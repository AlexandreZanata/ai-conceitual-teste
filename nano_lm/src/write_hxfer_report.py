"""Render H-XFER smoke — transfer PACK/QPACK/TPACK vs tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from xfer_ops import XFER_PACKS, XFER_RECIPES, decide_hxfer
from xfer_score import means_decode, means_train


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


def _tpack_table(rows: list[dict]) -> list[str]:
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
    decision = data.get("decision") or decide_hxfer(verdicts)
    title = "Formal H-XFER" if formal else "H-XFER smoke"
    lines = [
        f"# {title} — PACK/QPACK/TPACK on heldout / elongated / OOD",
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
            "Transfer audit: re-score official recipes on packs the harness did not "
            "claim on. Kill if any recipe loses its dual gate on any pack.",
            f"Mode: `{data.get('mode')}`; packs=`{data.get('packs')}`.",
            "",
            "| recipe | heldout | elongated | ood |",
            "|--------|---------|-----------|-----|",
        ]
    )
    for recipe in XFER_RECIPES:
        row = verdicts.get(recipe, {})
        cells = [str(row.get(p, "—"))[:40] for p in XFER_PACKS]
        lines.append(f"| {recipe} | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.extend(["", f"**Decision: {decision}**", ""])
    for pack in XFER_PACKS:
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
        lines.extend(["", "### H-QPACK", ""])
        lines.extend(
            _pack_table(
                data.get("qpack_rows", {}).get(pack, []),
                "H-POOL",
                ("H-POOL", "H-FLAYB"),
            )
        )
        lines.extend(["", "### H-TPACK", ""])
        lines.extend(_tpack_table(data.get("tpack_rows", {}).get(pack, [])))
        lines.append("")
    cmd = (
        "`npm run nano:formal:hxfer` → `npm run nano:formal:hxfer:report`"
        if formal
        else "`npm run nano:xfer` → `npm run nano:xfer:report`"
    )
    lines.extend(
        [
            "Tips unchanged. Wave U transfer hygiene.",
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
        default=Path("results/nano-lm/student-matrix/xfer_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hxfer-transfer.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
