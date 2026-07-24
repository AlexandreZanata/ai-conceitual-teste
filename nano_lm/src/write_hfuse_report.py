"""Render H-FUSE protocol smoke (FLASH ⊕ KVSEL; not a tip)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from fuse_ops import decide_hfuse


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
    s = stats.get("H-FUSE", {})
    decision = decide_hfuse(s, stats) if s else "needs H-FUSE rows"
    early = stats.get("H-EARLY", {})
    flash = stats.get("H-FLASH", {})
    kvsel = stats.get("H-KVSEL", {})
    floor = min(
        flash.get("mean_wall", float("nan")),
        kvsel.get("mean_wall", float("nan")),
    )
    lines = [
        "# H-FUSE protocol — FLASH ⊕ KVSEL",
        "",
        "Stack **decode utils** H-FLASH (SDPA) and H-KVSEL (gated KV) on frozen "
        "EARLY tip genes + frozen `kv_threshold` from prior KVSEL smoke.",
        "Dual-budget mean over the same budgets as H-KVSEL.",
        "This is a **protocol note**, not a compose tip H-ID.",
        "PROTOCOL iff lp ≥ EARLY−ε and wall < min(FLASH, KVSEL); else KILL.",
        f"Note: `{data.get('note')}`. Budgets: `{data.get('budgets')}`.",
        "",
        "| family | mean teacher_lp | Δ lp vs EARLY | mean wall_ms | "
        "Δ vs min(F,K) | mean est GFLOPs | n |",
        "|--------|-----------------|---------------|--------------|"
        "---------------|-----------------|---|",
    ]
    for fam in ("H-EARLY", "H-FLASH", "H-KVSEL", "H-FUSE"):
        if fam not in stats:
            continue
        st = stats[fam]
        if fam == "H-EARLY":
            d1 = d2 = "—"
        elif fam == "H-FUSE":
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
            "Tips stay separate: decode **H-EARLY** (+ optional FLASH or KVSEL). "
            "Do not invent H-FUSE tip.",
            "",
            "Commands: `npm run nano:fuse` → `npm run nano:fuse:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/fuse_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hfuse-protocol.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
