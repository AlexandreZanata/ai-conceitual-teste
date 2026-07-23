"""Build kill/promote matrix markdown from matrix.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import decision, mean_by_family

ORDER = [
    "B0",
    "B1",
    "B2",
    "B3",
    "B4",
    "H-SPEC",
    "H-DEC",
    "H-SEL",
    "H-BAL",
    "H-LAM",
    "H-ELI",
    "H-FIT",
    "H-ENT",
    "KD-cos",
    "H-ANN",
    "H-BON",
    "H-MAE",
    "H-SUP",
    "H-INT",
    "BoN-uniform",
]

NOTES = [
    "",
    "## Notes",
    "",
    "- Smoke budgets (few steps / small pop). Formal claims need longer runs.",
    "- B3/B4/H-SPEC decode on B2 checkpoints; H-SPEC vs B3 on speed+quality.",
    "- H-SPEC smoke detail: `docs/results/nano-lm/hspec-vs-b3.md`.",
    "- H-BAL smoke detail: `docs/results/nano-lm/hbal-vs-b2.md`.",
    "- H-DEC smoke detail: `docs/results/nano-lm/hdec-vs-b4.md`.",
    "- H-LAM smoke detail: `docs/results/nano-lm/hlam-vs-hbal.md`.",
    "- H-ELI smoke detail: `docs/results/nano-lm/heli-vs-hsel.md`.",
    "- H-ENT smoke detail: `docs/results/nano-lm/hent-vs-b2.md`.",
    "- H-ANN smoke detail: `docs/results/nano-lm/hann-vs-kdcos.md`.",
    "- H-FIT smoke detail: `docs/results/nano-lm/hfit-vs-hsel.md`.",
    "- H-SUP/H-INT rows are decode selection scores on teacher, not trained students.",
    "- H-SEL smoke PROMOTE was reversed on formal — see `formal-hsel-vs-b2.md`.",
    "- Agenda: `docs/NANO-STUDENT-AGENDA.md`.",
    "",
]


def render(matrix_path: Path) -> str:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
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
        "H-LAM gate: stable and teacher_lp > H-BAL.",
        "H-ELI gate: no diversity collapse and teacher_lp > H-SEL.",
        "H-ENT gate: heads not collapsed and teacher_lp > B2.",
        "H-ANN gate: teacher_lp > KD-cos (cosine schedule control).",
        "H-FIT gate: teacher_lp > H-SEL (claim-aligned fitness).",
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
            f"{int(s['n'])} | {decision(fam, s, stats)} |"
        )
    lines.extend(NOTES)
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
