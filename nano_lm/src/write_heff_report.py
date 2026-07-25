"""Render H-EFF smoke — PACK efficiency on prog+btc vs Phase B."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eff_ops import PHASE_B_SERVE, decide_heff


def _domain_table(
    name: str,
    means: dict,
    baseline: dict[str, float],
) -> list[str]:
    serve = (means.get(name) or {}).get("H-SERVE") or {}
    early = (means.get(name) or {}).get("H-EARLY") or {}
    lines = [
        f"### {name}",
        "",
        "| arm | mean teacher_lp | mean tok/s | mean wall_ms | mean GFLOPs |",
        "|-----|-----------------|------------|--------------|-------------|",
    ]
    for fam, st in (("H-EARLY", early), ("H-SERVE", serve)):
        if not st:
            continue
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_tps']:.1f} | "
            f"{st['mean_wall']:.0f} | {st['mean_gflops']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"Phase B SERVE baseline: lp={baseline['mean_lp']:.4f}, "
            f"tok/s={baseline['mean_tps']:.1f}, wall_ms={baseline['mean_wall']:.0f}.",
            "",
        ]
    )
    return lines


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    means = data.get("means") or {}
    baselines = data.get("baselines") or PHASE_B_SERVE
    decision = data.get("decision") or decide_heff(means, baselines=baselines)
    title = "Formal H-EFF" if formal else "H-EFF smoke"
    lines = [
        f"# {title} — PACK efficiency on prog+btc vs Phase B",
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
            "Wave W efficiency: re-measure **H-PACK** SERVE wall/tok/s/GFLOPs "
            "on programming + bitcoin packs @128 vs Phase B formal baselines. "
            "PROMOTE iff any domain is at quality floor (SERVE ≥ EARLY−ε) "
            "**and** wall↓ or tok/s↑ vs Phase B; else **HOLD**. "
            "No new genes. TPACK/AMORT remain story-train-only.",
            f"Mode: `{data.get('mode')}`; cpu_threads=`{data.get('cpu_threads')}`; "
            f"packs=`{data.get('packs')}`.",
            "",
            f"**Decision: {decision}**",
            "",
        ]
    )
    for name in ("prog", "btc"):
        if name in baselines:
            lines.extend(_domain_table(name, means, baselines[name]))
    cmd = (
        "`npm run nano:formal:heff` → `npm run nano:formal:heff:report`"
        if formal
        else "`npm run nano:eff` → `npm run nano:eff:report`"
    )
    lines.extend(["", f"Commands: {cmd}.", ""])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/heff_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/heff-efficiency.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
