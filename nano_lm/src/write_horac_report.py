"""Render H-ORAC smoke vs H-EARLY + H-DECM tips."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_report_lib import mean_by_family
from orac_ops import decide_horac


def _load_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("rows", []))


def render(
    orac_path: Path, early_path: Path, decm_path: Path, matrix_path: Path
) -> str:
    rows = _load_rows(orac_path) + _load_rows(early_path) + _load_rows(decm_path)
    matrix = (
        json.loads(matrix_path.read_text(encoding="utf-8"))
        if matrix_path.is_file()
        else {}
    )
    tip_fams = {"H-EARLY", "H-DECM", "H-ORAC"}
    kept = [r for r in matrix.get("rows", []) if r.get("family") not in tip_fams]
    stats = mean_by_family(kept + rows)
    s = stats.get("H-ORAC", {})
    decision = decide_horac(s, stats) if s else "needs H-ORAC rows"
    early = stats.get("H-EARLY", {})
    decm = stats.get("H-DECM", {})
    max_lp = max(early.get("mean_lp", float("nan")), decm.get("mean_lp", float("nan")))
    lines = [
        "# H-ORAC smoke vs H-EARLY × H-DECM (teacher-oracle tip pick)",
        "",
        "Decode both frozen tip genes; teacher picks; charge **winner wall only**.",
        "Diagnostic dual-gate bound. Kill if ≤ max tip or no wall win vs faster tip.",
        "",
        "| family | mean teacher_lp | mean wall_ms | Δ lp vs max tip | n |",
        "|--------|-----------------|--------------|-----------------|---|",
    ]
    for fam in ("H-EARLY", "H-DECM", "H-ORAC"):
        if fam not in stats:
            continue
        st = stats[fam]
        delta = "—" if fam != "H-ORAC" else f"{st['mean_lp'] - max_lp:+.4f}"
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {st['mean_wall']:.0f} | {delta} | "
            f"{int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:orac` → `npm run nano:orac:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--orac",
        type=Path,
        default=Path("results/nano-lm/student-matrix/orac_smoke.json"),
    )
    p.add_argument(
        "--early",
        type=Path,
        default=Path("results/nano-lm/student-matrix/early_smoke.json"),
    )
    p.add_argument(
        "--decm",
        type=Path,
        default=Path("results/nano-lm/student-matrix/decm_smoke.json"),
    )
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/horac-vs-tips.md"),
    )
    args = p.parse_args()
    text = render(args.orac, args.early, args.decm, args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
