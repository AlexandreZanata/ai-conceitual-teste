"""Render H-BEAMKV smoke — shared KV vs indep prefills on QT PFB K=2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from beamkv_ops import decide_hbeamkv


def _arm(name: str, m: dict) -> str:
    wb = m.get("weight_bytes")
    wb_s = f"{int(wb)}" if wb is not None and wb == wb else "—"
    te = m.get("mean_token_evals")
    te_s = f"{te:.1f}" if te is not None and te == te else "—"
    return (
        f"| {name} | {m['mean_story_lp']:.4f} | {m['mean_code_lp']:.4f} | "
        f"{m['mean_wall_ms']:.0f} | {te_s} | "
        f"{m.get('mean_unique', float('nan')):.3f} | "
        f"{m.get('mean_elig', float('nan')):.2f} | "
        f"{m.get('mean_switch', float('nan')):.2f} | {wb_s} | {int(m['n'])} |"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hbeamkv_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hbeamkv-beamkv.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    naive = data["naive_means"]
    beamkv = data["beamkv_means"]
    decision = data.get("decision") or decide_hbeamkv(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        beamkv_story=float(beamkv["mean_story_lp"]),
        beamkv_code=float(beamkv["mean_code_lp"]),
        mean_unique=float(beamkv["mean_unique"]),
        mean_elig=float(beamkv["mean_elig"]),
        mean_switch=float(beamkv["mean_switch"]),
        beamkv_wall=float(beamkv["mean_wall_ms"]),
        naive_wall=float(naive["mean_wall_ms"]),
        identical=False,
    )
    title = (
        "Formal H-BEAMKV — shared KV vs indep prefills"
        if args.formal
        else "H-BEAMKV smoke — shared KV vs indep prefills on QT PFB K=2"
    )
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', 'H-QT')}` · "
        f"k={data.get('k')} · bits={data.get('bits')} · "
        f"temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean token_evals | mean unique | mean n_elig | mean switch | "
        "weight_bytes | n |",
        "|-----|---------------|--------------|--------------|"
        "------------------|-------------|-------------|--------------|"
        "--------------|---|",
        _arm("H-QT-int8 n=1", parent),
        _arm("H-BEAMKV-naive indep", naive),
        _arm("H-BEAMKV shared", beamkv),
        "",
        "Tips unchanged. Wave Y H-BEAMKV (cache on QPFB2 spine).",
        "",
        "Reproduce:",
        "`npm run nano:beamkv` → `npm run nano:beamkv:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hbeamkv` → "
                "`npm run nano:formal:hbeamkv:report`",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
