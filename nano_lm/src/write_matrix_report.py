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
    "H-TOU",
    "H-XOV",
    "H-NIC",
    "H-MUT",
    "H-RAN",
    "H-AGE",
    "H-MOR",
    "H-SPE",
    "H-SEX",
    "H-ANTI",
    "H-TAX",
    "H-CAN",
    "H-PAR",
    "H-SYM",
    "H-FOS",
    "H-ZOM",
    "H-LOTU",
    "H-GLD",
    "H-SEA",
    "H-RPS",
    "H-CAT",
    "H-HIB",
    "H-SHO",
    "H-HOLD",
    "H-FXS",
    "H-LOFI",
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
    "- H-TOU smoke detail: `docs/results/nano-lm/htou-vs-hsel.md`.",
    "- H-XOV smoke detail: `docs/results/nano-lm/hxov-vs-hsel.md`.",
    "- H-NIC smoke detail: `docs/results/nano-lm/hnic-vs-hsel.md`.",
    "- H-MUT smoke detail: `docs/results/nano-lm/hmut-vs-hsel.md`.",
    "- H-RAN smoke detail: `docs/results/nano-lm/hran-vs-hsel.md`.",
    "- H-AGE smoke detail: `docs/results/nano-lm/hage-vs-hsel.md`.",
    "- H-MOR smoke detail: `docs/results/nano-lm/hmor-vs-hsel.md`.",
    "- H-SPE smoke detail: `docs/results/nano-lm/hspe-vs-hsel.md`.",
    "- H-SEX smoke detail: `docs/results/nano-lm/hsex-vs-hsel.md`.",
    "- H-ANTI smoke detail: `docs/results/nano-lm/hanti-vs-hsel.md`.",
    "- H-TAX smoke detail: `docs/results/nano-lm/htax-vs-hsel.md`.",
    "- H-CAN smoke detail: `docs/results/nano-lm/hcan-vs-hsel.md`.",
    "- H-PAR smoke detail: `docs/results/nano-lm/hpar-vs-hsel.md`.",
    "- H-SYM smoke detail: `docs/results/nano-lm/hsym-vs-hsel.md`.",
    "- H-FOS smoke detail: `docs/results/nano-lm/hfos-vs-hsel.md`.",
    "- H-ZOM smoke detail: `docs/results/nano-lm/hzom-vs-hsel.md`.",
    "- H-LOTU smoke detail: `docs/results/nano-lm/hlotu-vs-hsel.md`.",
    "- H-GLD smoke detail: `docs/results/nano-lm/hgld-vs-hfit.md`.",
    "- H-SEA smoke detail: `docs/results/nano-lm/hsea-vs-hfit.md`.",
    "- H-RPS smoke detail: `docs/results/nano-lm/hrps-vs-hsel.md`.",
    "- H-CAT smoke detail: `docs/results/nano-lm/hcat-vs-hsel.md`.",
    "- H-HIB smoke detail: `docs/results/nano-lm/hhib-vs-hsel.md`.",
    "- H-SHO smoke detail: `docs/results/nano-lm/hsho-vs-hsel.md`.",
    "- H-HOLD smoke detail: `docs/results/nano-lm/hhold-vs-b2.md`.",
    "- H-FXS smoke detail: `docs/results/nano-lm/hfxs-vs-fit-xov.md`.",
    "- H-LOFI smoke detail: `docs/results/nano-lm/hlofi-vs-hfit.md`.",
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
        "H-TOU gate: teacher_lp > H-SEL (tournament vs truncation).",
        "H-XOV gate: no diversity collapse and teacher_lp > H-SEL.",
        "H-NIC gate: diversity↑ and teacher_lp > H-SEL.",
        "H-MUT gate: teacher_lp > H-SEL (adaptive vs fixed mutate).",
        "H-RAN gate: teacher_lp > H-SEL (rank vs truncation).",
        "H-AGE gate: teacher_lp > H-SEL (ALPS vs flat).",
        "H-MOR gate: teacher_lp > H-SEL (mortality vs no cull).",
        "H-SPE gate: teacher_lp > H-SEL (islands vs single).",
        "H-SEX gate: teacher_lp > H-SEL (mate choice vs truncation).",
        "H-ANTI gate: teacher_lp > H-SEL (anti-selection vs truncation).",
        "H-TAX gate: teacher_lp > H-SEL (wealth tax vs no tax).",
        "H-CAN gate: no NaN and teacher_lp > H-SEL (LN cannibalism).",
        "H-PAR gate: parasite does not dominate and teacher_lp > H-SEL.",
        "H-SYM gate: teacher_lp > H-SEL (obligate pair vs truncation).",
        "H-FOS gate: teacher_lp > H-SEL (fossil resurrect vs no-resurrect).",
        "H-ZOM gate: no diverge and teacher_lp > H-SEL (zombie reinject).",
        "H-LOTU gate: teacher_lp > H-SEL (underdog lottery vs truncation).",
        "H-GLD gate: teacher_lp > H-FIT (Goldilocks vs max-lp fitness).",
        "H-SEA gate: teacher_lp > H-FIT (seasonal vs fixed H-FIT).",
        "H-RPS gate: ≥2 niches and teacher_lp > H-SEL (RPS niches).",
        "H-CAT gate: teacher_lp > H-SEL (catastrophe vs steady).",
        "H-HIB gate: teacher_lp > H-SEL (hibernate vs full eval).",
        "H-SHO gate: teacher_lp > H-SEL (shock vs plain mutate).",
        "H-HOLD gate: no overfit and teacher_lp > B2 (holdout fit≠eval).",
        "H-FXS gate: teacher_lp > max(H-FIT, H-XOV) (FIT×XOV×SHO stack).",
        "H-LOFI gate: teacher_lp ≥ H-FIT−ε and wall_save (fewer teacher forwards).",
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
