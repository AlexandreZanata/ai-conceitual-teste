"""Render H-PFB256 smoke — PFB2 on prog@256 vs EARLY@256."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pfb256_ops import decide_hpfb256


def _arm(name: str, m: dict) -> str:
    return (
        f"| {name} | {m['mean_story_lp']:.4f} | {m['mean_code_lp']:.4f} | "
        f"{m['mean_wall_ms']:.0f} | "
        f"{m.get('mean_unique', float('nan')):.3f} | "
        f"{m.get('mean_elig', float('nan')):.2f} | "
        f"{m.get('mean_switch', float('nan')):.2f} | {int(m['n'])} |"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hpfb256_smoke.json"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hpfb256-pfb256.md"),
    )
    ap.add_argument("--formal", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.inp.read_text(encoding="utf-8"))
    parent = data["parent_means"]
    pfb = data["pfb256_means"]
    decision = data.get("decision") or decide_hpfb256(
        parent_story=float(parent["mean_story_lp"]),
        parent_code=float(parent["mean_code_lp"]),
        pfb256_story=float(pfb["mean_story_lp"]),
        pfb256_code=float(pfb["mean_code_lp"]),
        mean_unique=float(pfb["mean_unique"]),
        mean_elig=float(pfb["mean_elig"]),
        mean_switch=float(pfb["mean_switch"]),
        wall_256=float(data["wall_256_ms"]),
        wall_128=float(data["wall_128_ms"]),
        identical=False,
    )
    title = (
        "Formal H-PFB256 — PFB2 on prog@256 vs EARLY@256"
        if args.formal
        else "H-PFB256 smoke — PFB2 on prog@256 vs EARLY@256"
    )
    lines = [
        f"# {title}",
        "",
        f"Decision: **{decision}**",
        "",
        f"Parent: `{data.get('parent', '')}` · k={data.get('k')} · "
        f"temp={data.get('pfb_temp')} · "
        f"mechanism: `{data.get('mechanism', '')}`",
        "",
        f"Wall compare: PFB2@256={data['wall_256_ms']:.0f} ms · "
        f"PFB2@128={data['wall_128_ms']:.0f} ms "
        f"(L={data.get('pack256', {}).get('target_tokens')} vs "
        f"{data.get('pack128', {}).get('target_tokens')})",
        "",
        "| arm | mean story_lp | mean code_lp | mean wall_ms | "
        "mean unique | mean n_elig | mean switch | n |",
        "|-----|---------------|--------------|--------------|"
        "-------------|-------------|--------------|---|",
        _arm("H-EARLY@256", parent),
        _arm("H-PFB256 K=2", pfb),
        "",
        "Tips unchanged. Wave Y H-PFB256 (elongate ≠ CTX chunked-KV).",
        "",
        "Reproduce:",
        "`npm run nano:pfb256` → `npm run nano:pfb256:report`",
    ]
    if decision.startswith("PROMOTE") and not args.formal:
        lines.extend(
            [
                "",
                "Next formal:",
                "`npm run nano:formal:hpfb256` → "
                "`npm run nano:formal:hpfb256:report`",
            ]
        )
    elif decision.startswith("KILL"):
        lines.extend(
            [
                "",
                "Archive if confirmed formal KILL — do not claim C1@256 via PFB alone.",
            ]
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "decision": decision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
