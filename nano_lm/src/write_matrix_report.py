"""Build kill/promote matrix markdown from matrix.json."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def _mean_by_family(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[r["family"]].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in buckets.items():
        lps = [float(x["teacher_mean_logprob"]) for x in items]
        walls = [
            float(x["mean_wall_ms"])
            for x in items
            if x.get("mean_wall_ms") is not None
        ]
        out[fam] = {
            "mean_lp": sum(lps) / len(lps),
            "mean_wall": sum(walls) / len(walls) if walls else float("nan"),
            "n": float(len(items)),
        }
    return out


def render(matrix_path: Path) -> str:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = _mean_by_family(data["rows"])
    b2 = stats.get("B2", {}).get("mean_lp")
    lines = [
        "# Nano student — kill / promote matrix",
        "",
        f"Source: `{matrix_path}`",
        f"Wall clock (matrix): {data.get('wall_s', 'n/a'):.1f}s"
        if isinstance(data.get("wall_s"), (int, float))
        else f"Wall clock (matrix): {data.get('wall_s', 'n/a')}",
        "",
        "Primary metric: teacher (TinyStories-33M) mean log-prob of student "
        "completions (higher / less negative is better).",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n | decision |",
        "|--------|-----------------|---------|--------------|---|-----------|",
    ]
    order = [
        "B0",
        "B1",
        "B2",
        "H-SEL",
        "H-BON",
        "H-MAE",
        "H-SUP",
        "H-INT",
        "BoN-uniform",
    ]
    for fam in order:
        if fam not in stats:
            continue
        s = stats[fam]
        delta = "" if b2 is None or fam == "B2" else f"{s['mean_lp'] - b2:+.4f}"
        if fam == "B2":
            decision = "BASELINE (claim gate)"
        elif fam in {"B0", "B1"}:
            decision = "control"
        elif fam in {"H-SUP", "H-INT", "BoN-uniform"}:
            # inference selection ablation — compare to BoN-uniform
            bon = stats.get("BoN-uniform", {}).get("mean_lp")
            if bon is None:
                decision = "ablation"
            elif fam == "BoN-uniform":
                decision = "ablation control"
            elif s["mean_lp"] > bon + 1e-6:
                decision = "PROMOTE (vs uniform BoN)"
            else:
                decision = "KILL (≤ uniform BoN)"
        else:
            if b2 is not None and s["mean_lp"] > b2 + 1e-6:
                decision = "PROMOTE (beats B2)"
            else:
                decision = "KILL / hold (≤ B2)"
        wall = f"{s['mean_wall']:.0f}" if s["mean_wall"] == s["mean_wall"] else "—"
        lines.append(
            f"| {fam} | {s['mean_lp']:.4f} | {delta or '—'} | {wall} | "
            f"{int(s['n'])} | {decision} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Smoke budgets (few steps / small pop). Formal claims need longer runs.",
            "- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.",
            "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/kill-promote-matrix.md"),
    )
    args = p.parse_args()
    text = render(args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
