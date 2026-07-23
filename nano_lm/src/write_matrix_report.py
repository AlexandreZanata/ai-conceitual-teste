"""Build kill/promote matrix markdown from matrix.json."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ORDER = [
    "B0",
    "B1",
    "B2",
    "B3",
    "B4",
    "H-SPEC",
    "H-SEL",
    "H-BON",
    "H-MAE",
    "H-SUP",
    "H-INT",
    "BoN-uniform",
]
EPS_LP = 0.05  # quality tolerance vs B3 for H-SPEC


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
        speeds = [
            float(x["mean_tokens_per_s"])
            for x in items
            if x.get("mean_tokens_per_s") is not None
        ]
        out[fam] = {
            "mean_lp": sum(lps) / len(lps),
            "mean_wall": sum(walls) / len(walls) if walls else float("nan"),
            "mean_tps": sum(speeds) / len(speeds) if speeds else float("nan"),
            "n": float(len(items)),
        }
    return out


def _decision(fam: str, s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    b2 = stats.get("B2", {}).get("mean_lp")
    if fam == "B2":
        return "BASELINE (claim gate)"
    if fam in {"B0", "B1"}:
        return "control"
    if fam == "B3":
        return "decode control (AR)"
    if fam == "B4":
        return "decode control (BoN)"
    if fam == "H-SPEC":
        return _decide_hspec(s, stats)
    if fam in {"H-SUP", "H-INT", "BoN-uniform"}:
        return _decide_quantum(fam, s, stats)
    if b2 is not None and s["mean_lp"] > b2 + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL / hold (≤ B2)"


def _decide_hspec(s: dict[str, float], stats: dict[str, dict[str, float]]) -> str:
    b3 = stats.get("B3")
    if b3 is None:
        return "needs B3 control"
    faster = s["mean_tps"] > b3["mean_tps"] + 1e-6
    ok_q = s["mean_lp"] >= b3["mean_lp"] - EPS_LP
    if faster and ok_q:
        return "PROMOTE (faster vs B3, quality ok)"
    if not faster:
        return "KILL (no speedup vs B3)"
    return "KILL (quality drop vs B3)"


def _decide_quantum(
    fam: str, s: dict[str, float], stats: dict[str, dict[str, float]]
) -> str:
    bon = stats.get("BoN-uniform", {}).get("mean_lp")
    if bon is None:
        return "ablation"
    if fam == "BoN-uniform":
        return "ablation control"
    if s["mean_lp"] > bon + 1e-6:
        return "PROMOTE (vs uniform BoN)"
    return "KILL (≤ uniform BoN)"


def render(matrix_path: Path) -> str:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = _mean_by_family(data["rows"])
    b2 = stats.get("B2", {}).get("mean_lp")
    wall_s = data.get("wall_s", "n/a")
    wall_line = (
        f"Wall clock (matrix): {wall_s:.1f}s"
        if isinstance(wall_s, (int, float))
        else f"Wall clock (matrix): {wall_s}"
    )
    lines = [
        "# Nano student — kill / promote matrix",
        "",
        f"Source: `{matrix_path}`",
        wall_line,
        "",
        "Primary metric: teacher (TinyStories-33M) mean log-prob of student "
        "completions (higher / less negative is better).",
        "H-SPEC gate: tokens/s > B3 and teacher_lp ≥ B3 − 0.05.",
        "",
        "| family | mean teacher_lp | Δ vs B2 | mean wall_ms | tok/s | n | decision |",
        "|--------|-----------------|---------|--------------|-------|---|-----------|",
    ]
    for fam in ORDER:
        if fam not in stats:
            continue
        s = stats[fam]
        delta = "" if b2 is None or fam == "B2" else f"{s['mean_lp'] - b2:+.4f}"
        wall = f"{s['mean_wall']:.0f}" if s["mean_wall"] == s["mean_wall"] else "—"
        tps = f"{s['mean_tps']:.1f}" if s["mean_tps"] == s["mean_tps"] else "—"
        lines.append(
            f"| {fam} | {s['mean_lp']:.4f} | {delta or '—'} | {wall} | {tps} | "
            f"{int(s['n'])} | {_decision(fam, s, stats)} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Smoke budgets (few steps / small pop). Formal claims need longer runs.",
            "- B3/B4/H-SPEC decode on B2 checkpoints; H-SPEC vs B3 on speed+quality.",
            "- H-SPEC smoke detail: `docs/results/nano-lm/hspec-vs-b3.md`.",
            "- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.",
            "- H-SEL smoke PROMOTE was reversed on formal — see `formal-hsel-vs-b2.md`.",
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
