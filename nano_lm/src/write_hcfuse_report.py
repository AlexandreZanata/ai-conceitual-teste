"""Render H-CFUSE protocol smoke (CHUNK ⊕ FUSE; not a tip)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from cfuse_ops import decide_hcfuse


def _means(rows: list[dict]) -> dict[str, dict[str, float]]:
    bags: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        bags[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in bags.items():
        n = float(len(items))
        out[fam] = {
            "mean_lp": sum(float(x["teacher_mean_logprob"]) for x in items) / n,
            "mean_wall": sum(float(x["mean_wall_ms"]) for x in items) / n,
            "mean_gflops": sum(float(x["mean_est_gflops"]) for x in items) / n,
            "n": n,
        }
    return out


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = _means(data["rows"])
    s = stats.get("H-CFUSE", {})
    decision = decide_hcfuse(s, stats) if s else "needs H-CFUSE rows"
    early = stats.get("H-EARLY", {})
    chunk = stats.get("H-CHUNK", {})
    fuse = stats.get("H-FUSE", {})
    floor = min(
        chunk.get("mean_wall", float("nan")),
        fuse.get("mean_wall", float("nan")),
    )
    lines = [
        "# H-CFUSE protocol — CHUNK ⊕ FUSE (FLASH⊕KVSEL)",
        "",
        "Stack **decode utils** H-CHUNK (chunked KV prefill) and H-FUSE "
        "(FLASH SDPA ⊕ KVSEL gated KV) on frozen EARLY tip genes + frozen "
        "`kv_threshold` / `chunk_size`.",
        "Long prompts + dual-budget mean (same budgets as H-KVSEL).",
        "This is a **protocol note**, not a compose tip H-ID.",
        "PROTOCOL iff lp ≥ EARLY−ε and wall < min(CHUNK, FUSE); else KILL.",
        f"Note: `{data.get('note')}`. Budgets: `{data.get('budgets')}`. "
        f"chunk_size=`{data.get('chunk_size')}` "
        f"target_tokens=`{data.get('target_tokens')}`.",
        "",
        "| family | mean teacher_lp | Δ lp vs EARLY | mean wall_ms | "
        "Δ vs min(C,F) | mean est GFLOPs | n |",
        "|--------|-----------------|---------------|--------------|"
        "---------------|-----------------|---|",
    ]
    for fam in ("H-EARLY", "H-CHUNK", "H-FUSE", "H-CFUSE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = "—"
        elif fam == "H-CFUSE":
            d1 = f"{st['mean_lp'] - early.get('mean_lp', float('nan')):+.4f}"
            d2 = f"{st['mean_wall'] - floor:+.0f}"
        else:
            d1 = f"{st['mean_lp'] - early.get('mean_lp', float('nan')):+.4f}"
            d2 = "—"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d1} | {st['mean_wall']:.0f} | "
            f"{d2} | {st['mean_gflops']:.3f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Tips stay separate: decode **H-EARLY** (+ optional CHUNK / FUSE). "
            "Do not invent H-CFUSE tip.",
            "",
            "Commands: `npm run nano:cfuse` → `npm run nano:cfuse:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/cfuse_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hcfuse-protocol.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
